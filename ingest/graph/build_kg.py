"""Knowledge Graph Builder for QuranGraph.
Constructs semantic nodes and typed edges across text, language, curated entities,
narratives, themes, and learning paths.
Computes PageRank, Personalized PageRank (PPR), concept co-occurrence (NPMI),
thematic clustering, and lemma-based ayah similarity.
Outputs to:
  - SQLite: ingest/work/graph.sqlite
  - Sharded JSON: ingest/work/export/graph/
"""
import glob
import json
import math
import os
import sqlite3
from collections import Counter, defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "work", "quran.sqlite")
KB_DIR = os.path.join(BASE_DIR, "kb")
EXPLAIN_DIR = os.path.join(BASE_DIR, "content", "explain")
GRAPH_DB_PATH = os.path.join(BASE_DIR, "work", "graph.sqlite")
EXPORT_DIR = os.path.join(BASE_DIR, "work", "export", "graph")


def load_json(path):
    with open(path) as f:
        return json.load(f)


def parse_ayah_spec(spec):
    """Parses specs like '12:4-6' or '2:255' into a list of (surah, ayah) tuples."""
    results = []
    parts = spec.strip().split(":")
    if len(parts) != 2:
        return results
    surah = int(parts[0])
    ayah_range = parts[1]
    if "-" in ayah_range:
        start_a, end_a = map(int, ayah_range.split("-"))
        for a in range(start_a, end_a + 1):
            results.append((surah, a))
    else:
        results.append((surah, int(ayah_range)))
    return results


