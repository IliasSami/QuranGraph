# QuranGraph: Research & Build Plan

*A free, private-first website that turns the whole Quran into a connected knowledge graph for beginners: every
word, ayah, surah, concept, person, place and story linked together, explained in plain English and Bangla,
searchable in English, Arabic and Bangla, with recitation audio and a reproducible statistics lab.*

Prepared 3 Nov 2026. Based on (a) a full review of the architecture of `fahads-pdf-sync`
(slides.bible-study-library.workers.dev), and (b) five parallel research tracks covering text and translations,
linguistics datasets, tafsir/history, audio/fonts/hosting, and statistics plus competing products. Licence facts
marked **(verified)** were checked against the live source on 3 Nov 2026.

**Decisions already made by the owner**

| Question | Decision |
|---|---|
| Explanations | Written by AI **at build time**, grounded only in cited, recognised tafsir, and labelled as a simplified summary |
| Numerical claims | Reproducible counts with the method shown. Popular claims are labelled *verified / depends on counting rules / not reproducible / disputed by scholars* |
| Runtime | 100% static, $0/month, **no AI on the live site** |
| Review | **Launch privately first**, and open to the public only after religious review |

---

## 0. The short version

1. **Same architecture as the Bible library.** Heavy work happens offline in a Python pipeline. The site is plain
   static files on Cloudflare Workers Static Assets. Search runs in the visitor's browser in a Web Worker. Cost is
   $0/month.
2. **The text comes from the most trusted sources, and is never altered.**
   - **Arabic:** Tanzil, which is verified letter by letter against the Madani Mushaf.
   - **Translations and a short tafsir:** **QuranEnc.com** (Rowwad Translation Center and partners). It is the one
     authoritative source that explicitly allows republishing **(verified)**.
   - **Excluded:** the Quran.com API. Its 2026 terms forbid building static copies from its data.
3. **Every ayah gets three layers of meaning.**
   - **Licensed source text, shown exactly as published:** Saheeh International and Abu Bakr Zakaria translations,
     plus Al-Mukhtasar tafsir in English and Bangla.
   - **A simple explanation written for QuranGraph:** grounded in Mukhtasar, Sa'di, Ibn Kathir and Ma'ariful
     al-Qur'an, with a citation for each point.
   - **A real-life example:** short and practical, also grounded in those sources.
4. **The graph is built for the Quran, not a generic topic list.** Its node types are:
   - Words → lemmas → roots
   - Ayah, passage, surah
   - People, places, events, stories, nations
   - Names of Allah
   - Concepts and values: commands, prohibitions, virtues, parables, oaths, duas
   - Hadith and tafsir sources

   Every link records its origin: *the Quranic text*, *a cited source*, *AI-extracted and checked*, or *computed*.
5. **Search works in three languages.** It uses the same four-channel engine as the Bible library (words, entities,
   graph, references), upgraded:
   - Arabic search ignores diacritics and spelling variants, and can match by root.
   - Bangla text is normalised and lightly stemmed.
   - Transliterated queries are matched by sound, in Latin script ("ar-rahman") or Bangla script ("রহমান").
6. **Audio follows religious rules.**
   - Arabic is always a human reciter; Mishary Alafasy is the default, with words highlighted as they are recited.
   - English is the Saheeh International audio by Ibrahim Walk.
   - **No trusted Bangla translation audio exists anywhere.** We generate it with an open-licence neural voice
     reading the licensed Bangla text, label it clearly, and **never use synthetic speech for Arabic**.
7. **Learning comes first.** The site offers guided paths (start with al-Fatiha and the prayer surahs), a
   word-frequency vocabulary course with spaced repetition, story timelines and maps, concept maps, and a Numbers
   Lab. Notes and bookmarks work without an account. The site can be installed and used offline.
8. **A private launch, then a review gate.** The site starts behind Cloudflare Access (an email PIN) and blocked from
   search engines. Each surah becomes public only after a qualified reviewer signs off its explanations.
9. **About 8–9 weeks of build time**, in 8 phases with a quality gate after each. Section 13 lists the permission
   emails to send before launch.

---

## 1. What we learned from the Bible library, and what changes

| Keep (proven) | Change / upgrade |
|---|---|
| Static-only Astro site; Web Worker search with a fallback for old iPads; four-channel Reciprocal Rank Fusion with "why it matched" reasons | **One search file of 3.1 MB → sharded index.** Load the core first, then fetch per-language and tafsir shards on demand |
| BM25F scores precomputed and quantised to a byte; delta-encoded postings | Root and lemma postings from morphology, so a search like `رحم` finds every occurrence of the root (rahma, rahman, rahim…) |
| Personalized PageRank precomputed per entity; Leiden clusters; IDF-weighted "connected" items | Typed edges with **provenance**, and edge confidence shown in the UI |
| Per-unit JSON schema plus an automatic validator (`kg check`) | The validator also checks Arabic quotes match Tanzil **byte for byte**, verse references exist, and every claim cites a source ID |
| Golden-set search tests | Run in **CI on every push** (the old project had no CI) |
| `_headers` caching, CSP, noindex | Content-hashed filenames for data shards (immutable caching), and Cloudflare Access during the private phase |
| `build.sh` only rebuilds what changed | Generated data kept **out of git**: the repo holds only source data and code, unlike the old 1.1 GB repo |
| Accessibility for older readers (large type, 48 px targets) | WCAG 2.2 AA, full RTL support, dyslexia options, a screen-reader text mode, themes |
| Text normalisation shared by the index builder and the browser | **One** normaliser written in TypeScript and also run by the Python pipeline (no Python/TypeScript drift), with a parity test |

