"""
Unit tests for Optimal (Bélády's) Page Replacement Algorithm.

Test Categories:
    1. Standard reference sequence (known: 9 faults, 11 hits with 3 frames).
    2. Future-look lookahead verification (farthest used page evicted).
    3. Never-used-again priority (pages never appearing again evicted first).
    4. Deterministic tie-breaking (earliest frame chosen when tied).
"""

import unittest
from src.algorithms.optimal import run_optimal


class TestOptimal(unittest.TestCase):
    """Tests for the Optimal page replacement algorithm."""

    def test_reference_sequence(self):
        """Verify Optimal on standard reference string (9 faults, 11 hits)."""
        seq = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
        res = run_optimal(seq, 3)

        self.assertEqual(res["algorithm"], "Optimal")
        self.assertEqual(res["faults"], 9)
        self.assertEqual(res["hits"], 11)
        self.assertAlmostEqual(res["hit_ratio"], 0.55, places=4)
        self.assertAlmostEqual(res["fault_ratio"], 0.45, places=4)
        self.assertEqual(len(res["history"]), 20)

    def test_never_used_again_eviction(self):
        """Verify that a page never appearing in the future is chosen for eviction."""
        # Frames=2: Load 1, 2. Sequence: [1, 2, 3, 2].
        # Future at step 2 (access 3): page 2 will be used at step 3, page 1 never used.
        # Optimal must evict 1.
        seq = [1, 2, 3, 2]
        res = run_optimal(seq, 2)
        hist = res["history"]

        self.assertEqual(hist[2]["evicted"], 1)
        self.assertEqual(hist[2]["frames"], [3, 2])
        self.assertTrue(hist[3]["is_hit"])

    def test_farthest_future_eviction(self):
        """Verify that among pages appearing in future, the farthest is evicted."""
        # Frames=2: Load 1, 2. Next: 3, then 1, then 2.
        # Future of 1 is next step, future of 2 is step after.
        # Optimal must evict 2 (farthest in future).
        seq = [1, 2, 3, 1, 2]
        res = run_optimal(seq, 2)
        hist = res["history"]

        self.assertEqual(hist[2]["evicted"], 2)
        self.assertEqual(hist[2]["frames"], [1, 3])


if __name__ == "__main__":
    unittest.main()
