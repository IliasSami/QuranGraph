import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";

test("Translation Integrity: Ayah 18:32 Bengali Translation & Ruku Header Elimination", () => {
  const corpusPath = path.resolve("web/src/lib/search/corpus.json");
  const corpus = JSON.parse(fs.readFileSync(corpusPath, "utf-8"));
  const v18_32 = corpus.find((x: any) => x.s === 18 && x.a === 32);

  assert.ok(v18_32, "Ayah 18:32 must exist in corpus.json");
  assert.equal(
    v18_32.bn,
    "আর আপনি তাদের কাছে পেশ করুন দু’ব্যক্তির উপমা: তাদের একজনকে আমরা দিয়েছিলাম দু’টি আঙ্গুরের বাগান এবং এ দু’টিকে আমরা খেজুর গাছ দিয়ে পরিবেষ্টিত করেছিলাম ও এ দু’টির মধ্যবর্তী স্থানকে করেছিলাম শস্যক্ষেত্র।"
  );
  assert.ok(!v18_32.bn.includes("<b>"), "Must not contain raw <b> HTML tag");
  assert.ok(!v18_32.bn.includes("</b>"), "Must not contain raw </b> HTML tag");
  assert.ok(!v18_32.bn.includes("পঞ্চম রুকু’"), "Must not contain ruku heading in verse translation");
});

test("Translation Integrity: Zero HTML Tags in Entire Corpus (All 6,236 Ayat)", () => {
  const corpusPath = path.resolve("web/src/lib/search/corpus.json");
  const corpus = JSON.parse(fs.readFileSync(corpusPath, "utf-8"));
  const htmlTagRegex = /<[^>]+>/;

  const violations: Array<{ ref: string; field: string; text: string }> = [];
  for (const item of corpus) {
    for (const key of ["bn", "en", "ar", "ar_u", "tr"]) {
      const val = item[key] || "";
      if (htmlTagRegex.test(val)) {
        violations.push({ ref: `${item.s}:${item.a}`, field: key, text: val });
      }
    }
  }

  assert.equal(violations.length, 0, `Found HTML tags in corpus fields: ${JSON.stringify(violations)}`);
});

test("Translation Integrity: Zero HTML Tags in quran.sqlite Text Column", () => {
  const dbPath = path.resolve("ingest/work/quran.sqlite");
  if (!fs.existsSync(dbPath)) return;

  const out = execSync(`sqlite3 "${dbPath}" "SELECT source, surah, ayah, text FROM text WHERE text LIKE '%<%>%';"`).toString().trim();
  assert.equal(out, "", `Found HTML tags in database text column: ${out}`);
});

test("Audio Metadata Integrity: Surah 18:32 Audio Alignment & Cleanliness", () => {
  const audioPath = path.resolve("web/public/audio/bn/018.json");
  assert.ok(fs.existsSync(audioPath), "018.json audio metadata must exist");

  const meta = JSON.parse(fs.readFileSync(audioPath, "utf-8"));
  const a32 = meta.ayat.find((x: any) => x.ayah === 32);

  assert.ok(a32, "Ayah 32 must exist in 018.json");
  assert.ok(!a32.text.includes("<b>"), "Audio text must not contain HTML tags");
  assert.ok(!a32.text.includes("পঞ্চম রুকু"), "Audio text must not be ruku marker");
  assert.ok(a32.duration_ms > 5000, `Audio duration must reflect full verse reading, got ${a32.duration_ms}ms`);
  assert.equal(
    a32.text,
    "আর আপনি তাদের কাছে পেশ করুন দু’ব্যক্তির উপমা: তাদের একজনকে আমরা দিয়েছিলাম দু’টি আঙ্গুরের বাগান এবং এ দু’টিকে আমরা খেজুর গাছ দিয়ে পরিবেষ্টিত করেছিলাম ও এ দু’টির মধ্যবর্তী স্থানকে করেছিলাম শস্যক্ষেত্র।"
  );
});

test("Audio Metadata Integrity: All 114 Surahs Free of Ruku/Juz/HTML Markers in Text", () => {
  const audioDir = path.resolve("web/public/audio/bn");
  if (!fs.existsSync(audioDir)) return;

  const files = fs.readdirSync(audioDir).filter((f) => f.endsWith(".json"));
  assert.equal(files.length, 114, "Must have 114 audio JSON files");

  const badEntries: Array<{ file: string; ayah: number; text: string }> = [];
  for (const f of files) {
    const data = JSON.parse(fs.readFileSync(path.join(audioDir, f), "utf-8"));
    for (const a of data.ayat || []) {
      const t = a.text || "";
      if (/<[^>]+>/.test(t) || ((t.includes("রুকু") || t.includes("পারা")) && t.length < 30)) {
        badEntries.push({ file: f, ayah: a.ayah, text: t });
      }
    }
  }

  assert.equal(badEntries.length, 0, `Found corrupted audio text entries: ${JSON.stringify(badEntries)}`);
});
