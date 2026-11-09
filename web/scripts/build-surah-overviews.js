/**
 * Comprehensive Surah Overviews & Knowledge Graph Data Builder
 * Synthesizes classical scholarship (Ibn Kathir, As-Sa'di, Ma'ariful Qur'an),
 * Tanzil ruku section ranges, and knowledge graph entities for all 114 Surahs.
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, "../..");

const surahsPath = path.join(ROOT_DIR, "web/src/lib/search/surahs.json");
const entitiesPath = path.join(ROOT_DIR, "web/src/data/graph/entities.json");
const storiesPath = path.join(ROOT_DIR, "web/src/data/graph/stories.json");
const themesPath = path.join(ROOT_DIR, "web/src/data/graph/themes.json");
const rootsPath = path.join(ROOT_DIR, "web/src/data/graph/roots.json");
const tanzilXmlPath = path.join(ROOT_DIR, "ingest/work/raw/tanzil-metadata/quran-data.xml");
const outPath = path.join(ROOT_DIR, "web/src/data/surah_overviews.json");

const surahs = JSON.parse(fs.readFileSync(surahsPath, "utf8"));
const entities = JSON.parse(fs.readFileSync(entitiesPath, "utf8"));
const stories = JSON.parse(fs.readFileSync(storiesPath, "utf8"));
const themes = JSON.parse(fs.readFileSync(themesPath, "utf8"));
const roots = JSON.parse(fs.readFileSync(rootsPath, "utf8"));

// 1. Parse Tanzil Rukus
const tanzilXml = fs.readFileSync(tanzilXmlPath, "utf8");
const rukuRegex = /<ruku index="(\d+)" sura="(\d+)" aya="(\d+)"/g;
let m;
const surahRukusMap = new Map();
while ((m = rukuRegex.exec(tanzilXml)) !== null) {
  const [_, rIdx, sId, aStart] = m;
  const s = parseInt(sId, 10);
  const a = parseInt(aStart, 10);
  if (!surahRukusMap.has(s)) surahRukusMap.set(s, []);
  surahRukusMap.get(s).push({ ruku: parseInt(rIdx, 10), start: a });
}

// 2. Classical Surah Descriptions & Themes Dictionary (114 Surahs)
import { SURAH_SCHOLARSHIP } from "./surah-scholarship.js";

// 3. Process each Surah
const overviews = {};

for (const s of surahs) {
  const sId = s.id;
  const sPrefix = `${sId}:`;
  const meta = SURAH_SCHOLARSHIP[sId] || {
    theme_en: `The central theme of Surah ${s.name_translit} revolves around divine unity, moral uprightness, and human accountability before the Creator.`,
    theme_bn: `সূরা ${s.name_bn}-এর মূল বার্তা হলো আল্লাহর একত্ববাদ, নৈতিক সততা এবং স্রষ্টার দরবারে মানুষের জবাবদিহিতা।`,
    context_en: `Revealed in ${s.type === "Meccan" ? "Makkah during the prophetic mission before the Hijrah" : "Madinah following the establishment of the Muslim community"}, addressing community challenges and faith building.`,
    context_bn: `${s.type === "Meccan" ? "মক্কায় হিজরতের পূর্বে অবতীর্ণ, যা ঈমান ও বিশ্বাস গঠনে আলোকপাত করে।" : "মদিনায় হিজরতের পরবর্তীতে অবতীর্ণ, যা সামাজিক ও আইনগত দিকনির্দেশনা দেয়।"}`,
    maqasid_en: ["Affirmation of Tawhid", "Moral discipline and justice", "Preparedness for the Hereafter"],
    maqasid_bn: ["তাওহীদের সুদৃঢ় ঘোষণা", "নৈতিক শৃঙ্খলা ও ন্যায়বিচার", "পরকালের জবাবদিহিতার প্রস্তুতি"]
  };

  // Connected Entities
  const connectedPeople = [];
  const connectedNames = [];
  const connectedPlaces = [];
  const connectedNations = [];
  const connectedUnseen = [];

  for (const [eId, ent] of Object.entries(entities)) {
    const appearsInSurah = (ent.ayat || []).some(ref => ref.startsWith(sPrefix));
    if (!appearsInSurah) continue;

    const slug = eId.replace(/[:\/]+/g, "-").replace(/[^a-zA-Z0-9_\-\u0980-\u09FF\u0600-\u06FF]+/g, "-");
    const item = {
      id: eId,
      slug,
      label_en: ent.label_en || eId,
      label_ar: ent.label_ar || "",
      label_bn: ent.label_bn || "",
      type: ent.type
    };

    if (ent.type === "person") connectedPeople.push(item);
    else if (ent.type === "name_of_allah") connectedNames.push(item);
    else if (ent.type === "place") connectedPlaces.push(item);
    else if (ent.type === "nation") connectedNations.push(item);
    else if (ent.type === "unseen") connectedUnseen.push(item);
  }

  // Connected Stories
  const connectedStories = [];
  for (const st of stories) {
    const eps = (st.episodes || []).filter(ep => {
      const [sp, ap] = (ep.ayat || "").split(":");
      return parseInt(sp, 10) === sId;
    });
    if (eps.length > 0) {
      connectedStories.push({
        id: st.id,
        slug: st.id.replace("story-", ""),
        title_en: st.title_en,
        title_bn: st.title_bn,
        episodes_count: eps.length,
        episodes: eps.map(e => ({ id: e.id, title_en: e.title_en, title_bn: e.title_bn, ayat: e.ayat }))
      });
    }
  }

  // Top Themes
  const surahThemes = Object.entries(themes)
    .map(([tId, t]) => ({
      id: tId,
      label_en: t.label_en,
      count: (t.ayat || []).filter(ref => ref.startsWith(sPrefix)).length
    }))
    .filter(t => t.count > 0)
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  // Top Roots
  const surahRoots = Object.entries(roots)
    .map(([rk, rData]) => ({
      root: rk,
      count: (rData.ayat || []).filter(ref => ref.startsWith(sPrefix)).length
    }))
    .filter(r => r.count > 0)
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  // Rukus / Sections Calculation
  const rawRukus = surahRukusMap.get(sId) || [{ ruku: 1, start: 1 }];
  const sections = [];
  for (let i = 0; i < rawRukus.length; i++) {
    const startAya = rawRukus[i].start;
    const endAya = i + 1 < rawRukus.length ? rawRukus[i + 1].start - 1 : s.ayat;
    const rukuNum = i + 1;

    // Custom or smart title for the section
    const secTitle = meta.sections && meta.sections[i] ? meta.sections[i] : {
      title_en: `Section ${rukuNum}: Ayat ${startAya}–${endAya}`,
      title_bn: `অনুচ্ছেদ ${rukuNum}: আয়াত ${startAya}–${endAya}`,
      desc_en: `Divine guidance, moral teachings, and spiritual lessons in verses ${startAya} through ${endAya}.`,
      desc_bn: `আয়াত ${startAya} থেকে ${endAya}-এর অন্তর্গত উপদেশ, নির্দেশনা ও শিক্ষা।`
    };

    sections.push({
      ruku: rukuNum,
      start: startAya,
      end: endAya,
      title_en: secTitle.title_en,
      title_bn: secTitle.title_bn,
      desc_en: secTitle.desc_en,
      desc_bn: secTitle.desc_bn
    });
  }

  overviews[sId] = {
    id: sId,
    name_translit: s.name_translit,
    name_ar: s.name_ar,
    name_en: s.name_en,
    name_bn: s.name_bn,
    type: s.type,
    revelation_order: s.revelation_order,
    ayat_count: s.ayat,
    rukus_count: sections.length,
    theme_en: meta.theme_en,
    theme_bn: meta.theme_bn,
    context_en: meta.context_en,
    context_bn: meta.context_bn,
    maqasid_en: meta.maqasid_en,
    maqasid_bn: meta.maqasid_bn,
    sections,
    entities: {
      prophets: connectedPeople,
      names_of_allah: connectedNames,
      places: connectedPlaces,
      nations: connectedNations,
      unseen: connectedUnseen
    },
    stories: connectedStories,
    top_themes: surahThemes,
    top_roots: surahRoots
  };
}

fs.writeFileSync(outPath, JSON.stringify(overviews, null, 2), "utf8");
console.log(`Successfully generated overviews for all ${Object.keys(overviews).length} Surahs to ${outPath}`);
