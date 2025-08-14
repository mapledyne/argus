"""Tests for formatters."""

import unittest
import json
import logging
from datetime import datetime

from argus.formatters import JSONFormatter, HumanReadableFormatter


class TestJSONFormatter(unittest.TestCase):
    """Test JSONFormatter."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = JSONFormatter()

    def test_format_basic_record(self):
        """Test formatting a basic log record."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.created = datetime.now().timestamp()
        
        # Add custom fields
        record.caller_module = "test_module"
        record.caller_func = "test_function"
        record.caller_lineno = 15
        
        formatted = self.formatter.format(record)
        parsed = json.loads(formatted)
        
        self.assertEqual(parsed["level"], "INFO")
        self.assertEqual(parsed["message"], "Test message")
        self.assertEqual(parsed["caller_module"], "test_module")
        self.assertEqual(parsed["caller_func"], "test_function")
        self.assertEqual(parsed["caller_lineno"], 15)
        self.assertEqual(parsed["logger"], "test_logger")
        self.assertIn("timestamp", parsed)

    def test_format_with_extra_fields(self):
        """Test formatting with extra fields."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.created = datetime.now().timestamp()
        record.caller_module = "test_module"
        record.caller_func = "test_function"
        record.caller_lineno = 15
        
        # Add extra fields
        record.extra_data = {
            "user_id": 123, 
            "action": "login"
        }
        
        formatted = self.formatter.format(record)
        parsed = json.loads(formatted)
        
        self.assertIn("extra_data", parsed)
        self.assertEqual(parsed["extra_data"]["user_id"], 123)
        self.assertEqual(parsed["extra_data"]["action"], "login")

    def test_format_with_missing_fields(self):
        """Test formatting with missing caller fields."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.created = datetime.now().timestamp()
        
        formatted = self.formatter.format(record)
        parsed = json.loads(formatted)
        
        self.assertEqual(parsed["caller_module"], "unknown")
        self.assertEqual(parsed["caller_func"], "unknown")
        self.assertEqual(parsed["caller_lineno"], 0)


class TestHumanReadableFormatter(unittest.TestCase):
    """Test HumanReadableFormatter."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = HumanReadableFormatter(display_extra_fields=True)

    def test_format_basic_record(self):
        """Test formatting a basic log record."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.created = datetime.now().timestamp()
        record.caller_module = "test_module"
        record.caller_func = "test_function"
        record.caller_lineno = 15
        
        formatted = self.formatter.format(record)
        
        self.assertIn("INFO", formatted)
        self.assertIn("Test message", formatted)
        self.assertIn("test_module.test_function:15", formatted)
        self.assertIn("Test message", formatted)

    def test_format_with_extra_fields(self):
        """Test formatting with extra fields."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.created = datetime.now().timestamp()
        record.caller_module = "test_module"
        record.caller_func = "test_function"
        record.caller_lineno = 15
        
        # Add extra fields
        record.extra_data = {
            "user_id": 123,
            "action": "login"
        }
        
        formatted = self.formatter.format(record)
        
        self.assertIn("user_id=123", formatted)
        self.assertIn("action=login", formatted)

    def test_format_without_extra_fields(self):
        """Test formatting without extra fields."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.created = datetime.now().timestamp()
        record.caller_module = "test_module"
        record.caller_func = "test_function"
        record.caller_lineno = 15
        
        formatted = self.formatter.format(record)
        
        # Should not contain extra field brackets when no extra fields
        # The format should end with just the message, not with extra fields in brackets
        self.assertNotIn("] [", formatted)  # No extra fields bracket after level bracket
        self.assertTrue(formatted.endswith("Test message"))

    def test_format_with_missing_fields(self):
        """Test formatting with missing caller fields."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.created = datetime.now().timestamp()
        
        formatted = self.formatter.format(record)
        
        self.assertIn("unknown.unknown:0", formatted)

    def test_format_different_levels(self):
        """Test formatting different log levels."""
        levels = [logging.DEBUG, logging.INFO, logging.WARNING, 
                 logging.ERROR, logging.CRITICAL]
        level_names = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level, level_name in zip(levels, level_names):
            record = logging.LogRecord(
                name="test_logger",
                level=level,
                pathname="test.py",
                lineno=10,
                msg="Test message",
                args=(),
                exc_info=None
            )
            record.created = datetime.now().timestamp()
            record.caller_module = "test_module"
            record.caller_func = "test_function"
            record.caller_lineno = 15
            
            formatted = self.formatter.format(record)
            self.assertIn(level_name, formatted)


if __name__ == '__main__':
    unittest.main()
