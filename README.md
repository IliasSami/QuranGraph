# QuranGraph — The Connected Quran Knowledge System & Multilingual Ontology

[![CI](https://github.com/IliasSami/QuranGraph/actions/workflows/ci.yml/badge.svg)](https://github.com/IliasSami/QuranGraph/actions/workflows/ci.yml)
[![QuranGraph CI & Deploy](https://github.com/IliasSami/QuranGraph/actions/workflows/deploy.yml/badge.svg)](https://github.com/IliasSami/QuranGraph/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-teal.svg)](LICENSE)
[![Framework: Astro 5](https://img.shields.io/badge/Framework-Astro_5-orange.svg)](https://astro.build)
[![Deployment: Cloudflare Workers](https://img.shields.io/badge/Deploy-Cloudflare_Workers-F38020.svg)](https://workers.cloudflare.com)
[![Privacy: Zero Trackers](https://img.shields.io/badge/Privacy-100%25_Zero_Trackers-success.svg)](#privacy--zero-cost-philosophy)

> **Explore the Holy Quran through a connected, multilingual semantic knowledge graph.** Every verse, root, lemma, prophetic narrative, divine name, and moral theme is linked together with verified classical tafsir explanations in plain English and natural Bangla.

🌐 **Live Application**: [https://qurangraph.iliassami57.workers.dev](https://qurangraph.iliassami57.workers.dev) · [https://qurangraph.com](https://qurangraph.com)

---

## 🌟 Core Features

### 1. 🔍 Intelligent Multilingual Search Engine
- **Trilingual Token Normalisation**: Search in **Arabic (Uthmani & Simple Clean)**, **English**, **Bangla**, or **ALA-LC Latin Transliterations** (*"ayatul kursi"*, *"ar-rahman"*, *"ধৈর্য"*, *"লাইলাতুল কদর"*, *"الصبر"*).
- **Natural Language Reference Parsing**: Type `"baqarah 255"`, `"বাকারা ২৫৫"`, or `"البقرة ٢٥٥"` to immediately navigate to the target ayah.
- **Phonetic & Typo Resilience**: Powered by bounded Damerau-Levenshtein distance and consonant sound keys.
- **Client-Side Speed**: 100% in-browser search executing across all 6,236 ayat in `< 10ms` with zero server overhead. 54-query golden test suite verified at 100% accuracy.

### 2. 🕸️ Interactive Knowledge Graph & Context Subgraphs
- **17,714 Semantic Nodes & 150,601 Typed Edges**: Links every ayah to its triliteral roots, lemmas, recurring themes, sacred geography, historical nations, and divine names.
- **Prophetic Narrative Arcs**: Chronological timeline integration for Quranic stories (Prophet Yusuf, Musa & Pharaoh, Ashab al-Kahf, etc.) with active scene highlights.
- **Force-Directed Interactive Canvas**: Deep-linkable visual graphs with mobile touch support, physics simulation, category filters, and accessible WCAG AAA text summaries.

### 3. 📖 100% Complete Verified Ayah Explanations (6,236 / 6,236 Ayat)
- **All 114 Surahs Complete**: Every single ayah features verified teaching summaries in plain English (Flesch-Kincaid Grade $\le 8.0$) and pure চলিত Bangla.
- **Grounded in Classical Tafsir**: Strictly derived from established authorities (Tafsir Ibn Kathir, Ma'ariful Qur'an, Tafsir al-Jalalayn, Tafsir as-Sa'di, and Ahsanul Bayan). Zero rulings, zero fatwas, zero unverified stories.
- **Practical Lessons & Real-Life Examples**: Everyday applications for family, work, patience, gratitude, and moral excellence.

### 4. 📊 Quran Numbers Lab & Frequency Mastery Roadmap
- **Reproducible Corpus Statistics**: 77,429 words, 1,651 roots, 4,763 lemmas analyzed without mystical pseudoscience.
- **Linguistic Frequency Curve**: Systematic Zipfian breakdown demonstrating that mastering just **58 core lemmas** unlocks **50% recitation comprehension**, and **232 lemmas** unlocks **70%**.
- **6-Level Progressive Curriculum**: Structured from Alphabet & Tajweed Fundamentals to Deep Rhetorical & Thematic Analysis.

### 5. 📱 App-Like Responsive User Experience
- **Mobile First Design**: Sticky bottom navigation dock, fluid touch targets, and 0 horizontal scroll across all device viewports (320px to 4K).
- **Accessibility & Adab**: Dynamic Arabic font scaler (`A-` / `A+`), light/dark high-contrast themes, screen reader navigation, and full keyboard shortcuts.
- **Human Recitation Audio**: Crystal clear Arabic audio recitation by Sheikh Mishary Rashid Alafasy.

---

## 🏛️ Architecture & Project Structure

QuranGraph is designed with a **heavy offline data pipeline** paired with a **lightweight, 100% static frontend** with zero database dependencies at runtime.

```
QuranGraph/
├── web/                             # Astro 5 Static Application
│   ├── src/
│   │   ├── pages/                   # Static routes (8,899 generated HTML pages + sitemap.xml)
│   │   │   ├── surah/[id].astro     # 114 Surah overview pages
│   │   │   ├── ayah/[surah]/[ayah].astro # 6,236 Ayah detail & study pages
│   │   │   ├── entity/[slug].astro  # 884 Curated entity pages
│   │   │   ├── root/[slug].astro    # 1,651 Linguistic root pages
│   │   │   ├── story/[slug].astro   # Prophetic storyline arc pages
│   │   │   ├── search.astro         # Multilingual live search portal
│   │   │   ├── graph.astro          # Macro Knowledge Graph explorer
│   │   │   ├── learn.astro          # Systematic learning roadmap
│   │   │   └── numbers.astro        # Numbers Lab & linguistic frequency
│   │   ├── components/              # AppTopControls, BottomNav, AyahContextGraph, AudioPlayer
│   │   ├── lib/search/              # In-browser BM25/prefix search engine & normalizer
│   │   └── data/graph/              # Static Graph JSON shards (entities, roots, themes, similar ayat)
│   ├── tests/                       # Unit tests and 54-query golden search benchmark suite
│   └── public/                      # Static assets, audio manifests, robots.txt, og-image
│
├── ingest/                          # Offline Python 3.12 Data Pipeline
│   ├── core/                        # Tanzil Uthmani text parser, Latin transliteration engine
│   ├── kb/                          # Curated knowledge base (prophets, places, divine names)
│   ├── content/explain/             # 6,236 verified ayah explanation JSON files
│   ├── graph/                       # Graph builder (SQLite, PageRank, lemma similarity, clusters)
│   └── stats/                       # Numbers Lab statistical calculations
│
├── .github/workflows/               # GitHub Actions CI & Cloudflare deployment
├── wrangler.toml                    # Cloudflare Workers configuration
└── LICENSE                          # MIT Open Source License
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js**: v20 or v22+
- **Python**: 3.12+ with [uv](https://docs.astral.sh/uv/)

### 1. Web Application (Astro 5)

```bash
# Clone the repository
git clone https://github.com/IliasSami/QuranGraph.git
cd QuranGraph/web

# Install dependencies
npm ci

# Start local development server
npm run dev
# -> Opens on http://localhost:4321

# Run the test suite (73 unit tests + 54 golden search benchmarks)
node --test "tests/*.test.ts"

# Build static production bundle
npm run build
```

### 2. Ingest Data Pipeline (Python)

```bash
cd QuranGraph/ingest

# Sync virtual environment with uv
uv sync

# Run pipeline text database build
uv run core/build_text.py

# Run Numbers Lab statistics generator
uv run stats/numbers_lab.py

# Build Knowledge Graph (SQLite + JSON shards)
uv run graph/build_kg.py

# Validate all 6,236 explanations
./qg check all
```

---

## 🔒 Privacy & Zero-Cost Philosophy

1. **100% Free & Open Source**: Licensed under the MIT License.
2. **Zero Advertisements & Zero Tracking**: No tracking cookies, no Google Analytics, no third-party telemetry, no monetisation.
3. **Infinite Global Scalability**: Hosted as 100% static assets on Cloudflare's global edge network ($0/month operating cost).

---

## 📚 Scholarly Sources & Attributions

QuranGraph maintains strict textual and scholarly fidelity to authoritative classical sources:

| Resource | Source / Provider | License / Policy | Use in QuranGraph |
|---|---|---|---|
| **Quranic Arabic Text** | [Tanzil Project](https://tanzil.net) | Tanzil Terms (CC BY 3.0) | Displayed verbatim (Uthmani & simple clean) |
| **English Translation** | Saheeh International ([QuranEnc](https://quranenc.com)) | Public attribution | Verbatim translation text |
| **Bengali Translation** | Dr. Abu Bakr Muhammad Zakaria ([QuranEnc](https://quranenc.com)) | Public attribution | Verbatim translation text |
| **Classical Brief Tafsir** | Al-Mukhtasar fi Tafsir al-Qur'an ([QuranEnc](https://quranenc.com)) | Public attribution | Verbatim classical summary |
| **Corpus & Morphology** | [Quranic Arabic Corpus](https://corpus.quran.com) (Univ. of Leeds) / [mustafa0x](https://github.com/mustafa0x/quran-morphology) | GNU GPL | Root, lemma, and part-of-speech indexes |
| **Scholarly Grounding** | Tafsir Ibn Kathir, Ma'ariful Qur'an, Jalalayn, As-Sa'di | Grounding only | Cited sources for ayah explanations |
| **Audio Recitation** | Sheikh Mishary Rashid Alafasy ([EveryAyah](https://everyayah.com)) | Free Islamic distribution | High-quality human recitation |

---

## 🤝 Contributing

We welcome community contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for architectural guidelines, reverence standards, and the pull request process.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
The sacred Quranic Arabic text is reproduced from the Tanzil Project under its established terms of use.