**Hard limit learned:** Workers Static Assets allows **20,000 files per deploy on the free plan** and 25 MiB per file
**(verified)**. The page plan in §6.4 is designed around it.

---

## 2. Sources

Every source shown to readers must be authoritative and licensed. A source we can't license may still be used as
**grounding**: our explanations paraphrase it with a citation, but its text is never shipped in the site files.

### 2.1 Quran text and structure

| Purpose | Source | Licence | How we use it |
|---|---|---|---|
| Arabic text (display) | **Tanzil Uthmani v1.1** (tanzil.net). Checked by program against grammar and recitation rules, then by hand against the Madani Mushaf with per-letter checksums, and reviewed by huffaz | CC BY 3.0, **verbatim only (verified)**; credit and a link to tanzil.net required; licence header kept in data files | Shown exactly as published. Never edited |
| Arabic text (search) | Tanzil Simple-clean | Same | Used only to build the search index; never shown as the Quran |
| Structure | Tanzil `quran-data.xml` | cc-by | Surah names, Meccan/Medinan, revelation order (Egyptian standard), juz, hizb, rub, manzil, ruku, page, sajda |
| Word segmentation and mushaf layout (604 pages × 15 lines) | QUL (qul.tarteel.ai) KFGQPC V2 word table and layout | **Unclear**: code is MIT, data licence unstated | Factual structure, so low risk. **Ask Tarteel in writing** |
| Cross-check | KFGQPC Unicode text (github ibnhazm/KFGQPC) | Free | Automated diff against Tanzil |

**Word counts depend on how words are split** (tokenisation): about 77,430 by the Quranic Arabic Corpus, 77,881 by
splitting Tanzil Uthmani on spaces, and 78,248 by splitting Tanzil Simple. QuranGraph uses one word index (QUL/QAC
segmentation) for words, and **always shows the tokenisation next to any count**.

### 2.2 Translations

| Language | Primary | Secondary | Excluded (no licence) |
|---|---|---|---|
| English | **Saheeh International**, QuranEnc `english_saheeh` v1.1.2 **(verified)** | Hilali-Khan (`english_hilali_khan` v1.1.2), Rowwad (`english_rwwad` v1.0.20), Pickthall (public domain, via Tanzil) | The Clear Quran (exclusive licence), Abdel Haleem (© OUP), anything via the Quran.com API |
| Bangla | **Dr. Abu Bakr Muhammad Zakaria**, QuranEnc `bengali_zakaria` **(verified)** | Rowwad Bangla (`bengali_rwwad`); Muhiuddin Khan (Tanzil, non-commercial, rights unclear; only with permission) | Taisirul Quran, Rawai al-Bayan, Mujibur Rahman, Islamic Foundation Bangladesh (all need publisher permission) |

**QuranEnc's republishing conditions (verified), which the build enforces automatically:**
1. No changes, additions or deletions.
2. Credit the publisher and QuranEnc.com.
3. Show the version number.
4. Keep the translation's information.
5. Report any errors to QuranEnc.
6. Update to the latest version (a CI job checks `last_update` every week).
7. No inappropriate ads.

### 2.3 Word level: morphology, word-by-word meanings, roots

| Purpose | Source | Licence | Note |
|---|---|---|---|
| Root, lemma, part of speech and grammar features for every segment (about 128k) | **mustafa0x/quran-morphology** (corrected Quranic Arabic Corpus v0.4), with the original QAC 0.4 as reference | GPL, plus the QAC "no changes" clause | Derived data published as a **separate GPL data bundle** with the QAC notice and a link. Site code stays MIT. Ask Kais Dukes about the "no changes" clause |
| Word-by-word English | QUL wbw id 92 (from QuranWBW) | Unclear; upstream forbids copying | **Permission needed.** Fallback: Quranic Arabic Corpus glosses (GPL) |
| Word-by-word Bangla | QUL wbw id 94 (Greentech / QuranWBW) | Unclear | **The biggest licence risk.** Email Greentech and QuranWBW. Fallback: AI-glossed from the lemma plus the licensed Zakaria translation, marked "draft" until reviewed |
| Word transliteration (Latin) | **Generated by rule** from the Arabic with diacritics (standard ALA-LC-style table) | Our own work | No licence issue, and consistent |
| Root meanings | **Lane's Lexicon** (public domain; Perseus TEI XML) → short glosses | Public domain / CC (check the XML file) | Hans Wehr and the Omar dictionary are excluded (copyright) |
| Topics, ayah themes, similar ayat, mutashabihat | QUL (3,158 topics, 1,049 themes, 4,001 similar, 5,278 mutashabihat) | Unclear, origin undocumented | Graph edges labelled "suggested similarity". **Ask Tarteel**. QurSim (pairs from Ibn Kathir) if its authors agree |
| Concept ontology seed | Quranic Arabic Corpus ontology (about 300 concepts, 350 relations; on the website only) | GPL | Used as a starting point, then curated and extended |
| IDs and coordinates for people/places | **Wikidata** | CC0 | Q-ids, coordinates, cross-language labels |

### 2.4 Meaning: tafsir, context, hadith, history

