"""
Unit tests for FIFO Page Replacement Algorithm.

Test Categories:
    1. Standard reference sequence (known: 15 faults, 5 hits with 3 frames).
    2. Edge cases: all hits, all faults, single page, single frame.
    3. Replacement verification: oldest loaded page is evicted.
    4. Schema verification: history contains step, page, frames, is_hit, evicted.
"""

import unittest
from src.algorithms.fifo import run_fifo


class TestFIFO(unittest.TestCase):
    """Tests for the FIFO page replacement algorithm."""

    def test_reference_sequence(self):
        """Verify FIFO on standard reference string (15 faults, 5 hits)."""
        seq = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
        res = run_fifo(seq, 3)

        self.assertEqual(res["algorithm"], "FIFO")
        self.assertEqual(res["faults"], 15)
        self.assertEqual(res["hits"], 5)
        self.assertAlmostEqual(res["hit_ratio"], 0.25, places=4)
        self.assertAlmostEqual(res["fault_ratio"], 0.75, places=4)
        self.assertEqual(len(res["history"]), 20)

    def test_result_structure_and_history(self):
        """Verify returned dictionary schema and history field contract."""
        seq = [1, 2, 3, 4]
        res = run_fifo(seq, 2)

        self.assertIn("algorithm", res)
        self.assertIn("page_sequence", res)
        self.assertIn("frame_count", res)
        self.assertIn("hits", res)
        self.assertIn("faults", res)
        self.assertIn("hit_ratio", res)
        self.assertIn("fault_ratio", res)
        self.assertIn("history", res)

        for item in res["history"]:
            self.assertIn("step", item)
            self.assertIn("page", item)
            self.assertIn("frames", item)
            self.assertIn("is_hit", item)
            self.assertIn("evicted", item)
            self.assertEqual(len(item["frames"]), 2)

    def test_all_pages_fit_in_frames(self):
        """When unique pages <= frame count, faults equal unique pages then all hits."""
        seq = [1, 2, 3, 1, 2, 3]
        res = run_fifo(seq, 3)
        self.assertEqual(res["faults"], 3)
        self.assertEqual(res["hits"], 3)

    def test_single_repeated_page(self):
        """Single repeated page produces exactly 1 initial fault and subsequent hits."""
        seq = [5, 5, 5, 5, 5]
        res = run_fifo(seq, 2)
        self.assertEqual(res["faults"], 1)
        self.assertEqual(res["hits"], 4)

    def test_single_frame(self):
        """Single frame: alternating pages cause faults on every transition."""
        seq = [1, 2, 1, 2]
        res = run_fifo(seq, 1)
        self.assertEqual(res["faults"], 4)
        self.assertEqual(res["hits"], 0)

    def test_fifo_eviction_order(self):
        """Verify that the page loaded earliest is evicted first."""
        # Load 1, 2 in frames=2. Then access 3 -> 1 must be evicted.
        seq = [1, 2, 3]
        res = run_fifo(seq, 2)
        hist = res["history"]

        self.assertEqual(hist[0]["evicted"], None)
        self.assertEqual(hist[1]["evicted"], None)
        self.assertEqual(hist[2]["evicted"], 1)
        self.assertEqual(hist[2]["frames"], [3, 2])


if __name__ == "__main__":
    unittest.main()
