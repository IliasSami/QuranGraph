# Phase 0 pilot report (3 Nov 2026)

**Scope:** al-Fatiha (7), al-Baqarah 1–20, and all of Juz 30 (surahs 78–114) = **591 ayat** (9.5% of the Quran).
Explanations were written by 13 parallel Claude Code agents following `ingest/agent/INSTRUCTIONS.md`, calibrated on
the al-Fatiha reference examples. Explanations: `ingest/content/explain/`. Review page: `ingest/work/review/index.html` (rebuild with `uv run generate/review_page.py`).

## Quality

| Measure | Result |
|---|---|
| Ayat passing the automatic validator | **591 / 591** (0 errors) |
| Claims per ayah, each citing its sources | 3.7 on average |
| Sources cited most | Sa'di 647 · Ibn Kathir 645 · Mukhtasar EN 623 / BN 608 · Jalalayn 595 · Muyassar 500 · Ahsanul Bayan 475 · Ma'ariful Qur'an 438 · Zakaria 415 |
| Differences of opinion recorded (`scholars_differ`) | 84 ayat, each naming the views and who holds them |
| Occasions of revelation | 20 (5 marked sahih, 15 "reported") |
| Self-rated confidence | min 0.84, average 0.91 |
| Sensitivity flags | eschatology 166 · aqeedah 21 · often-misquoted 10 · interfaith 6 · fiqh 4 |

**Spot checks** (112:1, 94:2, 109:6 and others): faithful to the sources; careful on aqeedah; 94:2 (the Prophet's ﷺ
"burden") gives all four scholarly views; 109:6 corrects the common misreading using the sources.

**One systematic style problem:** 515 of 591 explanations name sources inside the simple text ("Al-Mukhtasar
explains…"). That reads like a tafsir digest, not plain teaching. Fixed for the full run (instructions + a new
validator warning); the 591 pilot ayat need a short **polish pass** that moves attributions into `claims`.

**Review load:** 265 ayat are in the review queue, mostly eschatology. Suggest: aqeedah, often-misquoted, interfaith
and fiqh (41 ayat) and anything below 0.88 confidence as *must review*; eschatology as *sample review*.

## Source problems found (all logged in docs/SOURCE-ISSUES.md)

Fixed in the pipeline: Basmalah joined to ayah 1 in Tanzil (split out, text unchanged); a contaminated Jalalayn
mirror (replaced); a mislabelled "al-Wahidi" mirror that was another book (removed); mirrors repeating the previous
surah's passage (40 rows removed); 73 misaligned Al-Mukhtasar rows (hidden, not citable). To report to QuranEnc:
legacy-font characters in ~815 Bangla Mukhtasar ayat, misaligned rows, a few wording slips.

## Cost and time (measured)

- Reported agent usage averaged **about 6,000 tokens per ayah** (9 agents with complete figures: 2.55M tokens for 423 ayat).
- The pilot used about **two full usage windows** of your Claude plan (the 5-hour limit was reached twice).
- The full Quran needs about **15× the pilot's source text** (48.7M characters of context vs 3.3M) and 10.6× its ayat,
  so roughly **13× the pilot**: about 45M agent tokens, or **~25 usage windows** at this pace (5–7 days of
  stop-and-resume on this plan).

**Ways to cut it (for the Phase 3 decision):**
1. Run the full generation through the **Anthropic Message Batches API** (needs an API key; batch pricing is
   discounted and runs unattended overnight). An exact quote needs a 1-surah test run with a key.
2. Draft with a smaller model and use the larger model only to verify and fix flagged ayat — test on one surah first.
3. Trim the bundle: Saheeh International is almost never cited (1 time), so drop it from the context; cap very long
   Ibn Kathir passages per ayah instead of per passage.

## Gate (Phase 0 → Phase 1)

- [x] Sources fetched with licence manifest and checksums; text core verified (6,236 ayat, 77,429 words, 1,651 roots)
- [x] Shared normaliser with tests (6/6 pass)
- [x] Generation pipeline, schema, validator, review page
- [x] Pilot on 591 ayat; quality and cost measured
- [ ] **Scholarly review of the pilot** (the 41 must-review ayat at least) — needs a reviewer
- [ ] **Permission emails sent** (docs/permissions/EMAILS.md) — to be sent from your address
- [ ] Decision on how to run the full generation (subscription vs Batch API)
