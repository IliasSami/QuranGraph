import corpusData from "./corpus.json" with { type: "json" };
import knowledgeData from "./knowledge.json" with { type: "json" };
import surahsData from "./surahs.json" with { type: "json" };
import { parseReference, parseSurahOnly } from "./reference.ts";
import {
  arabicKey,
  arabicSkeleton,
  banglaKey,
  banglaStem,
  editDistance,
  latinFold,
  scriptOf,
  tokenize,
  translitKey
} from "./normalize.ts";

export interface SearchResult {
  ref: string; // "surah:ayah"
  score: number;
  matchType: "reference" | "surah" | "entity" | "arabic" | "phrase" | "concept" | "text";
  title?: string;
  s: number;
  a: number;
  surah_name_en: string;
  surah_name_ar: string;
  surah_name_bn: string;
  surah_translit: string;
  ar: string;
  ar_u: string;
  tr: string;
  en: string;
  bn: string;
  is_surah?: boolean;
  total_ayat?: number;
  surah_type?: string;
}

export interface AyahRecord {
  s: number;
  a: number;
  ar: string;
  ar_u?: string;
  en: string;
  bn: string;
  tr?: string;
}

export interface SurahRecord {
  id: number;
  name_ar: string;
  name_translit: string;
  name_en: string;
  name_bn: string;
  ayat: number;
  type?: string;
  revelation_order?: number;
  rukus?: number;
}

interface KnowledgeEntry {
  id: string;
  title_en: string;
  title_ar: string;
  title_bn: string;
  aliases: string[];
  ayat: string[];
}

const CORPUS: AyahRecord[] = corpusData;
const KNOWLEDGE: KnowledgeEntry[] = knowledgeData;
const SURAHS: SurahRecord[] = surahsData;

// Fast lookups
const corpusMap = new Map<string, AyahRecord>();
for (const c of CORPUS) {
  corpusMap.set(`${c.s}:${c.a}`, c);
}

const surahMap = new Map<number, SurahRecord>();
for (const s of SURAHS) {
  surahMap.set(s.id, s);
}

// Precompute normalised forms for knowledge entries
interface IndexedKnowledge {
  entry: KnowledgeEntry;
  latinAliases: string[];
  arabicAliases: string[];
  banglaAliases: string[];
  translitAliases: string[];
}

const INDEXED_KNOWLEDGE: IndexedKnowledge[] = KNOWLEDGE.map((entry) => {
  const latinAliases: string[] = [];
  const arabicAliases: string[] = [];
  const banglaAliases: string[] = [];
  const translitAliases: string[] = [];

  for (const a of entry.aliases) {
    const sc = scriptOf(a);
    if (sc === "arabic") {
      arabicAliases.push(arabicKey(a));
    } else if (sc === "bangla") {
      banglaAliases.push(banglaKey(a));
      banglaAliases.push(banglaStem(banglaKey(a)));
    } else {
      latinAliases.push(latinFold(a));
      translitAliases.push(translitKey(a));
    }
  }

  return {
    entry,
    latinAliases,
    arabicAliases,
    banglaAliases,
    translitAliases
  };
});

// Precompute corpus search keys
const CORPUS_KEYS = CORPUS.map((rec) => ({
  ref: `${rec.s}:${rec.a}`,
  s: rec.s,
  a: rec.a,
  arKey: arabicKey(rec.ar),
  arSkel: arabicSkeleton(arabicKey(rec.ar)),
  enLower: rec.en.toLowerCase(),
  enFold: latinFold(rec.en),
  bnKey: banglaKey(rec.bn),
  bnStemmed: banglaStem(banglaKey(rec.bn)),
  trFold: latinFold(rec.tr || ""),
  trKey: translitKey(rec.tr || "")
}));

/**
 * Searches the Quran by reference, entity, concept, Arabic text, English/Bangla translations, or transliteration.
 */