| Purpose | Source | Licence | Use |
|---|---|---|---|
| Short tafsir, shown with every ayah (English and Bangla) | **Al-Mukhtasar fi Tafsir al-Qur'an** (Tafsir Center for Quranic Studies, Riyadh): `english_mokhtasar`, `bengali_mokhtasar` **(verified)** | QuranEnc republishing terms | **Shown verbatim** under "Source", and also used as grounding |
| Deeper grounding (Arabic) | Tabari, Ibn Kathir, Qurtubi (public-domain classical texts), Sa'di (on QuranEnc; key to confirm), al-Muyassar (KFGQPC) | Public domain / QuranEnc / KFGQPC | Grounding plus short quotes |
| Deeper grounding (English) | Ibn Kathir abridged (Darussalam), Ma'ariful al-Qur'an, Jalalayn (Royal Aal al-Bayt Institute) | © publishers | **Grounding only**: paraphrase with citations, never shipped in bulk |
| Deeper grounding (Bangla) | Ahsanul Bayan, Abu Bakr Zakaria tafsir, Ibn Kathir in Bangla | © publishers / KFGQPC | Grounding only |
| Occasions of revelation (asbab al-nuzul) | Reports in Bukhari and Muslim first, then al-Wahidi (trans. Guezzou) and al-Suyuti's *Lubab al-Nuqul* | Hadith public domain; Wahidi © RABIIT | Every report labelled with its source and grading. Weak reports are marked or left out |
| Hadith | sunnah.com (request a key and data dump), fawazahmed0/hadith-api (IDs, Arabic text, grades), HadeethEnc (English and Bangla, confirm terms) | Request / Unlicense / likely QuranEnc-style | Show the grade always. Link Bukhari Book 65 and Tirmidhi Book 47 (both arranged by surah) to their ayat |
| Prophets' stories, life of the Prophet ﷺ, history | Ibn Kathir *Qasas al-Anbiya* and *al-Bidaya* (Arabic, public domain), Ibn Hisham, *Ar-Raheeq al-Makhtum* (facts and dates only), plus the ayat themselves | Public domain / © | Our own story text, every step citing an ayah or source |
| Excluded on authenticity grounds | Tanwir al-Miqbas (falsely attributed to Ibn Abbas), esoteric Sufi tafsirs, Fi Zilal, Tafsir Fathul Majid (author unconfirmed), QRCD (licence forbids changes) | — | — |

### 2.5 Audio, fonts, lexicon of the interface

| Purpose | Source | Licence | Note |
|---|---|---|---|
| Arabic recitation per ayah | **EveryAyah.com** (`/data/Alafasy_64kbps/SSSAAA.mp3`). Fallbacks: verses.quran.com, cdn.islamic.network | No stated terms; files are CORS-open and long-cached **(tested)** | Streamed straight from their servers, with the reciter credited. Courtesy email to EveryAyah. Self-hosting one reciter needs about 0.6 GB in R2 if ever required |
| Word highlighting during recitation | Quran.com reciter-7 (Alafasy) word segments, or QUL segments (Alafasy is the only reciter with word-level timings) | Quran Foundation terms / unclear | **Permission needed.** Fallback: verse-level highlighting only |
| Teaching recitation | EveryAyah `Husary_Muallim_128kbps` | Same | For learners repeating after the reciter |
| Word-by-word audio | audio.qurancdn.com/wbw | Quran Foundation | Permission needed; otherwise left out |
| English translation audio | EveryAyah `English/Sahih_Intnl_Ibrahim_Walk_192kbps` | Same as EveryAyah | Matches the primary English translation |
| Bangla translation audio | **We generate it**: AI4Bharat Indic Parler-TTS (Apache-2.0), or Azure neural bn-BD voices, reading the licensed Zakaria text | Our own output | Labelled "computer voice reading the Zakaria translation". About 200 MB at Opus 24 kbps, one file per surah plus a timing file per ayah |
| Arabic fonts | **Amiri Quran** (OFL) as default; KFGQPC Uthmanic Hafs as an option (unmodified, credited, permission requested); Scheherazade New (OFL) | OFL / unclear | No subsetting of the KFGQPC font |
| Bangla and English fonts | Noto Serif/Sans Bengali, Hind Siliguri (OFL); Atkinson Hyperlegible and Lexend (OFL) for dyslexia mode | OFL | Self-hosted |
| Tajweed colours | alquran.cloud `quran-tajweed` markup (built on Tanzil) | Tanzil terms (letters unchanged) | Colour is never the only cue: each rule has a legend, a name and an underline style |

---

## 3. Gap analysis: what is missing from today's Quran sites, and what we add

Existing products:
- **Quran.com** is excellent for reading and listening.
- **Quranic Arabic Corpus** is the gold standard for grammar, but it is expert-only and dated.
- **QuranHive** and **Greentech** are strong word-study apps, but mobile-only.
- **Bayyinah** is deep teaching, but paid video.
- **Bangla apps** are fragmented and ad-heavy.

**No product joins concepts, stories, words, hadith and statistics into one connected, beginner-first experience,
and none does it well in Bangla.**

Your 11 requested features are all in the plan. Here are the **additions** from the research, and why each one
matters:

