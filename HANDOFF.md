# QuranGraph — Handoff for the next coding agent

**Read this file completely before touching anything.** It is the single entry point: what the project is, every
decision already made, exactly where work stopped, how to set up, how to write explanations at the same quality,
and the next tasks in order. Written 3 Nov 2026 at the end of Phase 0.

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

## 4. Where work stopped (state at handoff)

**Phase 0 is done; its gate is waiting on the owner** (scholar review, permission emails, generation decision).

| Item | State |
|---|---|
| Source manifest + fetcher with SHA-256 lock | Done: `ingest/sources.yaml`, `ingest/sources.lock.json`, `ingest/fetch/fetch.py` |
| Text core database | Done: `ingest/work/quran.sqlite` (regenerable) — 6,236 ayat, 77,429 words, 1,651 roots, 4,763 lemmas, 9 display editions + 6 grounding sources |
| Shared normaliser (Arabic/Bangla/Latin/transliteration) | Done: `web/src/lib/search/normalize.ts`, Python bridge `ingest/core/normalize.py`, tests 6/6 pass |
| Explanation toolkit | Done: `ingest/qg` (ctx/word/root/put/check/todo/warned/stats), schema + validator `ingest/generate/schema.py`, review page `ingest/generate/review_page.py` |
| **Explanations written** | **591 / 6,236 ayat**: surah 1 (all), 2:1–20, surahs 78–114 (all). All pass the validator (0 errors). Stored in `ingest/content/explain/<sss>/<aaa>.json` |
| Search golden set | Written: `web/tests/golden.json` (55 queries, 3 languages); engine not built yet (Phase 5) |
| Permission emails | Drafted, **not sent** (owner sends) |
| Git | Initial commit `8c157ca` on `main` (no remote yet). `ingest/work/` is ignored and regenerable |

**Known open problem in the 591 pilot ayat:** 515 of them name tafsir sources inside the teaching text
("Al-Mukhtasar explains…"). The rules now forbid this (INSTRUCTIONS "Teach, don't cite, in the text") and the
validator warns about it. They need the polish pass in §8 task 1.

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
cd .. && node --test "web/tests/*.test.ts"     # expect: pass 6, fail 0
```

```bash
ingest/qg stats                       # expect: explained 591/6236 ayat
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
  generate/qg.py          the `ingest/qg` CLI (wrapper script: ingest/qg)
  generate/schema.py      validate(d, db) -> (errors, warnings)
  generate/review_page.py → ingest/work/review/index.html (all explained ayat, filters for flagged ones)
  agent/INSTRUCTIONS.md   explanation rules + JSON schema + theme list
  agent/examples/         reference explanations
  content/explain/        THE OUTPUT: one JSON per ayah
  kb/                     (empty) curated knowledge base, Phase 2
  work/                   (ignored) raw downloads, quran.sqlite, scratch/, review/
web/
  src/lib/search/normalize.ts   the ONE normaliser (scriptOf, arabicKey, arabicSkeleton, arabicVariants, banglaKey,
                                banglaStem, banglaToLatin, translitKey, consonantKey, stem, tokenize, editDistance)
  scripts/normalize-cli.ts      JSON stdin → tokens [term, surface, script, stop, skeleton]
  tests/normalize.test.ts       node:test
  tests/golden.json             search golden set for Phase 5
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

**What the validator enforces** (so you know why it complains): required fields; ayah exists; word counts per
field; reading grade; banned robotic phrases and `!`; Bangla fields really Bangla; Arabic inside your text must
match Quran text; `key_words[].pos` exists and its `root` equals the morphology root (use `null` for particles —
the `WORDS` line shows `-`, write `null`); every claim cites a source that has usable text for that ayah or its
passage; at least one claim cites the displayed tafsir (Mukhtasar/Muyassar); known `kinds`, `sensitivity`,
`entities` keys; `scholars_differ: true` requires `differ_note_en` (and `differ_note_bn`); no source names in the
teaching text.

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

## 8. Next tasks, in order

1. **Polish pass on the 591 pilot ayat (style only).**
   - Find them: `for s in 1 2 $(seq 78 114); do ingest/qg warned $s "names a tafsir"; done` (prints ayah ranges per surah).
   - For each, rewrite only `simple_*`/`lesson_*`/`real_life_*` so they teach in plain words without naming sources,
     keeping every fact. Move nothing out of `claims` — attributions already live there.
   - Keep `differ_note_*` attributions.
   - Re-put via a scratch file, then `qg check` until those warnings are gone.
   - Done when the 591 ayat have 0 errors and 0 "names a tafsir" warnings.
2. **Improve the context bundle** (`ingest/generate/qg.py`, `CTX_SOURCES` and `ctx()`):
   - Raise the Zakaria footnote cap from 1,500 to 3,000 characters.
   - Raise the Ibn Kathir cap for passages longer than 8 ayat (cut sentences, not mid-word).
   - Drop Saheeh International from the bundle (cited once in 591 ayat; it is still displayed on the site).
   - Re-measure the bundle size and record it in `docs/PILOT-REPORT.md`.
3. **Review-priority field.** In `qg stats` and the review page, split flags into *must review* (aqeedah, fiqh,
   often-misquoted, interfaith, confidence < 0.88, `scholars_differ` on aqeedah) and *sample review* (eschatology only).
4. **CI** (ask the owner before adding a remote or pushing).
   - Add `.github/workflows/ci.yml` running: `uv sync`, the normaliser tests, and a `qg check` over every explained surah.
   - The workflow needs `quran.sqlite`, so it either runs `fetch.py` + `build_text.py` (slow, ~15 min) or caches
     `ingest/work/raw` keyed on `sources.lock.json`.
5. **Phase 1 completion items from PLAN §12** (text core is mostly done):
   - Rule-based Latin transliteration from vocalised Arabic (`ingest/core/translit.py`).
   - Bangla surah names (curated, reviewed).
   - Weekly `fetch.py --check` job.
6. **Phase 2 — curated knowledge base** (`ingest/kb/`, PLAN §4): people, places, nations, stories → episodes,
   names of Allah, glossary, learning paths, with Wikidata Q-ids. Normalise the `entities` and `themes` already in
   the 591 explanations against it.
7. **Phase 3 — full generation** of the remaining 5,645 ayat, only after the owner decides how (Claude/Gemini
   agent sessions vs. Anthropic Batch API) and after a scholar has reviewed the pilot. Go in Quran order or by juz;
   al-Baqarah 21–286 next.
8. Phases 4–8 as in PLAN §12 (graph + stats, search engine with the golden set, website, audio, launch).

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

## 10. Gotchas

- Run `uv run …` from `ingest/`; `ingest/qg` works from anywhere (absolute paths inside).
- zsh doesn't split variables: inside loops use `ingest/qg ctx ${=spec}` or pass arguments separately.
- `ingest/qg ctx … | head` may print a harmless `BrokenPipeError`.
- The validator calls Node for Arabic checks — Node must be on PATH.
- `fetch.py` skips sources already in the lock; use `--force <id>` to refetch one.
- `build_text.py` deletes and rebuilds `quran.sqlite` — explanations are not stored there, so it is safe.

## 11. Waiting on the owner (don't do these yourself)

- Send the 9 permission emails (`docs/permissions/EMAILS.md`) and record replies in its tracking table.
- Find a qualified reviewer; the 41 must-review pilot ayat come first (`docs/SOURCE-ISSUES.md`, "Priority review items").
- Choose how to run the full generation.
- Domain name; where to push (no git remote yet).
