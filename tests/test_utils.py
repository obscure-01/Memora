"""
Unit tests for Memora Utilities (Logger and File Handler).

Tests functional Phase 1 utility operations:
- Logger initialization and formatting
- File handler path constants and directory creation
"""

import os
import unittest
from src.utils.logger import get_logger, LOG_DIR, LOG_FILE
from src.utils.file_handler import (
    PROJECT_ROOT,
    DATASETS_DIR,
    REPORTS_DIR,
    CHARTS_DIR,
    LOGS_DIR,
    ensure_output_directories,
)


class TestUtils(unittest.TestCase):
    """Tests for utility modules."""

    def test_logger_initialization_and_handlers(self):
        """Test logger setup and duplicate handler prevention."""
        logger = get_logger("test.utils.logger")
        self.assertIsNotNone(logger)
        self.assertEqual(len(logger.handlers), 2)  # Console + File handlers

        # Calling get_logger with same name should not add duplicate handlers
        logger_repeat = get_logger("test.utils.logger")
        self.assertEqual(len(logger_repeat.handlers), 2)

    def test_logger_writes_to_file(self):
        """Test that logger messages are written to log file."""
        logger = get_logger("test.utils.file_writer")
        test_msg = "Phase 1 audit log verification message"
        logger.info(test_msg)

        self.assertTrue(os.path.exists(LOG_FILE))
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn(test_msg, content)

    def test_path_constants_exist(self):
        """Verify project path constants point to valid locations."""
        self.assertTrue(os.path.isdir(PROJECT_ROOT))
        self.assertTrue(os.path.isdir(DATASETS_DIR))
        self.assertEqual(os.path.basename(PROJECT_ROOT), "Memora")

    def test_ensure_output_directories(self):
        """Verify output directory creation is safe and idempotent."""
        ensure_output_directories()
        self.assertTrue(os.path.isdir(REPORTS_DIR))
        self.assertTrue(os.path.isdir(CHARTS_DIR))
        self.assertTrue(os.path.isdir(LOGS_DIR))


if __name__ == "__main__":
    unittest.main()
