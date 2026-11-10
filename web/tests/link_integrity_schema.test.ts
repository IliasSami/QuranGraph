import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { entityIdToSlug } from "../src/lib/graph/subgraph.ts";
import surahsData from "../src/lib/search/surahs.json" with { type: "json" };
import entitiesData from "../src/data/graph/entities.json" with { type: "json" };
import storiesData from "../src/data/graph/stories.json" with { type: "json" };
import rootsData from "../src/data/graph/roots.json" with { type: "json" };
import overviewsData from "../src/data/surah_overviews.json" with { type: "json" };

const BASE_URL = "https://qurangraph.iliassami57.workers.dev";

test("Surah Overviews: 114 Surahs complete coverage and structure", () => {
  const surahIds = Object.keys(overviewsData).map(Number);
  assert.equal(surahIds.length, 114, "Expected all 114 surahs to be in surah_overviews.json");

  for (let sId = 1; sId <= 114; sId++) {
    const ov = (overviewsData as Record<string, any>)[String(sId)];
    assert.ok(ov, `Surah ${sId} overview must exist`);
    assert.equal(ov.id, sId);
    assert.ok(ov.name_translit, `Surah ${sId} must have name_translit`);
    assert.ok(ov.name_ar, `Surah ${sId} must have name_ar`);
    assert.ok(ov.name_en, `Surah ${sId} must have name_en`);
    assert.ok(ov.name_bn, `Surah ${sId} must have name_bn`);
  }
});

test("Surah Overviews: Ruku passage ranges and Tanzil alignment", () => {
  const surahMap = new Map(surahsData.map((s) => [s.id, s]));
  let totalSections = 0;

  for (let sId = 1; sId <= 114; sId++) {
    const ov = (overviewsData as Record<string, any>)[String(sId)];
    const surah = surahMap.get(sId);
    assert.ok(surah, `Surah ${sId} metadata must exist`);

    const sections = ov.sections || [];
    assert.ok(sections.length > 0, `Surah ${sId} must have sections`);
    assert.equal(sections.length, ov.rukus_count, `Surah ${sId} sections count must match rukus_count`);
    totalSections += sections.length;

    let expectedStart = 1;
    for (let i = 0; i < sections.length; i++) {
      const sec = sections[i];
      assert.equal(sec.ruku, i + 1, `Surah ${sId} section ${i} ruku number mismatch`);
      assert.ok(Number.isInteger(sec.start) && sec.start > 0, `Surah ${sId} ruku ${sec.ruku} start must be positive integer`);
      assert.ok(Number.isInteger(sec.end) && sec.end > 0, `Surah ${sId} ruku ${sec.ruku} end must be positive integer`);
      assert.ok(sec.start <= sec.end, `Surah ${sId} ruku ${sec.ruku} start (${sec.start}) must be <= end (${sec.end})`);
      assert.ok(sec.end <= surah.ayat, `Surah ${sId} ruku ${sec.ruku} end (${sec.end}) must be <= surah.ayat (${surah.ayat})`);
      assert.equal(sec.start, expectedStart, `Surah ${sId} ruku ${sec.ruku} must start at ${expectedStart} (no gaps or overlaps)`);

      assert.ok(sec.title_en && sec.title_en.length > 3, `Surah ${sId} ruku ${sec.ruku} must have title_en`);
      assert.ok(sec.title_bn && sec.title_bn.length > 3, `Surah ${sId} ruku ${sec.ruku} must have title_bn`);
      assert.ok(sec.desc_en && sec.desc_en.length > 5, `Surah ${sId} ruku ${sec.ruku} must have desc_en`);
      assert.ok(sec.desc_bn && sec.desc_bn.length > 5, `Surah ${sId} ruku ${sec.ruku} must have desc_bn`);

      expectedStart = sec.end + 1;
    }

    assert.equal(expectedStart - 1, surah.ayat, `Surah ${sId} last section must end exactly at total verses (${surah.ayat})`);
  }

  // The Quran has exactly 556 rukus in the classical Tanzil index
  assert.equal(totalSections, 556, "Total rukus across all 114 surahs must equal 556");
});

test("Surah Overviews: Maqasid, Context, and Thesis non-empty and non-placeholder", () => {
  const placeholders = ["placeholder", "tbd", "todo", "lorem", "coming soon", "n/a"];

  for (let sId = 1; sId <= 114; sId++) {
    const ov = (overviewsData as Record<string, any>)[String(sId)];

    // Theme (thesis)
    assert.ok(ov.theme_en && ov.theme_en.trim().length >= 15, `Surah ${sId} theme_en is too short`);
    assert.ok(ov.theme_bn && ov.theme_bn.trim().length >= 15, `Surah ${sId} theme_bn is too short`);

    // Context (historical context)
    assert.ok(ov.context_en && ov.context_en.trim().length >= 15, `Surah ${sId} context_en is too short`);
    assert.ok(ov.context_bn && ov.context_bn.trim().length >= 15, `Surah ${sId} context_bn is too short`);

    // Maqasid (primary objectives)
    assert.ok(Array.isArray(ov.maqasid_en) && ov.maqasid_en.length >= 2, `Surah ${sId} maqasid_en must have >= 2 items`);
    assert.ok(Array.isArray(ov.maqasid_bn) && ov.maqasid_bn.length >= 2, `Surah ${sId} maqasid_bn must have >= 2 items`);

    for (const p of placeholders) {
      assert.ok(!ov.theme_en.toLowerCase().includes(p), `Surah ${sId} theme_en contains placeholder '${p}'`);
      assert.ok(!ov.context_en.toLowerCase().includes(p), `Surah ${sId} context_en contains placeholder '${p}'`);
    }
  }
});

