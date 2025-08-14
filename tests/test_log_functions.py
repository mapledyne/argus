"""Tests for core logging functions."""

import os
import unittest
import tempfile
import shutil
import logging

import argus


class TestLogFunctions(unittest.TestCase):
    """Test the core logging functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        argus.set_log_directory(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        argus.set_log_directory(None)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_debug_logging(self):
        """Test debug level logging."""
        with self.assertLogs('ArgusLogger', level='DEBUG') as cm:
            argus.debug("Test debug message")
        
        self.assertIn("Test debug message", cm.output[0])

    def test_info_logging(self):
        """Test info level logging."""
        with self.assertLogs('ArgusLogger', level='INFO') as cm:
            argus.info("Test info message")
        
        self.assertIn("Test info message", cm.output[0])

    def test_warning_logging(self):
        """Test warning level logging."""
        with self.assertLogs('ArgusLogger', level='WARNING') as cm:
            argus.warning("Test warning message")
        
        self.assertIn("Test warning message", cm.output[0])

    def test_error_logging(self):
        """Test error level logging."""
        with self.assertLogs('ArgusLogger', level='ERROR') as cm:
            argus.error("Test error message")
        
        self.assertIn("Test error message", cm.output[0])

    def test_critical_logging(self):
        """Test critical level logging."""
        with self.assertLogs('ArgusLogger', level='CRITICAL') as cm:
            argus.critical("Test critical message")
        
        self.assertIn("Test critical message", cm.output[0])

    def test_logging_with_extra_fields(self):
        """Test logging with extra fields."""
        with self.assertLogs('ArgusLogger', level='INFO') as cm:
            argus.info("Test message", user_id=123, action="login")
        
        log_output = cm.output[0]
        self.assertIn("Test message", log_output)
        # Extra fields should be included in the log

    def test_warning_with_warning_type(self):
        """Test warning with warning type."""
        with self.assertLogs('ArgusLogger', level='WARNING') as cm:
            with self.assertWarns(UserWarning):
                argus.warning("Test warning", warning_type=UserWarning)
        
        self.assertIn("Test warning", cm.output[0])

    def test_error_with_exception_type(self):
        """Test error with exception type."""
        with self.assertLogs('ArgusLogger', level='ERROR') as cm:
            with self.assertRaises(ValueError):
                argus.error("Test error", error_type=ValueError)
        
        self.assertIn("Test error", cm.output[0])

    def test_critical_with_exception_type(self):
        """Test critical with exception type."""
        with self.assertLogs('ArgusLogger', level='CRITICAL') as cm:
            with self.assertRaises(RuntimeError):
                argus.critical("Test critical", error_type=RuntimeError)
        
        self.assertIn("Test critical", cm.output[0])


class TestLogLevels(unittest.TestCase):
    """Test LogLevels enum."""

    def test_log_levels_enum(self):
        """Test LogLevels enum values."""
        self.assertEqual(argus.DEBUG, logging.DEBUG)
        self.assertEqual(argus.INFO, logging.INFO)
        self.assertEqual(argus.WARNING, logging.WARNING)
        self.assertEqual(argus.ERROR, logging.ERROR)
        self.assertEqual(argus.CRITICAL, logging.CRITICAL)

    def test_log_levels_usage(self):
        """Test using LogLevels enum with log_level function."""
        argus.log_level(argus.DEBUG)
        self.assertEqual(argus.logger.level, logging.DEBUG)

        argus.log_level(argus.ERROR)
        self.assertEqual(argus.logger.level, logging.ERROR)


if __name__ == '__main__':
    unittest.main()
