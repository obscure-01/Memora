"""
Unit tests for Input Validator.

Test Categories:
    1. Valid inputs accepted.
    2. Empty page sequence rejected.
    3. Negative page numbers rejected.
    4. Non-integer page values rejected.
    5. Boolean values explicitly rejected for pages and frames.
    6. Frame count <= 0 rejected.
    7. Dataset structure validation.
"""

import unittest
from src.core.validator import (
    validate_page_sequence,
    validate_frame_count,
    validate_dataset,
)


class TestValidator(unittest.TestCase):
    """Tests for the input validation module."""

    def test_valid_page_sequence(self):
        """Valid integer sequence passes validation."""
        valid, err = validate_page_sequence([7, 0, 1, 2, 0, 3])
        self.assertTrue(valid)
        self.assertEqual(err, "")

    def test_empty_sequence_rejected(self):
        """Empty page sequence is rejected."""
        valid, err = validate_page_sequence([])
        self.assertFalse(valid)
        self.assertIn("empty", err.lower())

    def test_negative_page_rejected(self):
        """Negative page number is rejected."""
        valid, err = validate_page_sequence([1, -2, 3])
        self.assertFalse(valid)
        self.assertIn("non-negative", err.lower())

    def test_non_integer_page_rejected(self):
        """Non-integer page number (e.g., string, float) is rejected."""
        valid, err = validate_page_sequence([1, "a", 3])
        self.assertFalse(valid)
        self.assertIn("integer", err.lower())

        valid2, err2 = validate_page_sequence([1, 2.5, 3])
        self.assertFalse(valid2)
        self.assertIn("integer", err2.lower())

    def test_boolean_values_rejected(self):
        """Booleans (True/False) must be rejected even though bool is subclass of int."""
        valid, err = validate_page_sequence([1, True, 3])
        self.assertFalse(valid)
        self.assertIn("boolean", err.lower())

        valid_fc, err_fc = validate_frame_count(True)
        self.assertFalse(valid_fc)
        self.assertIn("boolean", err_fc.lower())

    def test_valid_frame_count(self):
        """Positive integer frame count passes."""
        valid, err = validate_frame_count(3)
        self.assertTrue(valid)
        self.assertEqual(err, "")

    def test_invalid_frame_count_zero_and_negative(self):
        """Zero and negative frame counts are rejected."""
        v0, err0 = validate_frame_count(0)
        self.assertFalse(v0)
        self.assertIn("positive", err0.lower())

        vn, errn = validate_frame_count(-1)
        self.assertFalse(vn)
        self.assertIn("positive", errn.lower())

    def test_validate_dataset_valid(self):
        """Valid dataset dictionary passes."""
        ds = {"page_sequence": [1, 2, 3], "frame_count": 2}
        valid, err = validate_dataset(ds)
        self.assertTrue(valid)

    def test_validate_dataset_missing_fields(self):
        """Dataset missing required fields is rejected."""
        ds1 = {"page_sequence": [1, 2, 3]}
        valid1, err1 = validate_dataset(ds1)
        self.assertFalse(valid1)
        self.assertIn("frame_count", err1)

        ds2 = {"frame_count": 3}
        valid2, err2 = validate_dataset(ds2)
        self.assertFalse(valid2)
        self.assertIn("page_sequence", err2)


if __name__ == "__main__":
    unittest.main()