test("Surah Overviews: Entity references and slug integrity against Knowledge Graph", () => {
  const entityKg = entitiesData as Record<string, any>;
  const storyKg = storiesData as any[];
  const validStoryIds = new Set(storyKg.map((s) => s.id));
  const validStorySlugs = new Set(storyKg.map((s) => s.id.replace("story-", "")));

  const rootsKg = rootsData as Record<string, any>;

  for (let sId = 1; sId <= 114; sId++) {
    const ov = (overviewsData as Record<string, any>)[String(sId)];
    const ents = ov.entities || {};

    for (const cat of ["prophets", "names_of_allah", "places", "nations", "unseen"]) {
      const list = ents[cat] || [];
      for (const ent of list) {
        assert.ok(ent.id, `Surah ${sId} entity in ${cat} must have id`);
        assert.ok(entityKg[ent.id], `Surah ${sId} entity ${ent.id} must exist in entities.json`);
        assert.ok(ent.slug, `Surah ${sId} entity ${ent.id} must have slug`);
        assert.equal(ent.slug, entityIdToSlug(ent.id), `Surah ${sId} entity ${ent.id} slug must equal entityIdToSlug`);
      }
    }

    for (const st of ov.stories || []) {
      assert.ok(validStoryIds.has(st.id), `Surah ${sId} story ${st.id} must exist in stories.json`);
      assert.ok(validStorySlugs.has(st.slug), `Surah ${sId} story slug ${st.slug} must exist in stories.json`);
    }

    for (const rk of ov.top_roots || []) {
      assert.ok(rk.root, `Surah ${sId} top root must have root`);
      assert.ok(rootsKg[rk.root], `Surah ${sId} top root ${rk.root} must exist in roots.json`);
    }
  }
});

test("Entity Slugs: All 884 entities produce clean, valid slugs and canonical merge paths", () => {
  const entries = Object.entries(entitiesData as Record<string, any>);
  assert.equal(entries.length, 884);

  const uniqueSlugs = new Set<string>();
  const slugToIds = new Map<string, string[]>();

  for (const [id] of entries) {
    const slug = entityIdToSlug(id);
    assert.ok(slug.length > 0, `Slug for ${id} cannot be empty`);
    assert.ok(!slug.startsWith("-"), `Slug for ${id} cannot start with dash: ${slug}`);
    assert.ok(!slug.endsWith("-"), `Slug for ${id} cannot end with dash: ${slug}`);
    assert.ok(!slug.includes("--"), `Slug for ${id} cannot contain double dashes: ${slug}`);

    uniqueSlugs.add(slug);
    const list = slugToIds.get(slug) || [];
    list.push(id);
    slugToIds.set(slug, list);
  }

  // 884 entity IDs map to 876 canonical page routes (8 natural transliteration aliases merged)
  assert.equal(uniqueSlugs.size, 876);

  // Verify known transliteration alias pairs map to the same canonical slug
  const knownAliasPairs = [
    ["person:isa", "person:'isa", "person-isa"],
    ["name_of_allah:al-aleem", "name_of_allah:al-'aleem", "name_of_allah-al-aleem"],
    ["name_of_allah:al-wasi'", "name_of_allah:al-wasi", "name_of_allah-al-wasi"],
    ["name_of_allah:as-samee'", "name_of_allah:as-samee", "name_of_allah-as-samee"],
    ["nation:aad", "nation:'aad", "nation-aad"],
    ["person:ammar-ibn-yasir", "person:'ammar-ibn-yasir", "person-ammar-ibn-yasir"]
  ];

  for (const [id1, id2, expectedSlug] of knownAliasPairs) {
    assert.equal(entityIdToSlug(id1), expectedSlug);
    assert.equal(entityIdToSlug(id2), expectedSlug);
    const mapped = slugToIds.get(expectedSlug);
    assert.ok(mapped?.includes(id1));
    assert.ok(mapped?.includes(id2));
  }
});

