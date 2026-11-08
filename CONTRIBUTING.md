# Contributing to QuranGraph

Alhamdulillah, we welcome contributions from developers, designers, linguists, and researchers worldwide. QuranGraph is a **100% free, open-source, non-profit knowledge platform** dedicated to making the Holy Quran accessible, interconnected, and clear for learners across the globe.

---

## 1. Non-Negotiable Core Principles

When contributing code, data, or documentation, the following strict principles apply at all times:

1. **Absolute Textual Reverence & Integrity**:
   - The Arabic text is sourced exclusively from the **Tanzil Project** and must **never** be edited, re-typed, or altered. Displayed Arabic text is always reproduced verbatim.
   - Translations from **QuranEnc** (Saheeh International, Dr. Abu Bakr Zakaria, Al-Mukhtasar, Al-Muyassar) are preserved exactly as provided by their publishers.

2. **Rigorous Scholarly Grounding**:
   - No rulings, personal fatwas, or theological speculation.
   - All explanations must strictly cite established classical sources (such as Tafsir Ibn Kathir, Ma'ariful Qur'an, Tafsir al-Jalalayn, and Tafsir as-Sa'di).
   - Zero invented hadith, historical accounts, or unverified claims.

3. **Neutral, Open & Accessible**:
   - QuranGraph operates under mainstream Islamic scholarship. Differences of opinion among classical scholars are objectively documented, never arbitrarily resolved.
   - 100% static architecture, $0 runtime cost, no user tracking, no cookies, no advertisements.

---

## 2. Project Architecture

The repository is organized into two primary layers:

```
├── web/                   # Astro 5 Static Website & In-Browser Multilingual Search
│   ├── src/pages/         # Static routes (surah, ayah, entity, root, story, search, graph, learn)
│   ├── src/components/    # UI components (AudioPlayer, AyahContextGraph, NetworkGraph, BottomNav)
│   ├── src/lib/search/    # High-performance in-browser search engine & token normaliser
│   ├── src/data/graph/    # Static Knowledge Graph JSON shards (entities, roots, stories, themes)
│   └── tests/             # Automated unit tests and 54-query Golden Search benchmark suite
│
├── ingest/                # Offline Python Pipeline (Text, Knowledge Graph, Morphology & Stats)
│   ├── core/              # Tanzil parser, normalization bridge, rule-based transliteration
│   ├── kb/                # Curated knowledge base (prophets, places, nations, divine names)
│   ├── content/explain/   # 6,236 verified ayah explanations in English and Bangla
│   ├── graph/             # Graph builder (SQLite, PageRank, semantic edges, similarity)
│   └── stats/             # Quran Numbers Lab statistical calculations & lemma metrics
│
├── .github/workflows/     # Automated CI verification and Cloudflare deployment
├── wrangler.toml          # Cloudflare Workers Static Assets configuration
└── README.md              # Project overview, architecture tour, and live links
```

---

## 3. Local Development Setup

### Prerequisites
- **Node.js**: v20 or v22+
- **Python**: 3.12+
- **uv**: Fast Python package manager ([docs.astral.sh/uv](https://docs.astral.sh/uv/))

### Web Application (Astro 5)

```bash
# Clone the repository
git clone https://github.com/IliasSami/QuranGraph.git
cd QuranGraph/web

# Install dependencies
npm ci

# Run development server
npm run dev

# Run all unit tests & 54 golden search benchmarks
node --test "tests/*.test.ts"

# Build static production bundle (generates 8,899 pages + sitemap.xml)
npm run build
```

### Ingest & Data Pipeline (Python)

```bash
cd ingest

# Sync Python virtual environment
uv sync

# Run Python unit tests
uv run python3 -m unittest discover -s . -p "test_*.py"

# Verify all 6,236 explanations
./qg check all
```

---

## 4. Submitting Pull Requests

1. **Create a descriptive feature branch**:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. **Ensure all tests pass**:
   ```bash
   node --test "web/tests/*.test.ts"
   cd web && npm run build
   ```
3. **Commit with Conventional Commits** (`feat:`, `fix:`, `docs:`, `perf:`).
4. **Submit a Pull Request** with a concise summary of the changes and screenshots for UI updates.

---

## 5. Code of Conduct

We expect all contributors to maintain respectful, gracious, and courteous communication (adab) reflecting the sacred reverence of the Quran. Harassment, condescension, or sectarian polemics will not be tolerated.
