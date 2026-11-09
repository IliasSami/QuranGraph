import { test } from "node:test";
import assert from "node:assert/strict";
import { parseReference, parseSurahOnly } from "../src/lib/search/reference.ts";
import { search } from "../src/lib/search/engine.ts";

test("Enhanced Reference Parsing: Multilingual & Colloquial", () => {
  // Punctuation tolerance
  assert.deepEqual(parseReference("2:255?"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("(2:255)"), { surah: 2, ayah: 255, ref: "2:255" });

  // Natural language English
  assert.deepEqual(parseReference("surah 2 verse 255"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("chapter 2 verse 255"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("verse 255 of surah baqarah"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("baqra 255"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("yaseen 1"), { surah: 36, ayah: 1, ref: "36:1" });
  assert.deepEqual(parseReference("kahf 10"), { surah: 18, ayah: 10, ref: "18:10" });

  // Bangla natural language & numerals
  assert.deepEqual(parseReference("সূরা বাকারা ২৫৫"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("বাকারা ২৫৫"), { surah: 2, ayah: 255, ref: "2:255" });
  assert.deepEqual(parseReference("সুরা ২ আয়াত ২৫৫"), { surah: 2, ayah: 255, ref: "2:255" });

  // Arabic
  assert.deepEqual(parseReference("البقرة 255"), { surah: 2, ayah: 255, ref: "2:255" });
});

test("Direct Surah Parsing", () => {
  assert.equal(parseSurahOnly("surah mulk"), 67);
  assert.equal(parseSurahOnly("mulk"), 67);
  assert.equal(parseSurahOnly("yaseen"), 36);
  assert.equal(parseSurahOnly("kahaf"), 18);
  assert.equal(parseSurahOnly("surah 18"), 18);
  assert.equal(parseSurahOnly("সূরা বাকারা"), 2);
});

test("Search Engine: Rich Result Enrichment", () => {
  const results = search("2:255", 1);
  assert.equal(results.length, 1);
  const r = results[0];

  assert.equal(r.ref, "2:255");
  assert.equal(r.s, 2);
  assert.equal(r.a, 255);
  assert.equal(r.surah_translit, "Al-Baqara");
  assert.ok(r.ar_u.includes("ٱللَّهُ"));
  assert.ok(r.tr.includes("Allāhu"));
  assert.ok(r.en.includes("Ever-Living"));
  assert.ok(r.bn.includes("আল্লাহ্‌"));
});

test("Search Engine: Typo Resilience", () => {
  const results = search("patince", 1);
  assert.ok(results.length > 0);
  assert.equal(results[0].ref, "2:153"); // Patience concept ayah
});

test("Search Engine: Transliteration Matching across Corpus", () => {
  const results = search("iyyaka nabudu", 1);
  assert.ok(results.length > 0);
  assert.equal(results[0].ref, "1:5");
  assert.ok(results[0].tr.includes("na‘budu"));
});

test("Lemmas Lab Dataset Integrity: Transliteration & Lexicon Definitions", async () => {
  const { default: lemmasData } = await import("../src/lib/search/lemmas_lab.json", { with: { type: "json" } });
  assert.equal(lemmasData.length, 65);

  const arabicRegex = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;

  for (const item of lemmasData) {
    // Zero Arabic characters permitted in transliteration
    assert.equal(
      arabicRegex.test(item.translit),
      false,
      `Rank ${item.rank} (${item.lemma}) contains Arabic script in translit: '${item.translit}'`
    );

    // No placeholder generic fallback text
    assert.notEqual(item.meaning_en, "Quranic vocabulary", `Rank ${item.rank} (${item.lemma}) has placeholder meaning_en`);
    assert.notEqual(item.meaning_bn, "কুরআনিক শব্দ", `Rank ${item.rank} (${item.lemma}) has placeholder meaning_bn`);

    // Ensure sample verse texts are present
    assert.ok(item.sample_ar.length > 0, `Rank ${item.rank} missing sample_ar`);
    assert.ok(item.sample_en.length > 0, `Rank ${item.rank} missing sample_en`);
    assert.ok(item.sample_bn.length > 0, `Rank ${item.rank} missing sample_bn`);
  }

  // Spot-check key previously broken lemmas
  const sabil = lemmasData.find((l) => l.lemma === "سَبِيل");
  assert.ok(sabil);
  assert.equal(sabil.translit, "sabīl");
  assert.ok(sabil.meaning_en.includes("way / path"));
  assert.ok(sabil.meaning_bn.includes("পথ"));

  const kadhdhaba = lemmasData.find((l) => l.lemma === "كَذَّبَ");
  assert.ok(kadhdhaba);
  assert.equal(kadhdhaba.translit, "kadhdhaba");
  assert.ok(kadhdhaba.meaning_en.includes("denied"));

  const daa = lemmasData.find((l) => l.lemma === "دَعا");
  assert.ok(daa);
  assert.equal(daa.translit, "da‘ā");
  assert.ok(daa.meaning_en.includes("called / supplicated"));

  const ittaqa = lemmasData.find((l) => l.lemma === "اتَّقَى");
  assert.ok(ittaqa);
  assert.equal(ittaqa.translit, "ittaqā");
  assert.ok(ittaqa.meaning_en.includes("feared Allah"));
});

test("Lexicon: Core Root Glosses Coverage", async () => {
  const { getRootGloss } = await import("../src/lib/graph/lexicon.ts");

  const qawm = getRootGloss("قوم");
  assert.equal(qawm.label_en, "q-w-m · People, Standing & Nation (Qawm / Qiyam)");
  assert.ok(qawm.label_bn.includes("জাতি"));

  const sabil = getRootGloss("سبل");
  assert.equal(sabil.label_en, "s-b-l · Path, Way & Road (Sabil)");
  assert.ok(sabil.label_bn.includes("পথ"));

  const taqwa = getRootGloss("وقي");
  assert.equal(taqwa.label_en, "w-q-y · Protection, Piety & Taqwa (Taqwa / Wiqayah)");
  assert.ok(taqwa.label_bn.includes("তাকওয়া"));
});
