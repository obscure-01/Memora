"""
Unit tests for Metrics Calculator.

Test Categories:
    1. Correct hit and fault counting from history.
    2. Correct hit and fault ratio calculation (sum to 1.0).
    3. Empty / zero fault / zero hit edge cases.
    4. compare_metrics functionality including tied winners.
"""

import unittest
from src.core.metrics import calculate_metrics, compare_metrics


class TestMetrics(unittest.TestCase):
    """Tests for the metrics calculation module."""

    def test_calculate_metrics_basic(self):
        """Verify metric calculation from a mock history list."""
        history = [
            {"is_hit": False},
            {"is_hit": False},
            {"is_hit": True},
            {"is_hit": False},
        ]
        result = {"history": history}
        res = calculate_metrics(result)

        self.assertEqual(res["hits"], 1)
        self.assertEqual(res["faults"], 3)
        self.assertAlmostEqual(res["hit_ratio"], 0.25, places=4)
        self.assertAlmostEqual(res["fault_ratio"], 0.75, places=4)
        self.assertEqual(res["hit_ratio"] + res["fault_ratio"], 1.0)

    def test_all_hits_and_all_faults(self):
        """Verify 100% hits and 100% faults metrics."""
        all_hits = {"history": [{"is_hit": True}, {"is_hit": True}]}
        res_h = calculate_metrics(all_hits)
        self.assertEqual(res_h["hit_ratio"], 1.0)
        self.assertEqual(res_h["fault_ratio"], 0.0)

        all_faults = {"history": [{"is_hit": False}, {"is_hit": False}]}
        res_f = calculate_metrics(all_faults)
        self.assertEqual(res_f["hit_ratio"], 0.0)
        self.assertEqual(res_f["fault_ratio"], 1.0)

    def test_compare_metrics_single_winner(self):
        """Verify compare_metrics correctly identifies a single best algorithm."""
        results = [
            {"algorithm": "FIFO", "faults": 15, "hits": 5, "hit_ratio": 0.25, "fault_ratio": 0.75},
            {"algorithm": "LRU", "faults": 12, "hits": 8, "hit_ratio": 0.40, "fault_ratio": 0.60},
            {"algorithm": "Optimal", "faults": 9, "hits": 11, "hit_ratio": 0.55, "fault_ratio": 0.45},
        ]
        comp = compare_metrics(results)
        self.assertEqual(comp["fewest_faults"], 9)
        self.assertEqual(comp["best_algorithm"], "Optimal")
        self.assertEqual(comp["best_algorithms"], ["Optimal"])

    def test_compare_metrics_tied_winners(self):
        """Verify compare_metrics reports all tied algorithms without arbitrary selection."""
        results = [
            {"algorithm": "FIFO", "faults": 5, "hits": 5, "hit_ratio": 0.5, "fault_ratio": 0.5},
            {"algorithm": "LRU", "faults": 5, "hits": 5, "hit_ratio": 0.5, "fault_ratio": 0.5},
            {"algorithm": "Optimal", "faults": 5, "hits": 5, "hit_ratio": 0.5, "fault_ratio": 0.5},
        ]
        comp = compare_metrics(results)
        self.assertEqual(comp["fewest_faults"], 5)
        self.assertEqual(comp["best_algorithms"], ["FIFO", "LRU", "Optimal"])
        self.assertIn("FIFO", comp["best_algorithm"])
        self.assertIn("LRU", comp["best_algorithm"])
        self.assertIn("Optimal", comp["best_algorithm"])


if __name__ == "__main__":
    unittest.main()
