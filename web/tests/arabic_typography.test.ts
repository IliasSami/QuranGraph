import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { fileURLToPath } from "node:url";
import lemmasData from "../src/lib/search/lemmas_lab.json" with { type: "json" };

function resolveWebPath(rel: string): string {
  return fileURLToPath(new URL(`../${rel}`, import.meta.url));
}

test("Arabic Typography: Numbers Lab Lemma Container Safety", () => {
  const numbersFile = fs.readFileSync(resolveWebPath("src/pages/numbers.astro"), "utf-8");
  
  // Ensure unsafe line-height: 1.2 is eliminated
  assert.ok(
    !numbersFile.includes('class="arabic-text" lang="ar" dir="rtl" style="font-size: 2.2rem; color: var(--text-arabic); line-height: 1.2;"'),
    "Unsafe line-height: 1.2 on Arabic lemma must be eliminated"
  );
  
  // Ensure safe line-height 1.6 and min-height are present
  assert.ok(
    numbersFile.includes("line-height: 1.6; min-height: 3.6rem;"),
    "Arabic lemma must have safe line-height >= 1.6 and min-height for stable clearance"
  );

  // Ensure transliteration has distinct margin-top to prevent descender collision
  assert.ok(
    numbersFile.includes("margin-top: 0.5rem;"),
    "Transliteration element must have distinct margin-top >= 0.5rem to prevent descender overlap"
  );
});

test("Arabic Typography: Flashcards & Learning Quiz Clearance", () => {
  const flashcardsFile = fs.readFileSync(resolveWebPath("src/components/Flashcards.astro"), "utf-8");
  assert.ok(
    !flashcardsFile.includes("line-height: 1.2;"),
    "Flashcards Arabic lemma must not use unsafe line-height 1.2"
  );
  assert.ok(
    flashcardsFile.includes("line-height: 1.6; min-height: 5.5rem;"),
    "Flashcards Arabic lemma must use safe line-height 1.6 and min-height 5.5rem"
  );
  assert.ok(
    flashcardsFile.includes('id="fc-translit"') && flashcardsFile.includes("margin-top: 0.5rem;"),
    "Flashcards transliteration must have margin-top 0.5rem"
  );

  const quizFile = fs.readFileSync(resolveWebPath("src/components/LearningQuiz.astro"), "utf-8");
  assert.ok(
    !quizFile.includes("line-height: 1.2;"),
    "Quiz Arabic question must not use unsafe line-height 1.2"
  );
  assert.ok(
    quizFile.includes("line-height: 1.6; min-height: 5.2rem;"),
    "Quiz Arabic question must use safe line-height 1.6 and min-height 5.2rem"
  );
  assert.ok(
    quizFile.includes('id="quiz-q-translit"') && quizFile.includes("margin-top: 0.5rem;"),
    "Quiz transliteration must have margin-top 0.5rem"
  );
});

test("Arabic Typography: Learn Page Root Families Clearance", () => {
  const learnFile = fs.readFileSync(resolveWebPath("src/pages/learn.astro"), "utf-8");
  
  // Unsafe line-height 1.1 must be eliminated from root titles
  assert.ok(
    !learnFile.includes("line-height: 1.1; margin-bottom: 0.25rem;"),
    "Unsafe line-height 1.1 on roots in learn.astro must be eliminated"
  );
  
  // Check safe root line-height and margin-top on labels
  assert.ok(
    learnFile.includes("line-height: 1.6; min-height: 4.2rem;"),
    "Root titles in learn.astro must use safe line-height 1.6 and min-height"
  );
  assert.ok(
    learnFile.includes("margin-top: 0.5rem; margin-bottom: 0.2rem;"),
    "Root labels in learn.astro must have margin-top 0.5rem to clear root letter descenders"
  );
});

test("Arabic Typography: Global CSS Defaults & Line-Height Standards", () => {
  const cssFile = fs.readFileSync(resolveWebPath("src/styles/global.css"), "utf-8");
  
  // Check default line-height
  assert.ok(
    cssFile.includes("line-height: var(--arabic-line-height, 2.4);"),
    "Global .arabic-text must have safe default line-height (>= 2.0 for verses)"
  );
  
  // Check .arabic-display rule
  assert.ok(
    cssFile.includes(".arabic-display"),
    ".arabic-display modifier must be available for isolated display lemmas"
  );
});

test("Arabic Typography: Complex Lemmas with Deep Descenders & Tashkeel", () => {
  // Verify diverse test lemmas: short, medium, long, with kasrah, shaddah, ya, ra, etc.
  const testLemmas = [
    { rank: 6, lemma: "إِنّ", translit: "inna", desc: "Hamzah with kasrah and shaddah" },
    { rank: 4, lemma: "فِي", translit: "fī", desc: "Deep loop ya descender" },
    { rank: 8, lemma: "الَّذِي", translit: "alladhī", desc: "Long relative pronoun with shaddah and ya" },
    { rank: 9, lemma: "عَلَى", translit: "‘alā", desc: "Alif maqsurah with deep tail" },
    { rank: 7, lemma: "قالَ", translit: "qāla", desc: "Deep lam descender" },
    { rank: 58, lemma: "خَيْر", translit: "khayr", desc: "Ra descender" },
    { rank: 52, lemma: "مُؤْمِن", translit: "mu'min", desc: "Nun descender and sukoon on waw-hamzah" },
  ];

  for (const item of testLemmas) {
    const found = lemmasData.find((l) => l.rank === item.rank);
    assert.ok(found, `Lemma rank #${item.rank} should exist in lemmas_lab.json`);
    assert.ok(found.lemma.length > 0, `Lemma rank #${item.rank} must have Arabic content`);
    assert.ok(found.translit.length > 0, `Lemma rank #${item.rank} must have transliteration`);
  }
});
