import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parseReference, parseSurahOnly } from "../src/lib/search/reference.ts";
import { search } from "../src/lib/search/engine.ts";
import { entityIdToSlug } from "../src/lib/graph/subgraph.ts";
import entitiesData from "../src/data/graph/entities.json" with { type: "json" };
import { GET as getSitemap } from "../src/pages/sitemap.xml.ts";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const webSrcDir = path.resolve(__dirname, "../src");

test("Search Edge Cases: Quotations and Punctuation Stripping", () => {
  // Phrase searches with ASCII and typographic quotes
  const r1 = search('"light upon light"', 5);
  assert.ok(r1.length > 0, 'Exact quote "light upon light" should return matching verses');
  assert.equal(r1[0].ref, "24:35", "Should return the Verse of Light (24:35)");

  const r2 = search('"rahman"', 5);
  assert.ok(r2.length > 0, 'Quoted "rahman" should match');

  const r3 = search("'ilm", 5);
  assert.ok(r3.length > 0, "Query with single quote 'ilm should match knowledge dua or verses");

  // Colons and whitespace variations
  assert.deepEqual(parseReference("al-baqarah:255"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("2: 255"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("2 : 255"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("2, 255"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("al-baqarah : 255"), { surah: 2, ayah: 255, ref: "2:255" });
});

test("Search Edge Cases: Single Character Resilience", () => {
  // Single latin character should not throw or return corrupt data
  const rA = search("a", 10);
  assert.ok(Array.isArray(rA));

  // Single Bengali character "ম" should not match Basmalah or unrelated concepts via channel 2
  const rM = search("ম", 10);
  assert.ok(Array.isArray(rM));
  // If results returned, none should be concept-basmalah purely from single letter substring
  const hasBasmalahFalseMatch = rM.some((r) => r.ref === "1:1" && r.confidence === 1.0);
  assert.strictEqual(hasBasmalahFalseMatch, false, "Single character 'ম' must not trigger false concept-basmalah alias match");

  // Single Arabic letter "ق" (Surah Qaf, 50)
  const rQaf = search("ق", 10);
  assert.ok(Array.isArray(rQaf));
  assert.ok(rQaf.length > 0, "Single Arabic letter 'ق' should resolve to Surah 50 (Qaf)");
  assert.equal(rQaf[0].s, 50, "Top result for 'ق' should be Surah Qaf");
});

test("Search Edge Cases: Bengali Spelling Variants & Phonetic Unification", () => {
  // Quran variations: কোরআন vs কুরআন
  const rQuran1 = search("কুরআন", 5);
  const rQuran2 = search("কোরআন", 5);
  assert.ok(rQuran1.length > 0, "কুরআন should match");
  assert.ok(rQuran2.length > 0, "কোরআন should match");
  assert.equal(rQuran1[0].ref, rQuran2[0].ref, "Both variants should return the same top Quran concept verse");

  // Fasting variations: রোজা vs রোযা
  const rRoja1 = search("রোজা", 5);
  const rRoja2 = search("রোযা", 5);
  assert.ok(rRoja1.length > 0);
  assert.ok(rRoja2.length > 0);
  assert.equal(rRoja1[0].ref, rRoja2[0].ref, "রোজা and রোযা should map to Ramadan/Fasting verse");

  // Prayer variations: সালাত vs নামায vs নামাজ
  const rSalat = search("সালাত", 5);
  const rNamaz = search("নামাজ", 5);
  const rNamayz = search("নামায", 5);
  assert.ok(rSalat.length > 0);
  assert.ok(rNamaz.length > 0);
  assert.ok(rNamayz.length > 0);
  assert.equal(rSalat[0].ref, rNamaz[0].ref, "সালাত and নামাজ should map to prayer verses");
  assert.equal(rNamaz[0].ref, rNamayz[0].ref, "নামাজ and নামায should map to prayer verses");

  // Prophet Dhul-Qarnayn: যুলকারনাইন vs জুলকারনাইন
  const rZul1 = search("যুলকারনাইন", 5);
  const rZul2 = search("জুলকারনাইন", 5);
  assert.ok(rZul1.length > 0);
  assert.ok(rZul2.length > 0);
  assert.equal(rZul1[0].ref, rZul2[0].ref, "Dhul-Qarnayn spelling variants should resolve identically");
});

test("Search Edge Cases: Complex Colloquial Verse References", () => {
  assert.deepEqual(parseReference("surah 2 ayah 255"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("ayah 255 of baqarah"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("verse 255 of al baqarah"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("বাকারা ২৫৫ নম্বর আয়াত"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("বাকারা ২৫৫ নং আয়াত"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("সুরা বাকারা ২৫৫ নম্বর আয়াত"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("সুরা বাকারা ২৫৫ তম আয়াত"), { surah: 2, ayah: 255, ref: "2:255" });
});

test("Multilingual & BCP-47 Compliance across Astro Source Files", () => {
  function scanDir(dir: string, fileList: string[] = []): string[] {
    const files = fs.readdirSync(dir);
    for (const file of files) {
      const fullPath = path.join(dir, file);
      const stat = fs.statSync(fullPath);
      if (stat.isDirectory()) {
        scanDir(fullPath, fileList);
      } else if (file.endsWith(".astro")) {
        fileList.push(fullPath);
      }
    }
    return fileList;
  }

  const astroFiles = scanDir(webSrcDir);

  for (const file of astroFiles) {
    const content = fs.readFileSync(file, "utf-8");
    const relPath = path.relative(webSrcDir, file);

    // Rule 1: Every element with class="bangla-text" must have lang="bn"
    const banglaMatches = content.matchAll(/<([a-zA-Z0-9]+)[^>]*class="[^"]*bangla-text[^"]*"[^>]*>/g);
    for (const match of banglaMatches) {
      const tag = match[0];
      assert.ok(
        tag.includes('lang="bn"'),
        `File ${relPath} has a .bangla-text element missing lang="bn": ${tag}`
      );
    }

    // Rule 2: Every element with class="arabic-text" must have dir="rtl" and lang="ar"
    const arabicMatches = content.matchAll(/<([a-zA-Z0-9]+)[^>]*class="[^"]*arabic-text[^"]*"[^>]*>/g);
    for (const match of arabicMatches) {
      const tag = match[0];
      assert.ok(
        tag.includes('dir="rtl"'),
        `File ${relPath} has an .arabic-text element missing dir="rtl": ${tag}`
      );
      assert.ok(
        tag.includes('lang="ar"'),
        `File ${relPath} has an .arabic-text element missing lang="ar": ${tag}`
      );
    }
  }
});

test("SEO Metadata: All Route Templates Define Non-Default Titles & Descriptions", () => {
  const pagesDir = path.join(webSrcDir, "pages");
  const pageFiles = [
    "index.astro",
    "search.astro",
    "about.astro",
    "stats.astro",
    "sources.astro",
    "numbers.astro",
    "learn.astro",
    "graph.astro",
    "404.astro",
    "surahs/index.astro",
    "surah/[id].astro",
    "ayah/[surah]/[ayah].astro",
    "root/[slug].astro",
    "entity/[slug].astro",
    "story/[slug].astro"
  ];

  for (const p of pageFiles) {
    const fullPath = path.join(pagesDir, p);
    assert.ok(fs.existsSync(fullPath), `Route template ${p} must exist`);
    const content = fs.readFileSync(fullPath, "utf-8");

    // Must have <Layout ... title= ... description= ...>
    assert.ok(
      content.includes("<Layout") && content.includes("title="),
      `Route ${p} must pass a title prop to <Layout>`
    );
    assert.ok(
      content.includes("description="),
      `Route ${p} must pass an explicit description prop to <Layout>`
    );
  }
});

test("Sitemap XML: Integrity, Exclusivity, and Zero Duplicate URLs", async () => {
  const fakeContext: any = {
    site: new URL("https://qurangraph.iliassami57.workers.dev")
  };

  const response = await getSitemap(fakeContext);
  assert.equal(response.status, 200);
  assert.equal(response.headers.get("Content-Type"), "application/xml; charset=utf-8");

  const xmlText = await response.text();
  assert.ok(xmlText.startsWith('<?xml version="1.0" encoding="UTF-8"?>'));
  assert.ok(xmlText.includes("<urlset"));

  // Extract all <loc> URLs
  const locMatches = [...xmlText.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
  assert.ok(locMatches.length > 8000, `Sitemap must contain >8000 URLs, got ${locMatches.length}`);

  // Test zero duplicates
  const seen = new Set<string>();
  const duplicates: string[] = [];
  for (const loc of locMatches) {
    if (seen.has(loc)) {
      duplicates.push(loc);
    }
    seen.add(loc);
  }

  assert.equal(
    duplicates.length,
    0,
    `Sitemap must contain 0 duplicate URLs. Found: ${duplicates.join(", ")}`
  );

  // Check required pages exist
  assert.ok(locMatches.includes("https://qurangraph.iliassami57.workers.dev/about"), "Sitemap must include /about");
  assert.ok(locMatches.includes("https://qurangraph.iliassami57.workers.dev/stats"), "Sitemap must include /stats");
  assert.ok(locMatches.includes("https://qurangraph.iliassami57.workers.dev/search"), "Sitemap must include /search");
  assert.ok(locMatches.includes("https://qurangraph.iliassami57.workers.dev/learn"), "Sitemap must include /learn");
  assert.ok(locMatches.includes("https://qurangraph.iliassami57.workers.dev/numbers"), "Sitemap must include /numbers");
  assert.ok(locMatches.includes("https://qurangraph.iliassami57.workers.dev/sources"), "Sitemap must include /sources");
});

test("Entity Slugs: Overlapping Entity Merging Preserves All Ayat", () => {
  const bySlug = new Map<string, any>();
  for (const [id, data] of Object.entries(entitiesData as Record<string, any>)) {
    const slug = entityIdToSlug(id);
    if (!bySlug.has(slug)) {
      bySlug.set(slug, { ...data, slug, id, count: (data.ayat || []).length });
    } else {
      const existing = bySlug.get(slug);
      const mergedAyat = Array.from(new Set([...(existing.ayat || []), ...(data.ayat || [])]));
      existing.ayat = mergedAyat;
      existing.count = mergedAyat.length;
    }
  }

  // Check Prophet Isa ('isa and isa combined)
  const isa = bySlug.get("person-isa");
  assert.ok(isa, "person-isa slug must exist");
  assert.ok(isa.count >= 54, `Merged Prophet Isa should have at least 54 verses, found ${isa.count}`);
});
