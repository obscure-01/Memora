"""
Unit tests for Sample Datasets and Test Cases.

Tests Phase 1 data artifacts:
- datasets/sample_input.json schema and validity
- datasets/test_cases.json schema, validity, and mathematical consistency
"""

import json
import os
import unittest
from src.utils.file_handler import DATASETS_DIR


class TestDatasets(unittest.TestCase):
    """Tests for dataset and test case definitions."""

    def test_sample_input_json_structure(self):
        """Verify sample_input.json exists, is valid JSON, and has all required fields."""
        path = os.path.join(DATASETS_DIR, "sample_input.json")
        self.assertTrue(os.path.isfile(path), f"File not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("datasets", data)
        datasets = data["datasets"]
        self.assertGreaterEqual(len(datasets), 8)

        required_fields = {"name", "description", "page_sequence", "frame_count", "purpose"}
        for ds in datasets:
            self.assertTrue(required_fields.issubset(set(ds.keys())))
            self.assertIsInstance(ds["page_sequence"], list)
            self.assertGreater(len(ds["page_sequence"]), 0)
            self.assertIsInstance(ds["frame_count"], int)
            self.assertGreaterEqual(ds["frame_count"], 1)
            for page in ds["page_sequence"]:
                self.assertIsInstance(page, int)
                self.assertGreaterEqual(page, 0)

    def test_test_cases_json_structure_and_math(self):
        """Verify test_cases.json has mathematically verified hit/fault counts."""
        path = os.path.join(DATASETS_DIR, "test_cases.json")
        self.assertTrue(os.path.isfile(path), f"File not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("test_cases", data)
        test_cases = data["test_cases"]
        self.assertGreaterEqual(len(test_cases), 10)

        for tc in test_cases:
            if tc.get("expected_validation_error", False):
                continue

            self.assertIsInstance(tc["page_sequence"], list)
            self.assertIsInstance(tc["frame_count"], int)
            self.assertIn("expected", tc)

            total_accesses = len(tc["page_sequence"])
            for algo, expected in tc["expected"].items():
                self.assertIn("hits", expected)
                self.assertIn("faults", expected)
                hits = expected["hits"]
                faults = expected["faults"]
                self.assertEqual(
                    hits + faults,
                    total_accesses,
                    f"In {tc['name']} ({algo}): hits ({hits}) + faults ({faults}) != total ({total_accesses})",
                )


if __name__ == "__main__":
    unittest.main()