class KnowledgeGraphBuilder:
    def __init__(self, quran_db_path=DB_PATH):
        self.quran_db = sqlite3.connect(quran_db_path)
        self.nodes = {}  # node_id -> dict
        self.edges = []  # list of dicts
        self.adj = defaultdict(list)  # source_id -> list of target_id
        self.undirected_adj = defaultdict(set)  # u -> set(v)

    def add_node(self, node_id, node_type, label_en, label_ar="", label_bn="", properties=None):
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "type": node_type,
                "label_en": label_en or "",
                "label_ar": label_ar or "",
                "label_bn": label_bn or "",
                "properties": properties or {}
            }

    def add_edge(self, source_id, target_id, rel_type, origin="text", weight=1.0, confidence=1.0):
        self.edges.append({
            "source_id": source_id,
            "target_id": target_id,
            "rel_type": rel_type,
            "origin": origin,
            "weight": float(weight),
            "confidence": float(confidence)
        })
        self.adj[source_id].append(target_id)
        self.undirected_adj[source_id].add(target_id)
        self.undirected_adj[target_id].add(source_id)

    def build_text_and_morphology(self):
        print("Indexing Surahs, Ayat, Roots, and Lemmas...")
        c = self.quran_db.cursor()

        # Surahs
        c.execute("SELECT id, name_ar, name_translit, name_en, name_bn, type, revelation_order, ayat, rukus FROM surah")
        for s_id, n_ar, n_tr, n_en, n_bn, s_type, rev_order, num_ayat, rukus in c.fetchall():
            self.add_node(
                node_id=f"surah:{s_id}",
                node_type="surah",
                label_en=n_en,
                label_ar=n_ar,
                label_bn=n_bn,
                properties={
                    "surah": s_id,
                    "name_translit": n_tr,
                    "type": s_type,
                    "revelation_order": rev_order,
                    "ayat_count": num_ayat,
                    "rukus": rukus
                }
            )

        # Ayat
        c.execute("SELECT id, surah, ayah, text_uthmani, text_simple, juz, page, ruku FROM ayah")
        for a_id, s_id, a_num, uthmani, simple, juz, page, ruku in c.fetchall():
            ayah_node_id = f"ayah:{s_id}:{a_num}"
            self.add_node(
                node_id=ayah_node_id,
                node_type="ayah",
                label_en=f"{s_id}:{a_num}",
                label_ar=simple[:40] + ("..." if len(simple) > 40 else ""),
                label_bn=f"{s_id}:{a_num}",
                properties={
                    "id": a_id,
                    "surah": s_id,
                    "ayah": a_num,
                    "juz": juz,
                    "page": page,
                    "ruku": ruku,
                    "text_uthmani": uthmani,
                    "text_simple": simple
                }
            )
            # Edge: Ayah -> Surah
            self.add_edge(ayah_node_id, f"surah:{s_id}", "in_surah", origin="text")

        # Roots and Lemmas
        c.execute("SELECT DISTINCT root FROM word WHERE root IS NOT NULL")
        for (root,) in c.fetchall():
            self.add_node(
                node_id=f"root:{root}",
                node_type="root",
                label_en=root,
                label_ar=root,
                label_bn=root
            )

        c.execute("SELECT DISTINCT lemma, root FROM word WHERE lemma IS NOT NULL")
        for lemma, root in c.fetchall():
            lemma_node_id = f"lemma:{lemma}"
            self.add_node(
                node_id=lemma_node_id,
                node_type="lemma",
                label_en=lemma,
                label_ar=lemma,
                label_bn=lemma,
                properties={"root": root}
            )
            if root:
                self.add_edge(f"root:{root}", lemma_node_id, "root_has_lemma", origin="morphology")

        # Ayah -> Root & Ayah -> Lemma occurrences
        c.execute("SELECT DISTINCT surah, ayah, root, lemma FROM word WHERE root IS NOT NULL")
        for s_id, a_num, root, lemma in c.fetchall():
            ayah_node_id = f"ayah:{s_id}:{a_num}"
            if root:
                self.add_edge(ayah_node_id, f"root:{root}", "has_root", origin="morphology")
            if lemma:
                self.add_edge(ayah_node_id, f"lemma:{lemma}", "has_lemma", origin="morphology")

    def build_kb_entities(self):
        print("Indexing Curated Knowledge Base entities...")
        # People
        people_file = os.path.join(KB_DIR, "people.json")
        if os.path.exists(people_file):
            for p in load_json(people_file):
                self.add_node(
                    node_id=f"person:{p['id']}",
                    node_type="person",
                    label_en=p["name_en"],
                    label_ar=p["name_ar"],
                    label_bn=p["name_bn"],
                    properties={"role": p.get("role"), "wikidata": p.get("wikidata"), "aliases": p.get("aliases", [])}
                )

        # Places
        places_file = os.path.join(KB_DIR, "places.json")
        if os.path.exists(places_file):
            for pl in load_json(places_file):
                self.add_node(
                    node_id=f"place:{pl['id']}",
                    node_type="place",
                    label_en=pl["name_en"],
                    label_ar=pl["name_ar"],
                    label_bn=pl["name_bn"],
                    properties={"wikidata": pl.get("wikidata"), "lat": pl.get("lat"), "lon": pl.get("lon"), "aliases": pl.get("aliases", [])}
                )

        # Nations
        nations_file = os.path.join(KB_DIR, "nations.json")
        if os.path.exists(nations_file):
            for n in load_json(nations_file):
                self.add_node(
                    node_id=f"nation:{n['id']}",
                    node_type="nation",
                    label_en=n["name_en"],
                    label_ar=n["name_ar"],
                    label_bn=n["name_bn"],
                    properties={"wikidata": n.get("wikidata"), "aliases": n.get("aliases", [])}
                )

        # Unseen
        unseen_file = os.path.join(KB_DIR, "unseen.json")
        if os.path.exists(unseen_file):
            for u in load_json(unseen_file):
                self.add_node(
                    node_id=f"unseen:{u['id']}",
                    node_type="unseen",
                    label_en=u["name_en"],
                    label_ar=u["name_ar"],
                    label_bn=u["name_bn"],
                    properties={"type": u.get("type"), "wikidata": u.get("wikidata"), "aliases": u.get("aliases", [])}
                )

        # Names of Allah
        names_file = os.path.join(KB_DIR, "names_of_allah.json")
        if os.path.exists(names_file):
            for noa in load_json(names_file):
                self.add_node(
                    node_id=f"name_of_allah:{noa['id']}",
                    node_type="name_of_allah",
                    label_en=noa["name_en"],
                    label_ar=noa["name_ar"],
                    label_bn=noa["name_bn"],
                    properties={"meaning_en": noa.get("meaning_en"), "meaning_bn": noa.get("meaning_bn")}
                )

        # Glossary
        glossary_file = os.path.join(KB_DIR, "glossary.json")
        if os.path.exists(glossary_file):
            for g in load_json(glossary_file):
                self.add_node(
                    node_id=f"glossary:{g['id']}",
                    node_type="glossary",
                    label_en=g["term_en"],
                    label_ar=g["term_ar"],
                    label_bn=g["term_bn"],
                    properties={"def_en": g.get("def_en"), "def_bn": g.get("def_bn")}
                )

        # Stories and Episodes
        stories_file = os.path.join(KB_DIR, "stories.json")
        if os.path.exists(stories_file):
            for s in load_json(stories_file):
                story_node_id = f"story:{s['id']}"
                self.add_node(
                    node_id=story_node_id,
                    node_type="story",
                    label_en=s["title_en"],
                    label_ar="",
                    label_bn=s["title_bn"],
                    properties={"surah_refs": s.get("surah_refs", [])}
                )
                for ep in s.get("episodes", []):
                    ep_node_id = f"episode:{ep['id']}"
                    self.add_node(
                        node_id=ep_node_id,
                        node_type="episode",
                        label_en=ep["title_en"],
                        label_ar="",
                        label_bn=ep["title_bn"],
                        properties={"story_id": s["id"], "ayat": ep.get("ayat")}
                    )
                    self.add_edge(ep_node_id, story_node_id, "in_story", origin="kb")
                    for s_num, a_num in parse_ayah_spec(ep.get("ayat", "")):
                        self.add_edge(f"ayah:{s_num}:{a_num}", ep_node_id, "in_episode", origin="kb")

        # Learning Paths
        paths_file = os.path.join(KB_DIR, "learning_paths.json")
        if os.path.exists(paths_file):
            for lp in load_json(paths_file):
                path_node_id = f"learning_path:{lp['id']}"
                self.add_node(
                    node_id=path_node_id,
                    node_type="learning_path",
                    label_en=lp["title_en"],
                    label_ar="",
                    label_bn=lp["title_bn"],
                    properties={"description_en": lp.get("description_en"), "steps": lp.get("steps", [])}
                )
                for step_spec in lp.get("steps", []):
                    for s_num, a_num in parse_ayah_spec(step_spec):
                        self.add_edge(f"ayah:{s_num}:{a_num}", path_node_id, "in_path", origin="kb")

    def build_explanation_links(self):
        print("Indexing pilot explanations and connecting themes/entities...")
        alias_map = {}
        # Build lookup from alias / name -> entity node_id
        for n_id, n in self.nodes.items():
            if n["type"] in ("person", "place", "nation", "unseen", "name_of_allah", "glossary"):
                alias_map[(n["type"], n["label_en"].lower())] = n_id
                alias_map[(n["type"], n["label_ar"].lower())] = n_id
                aliases = n.get("properties", {}).get("aliases", [])
                for al in aliases:
                    alias_map[(n["type"], al.lower())] = n_id

        # Also generic lookup across types
        generic_alias_map = {}
        for (ntype, name_low), n_id in alias_map.items():
            generic_alias_map[name_low] = n_id

        files = sorted(glob.glob(os.path.join(EXPLAIN_DIR, "*", "*.json")))
        ayah_themes = defaultdict(list)

        for path in files:
            d = load_json(path)
            aid = d.get("id")  # e.g. "1:2"
            if not aid or ":" not in aid:
                continue
            s_num, a_num = aid.split(":")
            ayah_node_id = f"ayah:{s_num}:{a_num}"
            conf = d.get("confidence", 0.9)

            # Themes
            for theme in d.get("themes", []):
                t_clean = theme.strip()
                if not t_clean:
                    continue
                theme_slug = t_clean.lower().replace(" ", "-")
                theme_node_id = f"theme:{theme_slug}"
                self.add_node(
                    node_id=theme_node_id,
                    node_type="theme",
                    label_en=t_clean.capitalize(),
                    label_ar="",
                    label_bn=""
                )
                self.add_edge(ayah_node_id, theme_node_id, "teaches_theme", origin="ai_checked", confidence=conf)
                ayah_themes[ayah_node_id].append(theme_node_id)

            # Entities
            ents = d.get("entities", {})
            cat_rel_map = {
                "people": ("person", "mentions_person"),
                "places": ("place", "mentions_place"),
                "nations": ("nation", "mentions_nation"),
                "unseen": ("unseen", "mentions_unseen"),
                "names_of_allah": ("name_of_allah", "names_allah"),
            }

            for cat, items in ents.items():
                if cat in cat_rel_map:
                    target_type, rel_name = cat_rel_map[cat]
                    for item in items:
                        item_low = item.strip().lower()
                        target_node = alias_map.get((target_type, item_low)) or generic_alias_map.get(item_low)
                        if target_node:
                            self.add_edge(ayah_node_id, target_node, rel_name, origin="ai_checked", confidence=conf)
                        else:
                            # Dynamic entity node
                            slug = item_low.replace(" ", "-")
                            dyn_id = f"{target_type}:{slug}"
                            self.add_node(dyn_id, target_type, label_en=item)
                            self.add_edge(ayah_node_id, dyn_id, rel_name, origin="ai_checked", confidence=conf)

        # Concept Co-occurrence (NPMI)
        print("Computing Theme co-occurrence and NPMI...")
        co_counts = Counter()
        theme_counts = Counter()
        total_explained_ayat = len(ayah_themes)

        for a_id, t_list in ayah_themes.items():
            unique_t = sorted(set(t_list))
            for t in unique_t:
                theme_counts[t] += 1
            for i in range(len(unique_t)):
                for j in range(i + 1, len(unique_t)):
                    co_counts[(unique_t[i], unique_t[j])] += 1

        for (t1, t2), count in co_counts.items():
            if count >= 2:  # appear together at least twice
                p_t1 = theme_counts[t1] / total_explained_ayat
                p_t2 = theme_counts[t2] / total_explained_ayat
                p_12 = count / total_explained_ayat
                pmi = math.log2(p_12 / (p_t1 * p_t2))
                npmi = pmi / (-math.log2(p_12)) if p_12 < 1.0 else 1.0
                if npmi > 0.15:
                    self.add_edge(t1, t2, "co_occurs_with", origin="computed", weight=round(npmi, 3), confidence=0.85)

    def compute_pagerank(self, damping=0.85, max_iter=25):
        print(f"Computing PageRank across {len(self.nodes)} nodes...")
        n = len(self.nodes)
        if n == 0:
            return {}

        node_keys = list(self.nodes.keys())
        node_idx = {k: i for i, k in enumerate(node_keys)}
        scores = [1.0 / n] * n

        adj_idx = defaultdict(list)
        for u_id, neighbors in self.adj.items():
            if u_id in node_idx:
                u_i = node_idx[u_id]
                for v_id in neighbors:
                    if v_id in node_idx:
                        adj_idx[u_i].append(node_idx[v_id])

        dangling_nodes = [i for i in range(n) if len(adj_idx[i]) == 0]
        active_nodes = [i for i in range(n) if len(adj_idx[i]) > 0]

        for _ in range(max_iter):
            new_scores = [0.0] * n
            for u_i in active_nodes:
                share = scores[u_i] / len(adj_idx[u_i])
                for v_i in adj_idx[u_i]:
                    new_scores[v_i] += share

            dangling_sum = sum(scores[d_i] for d_i in dangling_nodes)
            teleport = ((1.0 - damping) + damping * dangling_sum) / n
            scores = [teleport + damping * new_scores[i] for i in range(n)]

        return {node_keys[i]: scores[i] for i in range(n)}

    def compute_similar_ayat(self, top_k=3):
        print("Computing lemma-based Ayah similarity...")
        c = self.quran_db.cursor()

        # Build in-memory index in one pass: lemma -> set of (surah, ayah)
        c.execute("SELECT surah, ayah, lemma FROM word WHERE lemma IS NOT NULL")
        ayah_lemmas = defaultdict(set)
        lemma_to_ayat = defaultdict(set)

        for s_id, a_num, lemma in c.fetchall():
            aid = f"{s_id}:{a_num}"
            ayah_lemmas[aid].add(lemma)
            lemma_to_ayat[lemma].add(aid)

        total_ayat = len(ayah_lemmas)
        lemma_idf = {l: math.log(total_ayat / (len(ayats) + 1)) for l, ayats in lemma_to_ayat.items()}

        explain_files = glob.glob(os.path.join(EXPLAIN_DIR, "*", "*.json"))
        target_ayat = []
        for path in explain_files:
            d = load_json(path)
            if d.get("id"):
                target_ayat.append(d["id"])

        similar_map = {}
        for aid in target_ayat:
            t_lemmas = ayah_lemmas.get(aid, set())
            if len(t_lemmas) < 2:
                continue

            candidates = Counter()
            for l in t_lemmas:
                matching_ayats = lemma_to_ayat.get(l, set())
                if len(matching_ayats) < 800:
                    weight = lemma_idf.get(l, 1.0)
                    for cand_id in matching_ayats:
                        if cand_id != aid:
                            candidates[cand_id] += weight

            top_matches = []
            for cand_id, score in candidates.most_common(top_k):
                cand_lemmas = ayah_lemmas.get(cand_id, set())
                intersection = t_lemmas.intersection(cand_lemmas)
                union = t_lemmas.union(cand_lemmas)
                jaccard = len(intersection) / len(union) if union else 0.0
                if jaccard >= 0.15:
                    top_matches.append({
                        "ayah": cand_id,
                        "score": round(jaccard, 3),
                        "shared_lemmas": list(intersection)[:4]
                    })
                    self.add_edge(f"ayah:{aid}", f"ayah:{cand_id}", "similar_ayah", origin="computed", weight=round(jaccard, 3))

            if top_matches:
                similar_map[aid] = top_matches

        return similar_map

    def compute_theme_clusters(self):
        print("Clustering Themes into thematic communities...")
        # Greedy community detection on theme-theme co-occurrence graph
        theme_nodes = [nid for nid, n in self.nodes.items() if n["type"] == "theme"]
        theme_set = set(theme_nodes)

        # Build theme adjacency
        theme_adj = defaultdict(set)
        for e in self.edges:
            if e["rel_type"] == "co_occurs_with" and e["source_id"] in theme_set and e["target_id"] in theme_set:
                theme_adj[e["source_id"]].add(e["target_id"])
                theme_adj[e["target_id"]].add(e["source_id"])

        visited = set()
        clusters = []
        cluster_id_map = {}

        for t in theme_nodes:
            if t not in visited:
                # BFS to find connected component
                comp = []
                queue = [t]
                visited.add(t)
                while queue:
                    curr = queue.pop(0)
                    comp.append(curr)
                    for nbr in theme_adj[curr]:
                        if nbr not in visited:
                            visited.add(nbr)
                            queue.append(nbr)
                if len(comp) > 1:
                    c_id = len(clusters)
                    clusters.append({
                        "cluster_id": c_id,
                        "themes": [self.nodes[tid]["label_en"] for tid in comp],
                        "size": len(comp)
                    })
                    for tid in comp:
                        cluster_id_map[tid] = c_id
                else:
                    cluster_id_map[t] = -1

        return clusters, cluster_id_map

    def save_sqlite(self, pagerank_scores, cluster_id_map, similar_map):
        print(f"Writing graph to SQLite: {GRAPH_DB_PATH}...")
        if os.path.exists(GRAPH_DB_PATH):
            os.remove(GRAPH_DB_PATH)

        db = sqlite3.connect(GRAPH_DB_PATH)
        c = db.cursor()

        c.execute("""
            CREATE TABLE node (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                label_en TEXT,
                label_ar TEXT,
                label_bn TEXT,
                properties TEXT
            )
        """)

        c.execute("""
            CREATE TABLE edge (
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                rel_type TEXT NOT NULL,
                origin TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                confidence REAL DEFAULT 1.0
            )
        """)

        c.execute("""
            CREATE TABLE node_metric (
                node_id TEXT PRIMARY KEY,
                in_degree INTEGER,
                out_degree INTEGER,
                total_degree INTEGER,
                pagerank REAL,
                cluster_id INTEGER
            )
        """)

        c.execute("""
            CREATE TABLE similar_ayah (
                ayah TEXT NOT NULL,
                similar_ayah TEXT NOT NULL,
                score REAL NOT NULL,
                shared_lemmas TEXT
            )
        """)

        # Insert nodes
        node_rows = [
            (
                n["id"],
                n["type"],
                n["label_en"],
                n["label_ar"],
                n["label_bn"],
                json.dumps(n["properties"], ensure_ascii=False)
            )
            for n in self.nodes.values()
        ]
        c.executemany("INSERT INTO node VALUES (?, ?, ?, ?, ?, ?)", node_rows)

        # Insert edges
        edge_rows = [
            (
                e["source_id"],
                e["target_id"],
                e["rel_type"],
                e["origin"],
                e["weight"],
                e["confidence"]
            )
            for e in self.edges
        ]
        c.executemany("INSERT INTO edge VALUES (?, ?, ?, ?, ?, ?)", edge_rows)

        # In & Out degree counters
        in_degrees = Counter(e["target_id"] for e in self.edges)
        out_degrees = Counter(e["source_id"] for e in self.edges)

        metric_rows = [
            (
                nid,
                in_degrees[nid],
                out_degrees[nid],
                in_degrees[nid] + out_degrees[nid],
                pagerank_scores.get(nid, 0.0),
                cluster_id_map.get(nid, -1)
            )
            for nid in self.nodes.keys()
        ]
        c.executemany("INSERT INTO node_metric VALUES (?, ?, ?, ?, ?, ?)", metric_rows)

        # Similar ayat
        sim_rows = []
        for aid, matches in similar_map.items():
            for m in matches:
                sim_rows.append((aid, m["ayah"], m["score"], json.dumps(m["shared_lemmas"], ensure_ascii=False)))
        c.executemany("INSERT INTO similar_ayah VALUES (?, ?, ?, ?)", sim_rows)

        # Create indexes
        c.execute("CREATE INDEX idx_node_type ON node (type)")
        c.execute("CREATE INDEX idx_edge_source ON edge (source_id)")
        c.execute("CREATE INDEX idx_edge_target ON edge (target_id)")
        c.execute("CREATE INDEX idx_edge_rel ON edge (rel_type)")
        c.execute("CREATE INDEX idx_similar_ayah ON similar_ayah (ayah)")

        db.commit()
        db.close()
        print(f"Saved {len(self.nodes)} nodes and {len(self.edges)} edges to graph.sqlite.")

    def export_json(self, pagerank_scores, clusters, similar_map):
        print(f"Exporting static JSON shards to {EXPORT_DIR}...")
        os.makedirs(EXPORT_DIR, exist_ok=True)

        # Top 30 nodes by PageRank
        top_pr = sorted(
            [(nid, score) for nid, score in pagerank_scores.items()],
            key=lambda x: x[1],
            reverse=True
        )[:30]

        summary = {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "node_types": dict(Counter(n["type"] for n in self.nodes.values())),
            "edge_types": dict(Counter(e["rel_type"] for e in self.edges)),
            "top_nodes_pagerank": [
                {
                    "id": nid,
                    "type": self.nodes[nid]["type"],
                    "label_en": self.nodes[nid]["label_en"],
                    "label_ar": self.nodes[nid]["label_ar"],
                    "pagerank": round(score, 6)
                }
                for nid, score in top_pr
            ],
            "theme_clusters_count": len(clusters)
        }
        with open(os.path.join(EXPORT_DIR, "summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        # Entities export
        entities_export = {}
        for nid, n in self.nodes.items():
            if n["type"] in ("person", "place", "nation", "unseen", "name_of_allah", "glossary"):
                # Connected ayat
                connected_ayat = [
                    e["source_id"].replace("ayah:", "")
                    for e in self.edges
                    if e["target_id"] == nid and e["source_id"].startswith("ayah:")
                ]
                entities_export[nid] = {
                    "id": n["id"],
                    "type": n["type"],
                    "label_en": n["label_en"],
                    "label_ar": n["label_ar"],
                    "label_bn": n["label_bn"],
                    "properties": n["properties"],
                    "pagerank": round(pagerank_scores.get(nid, 0.0), 6),
                    "connected_ayat_count": len(connected_ayat),
                    "ayat": connected_ayat[:50]  # sample up to 50
                }
        with open(os.path.join(EXPORT_DIR, "entities.json"), "w", encoding="utf-8") as f:
            json.dump(entities_export, f, ensure_ascii=False, indent=2)

        # Roots export
        roots_export = {}
        for nid, n in self.nodes.items():
            if n["type"] == "root":
                root_str = n["id"].replace("root:", "")
                lemmas = sorted(list(set(
                    e["target_id"].replace("lemma:", "")
                    for e in self.edges
                    if e["source_id"] == nid and e["rel_type"] == "root_has_lemma"
                )))
                ayat = sorted(list(set(
                    e["source_id"].replace("ayah:", "")
                    for e in self.edges
                    if e["target_id"] == nid and e["rel_type"] == "has_root"
                )), key=lambda x: [int(p) for p in x.split(":")])
                roots_export[root_str] = {
                    "root": root_str,
                    "pagerank": round(pagerank_scores.get(nid, 0.0), 6),
                    "occurrences": len(ayat),
                    "lemmas": lemmas,
                    "ayat": ayat[:50],
                    "total_ayat": len(ayat)
                }
        with open(os.path.join(EXPORT_DIR, "roots.json"), "w", encoding="utf-8") as f:
            json.dump(roots_export, f, ensure_ascii=False, indent=2)

        # Stories export
        stories_file = os.path.join(KB_DIR, "stories.json")
        if os.path.exists(stories_file):
            stories_raw = load_json(stories_file)
            with open(os.path.join(EXPORT_DIR, "stories.json"), "w", encoding="utf-8") as f:
                json.dump(stories_raw, f, ensure_ascii=False, indent=2)

        # Themes export
        themes_export = {}
        for nid, n in self.nodes.items():
            if n["type"] == "theme":
                connected_ayat = [
                    e["source_id"].replace("ayah:", "")
                    for e in self.edges
                    if e["target_id"] == nid and e["source_id"].startswith("ayah:")
                ]
                themes_export[nid] = {
                    "id": n["id"],
                    "label_en": n["label_en"],
                    "pagerank": round(pagerank_scores.get(nid, 0.0), 6),
                    "ayat_count": len(connected_ayat),
                    "ayat": connected_ayat[:20]
                }
        with open(os.path.join(EXPORT_DIR, "themes.json"), "w", encoding="utf-8") as f:
            json.dump(themes_export, f, ensure_ascii=False, indent=2)

        # Similar Ayat export
        with open(os.path.join(EXPORT_DIR, "similar_ayat.json"), "w", encoding="utf-8") as f:
            json.dump(similar_map, f, ensure_ascii=False, indent=2)

        # Clusters export
        with open(os.path.join(EXPORT_DIR, "clusters.json"), "w", encoding="utf-8") as f:
            json.dump(clusters, f, ensure_ascii=False, indent=2)

        print("JSON graph shards exported successfully.")


def main():
    builder = KnowledgeGraphBuilder()
    builder.build_text_and_morphology()
    builder.build_kb_entities()
    builder.build_explanation_links()

    pagerank_scores = builder.compute_pagerank()
    similar_map = builder.compute_similar_ayat()
    clusters, cluster_id_map = builder.compute_theme_clusters()

    builder.save_sqlite(pagerank_scores, cluster_id_map, similar_map)
    builder.export_json(pagerank_scores, clusters, similar_map)


if __name__ == "__main__":
    main()