| # | Addition | Why |
|---|---|---|
| A1 | **Start Here path**: al-Fatiha → the short surahs recited in prayer → Ayat al-Kursi → the last two ayat of al-Baqarah, with the meaning of each part of the prayer | Beginners meet these ayat daily but rarely understand them |
| A2 | **Frequency-first vocabulary course with spaced repetition**: "these 125 words make up about half of all words recited" (exact figure computed from our own data), with flashcards linked to real ayat; progress saved in the browser | Proven demand (Understand Quran Academy); no graph-linked version exists |
| A3 | **Context view**: every ayah shows the passage it belongs to, what comes before and after, and the surah's structure | Reading an ayah alone is the most common beginner mistake |
| A4 | **Sensitive-ayah notes**: ayat that are often quoted out of context (fighting, inheritance, marriage, punishments) get a careful "read with context" note grounded in mainstream tafsir | Protects beginners and the project's credibility |
| A5 | **Names of Allah explorer**: every name, where it closes an ayah, what the ayah teaches about it | A classic study the graph makes natural |
| A6 | **Duas of the Quran, parables, oaths, and "O you who believe" commands**, each as browsable collections | High practical value, easy to extract reliably |
| A7 | **Glossary of Islamic terms** (taqwa, iman, ihsan, ghayb …) in plain English and Bangla, linked everywhere | Removes jargon, as the brief asks |
| A8 | **Translation comparison**: two or three licensed translations side by side, each word linked to the Arabic | Shows that translation is interpretation |
| A9 | **Story timelines and maps**: the prophets in order, the life of the Prophet ﷺ in Mecca and Medina, places on a map | The brief asks for history and storylines |
| A10 | **Surah structure diagrams**: the themes of each surah, its ring structure where scholars have shown one (Farrin, Cuypers, Islahi's coherence theory), all cited | Shows how the Quran is organised |
| A11 | **Numbers Lab** with methodology toggles and claim labels (§7) | Trust: reproducible, not sensational |
| A12 | **Notes, bookmarks, highlights and reading progress with no account**: stored in the browser, exportable as a file | Privacy, and no login for beginners |
| A13 | **Installable and offline**, with downloads per juz and per language | Unreliable data connections in Bangladesh |
| A14 | **Daily ayah and word of the day**, and shareable image cards (Arabic, translation, citation) | Habit and sharing |
| A15 | **Memorisation (hifz) helper**: hide/reveal, first-letter mode, repeat-ayah loops, a teaching reciter | Low effort with the data we already have |
| A16 | **Self-check quizzes** after each path step (generated, then reviewed) | Active recall makes learning stick |
| A17 | **Methodology and Sources page**, generated automatically from the licence manifest, with version numbers | QuranEnc requires it; it builds trust |
| A18 | **"Report a mistake"** on every explanation, as a pre-filled email or form, with every content version logged | Required for a responsibly reviewed AI layer |
| A19 | **UI in English and Bangla** (not only the content) | Bangla speakers are a primary audience |
| Later | Kids mode (illustrated stories), more languages (Urdu, Indonesian), a public data dump of the graph (CC/GPL), embedding-based "related ayat" with feedback | After launch |

Left out on purpose: AI question-answering at runtime (owner's decision), new rulings or fatwas, and recitation
checking with speech AI (Tarteel already does it well).

---

## 4. The knowledge model

### 4.1 Node types (estimated counts)

| Layer | Nodes | Count |
|---|---|---|
| Text | Surah · Passage (ruku / thematic section) · Ayah · Word (position) | 114 · ~560 · 6,236 · ~77,430 |
| Language | Lemma · Root · Grammatical form (verb forms I–X, patterns) | ~4,800 · ~1,650 · ~40 |
| Beings & places | Person (prophets, figures, groups of people), Nation/Group (Bani Isra'il, Ad, Thamud…), Place (with coordinates), Unseen beings (angels, jinn) | ~350 |
| Narrative | Story (e.g. Yusuf, Musa and Pharaoh), Story episode, Event, Era (pre-prophetic, Meccan, Medinan) | ~60 stories / ~600 episodes |
| Meaning | Concept/Theme · Value/Virtue · Command · Prohibition · Promise · Warning · Parable · Oath · Dua · Name of Allah · Glossary term | ~2,500 |
| Context | Occasion of revelation · Hadith reference · Tafsir citation | ~1,000 · ~2,000 · many |
| Learning | Path, Lesson, Vocabulary card, Quiz item | Generated |
| Numbers | Count (with its counting rule), Pattern, Claim | ~300 |

### 4.2 Edges and where each comes from

| Edge | Source of truth | Shown to readers as |
|---|---|---|
| ayah contains word; word → lemma → root | Morphology data | "Word" |
| ayah in passage, surah, juz, page; revelation order | Tanzil metadata | Structure |
| ayah mentions person/place/nation | The Quranic Arabic Corpus ontology plus AI extraction **checked against the word index** (the name must actually appear in the ayah, or a cited tafsir must say who is meant) | "Mentioned in this ayah" / "Refers to (according to Ibn Kathir)" |
| ayah teaches concept/value/command | AI extraction grounded in Mukhtasar; reviewed | "Theme" |
| ayah ↔ ayah (explains, parallel, similar wording) | Cross-references in tafsir (QurSim/Ibn Kathir), QUL similar-ayah and mutashabihat, shared rare lemmas | "Explained by", "Similar wording", "Same topic" |
| story → episode → ayat, in story order | Curated from Qasas al-Anbiya and tafsir, citing ayat | Timeline |
| ayah → occasion of revelation → hadith | Bukhari/Muslim first, then Wahidi/Suyuti, with grading | "Context of revelation (graded)" |
| Name of Allah → closing of ayah | Morphology plus a list of verse endings | "Closes with" |
| concept ↔ concept | Co-occurrence (NPMI) plus curated hierarchy (e.g. taqwa ⊂ iman) | "Related idea" |
| lemma ↔ lemma | Same root, and computed co-occurrence | "Same root" / "Often together" |

Every edge stores `{type, origin: text|source|ai_checked|computed, source_id, confidence}`, and the UI filters and
labels by origin. Computed edges never appear as scholarly claims.

---

## 5. Offline pipeline (`ingest/`, Python 3.12)

```
fetch/         pinned downloads with SHA-256 + licence manifest (sources.yaml)
  tanzil.py    Uthmani, Simple-clean, quran-data.xml        quranenc.py   translations + Mukhtasar (version-tracked)
  morphology.py mustafa0x/QAC                              qul.py        word table, layout, topics, similar (once permitted)
  lexicon.py   Lane TEI → root glosses                     wikidata.py   people/places Q-ids + coordinates
  hadith.py    graded hadith refs                           audio_meta.py EveryAyah index, segment timings
core/
  normalize    one normaliser (TS, run from Python via Node) + parity tests
  build_text   ayah/word/lemma/root tables (SQLite: work/quran.sqlite)
  translit     rule-based Latin transliteration from vocalised Arabic + Bangla-phonetic keys for search
generate/      LLM build-time layer (see §5.1) → work/explain/<surah>/<ayah>.json
validate/      `qg check`: schema, verbatim Arabic, citations exist, refs exist, entity names occur, Bangla script sanity
graph/         build_kg.py: entities, typed edges, PPR per entity, Leiden clusters, related ayat, story order
stats/         numbers_lab.py: all counts with their counting rules (§7) → reproducible notebook + JSON
tts/           Bangla audio generation (Parler-TTS / Azure) + forced alignment for ayah offsets
export/        site data (sharded JSON), search index shards, licence/attribution page data
```

### 5.1 How explanations are produced (AI at build time, grounded)

For each **passage** (about 560 runs, so neighbouring ayat share context):

1. **Retrieve** the passage's Arabic, the morphology, the Saheeh and Zakaria translations, Mukhtasar (EN/BN), Sa'di
   and Muyassar (Arabic), and Ibn Kathir / Ma'ariful / Jalalayn excerpts as private grounding only (never shipped).
   Also any graded occasion of revelation and related hadith.
2. **Generate** structured JSON per ayah:
   - `simple_en` and `simple_bn`: 2–5 plain sentences each.
   - `key_words`: the lemma and why it matters.
   - `lesson`: a practical takeaway.
   - `real_life`: one concrete example.
   - `entities` and `themes`: references to existing graph nodes, plus new candidates.
   - `context`: the passage flow.
   - `claims[]`, where every claim carries a `source_id` and an exact locator.
   - `sensitivity`: none, aqeedah, fiqh, or often misquoted.
3. **Validate automatically**:
   - every claim cites a retrieved source;
   - no Arabic quote differs from Tanzil;
   - every named entity occurs in the ayah or in a cited source;
   - reading level is checked (Flesch for English, sentence length for Bangla);
   - banned phrasing is caught: invented rulings, "scholars agree" without a source, robotic filler.
4. **Self-critique pass**: a second model run checks faithfulness against the sources and flags disagreements, so
   that "the scholars differ" is said whenever they do.
5. **Review queue**: any ayah flagged as sensitive, low-confidence or source-disagreeing goes to the reviewer page
   first. The surah summary is generated from the approved ayah explanations plus the Mukhtasar surah aims.
6. **Rules that never change**:
   - Arabic is shown only from Tanzil.
   - Translations are shown only verbatim from QuranEnc.
   - Our text is always labelled "Simplified explanation drawn from …".
   - No fiqh rulings are written. Those ayat point to scholars and summarise the mainstream view with sources.
   - The perspective is mainstream Sunni scholarship, and differences of opinion are noted.

**Tooling:** the generation runs through the Anthropic Message Batches API with the latest Claude model and
structured outputs. It can also run as Claude Code sessions with an `INSTRUCTIONS.md` and a `qg` helper command,
like `kg` in the Bible library. Phase 0 runs a pilot on al-Fatiha, Juz 30 and al-Baqarah 1–20 to measure quality,
token use and the exact cost before the full run.

### 5.2 Deterministic analysis (no AI)

- Lemma and root frequencies, and the vocabulary coverage curve.
- Collocations (PMI) and repeated phrases.
- Similar ayat: TF-IDF over lemmas, combined with QUL similar-ayah data.
- Verse length and rhyme (fasila) per surah.
- Personalized PageRank per entity; Leiden concept clusters; topic co-occurrence.
- Story ordering; timeline building; map coordinates.

---

## 6. Website

### 6.1 Stack

Astro (static) with small TypeScript scripts, as in the Bible library. Two kinds of interactive pieces run in the
browser and load only on the pages that use them:
- **Graph and visualisation:** Sigma.js (WebGL graph) plus D3 for charts and timelines, each with a list/table
  alternative for accessibility.
- **Maps:** MapLibre GL with a free vector-tile style, or a static SVG basemap to avoid tile limits.

The site is installable and works offline, with each juz and language downloadable separately.

### 6.2 Main screens

| Screen | What it shows |
|---|---|
| **Home** | Search box · Start Here path · daily ayah · continue reading · explore by story, concept, name of Allah, or number |
| **Surah** | Name and meaning, Meccan/Medinan, place in revelation order, summary, theme map / ring diagram, passages; play the whole surah |
| **Ayah** (core page) | Arabic (tajweed optional) with tappable words · translation(s) · **Simple explanation** · real-life example · context (before/after) · Mukhtasar source text · key words → roots · people/places/concepts · related ayat (labelled by type) · occasion of revelation (graded) · related hadith (graded) · audio: Arabic / English / Bangla |
| **Word / lemma / root** | Meaning (Lane gloss, simplified), every occurrence, forms, frequency rank, related roots, flashcard button |
| **Concept / value / command** | Plain definition · all ayat grouped by passage · connected concepts · mini graph |
| **Person / place / nation** | Who/what · every mention · story timeline · map · names in Arabic, English and Bangla |
| **Story** | Episodes in order, each with its ayat · characters · lessons · timeline · a "read in the Quran" path |
| **Explore graph** | Step-by-step explorer (as on the Bible library's Map of Ideas), full graph view, outline view |
| **Learn** | Paths · vocabulary course with spaced repetition · quizzes · hifz helper · progress |
| **Numbers Lab** | §7 |
| **Settings** | §6.5 |
| **Sources & Method** | Generated licence manifest, versions, review status per surah, how explanations are made |

### 6.3 Design language

Clean, minimal and compact, with depth one tap away:
- Text is organised in layers: summary first, then "more detail".
- Calm neutral palette with a single deep green accent and a gold focus colour. Light, dark, sepia and high-contrast
  themes.
- Arabic is shown generously: line-height of at least 2, never clipped.
- No hover-only controls; touch targets of at least 44 px.
- Visualisations are always optional, never the only way in.

### 6.4 Page budget (the free plan's 20,000-file limit)

| Item | Files |
|---|---|
| Ayah pages, each holding EN and BN content (the language toggle is client-side, so no duplicate pages) | 6,236 |
| Surah pages and passage anchors | 114 |
| Root pages (lemmas listed inside) | ~1,650 |
| Entity, story, concept, name and glossary pages | ~3,000 |
| Paths, lessons, labs, static pages | ~200 |
| Search shards, data shards, fonts, JS/CSS | ~800 |
| Bangla audio (one file per surah) plus timing files | ~230 |
| **Total** | **~12,300 (60% of the limit)** |

**Fallback:** if the site grows beyond this, either move media to R2 behind a custom domain, or upgrade to Workers
Paid ($5/month, 100,000 files).

### 6.5 Accessibility and customisation (WCAG 2.2 AA)

**Reading settings:**
- Separate size controls for Arabic, translation and interface text.
- Line and letter spacing; a reading-ruler overlay.
- Dyslexia font (Lexend or Atkinson Hyperlegible).
- Show or hide each layer: Arabic, transliteration, translations, explanation.
- Mushaf (page) mode or ayah-by-ayah mode.
- Tajweed colours on/off, with a legend and underline styles so colour is never the only cue.

**Themes:**
- Light, dark, sepia and high contrast.
- Respects the system's forced-colours mode and `prefers-reduced-motion`.

**Screen readers and keyboard:**
- A "screen-reader text" mode that exposes simple Arabic (Imlaei) instead of Uthmani symbols, which screen readers
  read badly.
- Every block carries its `lang` and `dir`.
- Full keyboard control with shortcuts that can be remapped or switched off.

**Audio and interface language:**
- No autoplay. Playback speed control. Repeat-ayah loops.
- Interface language: English or Bangla.

### 6.6 Search engine (in the browser, sharded)

- **Channels:** words (BM25F impacts), entities (names in AR/EN/BN, transliterations, aliases), graph (PPR), and
  references (`2:255`, `al-Baqarah 255`, `বাকারা ২৫৫`, `البقرة ٢٥٥`, with Arabic and Bangla digits).
- **Fields:** Arabic (simple), Arabic root and lemma, English translations, Bangla translations, explanations,
  Mukhtasar, entity names, glossary.
- **Normalisation:**
  - Arabic: strip diacritics and Quranic marks; unify alef/hamza, ya/alif maqsura and ta marbuta; remove tatweel;
    find roots through morphology lookup, with a light stemmer for words outside the Quran.
  - Bangla: NFC normalisation; nukta forms unified; ZWJ/ZWNJ removed; a light suffix stemmer (-ের, -কে, -রা, -গুলো,
    -টি, -দের …).
  - English: case folding, accent folding and a light stemmer.
- **Transliteration:** phonetic keys for Latin ("rahmaan" ≈ "rahman" ≈ "rehman") and for Bangla phonetic spellings,
  using rules adapted from Avro Phonetic (MIT/MPL; licence to check). Queries in any script are matched against the
  names of Arabic words and entities. Typo tolerance uses edit distance ≤ 1–2.
- **Shards:** the core (entities, references, Arabic) loads first, at about 400–600 KB compressed. Each language and
  the explanation index load the first time they are needed. Shards have hashed filenames and are cached
  permanently.
- **Results:** grouped by ayah or passage, with the reason each matched, and a "knowledge card" at the top for a
  person, concept, root or name of Allah.

---

## 7. Numbers Lab (statistics done honestly)

- **Every count shows its rule:** text edition, script, tokenisation, matching by surface form / lemma / root, which
  forms are included, and whether the unnumbered basmalas are included. Toggles change the rule and update the
  count live. Every count links to the exact list of matching ayat and word positions.
- **Baseline facts:**
  - 114 surahs; 6,236 ayat (Kufan count, used with Hafs).
  - Other verse-counting schools are explained: same text, different verse breaks.
  - Word and letter totals are shown under each tokenisation.
- **Real analyses:**
  - Root, lemma and word frequency; Zipf's law plot; words that occur only once (hapax).
  - The vocabulary coverage curve.
  - Repeated phrases; Names of Allah at ayah endings.
  - Verse length across revelation order; rhyme "barcodes" per surah.
  - Concept networks; Meccan vs Medinan vocabulary.
  - Ring structures (cited scholarship, not computed).
- **Popular claims** ("day" 365 times, "month" 12, man/woman, sea/land, Code 19): each is tested and labelled
  *Verified · Depends on counting rules · Not reproducible · Disputed by scholars*, with a scholar's view cited.
  Code 19 is presented only as a documented controversy, including the removal of 9:128–129 by its originator.
  Headings say "pattern" or "claim", never "miracle".
- **A short explainer** on why matching numbers can happen by chance among thousands of word pairs (the "look-elsewhere
  effect").
- **Outputs:** a public Jupyter notebook and JSON, so every number can be reproduced.

---

## 8. Audio and text to speech

- **Arabic:** human recitation only, streamed from EveryAyah. The default reciter is Alafasy. Users can choose
  others: Husary, Minshawi, Sudais and others, plus the Husary teaching recitation (Muallim).
  - Words are highlighted as they are recited, from the segment timings (once permitted).
  - Play an ayah, a passage or a surah, with repeat, speed control, and continuous play that follows the page.
- **English:** per-ayah Saheeh International audio by Ibrahim Walk, streamed from EveryAyah.
- **Bangla:** our own pre-generated narration of the Zakaria translation, clearly labelled.
  - About 200 MB, one Opus file per surah, with per-ayah offsets read from forced alignment.
  - The browser's built-in voice is used only as a labelled fallback.
- **Playback modes:** Arabic only; Arabic then English; Arabic then Bangla.

---

## 9. Repository layout

```
QuranGraph/
  ingest/        fetch/ core/ generate/ validate/ graph/ stats/ tts/ export/   (Python, uv)
    sources.yaml   every source: URL, version, SHA-256, licence, attribution text, display|grounding
    kb/            curated: people, places, stories, names of Allah, glossary, aliases (AR/EN/BN), paths
    agent/INSTRUCTIONS.md   generation + review rules (repo-relative paths only)
  web/           Astro site, src/lib/search (engine + worker), scripts/ (index + shard builders), tests/
  review/        local reviewer app: queue, side-by-side sources, approve/edit/reject, review log
  notebooks/     Numbers Lab reproducible analysis
  .github/workflows/  ci.yml (test, validate, build), deploy.yml, sources-check.yml (weekly QuranEnc version check)
  PLAN.md  README.md  LICENSES.md (code MIT · GPL data bundle · per-source attributions)
```

Generated data (`work/`, `dist/`, audio) stays out of git. It is rebuilt in CI, or stored in a private R2 bucket or
as release assets.

---

## 10. Deployment and DevOps

- **Hosting:**
  - Cloudflare Workers Static Assets, assets-only (no Worker code), so all requests are free and unlimited.
  - A custom domain is recommended.
  - R2 is used only if media grows (free egress and 10 GB free storage; never the rate-limited `r2.dev` address in
    production).
- **Private phase:**
  - Cloudflare Access with an email PIN in front of the whole site (free up to 50 users; confirm the current limit
    when setting it up).
  - Search engines blocked three ways: the `X-Robots-Tag` header, a `robots` meta tag, and `robots.txt`.
- **Going public:**
  - Each surah's pages open only when it has `review.status = approved`; the rest stay behind Access or show
    "under review".
- **CI, on every push:**
  1. Type-check and unit tests (normalisation parity, reference parser, Reciprocal Rank Fusion).
  2. `qg check` over all content.
  3. **Search golden set** (Recall@10 / MRR; fails if quality drops).
  4. Accessibility checks (axe) and Lighthouse budgets.
  5. Build.
  6. A preview version with `wrangler versions upload`.
- **On merge to `main`:** `wrangler deploy`. The data pipeline runs separately (manually or on schedule), so code
  deploys and data deploys stay independent.
- **Weekly jobs:** check QuranEnc versions (`last_update`) and open a pull request when one changes; check that all
  source URLs still resolve.
- **Caching:**
  - Hashed assets and data shards: immutable for 1 year.
  - Audio: 30 days.
  - HTML: revalidate on every request.
- **Security headers:** CSP without `unsafe-inline` (scripts bundled), plus `frame-ancestors 'none'`, nosniff, and
  Referrer- and Permissions-Policy headers.
- **Privacy:** no accounts, no cookies (beyond Access during the private phase), cookie-free analytics only
  (Cloudflare Web Analytics).

---

## 11. Quality and testing

| What | Target |
|---|---|
| Arabic text | 100% byte-identical to Tanzil (automated) |
| Translations | 100% identical to QuranEnc at the pinned version |
| Explanation faithfulness | Every claim cites a source. Reviewer sample: ≥ 95% "faithful and clear". Zero invented rulings |
| Plain language | English at reading grade ≤ 8. Short Bangla sentences. Banned-phrase list (no filler, no robotic phrasing) |
| Entity links | Hand-check 200 links: precision ≥ 95% |
| Search | Golden set of about 120 queries in English, Arabic, Bangla and transliteration, e.g. "ayatul kursi", "আয়াতুল কুরসি", "الكرسي", "patience", "ধৈর্য", "story of yusuf", "rahma root", "2:255", "who was luqman". Recall@10 ≥ 0.95 for references and names; ≥ 0.85 for concepts |
| Accessibility | axe: 0 serious issues. Lighthouse Accessibility 100, Performance ≥ 95. Tested on a real phone, iPad, VoiceOver and TalkBack |
| Usability | 5 beginners (including Bangla-first readers): task success ≥ 90% |

---

## 12. Phases (one developer with Claude Code)

| Phase | Time | Output | Gate |
|---|---|---|---|
| **0. Permissions and pilot** | 4 days | Permission emails sent (§13); fetchers with licence manifest; generation pilot on al-Fatiha, Juz 30 and al-Baqarah 1–20; normaliser; golden set v1 | Reviewer approves pilot quality; exact cost known |
| **1. Text core** | 4 days | quran.sqlite: ayat, words, lemmas, roots, metadata, translations, Mukhtasar; transliteration; validator | Byte-identical Arabic and translations |
| **2. Curated knowledge base** | 6 days | People, places, nations, stories and episodes, names of Allah, glossary, learning paths (EN/BN), Wikidata links | Curated lists reviewed |
| **3. Generation run** | 7 days (mostly unattended batch) | Explanations, examples, entities and themes for all 6,236 ayat; surah summaries; review queue | ≥ 98% pass the validator; queue triaged |
| **4. Graph and statistics** | 5 days | Typed graph, PPR, clusters, related ayat, story order, Numbers Lab notebook and data | Link precision ≥ 95%; counts reproducible |
| **5. Search** | 5 days | Sharded engine in three languages with transliteration; reference parser; golden-set tests in CI | Search targets met |
| **6. Website** | 10 days | All screens, audio, visualisations, learning tools, settings, offline install, reviewer app | Lighthouse/axe targets; works on phone and iPad |
| **7. Bangla audio, polish, private launch** | 5 days | TTS audio and alignment; usability test; fixes; Access-protected deploy | Usability ≥ 90% |
| **8. Review and staged public release** | Ongoing | Surahs published as they are approved, starting with Juz 30 and al-Fatiha | Reviewer sign-off per surah |

**About 46 working days, or 9 weeks**, to a complete private launch. A usable preview (reading, search, ayah pages
for Juz 30) is ready around week 4.

---

## 13. Permissions to request (I can draft each email)

| To | For | If refused |
|---|---|---|
| QuranEnc (notify, per their terms) | Saheeh International, Zakaria, Rowwad, Mukhtasar EN/BN republishing; Bangla TTS reading of the Zakaria translation | Terms already allow display; TTS falls back to the device voice |
| Tarteel / QUL | Word table, layout, word-by-word data, topics, similar ayat, mutashabihat, segment timings | Quranic Arabic Corpus segmentation, our own similarity, verse-level audio highlighting |
| Greentech / QuranWBW | Word-by-word Bangla and English | QAC glosses (English), reviewed AI glosses (Bangla) |
| Kais Dukes (QAC) | Clarify the "no changes" clause for derived JSON | Ship the original file plus a derived GPL bundle |
| Quran Foundation (developers@quran.com) | Alafasy word timings, word-by-word audio | Verse-level highlighting only |
| King Fahd Complex (KFGQPC) | Uthmanic Hafs font; Muyassar; Zakaria tafsir | Amiri Quran (OFL) |
| Royal Aal al-Bayt Institute (altafsir.com) | Display short Jalalayn / Wahidi excerpts | Grounding only |
| sunnah.com, HadeethEnc | Hadith data dump and display permission | Show reference, grade and link only |
| EveryAyah | Courtesy notice of streaming | Self-host one reciter on R2 |

---

## 14. Risks

| Risk | Mitigation |
|---|---|
| An AI explanation misstates the meaning | Grounded generation; a citation for every claim; a self-critique pass; mandatory review for sensitive ayat; private launch and per-surah publication; error reports and versioning |
| A source refuses permission | Every licence-unclear item has a fallback (§13); nothing unlicensed is shipped in the site files |
| Religious sensitivity (school of thought, disputed issues) | Mainstream Sunni sources; differences noted; no fiqh rulings; Numbers Lab neutral and labelled |
| Free-plan limits | Page budget at about 60% of the limit; R2 or $5 Workers Paid as fallback |
| Quality of the Bangla voice | Pilot two voices in Phase 0; device voice as fallback; never used for Arabic |
| Data drift (QuranEnc updates) | Weekly version check opens an update pull request; version shown on every translation |

---

## 15. Still open (needed before or during Phase 0)

1. **Domain name**, if any (otherwise `*.workers.dev`).
2. **Reviewer**: a qualified person to approve surahs (Arabic, ideally Bangla too) before public release.
3. **Translations**: Saheeh International and Zakaria as primary (recommended), with Rowwad and Hilali-Khan offered as
   alternates.
4. **Default reciter**: Alafasy (recommended, because word-level timings exist for this reciter only).
5. **Who sends the permission emails**: you, from your address (recommended), using drafts I prepare.
