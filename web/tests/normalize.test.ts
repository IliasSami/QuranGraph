// Normaliser behaviour that search depends on. Run: node --test web/tests/
import { test } from "node:test";
import assert from "node:assert/strict";
import { consonantKey, tokenize, arabicKey, arabicSkeleton, arabicVariants, banglaKey, banglaStem, banglaToLatin, translitKey, asciiDigits, editDistance } from "../src/lib/search/normalize.ts";

const terms = (s: string) => tokenize(s).filter((t) => !t.stop).map((t) => t.term);

test("Uthmani and simple Arabic meet on the skeleton key", () => {
  const pairs: [string, string][] = [
    ["ٱلرَّحْمَٰنِ", "الرحمن"], ["ٱلْعَٰلَمِينَ", "العالمين"], ["ٱلصِّرَٰطَ", "الصراط"], ["ٱلْكِتَٰبُ", "الكتاب"],
    ["إِيَّاكَ", "إياك"], ["مَٰلِكِ", "مالك"], ["ذَٰلِكَ", "ذلك"],
  ];
  for (const [u, s] of pairs) assert.equal(arabicSkeleton(arabicKey(u)), arabicSkeleton(arabicKey(s)), `${u} vs ${s}`);
});

test("Arabic key drops marks and unifies letter forms", () => {
  assert.equal(arabicKey("أَحَدٌ"), "احد");
  assert.equal(arabicKey("رَحْمَةً"), "رحمه");
  assert.equal(arabicKey("هُدًى"), "هدي");
  assert.ok(arabicVariants("والكتاب").includes("كتاب"));
  assert.ok(arabicVariants("بالصبر").includes("صبر"));
});

test("Bangla: spelling variants and suffixes", () => {
  assert.equal(banglaKey("আল্লাহ্‌"), banglaKey("আল্লাহ"));
  assert.equal(banglaKey("ঈমান"), banglaKey("ইমান"));
  assert.equal(banglaStem(banglaKey("নবীদের")), banglaStem(banglaKey("নবী")));
  assert.equal(banglaStem(banglaKey("রাসূলের")), banglaKey("রাসুল"));
  assert.deepEqual(terms("আল্লাহ্‌র"), terms("আল্লাহ"));
});

test("transliteration sound keys", () => {
  assert.equal(translitKey("Ar-Raḥmān"), translitKey("rahman"));
  assert.equal(translitKey("rahmaan"), translitKey("rehman"));
  assert.equal(translitKey("Yusuf"), translitKey("yoosuf"));
  assert.equal(translitKey("Dhul-Qarnayn"), translitKey("zul qarnain"));
  assert.equal(consonantKey(banglaToLatin(banglaKey("রহমান"))), consonantKey("rahman"));
  assert.equal(consonantKey(banglaToLatin(banglaKey("ইউসুফ"))), consonantKey("Yusuf"));
  assert.equal(consonantKey(banglaToLatin(banglaKey("মুসা"))), consonantKey("Musa"));
});

test("digits in three scripts", () => {
  assert.equal(asciiDigits("২:২৫৫"), "2:255");
  assert.equal(asciiDigits("٢:٢٥٥"), "2:255");
});

test("edit distance with transposition", () => {
  assert.equal(editDistance("mosue", "mouse"), 1);
  assert.equal(editDistance("ibrahim", "ibraheem", 2), 2);
  assert.ok(editDistance("abc", "xyzw", 1) > 1);
});
