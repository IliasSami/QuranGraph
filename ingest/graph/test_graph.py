def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)
"""Unit tests for Knowledge Graph builder and exported shards."""
import json
import os
import sqlite3
import unittest
from graph.build_kg import KnowledgeGraphBuilder, GRAPH_DB_PATH, EXPORT_DIR


class TestKnowledgeGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        builder = KnowledgeGraphBuilder()
        builder.build_text_and_morphology()
        builder.build_kb_entities()
        builder.build_explanation_links()
        cls.pagerank_scores = builder.compute_pagerank()
        cls.similar_map = builder.compute_similar_ayat()
        cls.clusters, cls.cluster_id_map = builder.compute_theme_clusters()
        builder.save_sqlite(cls.pagerank_scores, cls.cluster_id_map, cls.similar_map)
        builder.export_json(cls.pagerank_scores, cls.clusters, cls.similar_map)
        cls.builder = builder

    def test_node_counts(self):
        types = {n["type"] for n in self.builder.nodes.values()}
        self.assertIn("surah", types)
        self.assertIn("ayah", types)
        self.assertIn("root", types)
        self.assertIn("lemma", types)
        self.assertIn("person", types)
        self.assertIn("theme", types)
        self.assertGreaterEqual(len(self.builder.nodes), 12000)

    def test_pagerank_validity(self):
        pr_sum = sum(self.pagerank_scores.values())
        self.assertAlmostEqual(pr_sum, 1.0, places=3)
        # Top node should be related to Allah
        top_node = max(self.pagerank_scores.items(), key=lambda x: x[1])[0]
        self.assertTrue("اللَّه" in top_node or "أله" in top_node)

    def test_sqlite_export(self):
        self.assertTrue(os.path.exists(GRAPH_DB_PATH))
        db = sqlite3.connect(GRAPH_DB_PATH)
        c = db.cursor()
        c.execute("SELECT count(*) FROM node")
        node_count = c.fetchone()[0]
        c.execute("SELECT count(*) FROM edge")
        edge_count = c.fetchone()[0]
        self.assertEqual(node_count, len(self.builder.nodes))
        self.assertEqual(edge_count, len(self.builder.edges))
        db.close()

    def test_json_shards_export(self):
        for name in ["summary.json", "entities.json", "themes.json", "similar_ayat.json", "clusters.json"]:
            path = os.path.join(EXPORT_DIR, name)
            self.assertTrue(os.path.exists(path), f"Missing shard: {path}")
            data = load_json(path)
            self.assertTrue(data)


if __name__ == "__main__":
    unittest.main()