test("Structured Data (Schema.org JSON-LD): Validation and Domain Exclusivity", () => {
  // 1. Layout Base Schema
  const layoutBaseSchemas = [
    {
      "@type": "WebSite",
      "@id": `${BASE_URL}/#website`,
      "url": BASE_URL,
      "name": "QuranGraph",
      "description": "The Connected Quran Knowledge System & Multilingual Semantic Ontology",
      "inLanguage": ["en", "bn", "ar"],
      "publisher": {
        "@id": `${BASE_URL}/#organization`
      },
      "potentialAction": {
        "@type": "SearchAction",
        "target": `${BASE_URL}/search?q={search_term_string}`,
        "query-input": "required name=search_term_string"
      }
    },
    {
      "@type": "EducationalOrganization",
      "@id": `${BASE_URL}/#organization`,
      "name": "QuranGraph Project",
      "url": BASE_URL,
      "logo": `${BASE_URL}/og-image.png`,
      "sameAs": ["https://github.com/IliasSami/QuranGraph"]
    }
  ];

  for (const item of layoutBaseSchemas) {
    assert.ok(item["@type"]);
    assert.ok(item["@id"].startsWith(BASE_URL));
    assert.ok(item.url.startsWith(BASE_URL));
  }

  // 2. Surah & Ayah Schemas for all 114 Surahs
  for (const surah of surahsData) {
    const sId = surah.id;
    const sName = surah.name_translit;

    const surahBreadcrumbs = [
      { "@type": "ListItem", position: 1, name: "Home", item: BASE_URL },
      { "@type": "ListItem", position: 2, name: "Surahs", item: `${BASE_URL}/surahs` },
      { "@type": "ListItem", position: 3, name: `Surah ${sName}`, item: `${BASE_URL}/surah/${sId}` }
    ];

    const surahSchema = {
      "@context": "https://schema.org",
      "@graph": [
        ...layoutBaseSchemas,
        {
          "@type": "WebPage",
          "@id": `${BASE_URL}/surah/${sId}#webpage`,
          "url": `${BASE_URL}/surah/${sId}`,
          "name": `Surah ${sName} (${sId}) — QuranGraph`,
          "isPartOf": { "@id": `${BASE_URL}/#website` },
          "breadcrumb": { "@id": `${BASE_URL}/surah/${sId}#breadcrumb` }
        },
        {
          "@type": "BreadcrumbList",
          "@id": `${BASE_URL}/surah/${sId}#breadcrumb`,
          "itemListElement": surahBreadcrumbs
        }
      ]
    };

    // Serialize and parse to ensure strict validity
    const jsonStr = JSON.stringify(surahSchema);
    assert.ok(!jsonStr.includes("undefined"), `Surah ${sId} schema contains 'undefined' string`);
    assert.ok(!jsonStr.includes("null"), `Surah ${sId} schema contains 'null' string`);

    const parsed = JSON.parse(jsonStr);
    assert.equal(parsed["@context"], "https://schema.org");
    assert.ok(Array.isArray(parsed["@graph"]));

    // Verify Ayah schema for first, middle, and last verse
    for (const aNum of [1, Math.ceil(surah.ayat / 2), surah.ayat]) {
      const ayahBreadcrumbs = [
        { "@type": "ListItem", position: 1, name: "Home", item: BASE_URL },
        { "@type": "ListItem", position: 2, name: "Surahs", item: `${BASE_URL}/surahs` },
        { "@type": "ListItem", position: 3, name: `Surah ${sName}`, item: `${BASE_URL}/surah/${sId}` },
        { "@type": "ListItem", position: 4, name: `Ayah ${sId}:${aNum}`, item: `${BASE_URL}/ayah/${sId}/${aNum}` }
      ];

      const ayahSchema = {
        "@context": "https://schema.org",
        "@graph": [
          ...layoutBaseSchemas,
          {
            "@type": "WebPage",
            "@id": `${BASE_URL}/ayah/${sId}/${aNum}#webpage`,
            "url": `${BASE_URL}/ayah/${sId}/${aNum}`,
            "name": `${sName} ${sId}:${aNum} — Deep Ayah Study & Explanation`,
            "isPartOf": { "@id": `${BASE_URL}/#website` },
            "breadcrumb": { "@id": `${BASE_URL}/ayah/${sId}/${aNum}#breadcrumb` }
          },
          {
            "@type": "BreadcrumbList",
            "@id": `${BASE_URL}/ayah/${sId}/${aNum}#breadcrumb`,
            "itemListElement": ayahBreadcrumbs
          }
        ]
      };

      const ayahJson = JSON.stringify(ayahSchema);
      assert.ok(!ayahJson.includes("undefined"), `Ayah ${sId}:${aNum} schema contains 'undefined'`);
      assert.ok(!ayahJson.includes("null"), `Ayah ${sId}:${aNum} schema contains 'null'`);

      const parsedAyah = JSON.parse(ayahJson);
      assert.equal(parsedAyah["@context"], "https://schema.org");
      for (const node of parsedAyah["@graph"]) {
        if (node["@id"]) {
          assert.ok(node["@id"].startsWith(BASE_URL), `@id must point to ${BASE_URL}`);
        }
        if (node.url) {
          assert.ok(node.url.startsWith(BASE_URL), `url must point to ${BASE_URL}`);
        }
      }
    }
  }
});
