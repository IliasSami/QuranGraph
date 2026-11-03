# Agent guide — QuranGraph

Start here: **read `HANDOFF.md` fully before doing anything.** It holds the decisions already made, the hard rules,
the current state, setup, the explanation workflow and the next tasks in order.

Non-negotiable rules (details in HANDOFF.md §3):

- Never edit displayed Quran text (Tanzil) or QuranEnc translations/tafsir. They are shown verbatim.
- Sources with `use: grounding` in `ingest/sources.yaml` are never shipped in website files.
- Explanations follow `ingest/agent/INSTRUCTIONS.md` exactly, and every point cites a source. No rulings, no
  invented hadith, stories or numbers.
- `ingest/content/explain/` is the expensive output. Never delete or bulk-regenerate it.
- Ask the owner before sending emails, publishing, deploying, committing or pushing.

Quick check that the environment works:

```bash
cd ingest && uv sync && uv run fetch/fetch.py && uv run core/build_text.py && cd .. && node --test "web/tests/*.test.ts" && ingest/qg stats
```
