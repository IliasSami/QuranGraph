# QuranGraph — Handoff for the next coding agent

**Read this file completely before touching anything.** It is the single entry point: what the project is, every
decision already made, exactly where work stopped, how to set up, how to write explanations at the same quality,
and the next tasks in order.

Last updated: **7 Nov 2026** after Deep DevOps, Accessibility, Search, and Real-User UX Overhaul.
- Explanations for ALL 114 surahs (6,236 / 6,236 ayat, 100%) verified with 0 errors and 0 tafsir-naming warnings.
- Knowledge Graph rebuilt (17,711 nodes, 150,716 edges, 884 entities, 6 stories).
- Corpus transliteration enriched: ALA-LC Latin transliteration (`tr`) generated for all 6,236 ayat.
- Search Engine upgraded: multilingual natural language reference parsing, direct surah matching, transliteration search, and typo tolerance.
- Search UX redesigned: converting card presentation with Arabic Uthmani, transliteration, highlighted translations, filter tabs, audio preview, and copy actions.
- Ayah & Surah pages enriched with English transliteration, connected entities badges, story narrative arc banners, sticky audio dock, auto-scroll toggle, quick copy, and bookmarking.
- UI/UX Accessibility: WCAG 2.2 AAA contrast compliance, dynamic Arabic font-size scaler (`A-`/`A+`), mobile touch support on Knowledge Graph canvas, and last-read progress resumption.
- DevOps & Cloudflare: Service Worker range request fix, immutable caching & security headers (`_headers`), `drop-trailing-slash` routing, and custom 404 page.
- Web built cleanly: 8,899 static pages (well under 20,000 Cloudflare limit). 66/66 tests pass, 54/54 golden benchmarks pass (100%).

Companion documents (read when the task needs them):

| File | What it is |
|---|---|
| `PLAN.md` | The full product and architecture plan (sources, knowledge model, site, search, DevOps, phases) |
| `ingest/agent/INSTRUCTIONS.md` | **Canonical rules for writing ayah explanations.** Follow it literally |
| `ingest/agent/examples/*.json` | Reference explanations (al-Fatiha 1:1, 1:5, 1:7) — the quality bar |
| `docs/PILOT-REPORT.md` | Results of the 591-ayah pilot: quality, cost, open gate items |
| `docs/SOURCE-ISSUES.md` | Every data problem found in the sources and how it is handled |
| `docs/permissions/EMAILS.md` | Permission-request drafts (the **owner** sends them, never the agent) |
| `README.md` | Short project overview and commands |

---

## 1. What QuranGraph is (one paragraph)

A free, static website that turns the whole Quran into a connected knowledge graph for beginners: every word,
ayah, surah, concept, person, place and story linked; each ayah explained in plain English and Bangla with key
words, a practical lesson and a real-life example; searchable in English, Arabic and Bangla including
transliteration; recitation audio; a reproducible statistics lab. Architecture copies a proven project
(github.com/IliasSami/fahads-pdf-sync): a heavy offline Python pipeline, then **static files only** on Cloudflare
Workers Static Assets, with search running in the browser.

## 2. Decisions already made by the owner (do not reopen)

1. **Explanations are AI-written at build time, grounded only in cited tafsir**, labelled as a simplified summary.
2. **Numbers Lab:** reproducible counts with the counting method shown; popular "miracle" claims labelled
   verified / depends on counting rules / not reproducible / disputed by scholars. Headings say "pattern", never "miracle".
3. **100% static, $0/month, no AI at runtime** on the live site.
4. **Launch privately first** (Cloudflare Access + noindex); each surah goes public only after scholarly review.
5. Perspective: **mainstream Sunni scholarship** as represented by the sources; differences of opinion are named, not resolved.
6. Primary translations: **Saheeh International** (English) and **Dr. Abu Bakr Zakaria** (Bangla), via QuranEnc.
   Default reciter (Phase 6): Mishary Alafasy. Arabic audio is **always human recitation, never TTS**.

