# QuranGraph

A free, static website that turns the whole Quran into a connected knowledge graph for beginners: every word,
ayah, surah, concept, person, place and story linked, explained in plain English and Bangla, searchable in English,
Arabic and Bangla (including transliteration). See [PLAN.md](PLAN.md) for the full design.

**Status: Phase 0** (sources, text core, normaliser, explanation pilot). Private; not yet deployed.

## Layout

```
ingest/                    offline pipeline (Python 3.12, uv)
  sources.yaml             every source: licence, attribution, use (display | data | grounding), status
  sources.lock.json        exact version + SHA-256 of every downloaded file
  fetch/fetch.py           downloads sources into ingest/work/raw/ (not committed)
  core/build_text.py       builds ingest/work/quran.sqlite: surahs, ayat, words (root/lemma), translations, tafsir
  core/normalize.py        Python access to the shared normaliser (web/src/lib/search/normalize.ts, via Node)
  generate/qg.py           `ingest/qg`: context bundles, put/check/todo for ayah explanations
  generate/review_page.py  review page for explained ayat (ingest/work/review/index.html)
  content/explain/         the ayah explanations (one JSON per ayah) — committed, the real source of truth
  generate/schema.py       explanation schema + automatic checks
  agent/INSTRUCTIONS.md    how explanations are written (rules, schema, examples)
web/                       website (Astro, static) — from Phase 5
  src/lib/search/normalize.ts   the one text normaliser (Arabic, Bangla, Latin, transliteration)
  tests/                   normaliser tests, search golden set
docs/permissions/EMAILS.md permission requests to send, with a tracking table
```

## Build the text core

```bash
cd ingest && uv sync
```

```bash
uv run fetch/fetch.py
```

```bash
uv run core/build_text.py
```

Run the tests from the repository root:

```bash
node --test "web/tests/*.test.ts"
```

## Sources and licences

The Arabic text is from the [Tanzil Project](https://tanzil.net), shown verbatim (CC BY 3.0, no changes).
Translations and Al-Mukhtasar tafsir are from [QuranEnc.com](https://quranenc.com), shown unmodified with
publisher and version. Morphology is from the [Quranic Arabic Corpus](https://corpus.quran.com) (GPL), as corrected
by [mustafa0x/quran-morphology](https://github.com/mustafa0x/quran-morphology). Sources marked `grounding` in
`sources.yaml` are read by the explanation step only and are never published. Full list: `ingest/sources.yaml`.
