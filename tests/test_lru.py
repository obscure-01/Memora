"""
Unit tests for LRU Page Replacement Algorithm.

Test Categories:
    1. Standard reference sequence (known: 12 faults, 8 hits with 3 frames).
    2. Recency update verification (hits update access step, preventing eviction).
    3. Edge cases: all hits, single page, single frame.
    4. Schema verification: history contains step, page, frames, is_hit, evicted.
"""

import unittest
from src.algorithms.lru import run_lru


class TestLRU(unittest.TestCase):
    """Tests for the LRU page replacement algorithm."""

    def test_reference_sequence(self):
        """Verify LRU on standard reference string (12 faults, 8 hits)."""
        seq = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
        res = run_lru(seq, 3)

        self.assertEqual(res["algorithm"], "LRU")
        self.assertEqual(res["faults"], 12)
        self.assertEqual(res["hits"], 8)
        self.assertAlmostEqual(res["hit_ratio"], 0.40, places=4)
        self.assertAlmostEqual(res["fault_ratio"], 0.60, places=4)
        self.assertEqual(len(res["history"]), 20)

    def test_hit_updates_recency(self):
        """Verify that a page hit updates recency, saving it from eviction."""
        # Load 1, then 2. Frames: [1, 2].
        # In FIFO, accessing 1 does not change order (1 is evicted on 3).
        # In LRU, accessing 1 makes 2 the LRU page, so 3 evicts 2!
        seq = [1, 2, 1, 3]
        res = run_lru(seq, 2)
        hist = res["history"]

        self.assertTrue(hist[2]["is_hit"])  # Step 2: page 1 is HIT
        self.assertEqual(hist[3]["evicted"], 2)  # Step 3: page 3 evicts 2 (not 1)
        self.assertEqual(hist[3]["frames"], [1, 3])

    def test_all_pages_fit_in_frames(self):
        """When unique pages <= frame count, faults equal unique pages."""
        seq = [1, 2, 3, 1, 2, 3]
        res = run_lru(seq, 3)
        self.assertEqual(res["faults"], 3)
        self.assertEqual(res["hits"], 3)

    def test_single_frame(self):
        """Single frame behavior."""
        seq = [1, 2, 1, 2]
        res = run_lru(seq, 1)
        self.assertEqual(res["faults"], 4)
        self.assertEqual(res["hits"], 0)


if __name__ == "__main__":
    unittest.main()