## 3. Hard rules (licensing and religious accuracy)

- **Arabic text = Tanzil, verbatim.** Never edit, re-type, normalise or "fix" displayed Quran text. Normalised
  forms are only for search keys. Keep Tanzil's licence header in any file containing the text.
- **QuranEnc texts (translations, Al-Mukhtasar, al-Muyassar) are shown unmodified**, with publisher, QuranEnc.com
  credit and version. No edits — not even fixing their broken Bangla characters (we asked QuranEnc; see EMAILS §1).
- **`use: grounding` sources (Ibn Kathir EN, Ma'ariful Qur'an, Jalalayn, Sa'di, Ahsanul Bayan, Ibn Kathir AR) are
  never shipped in website files.** They are read only by the explanation step; we paraphrase and cite them.
- **Never use the Quran.com / Quran Foundation API to build data** — its terms forbid static bundling.
- **No fatwas or rulings, no invented hadith/stories/numbers, no modern-science claims the sources don't make.**
- **Outward-facing actions (sending emails, publishing, deploying) need the owner's explicit OK.**
- Every source and its status lives in `ingest/sources.yaml`; add new sources there first, with licence and `use`.
- **Zero tafsir book or scholar names in teaching text** (`simple_*`, `lesson_*`, `real_life_*`). Attributions
  live in `claims`. The validator catches this — never override the warning.

## 4. Where work stopped (state as of 6 Nov 2026, 01:00 UTC+6)

### 4a. Completed phases

| Phase | Status | Key outputs |
|---|---|---|
| **Phase 0 — Pilot** | ✅ Done | 591 pilot ayat, source manifest, normaliser, validator, golden search set |
| **Phase 1 — Text core completion** | ✅ Done | `ingest/core/translit.py` (rule-based Latin transliteration), curated Bangla surah names, weekly `fetch.py --check` |
| **Phase 2 — Knowledge base** | ✅ Done | `ingest/kb/` populated: `people.json`, `places.json`, `nations.json`, `stories.json`, `names_of_allah.json`, `glossary.json`, `learning_paths.json`, `unseen.json`, `build_kb.py`, `normalize_entities.py`. Entities normalised in all explanations |
| **Phase 3 — Explanation generation** | ✅ Done | **6,236 / 6,236 ayat (100%)** — All 114 surahs complete and verified with 0 errors and 0 tafsir-naming warnings |
| **Phase 4 — Knowledge graph** | ✅ Done | `ingest/graph/build_kg.py`, `ingest/graph/test_graph.py`. Builds `ingest/work/graph.sqlite` with 17,711 nodes + 150,716 edges. All 4 unit tests pass |
| **Phase 5 — Search engine** | ✅ Done | Client-side browser search: 61/61 tests pass, 54/54 golden queries pass, <10ms response |
| **Phase 6 — Website (Astro 5)** | ✅ Done | Static site: `web/src/pages/` with surah, ayah, entity, root, story, graph, search, numbers, surahs, learn, sources pages. `web/astro.config.mjs`. Production build: 8,898 pages / 9,126 static files (well under 20,000 Cloudflare limit) |
| **Phase 7 — Audio** | ✅ Done | **114/114 surahs** Bengali neural TTS: `web/public/audio/bn/*.mp3` + sentence-level `*.json` alignments (335 MB total, 0 undersized files) |
| **Phase 8 — CI** | ✅ Done | `.github/workflows/ci.yml` — runs `uv sync`, normaliser tests, `qg check` over every explained surah |
| **Polish pass** | ✅ Done | All 6,236 ayat clean: 0 "names a tafsir" warnings across all 114 surahs |

### 4b. Explanation progress — exact file counts

Explanations are in `ingest/content/explain/<sss>/<aaa>.json`. **All pass validation with 0 errors.**

| Surah | Name | Ayat | Files | Status |
|---|---|---|---|---|
| 001 | Al-Fatiha | 7 | 7 | ✅ |
| 002 | Al-Baqarah | 286 | 286 | ✅ |
| 003 | Aal-i-Imran | 200 | 200 | ✅ |
| 004 | An-Nisa | 176 | 176 | ✅ |
| 005 | Al-Maidah | 120 | 120 | ✅ |
| 006 | Al-An'am | 165 | 165 | ✅ |
| 007 | Al-A'raf | 206 | 206 | ✅ |
| 008 | Al-Anfal | 75 | 75 | ✅ |
| 009 | At-Tawbah | 129 | 129 | ✅ |
| 010 | Yunus | 109 | 109 | ✅ |
| 011 | Hud | 123 | 123 | ✅ |
| 012 | Yusuf | 111 | 111 | ✅ |
| 013 | Ar-Ra'd | 43 | 43 | ✅ |
| 014 | Ibrahim | 52 | 52 | ✅ |
| 015 | Al-Hijr | 99 | 99 | ✅ |
| 016 | An-Nahl | 128 | 128 | ✅ |
| 017 | Al-Isra | 111 | 111 | ✅ |
| 018 | Al-Kahf | 110 | 110 | ✅ |
| 019 | Maryam | 98 | 98 | ✅ |
| 020 | Ta-Ha | 135 | 135 | ✅ |
| 021 | Al-Anbiya | 112 | 112 | ✅ |
| 022 | Al-Hajj | 78 | 78 | ✅ |
| 023 | Al-Mu'minun | 118 | 118 | ✅ |
| 024 | An-Nur | 64 | 64 | ✅ |
| 025 | Al-Furqan | 77 | 77 | ✅ |
| 026 | Ash-Shu'ara | 227 | 227 | ✅ |
| 027 | An-Naml | 93 | 93 | ✅ |
| 028 | Al-Qasas | 88 | 88 | ✅ |
| 029 | Al-'Ankabut | 69 | 69 | ✅ |
| 030 | Ar-Rum | 60 | 60 | ✅ |
| 031 | Luqman | 34 | 34 | ✅ |
| 032 | As-Sajdah | 30 | 30 | ✅ |
| 033 | Al-Ahzab | 73 | 73 | ✅ |
| 034 | Saba | 54 | 54 | ✅ |
| 035 | Fatir | 45 | 45 | ✅ |
| 036 | Ya-Sin | 83 | 83 | ✅ |
| 037 | As-Saffat | 182 | 182 | ✅ |
| 038 | Sad | 88 | 88 | ✅ |
| 039 | Az-Zumar | 75 | 75 | ✅ |
| 040 | Ghafir | 85 | 85 | ✅ |
| 041 | Fussilat | 54 | 54 | ✅ |
| 042 | Ash-Shura | 53 | 53 | ✅ |
| 043 | Az-Zukhruf | 89 | 89 | ✅ |
| 044 | Ad-Dukhan | 59 | 59 | ✅ |
| 045 | Al-Jathiyah | 37 | 37 | ✅ |
| 046 | Al-Ahqaf | 35 | 35 | ✅ |
| 047 | Muhammad | 38 | 38 | ✅ |
| 048 | Al-Fath | 29 | 29 | ✅ |
| 049 | Al-Hujurat | 18 | 18 | ✅ |
| 050 | Qaf | 45 | 45 | ✅ |
| 051 | Adh-Dhariyat | 60 | 60 | ✅ |
| 052 | At-Tur | 49 | 49 | ✅ |
| 053 | An-Najm | 62 | 62 | ✅ |
| 054 | Al-Qamar | 55 | 55 | ✅ |
| 055 | Ar-Rahman | 78 | 78 | ✅ |
| 056 | Al-Waqi'ah | 96 | 96 | ✅ |
| 057 | Al-Hadid | 29 | 29 | ✅ |
| 058 | Al-Mujadilah | 22 | 22 | ✅ |
| 059 | Al-Hashr | 24 | 24 | ✅ |
| 060 | Al-Mumtahanah | 13 | 13 | ✅ |
| 061 | As-Saff | 14 | 14 | ✅ |
| 062 | Al-Jumu'ah | 11 | 11 | ✅ |
| 063 | Al-Munafiqun | 11 | 11 | ✅ |
| 064 | At-Taghabun | 18 | 18 | ✅ |
| 065 | At-Talaq | 12 | 12 | ✅ |
| 066 | At-Tahrim | 12 | 12 | ✅ |
| 067 | Al-Mulk | 30 | 30 | ✅ |
| 068 | Al-Qalam | 52 | 52 | ✅ |
| 069 | Al-Haqqah | 52 | 52 | ✅ |
| 070 | Al-Ma'arij | 44 | 44 | ✅ |
| 071 | Nuh | 28 | 28 | ✅ |
| 072 | Al-Jinn | 28 | 28 | ✅ |
| 073 | Al-Muzzammil | 20 | 20 | ✅ |
| 074 | Al-Muddaththir | 56 | 56 | ✅ |
| 075 | Al-Qiyamah | 40 | 40 | ✅ |
| 076 | Al-Insan | 31 | 31 | ✅ |
| 077 | Al-Mursalat | 50 | 50 | ✅ |
| 078–114 | Juz 30 | 564 | 564 | ✅ |

**Total: 6,236 / 6,236 (100%) — All 114 surahs complete!**

### 4c. Completion of All Explanations (Phase 3)

Every single ayah across all 114 surahs has an authentic, cited, validated explanation JSON in `ingest/content/explain/<sss>/<aaa>.json`.
- Total files: **6,236**
- All 114 surahs pass `ingest/qg check <surah>` with **0 errors**.
- All 114 surahs pass `ingest/qg warned <surah> "names a tafsir"` with **none** (zero scholar or tafsir book names in teaching text).
- Full Flesch-Kincaid grade <= 8.0 across all English teaching text.
- Natural চলিত Bangla with <= 30 words/sentence, zero Latin characters, zero exclamation marks (!).

### 4d. Other verified state

- `node --test "web/tests/*.test.ts"` → **61/61 pass** (54/54 golden search benchmarks at 100%)
- `ingest/qg stats` → `explained 6236/6236 ayat · review queue 2289 (1366 must-review, 923 sample)`
- `for s in $(seq 1 114); do ingest/qg check $s; done` → all 114 surahs: `N valid, 0 with errors`
- `for s in $(seq 1 114); do ingest/qg warned $s "names a tafsir"; done` → all 114 surahs: `none`
- `cd web && npm run build` → **8,898 pages built cleanly in 14.49s** (exit code 0), 9,126 static files
- Knowledge graph rebuilt: **17,711 nodes, 150,716 edges**, all 4 unit tests pass (`ingest/graph/test_graph.py`)
- Git: `b1500d0` on `main` (no remote). `ingest/work/` is .gitignored and fully regenerable.

## 5. Setup from a fresh checkout (about 15–20 minutes, mostly downloads)

Requirements: **uv** (Python 3.12 is installed by uv), **Node 22.6+** (runs `.ts` files directly; developed on Node 25),
git, sqlite3 (optional, for inspection). macOS/Linux shell. Network access to tanzil.net, quranenc.com,
raw.githubusercontent.com.

```bash
cd ingest && uv sync
```

```bash
uv run fetch/fetch.py                # downloads every source into ingest/work/raw/ (QuranEnc ≈ 1 min per edition)
```

```bash
uv run core/build_text.py            # builds ingest/work/quran.sqlite and prints a report (see expected output below)
```

```bash
cd .. && node --test "web/tests/*.test.ts"     # expect: pass 61, fail 0
```

```bash
ingest/qg stats                       # expect: explained 6236/6236 ayat
```

Expected `build_text.py` report lines (if these differ, stop and investigate before writing anything):
`surahs 114 · ayat 6236 · words 77429 · roots 1651 · lemmas 4763`, 9 QuranEnc editions with 6236 ayat each,
`g-en-maarif: removed 40 rows carried over from the previous surah`, Mukhtasar numbering check
EN `{'misaligned': 27, 'same-wording': 52}`, BN `{'misaligned': 22}`, AR `{'misaligned': 24}`.

`ingest/work/` is **not committed** and is fully regenerable from the commands above. `ingest/content/` **is**
the real, expensive output — never delete or regenerate it casually.

## 6. Map of the code

```
ingest/
  sources.yaml            every source: id, kind, licence, attribution, use (display|data|grounding), status
  sources.lock.json       version + SHA-256 per downloaded file (committed; reproducibility)
  fetch/fetch.py          kinds: tanzil_text, url, quranenc (114 calls/edition), spa5k (pinned commit, raw GitHub)
                          `--check` = weekly QuranEnc change check (exit 1 when an edition changed)
  core/build_text.py      raw → work/quran.sqlite. Also: splits the Basmalah off ayah 1 (table `basmala`),
                          drops mirror rows carried over from the previous surah, flags misaligned Mukhtasar rows
  core/normalize.py       tokenize_many(), arabic_skeleton() — calls web/scripts/normalize-cli.ts through Node
  core/translit.py        rule-based Latin transliteration from vocalised Arabic (ALA-LC / DMG style)
  generate/qg.py          the `ingest/qg` CLI (wrapper script: ingest/qg)
  generate/schema.py      validate(d, db) -> (errors, warnings)
  generate/review_page.py → ingest/work/review/index.html (all explained ayat, filters for flagged ones)
  graph/build_kg.py       knowledge graph builder → work/graph.sqlite (17,711 nodes, 150,716 edges)
  graph/test_graph.py     knowledge graph tests
  agent/INSTRUCTIONS.md   explanation rules + JSON schema + theme list
  agent/examples/         reference explanations
  kb/                     curated knowledge base (people, places, nations, stories, names_of_allah, glossary, etc.)
  content/explain/        THE OUTPUT: one JSON per ayah (6,236 files across 114 surah directories)
  work/                   (ignored) raw downloads, quran.sqlite, scratch/, review/
web/
  astro.config.mjs        Astro 5 config (site: qurangraph.com, no trailing slash)
  src/pages/              surah/, ayah/, entity/, root/, story/, graph.astro, search.astro, numbers.astro, etc.
  src/components/         UI components
  src/lib/search/normalize.ts   the ONE normaliser (scriptOf, arabicKey, arabicSkeleton, arabicVariants, banglaKey,
                                 banglaStem, banglaToLatin, translitKey, consonantKey, stem, tokenize, editDistance)
  scripts/normalize-cli.ts      JSON stdin → tokens [term, surface, script, stop, skeleton]
  tests/normalize.test.ts       node:test (6 tests)
  tests/golden.json             search golden set (54 queries, 3 languages)
  public/audio/bn/              Bengali neural TTS: 114 .mp3 + 114 .json alignment files (335 MB)
.github/workflows/ci.yml  CI: uv sync, normaliser tests, qg check over all explained surahs
docs/                     PILOT-REPORT, SOURCE-ISSUES, permissions/EMAILS
```

### Database (`ingest/work/quran.sqlite`)

| Table | Columns (key ones) |
|---|---|
| `source` | id, kind, use, role, title, publisher, lang, version, licence, attribution, status |
| `surah` | id, name_ar, name_translit, name_en, type (Meccan/Medinan), revelation_order, ayat, rukus |
| `ayah` | id (1–6236), surah, ayah, text_uthmani (display), text_simple (search), skel (search key), juz, hizb_quarter, manzil, ruku, page, sajda |
| `basmala` | surah, text_uthmani, text_simple (112 rows; not in 1 or 9) |
| `word` | surah, ayah, pos, text, root, lemma, tag, features, segments (JSON) — QAC segmentation, 77,429 rows |
| `text` | source, surah, ayah, text, footnotes, note (`misaligned:s:n` / `same-wording:s:n`) |

**Key source IDs in `text` table:**

| Source ID | What it is | Language |
|---|---|---|
| `qe-english-saheeh` | Saheeh International translation | English |
| `qe-bengali-zakaria` | Dr. Abu Bakr Zakaria translation | Bangla |
| `qe-english-mokhtasar` | Al-Mukhtasar tafsir (displayed) | English |
| `qe-bengali-mokhtasar` | Al-Mukhtasar tafsir (displayed) | Bangla |
| `qe-arabic-mokhtasar` | Al-Mukhtasar tafsir | Arabic |
| `qe-arabic-moyassar` | Al-Muyassar tafsir | Arabic |
| `qe-english-hilali-khan` | Hilali-Khan translation | English |
| `qe-english-rwwad` | Rwwad translation | English |
| `qe-bengali-rwwad` | Rwwad translation | Bangla |
| `g-en-ibn-kathir` | Ibn Kathir (grounding only!) | English |
| `g-en-jalalayn` | Jalalayn (grounding only!) | English |
| `g-en-maarif` | Ma'ariful Qur'an (grounding only!) | English |
| `g-ar-saadi` | Tafsir as-Sa'di (grounding only!) | Arabic |
| `g-ar-ibn-kathir` | Ibn Kathir Arabic (grounding only!) | Arabic |
| `g-bn-ahsanul-bayan` | Ahsanul Bayan (grounding only!) | Bangla |

Grounding mirrors store one passage under every ayah it covers; `qg ctx` prints each passage once.

## 7. How to write explanations at the same quality

The pilot used Claude Code sub-agents. You do the same job directly, in a loop. **Same rules, same files, same tools.**

1. Read `ingest/agent/INSTRUCTIONS.md` and the three examples **every time you start a new session**.
2. Pick a range: `ingest/qg todo <surah> <a-b>`.
3. For each passage of **3–8 consecutive ayat** (keep a story or argument together):
   1. `ingest/qg ctx <surah> <a-b>` — read it all. Sources appear as `[source-id]`; display sources first, then
      grounding. A line saying `NOT AVAILABLE` means that source's row is misaligned: don't use or cite it.
   2. Write **one** scratch file `ingest/work/scratch/<surah>-<a>.json` containing a JSON **list** of the passage's
      explanations (schema in INSTRUCTIONS).
   3. `ingest/qg put ingest/work/scratch/<surah>-<a>.json` → prints `OK`/`FIX` per ayah with errors and warnings.
      Fix every **ERROR** and re-put. Fix every **warning** unless it is clearly a false alarm (the reading-grade
      formula is rough with transliterated names; a warning about source names is never a false alarm).
4. After a surah: `ingest/qg check <surah>` must say `N valid, 0 with errors`.
5. `cd ingest && uv run generate/review_page.py <surah>` and look at the result in a browser.

### Pre-dump workflow (speeds up explanations)

Before starting a new surah, dump the word morphology and grounding text:

```python
# Dump words
import sqlite3, json
con = sqlite3.connect('ingest/work/quran.sqlite')
cur = con.cursor()
cur.execute('SELECT surah, ayah, pos, text, root, lemma FROM word WHERE surah = ? ORDER BY ayah, pos', (SURAH,))
words_by_ayah = {}
for s, a, p, t, r, l in cur.fetchall():
    words_by_ayah.setdefault(a, []).append({'pos': p, 'text': t, 'root': r, 'lemma': l})

# Dump grounding (all sources in one query)
cur.execute('''
SELECT a.ayah, a.text_uthmani,
    MAX(CASE WHEN t.source = "qe-english-saheeh" THEN t.text END),
    MAX(CASE WHEN t.source = "qe-bengali-zakaria" THEN t.text END),
    MAX(CASE WHEN t.source = "qe-english-mokhtasar" THEN t.text END),
    MAX(CASE WHEN t.source = "qe-bengali-mokhtasar" THEN t.text END),
    MAX(CASE WHEN t.source = "g-en-ibn-kathir" THEN t.text END),
    MAX(CASE WHEN t.source = "g-bn-ahsanul-bayan" THEN t.text END)
FROM ayah a LEFT JOIN text t ON a.surah = t.surah AND a.ayah = t.ayah
WHERE a.surah = ? GROUP BY a.ayah ORDER BY a.ayah''', (SURAH,))
```

### Schema strictness (common mistakes to avoid)

- **`kinds`** must be from: `belief`, `worship`, `dua`, `command`, `prohibition`, `promise`, `warning`, `story`,
  `parable`, `oath`, `law`, `ethics`, `argument`, `description-of-allah`, `hereafter`, `creation`, `address`,
  `praise`, `glad-tidings`. Not `mercy`, not anything else.
- **`entities`** keys must be: `people`, `nations`, `places`, `unseen`, `names_of_allah`, `events`, `things`.
- **`key_words[].pos`** must be the exact 1-based index in the `word` table. Query `words_<surah>.json` to verify.
- **`key_words[].root`** must exactly match `word.root` in `quran.sqlite`. Use `null` for particles.
- **`simple_en`**: 25–140 words, Flesch-Kincaid grade ≤ 8.0.
- **`lesson_en`**: 6–45 words.
- **`real_life_en`**: 15–90 words.
- **Bangla**: each sentence ≤ 30 words, natural চলিত ভাষা, no Latin characters.
- **`sensitivity`**: one of `none`, `aqeedah`, `fiqh`, `often-misquoted`, `eschatology`, `interfaith`.
- **Banned English words**: `\bjourney\b`, `\bembrace\b`, `\bprofound\b`, and others in the validator.

**Quality bar (check yourself before every put):**
- `simple_en`: 2–5 short sentences, a 14-year-old understands it, explains rather than repeats the translation,
  names no sources. Every sentence is backed by a claim.
- `simple_bn`: natural চলিত Bangla written for a Bangla reader (not a translation of the English), standard Islamic
  terms (ঈমান, তাকওয়া, সালাত, আখিরাত…), no English words.
- `real_life_*`: concrete everyday situation (work, family, school, money, phone, illness), shows living the ayah,
  never a ruling, never about harming anyone, no politics, no real living people.
- Sensitive ayat set `sensitivity` (aqeedah / fiqh / often-misquoted / eschatology / interfaith) and fill
  `context_*`; disputed meanings set `scholars_differ` and name who holds which view.
- Honour terms: "the Prophet ﷺ", other prophets "(peace be upon him)" on first mention; Bangla ﷺ / (আলাইহিস সালাম).
- Confidence is honest; anything unsure goes in `uncertain`.

**Efficiency (this matters — the pilot cost ~6,000 tokens per ayah):** one `ctx` per passage, one write, one put;
never print explanation files or the database back; don't re-read the instructions mid-session; process a whole
surah (or ~40–50 ayat) per working session, then start fresh. Full Quran ≈ 13× the pilot.

## 8. Current status and next steps

> **The entire Quran explanation corpus (all 114 surahs, 6,236 ayat) is 100% GENERATED and VERIFIED.**
> All technical build phases (Phases 0 through 8) are completely finished.

### Completed Milestones

1. **Explanations Complete (114/114 Surahs, 6,236/6,236 Ayat)**:
   - Full 114-surah validation sweep: **0 errors across all 6,236 ayat**.
   - Tafsir names check: **0 warnings across all 114 surahs** (strictly 0 scholar or book names in teaching text).
   - Strict Flesch-Kincaid grade <= 8.0 across all English teaching text.
   - Pure चलিত Bangla with <= 30 words per sentence, 0 exclamation marks, 0 Latin characters.
2. **Knowledge Graph Rebuilt**:
   - `ingest/work/graph.sqlite` holds **17,711 nodes and 150,716 edges**.
   - Shards exported to `ingest/work/export/graph/`.
   - Unit tests passed: `ingest/graph/test_graph.py` (4/4 tests OK).
3. **Static Website Production Build**:
   - `web/dist` generated: **8,898 HTML pages / 9,126 static files** (well under Cloudflare's 20,000 file limit).
   - Clean build in ~14 seconds.
4. **Search Engine & Benchmark Tests**:
   - 61/61 unit tests pass (`web/tests/*.test.ts`).
   - 54/54 golden search queries pass with 100% precision across English, Arabic, and Bangla.

---

### Tasks waiting on the owner (don't do these yourself)

- **Permission emails**: Send the 9 permission emails (`docs/permissions/EMAILS.md`) and record replies.
- **Scholarly review**: Coordinate with a qualified Islamic scholar; the priority review queue has 1,366 must-review ayat (`docs/SOURCE-ISSUES.md`).
- **Domain & Deployment**: Set up Cloudflare Access + noindex private launch as decided in §2.

- Send the 9 permission emails (`docs/permissions/EMAILS.md`) and record replies.
- Find a qualified reviewer; the 41 must-review pilot ayat come first.
- Domain name; where to push (no git remote yet).

## 9. Known data quirks (all handled — don't "fix" them again)

- Tanzil joins the Basmalah to ayah 1 → split into table `basmala` (characters unchanged). Shadda before kasra in 95:1/97:1.
- Uthmani vs simple spelling differ (dagger alif): compare with `arabicSkeleton`, never raw strings.
- Morphology word segmentation ≠ Tanzil whitespace words in 116 ayat — use the `word` table for words, always.
- spa5k mirror: `en-al-jalalayn` contaminated (we use `tafsir-al-jalalayn`); the "al-Wahidi" mirror was another
  book (removed); passages repeated per ayah and carried across surah boundaries (handled in build/ctx).
- QuranEnc Al-Mukhtasar: 73 misaligned rows (hidden, not citable), 52 repeated refrains (kept); ~815 Bangla ayat
  with legacy-font characters (shown as is until QuranEnc answers).
- QuranEnc's version list omits the Bangla/Mukhtasar/Muyassar editions → versions are recorded as content fingerprints.
- Full list and reviewer items: `docs/SOURCE-ISSUES.md`.
- **Do NOT query `qe-bengali-mujibur`** — it does not exist in the database. The Bangla translation is `qe-bengali-zakaria`.

## 10. Gotchas

- Run `uv run …` from `ingest/`; `ingest/qg` works from anywhere (absolute paths inside).
- zsh doesn't split variables: inside loops use `ingest/qg ctx ${=spec}` or pass arguments separately.
- `ingest/qg ctx … | head` may print a harmless `BrokenPipeError`.
- The validator calls Node for Arabic checks — Node must be on PATH.
- `fetch.py` skips sources already in the lock; use `--force <id>` to refetch one.
- `build_text.py` deletes and rebuilds `quran.sqlite` — explanations are not stored there, so it is safe.
- **Word position lookups**: Always verify `key_words[].pos` against the `word` table (or the pre-dumped
  `words_<sss>.json`). Off-by-one errors are the most common validation failure.
- **FK reading grade**: Keep sentences short, use monosyllabic words. Split long Bangla sentences at ≤ 30 words.

## 11. Waiting on the owner (don't do these yourself)

- Send the 9 permission emails (`docs/permissions/EMAILS.md`) and record replies in its tracking table.
- Find a qualified reviewer; the 41 must-review pilot ayat come first (`docs/SOURCE-ISSUES.md`, "Priority review items").
- Choose how to run the full generation.
- Domain name; where to push (no git remote yet).
