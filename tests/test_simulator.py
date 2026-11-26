"""
Unit tests for Simulator and Comparison Modules.

Tests:
    1. run_simulation with valid and invalid inputs.
    2. run_all_simulations returns all 3 algorithms.
    3. compare_algorithms integration.
"""

import unittest
from src.core.simulator import run_simulation, run_all_simulations
from src.analysis.comparison import compare_algorithms


class TestSimulator(unittest.TestCase):
    """Tests for simulator and comparison workflows."""

    def test_run_simulation_fifo(self):
        """Test run_simulation with FIFO."""
        res = run_simulation("FIFO", [1, 2, 3, 1], 2)
        self.assertEqual(res["algorithm"], "FIFO")
        self.assertIn("hits", res)
        self.assertIn("faults", res)

    def test_run_simulation_case_insensitive(self):
        """Test algorithm names are resolved case-insensitively."""
        res_lru = run_simulation("lru", [1, 2, 3], 2)
        self.assertEqual(res_lru["algorithm"], "LRU")

        res_opt = run_simulation("OPTIMAL", [1, 2, 3], 2)
        self.assertEqual(res_opt["algorithm"], "Optimal")

    def test_run_simulation_invalid_input(self):
        """Test that invalid inputs raise ValueError."""
        with self.assertRaises(ValueError):
            run_simulation("FIFO", [], 3)  # Empty sequence

        with self.assertRaises(ValueError):
            run_simulation("FIFO", [1, 2], 0)  # Zero frames

        with self.assertRaises(ValueError):
            run_simulation("NON_EXISTENT", [1, 2], 2)  # Invalid algorithm

    def test_run_all_simulations(self):
        """Test run_all_simulations returns results for FIFO, LRU, Optimal."""
        results = run_all_simulations([7, 0, 1, 2], 3)
        self.assertEqual(len(results), 3)
        algos = [r["algorithm"] for r in results]
        self.assertIn("FIFO", algos)
        self.assertIn("LRU", algos)
        self.assertIn("Optimal", algos)

    def test_compare_algorithms(self):
        """Test compare_algorithms integration."""
        comp = compare_algorithms([7, 0, 1, 2, 0, 3], 3)
        self.assertIn("results", comp)
        self.assertIn("summary", comp)
        self.assertEqual(len(comp["results"]), 3)
        self.assertIn("best_algorithm", comp["summary"])
        self.assertIn("fewest_faults", comp["summary"])


if __name__ == "__main__":
    unittest.main()
