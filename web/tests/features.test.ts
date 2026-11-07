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
