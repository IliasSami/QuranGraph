"""Unit tests for Numbers Lab statistics generator."""
import os
import unittest
from stats.numbers_lab import compute_numbers_lab, OUTPUT_PATH


class TestNumbersLab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = compute_numbers_lab()

    def test_baseline_counts(self):
        baseline = self.data["baseline"]
        self.assertEqual(baseline["surahs"], 114)
        self.assertEqual(baseline["ayat"], 6236)
        self.assertEqual(baseline["words_morphology"], 77429)
        self.assertEqual(baseline["words_whitespace"], 77800)
        self.assertEqual(baseline["letters_total"], 330709)
        self.assertEqual(baseline["distinct_roots"], 1651)
        self.assertEqual(baseline["distinct_lemmas"], 4763)

    def test_coverage_curve(self):
        curve = self.data["vocabulary_coverage"]["curve"]
        self.assertTrue(len(curve) >= 5)
        step_50 = next(s for s in curve if s["target_coverage_pct"] == 50)
        self.assertEqual(step_50["lemmas_needed"], 58)
        self.assertEqual(step_50["roots_needed"], 61)

    def test_audited_claims(self):
        claims = {c["id"]: c for c in self.data["audited_claims"]}
        self.assertIn("claim-shahr-12", claims)
        self.assertEqual(claims["claim-shahr-12"]["status"], "Verified")
        self.assertEqual(claims["claim-shahr-12"]["counts"]["singular_shahr"], 12)

        self.assertIn("claim-dunya-akhirah", claims)
        self.assertEqual(claims["claim-dunya-akhirah"]["status"], "Verified")
        self.assertEqual(claims["claim-dunya-akhirah"]["counts"]["dunya_count"], 115)
        self.assertEqual(claims["claim-dunya-akhirah"]["counts"]["akhirah_count"], 115)

    def test_output_file_exists(self):
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        self.assertGreater(os.path.getsize(OUTPUT_PATH), 1000)


if __name__ == "__main__":
    unittest.main()