export function search(rawQuery: string, limit = 10): SearchResult[] {
  const query = rawQuery.trim();
  if (!query) return [];

  const scores = new Map<
    string,
    {
      score: number;
      matchType: SearchResult["matchType"];
      title?: string;
      is_surah?: boolean;
    }
  >();

  const addScore = (
    ref: string,
    points: number,
    type: SearchResult["matchType"],
    title?: string,
    is_surah?: boolean
  ) => {
    const existing = scores.get(ref);
    if (!existing || points > existing.score) {
      scores.set(ref, {
        score: points,
        matchType: type,
        title: title || existing?.title,
        is_surah: is_surah ?? existing?.is_surah
      });
    } else if (existing) {
      existing.score += points * 0.2; // cumulative boost
    }
  };

  // Channel 1: Reference Parser ("2:255", "surah 2 verse 255", "al-baqarah 255", "বাকারা ২৫৫", "البقرة ٢٥٥")
  const refMatch = parseReference(query);
  if (refMatch) {
    addScore(refMatch.ref, 1000, "reference");
  }

  // Channel 0: Direct Surah match ("baqarah", "surah yasin", "surah mulk", "kahf", "সূরা বাকারা", "surah 18")
  const surahMatchId = parseSurahOnly(query);
  if (surahMatchId && surahMatchId >= 1 && surahMatchId <= 114) {
    const sInfo = surahMap.get(surahMatchId);
    if (sInfo) {
      const topAyahRef = `${surahMatchId}:1`;
      addScore(
        topAyahRef,
        980,
        "surah",
        `Surah ${sInfo.name_translit} (${sInfo.name_ar}) — ${sInfo.name_en}`,
        true
      );
      if (sInfo.ayat >= 2) {
        addScore(`${surahMatchId}:2`, 940, "surah");
      }
      if (sInfo.ayat >= 3) {
        addScore(`${surahMatchId}:3`, 930, "surah");
      }
    }
  }

  const qScript = scriptOf(query);
  const qLatin = latinFold(query);
  const qTranslit = translitKey(query);
  const qArabic = arabicKey(query);
  const qArabicSkel = arabicSkeleton(qArabic);
  const qBangla = banglaKey(query);
  const qBanglaStem = banglaStem(qBangla);

  // Channel 2: Curated Knowledge & Named Passages & Concepts
  for (const ik of INDEXED_KNOWLEDGE) {
    let matched = false;
    let rankScore = 0;

    if (qScript === "arabic") {
      for (const al of ik.arabicAliases) {
        if (qArabic === al || (al.length >= 2 && qArabic.includes(al)) || (qArabic.length >= 3 && al.includes(qArabic))) {
          matched = true;
          rankScore = 800;
          break;
        }
      }
    } else if (qScript === "bangla") {
      for (const al of ik.banglaAliases) {
        if (qBangla === al || qBanglaStem === al || (al.length >= 2 && qBangla.includes(al)) || (qBangla.length >= 3 && al.includes(qBangla))) {
          matched = true;
          rankScore = 800;
          break;
        }
      }
    } else {
      // Latin / English / Transliteration
      for (const al of ik.latinAliases) {
        if (
          qLatin === al ||
          (al.length >= 4 && qLatin.includes(al)) ||
          (qLatin.length >= 4 && al.includes(qLatin))
        ) {
          matched = true;
          rankScore = 800;
          break;
        }
      }
      if (!matched && qTranslit.length >= 3) {
        for (const al of ik.translitAliases) {
          if (qTranslit === al || editDistance(qTranslit, al, 1) <= 1) {
            matched = true;
            rankScore = 750;
            break;
          }
        }
      }
    }

    if (matched) {
      // Add ayat in knowledge order, decaying slightly for lower ranked ayat
      ik.entry.ayat.forEach((ayahRef, idx) => {
        const decay = Math.max(10, 50 - idx * 10);
        addScore(ayahRef, rankScore + decay, "concept", ik.entry.title_en);
      });
    }
  }

  // Channel 3: Corpus Text Search (Arabic, English, Bangla, Transliteration)
  const tokens = tokenize(query).filter((t) => !t.stop);
  const qTerms = tokens.map((t) => t.term);

  for (let i = 0; i < CORPUS_KEYS.length; i++) {
    const ck = CORPUS_KEYS[i];
    let ayahScore = 0;
    let matchType: SearchResult["matchType"] = "text";

    if (qScript === "arabic") {
      if (qArabic.length >= 3) {
        if (ck.arKey.includes(qArabic)) {
          ayahScore = 500 + qArabic.length * 10;
          matchType = "arabic";
        } else if (qArabicSkel.length >= 3 && ck.arSkel.includes(qArabicSkel)) {
          ayahScore = 400 + qArabicSkel.length * 10;
          matchType = "arabic";
        }
      }
    } else if (qScript === "bangla") {
      // Bangla translation search
      if (qBangla.length >= 3 && ck.bnKey.includes(qBangla)) {
        ayahScore = 450 + qBangla.length * 5;
        matchType = "phrase";
      } else if (tokens.length > 0) {
        let matchCount = 0;
        for (const t of qTerms) {
          if (ck.bnStemmed.includes(t)) matchCount++;
        }
        if (matchCount > 0) {
          ayahScore = matchCount * 60;
        }
      }
    } else {
      // Latin script: English translation or transliteration
      // 1. Exact phrase in English translation
      if (qLatin.length >= 4 && ck.enFold.includes(qLatin)) {
        ayahScore = 450 + qLatin.length * 5;
        matchType = "phrase";
      }
      // 2. Exact phrase in Arabic transliteration
      else if (qLatin.length >= 4 && ck.trFold.includes(qLatin)) {
        ayahScore = 550 + qLatin.length * 5;
        matchType = "phrase";
      }
      // 3. Phonetic transliteration phrase match
      else if (qTranslit.length >= 5 && ck.trKey.includes(qTranslit)) {
        ayahScore = 480 + qTranslit.length * 4;
        matchType = "phrase";
      }
      // 4. Token matches (English & Transliteration)
      else if (tokens.length > 0) {
        let enMatchCount = 0;
        let trMatchCount = 0;

        for (const t of qTerms) {
          if (ck.enFold.includes(t)) enMatchCount++;
          if (ck.trFold.includes(t) || (t.length >= 4 && ck.trKey.includes(translitKey(t)))) {
            trMatchCount++;
          }
        }

        if (trMatchCount > 0) {
          const ratio = trMatchCount / tokens.length;
          ayahScore = Math.max(ayahScore, ratio * 200 + trMatchCount * 45);
          matchType = "text";
        }

        if (enMatchCount > 0) {
          const ratio = enMatchCount / tokens.length;
          ayahScore = Math.max(ayahScore, ratio * 150 + enMatchCount * 30);
          matchType = "text";
        }
      }
    }

    if (ayahScore > 0) {
      addScore(ck.ref, ayahScore, matchType);
    }
  }

  // Channel 4: Typo Resiliency & Fuzzy Fallback
  if (scores.size === 0 && qLatin.length >= 4) {
    for (const ik of INDEXED_KNOWLEDGE) {
      for (const al of ik.latinAliases) {
        if (al.length >= 4 && editDistance(qLatin, al, 2) <= 2) {
          ik.entry.ayat.forEach((ayahRef, idx) => {
            const decay = Math.max(10, 40 - idx * 10);
            addScore(ayahRef, 300 + decay, "concept", ik.entry.title_en);
          });
          break;
        }
      }
      if (scores.size > 0) break;
    }
  }

  // Sort by score descending
  const sortedEntries = Array.from(scores.entries())
    .map(([ref, data]) => ({
      ref,
      score: Math.round(data.score),
      matchType: data.matchType,
      title: data.title,
      is_surah: data.is_surah
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);

  // Enrich results with complete text, transliteration and metadata
  const results: SearchResult[] = sortedEntries.map((item) => {
    const [sStr, aStr] = item.ref.split(":");
    const sId = parseInt(sStr, 10);
    const aNum = parseInt(aStr, 10);

    const surah = surahMap.get(sId);
    const ayah = corpusMap.get(item.ref);

    return {
      ref: item.ref,
      score: item.score,
      matchType: item.matchType,
      title: item.title,
      s: sId,
      a: aNum,
      surah_name_en: surah?.name_en || "",
      surah_name_ar: surah?.name_ar || "",
      surah_name_bn: surah?.name_bn || "",
      surah_translit: surah?.name_translit || `Surah ${sId}`,
      ar: ayah?.ar || "",
      ar_u: ayah?.ar_u || ayah?.ar || "",
      tr: ayah?.tr || "",
      en: ayah?.en || "",
      bn: ayah?.bn || "",
      is_surah: item.is_surah,
      total_ayat: surah?.ayat,
      surah_type: surah?.type
    };
  });

  return results;
}
