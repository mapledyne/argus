"""Tests for handlers."""

import unittest
import tempfile
import shutil
import json
import logging
import os
from datetime import datetime

from handlers import JSONFileHandler
from formatters import JSONFormatter


class TestJSONFileHandler(unittest.TestCase):
    """Test JSONFileHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_handler_initialization(self):
        """Test handler initialization."""
        handler = JSONFileHandler(self.log_file)
        handler.setFormatter(JSONFormatter())
        
        # Check that file was created and contains opening structure
        self.assertTrue(os.path.exists(self.log_file))
        
        with open(self.log_file, 'r') as f:
            content = f.read()
            self.assertIn('{"logs": [', content)
        
        # Close the handler to properly clean up the file stream
        handler.close()

    def test_emit_single_record(self):
        """Test emitting a single record."""
        handler = JSONFileHandler(self.log_file)
        handler.setFormatter(JSONFormatter())
        
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
        
        handler.emit(record)
        handler.close()
        
        # Check that file contains the log entry
        with open(self.log_file, 'r') as f:
            content = f.read()
            self.assertIn("Test message", content)
            self.assertIn("test_module", content)
            self.assertIn("test_function", content)

    def test_emit_multiple_records(self):
        """Test emitting multiple records."""
        handler = JSONFileHandler(self.log_file)
        handler.setFormatter(JSONFormatter())
        
        for i in range(3):
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="test.py",
                lineno=10,
                msg=f"Test message {i}",
                args=(),
                exc_info=None
            )
            record.created = datetime.now().timestamp()
            record.caller_module = "test_module"
            record.caller_func = "test_function"
            record.caller_lineno = 15
            
            handler.emit(record)
        
        handler.close()
        
        # Check that file contains all log entries
        with open(self.log_file, 'r') as f:
            content = f.read()
            for i in range(3):
                self.assertIn(f"Test message {i}", content)

    def test_handler_close_structure(self):
        """Test that handler close creates proper JSON structure."""
        handler = JSONFileHandler(self.log_file)
        handler.setFormatter(JSONFormatter())
        
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
        
        handler.emit(record)
        handler.close()
        
        # Check that file is valid JSON
        with open(self.log_file, 'r') as f:
            content = f.read()
            try:
                parsed = json.loads(content)
                self.assertIn("logs", parsed)
                self.assertIn("state", parsed)
                self.assertIn("diagnostics_state", parsed)
                self.assertEqual(len(parsed["logs"]), 1)
                self.assertEqual(parsed["logs"][0]["message"], "Test message")
            except json.JSONDecodeError as e:
                self.fail(f"Generated file is not valid JSON: {e}")

    def test_state_entries(self):
        """Test adding state entries."""
        handler = JSONFileHandler(self.log_file)
        handler.setFormatter(JSONFormatter())
        
        # Add state entries
        state_entry1 = json.dumps({"object": "test1", "status": "active"})
        state_entry2 = json.dumps({"object": "test2", "count": 42})
        
        handler.state_entries.append(state_entry1)
        handler.state_entries.append(state_entry2)
        
        handler.close()
        
        # Check that state entries are included
        with open(self.log_file, 'r') as f:
            content = f.read()
            try:
                parsed = json.loads(content)
                self.assertIn("state", parsed)
                state = parsed["state"]
                self.assertEqual(len(state), 2)
                # Parse the state entries to verify content
                state1 = state[0]
                state2 = state[1]
                
                self.assertEqual(state1["object"], "test1")
                self.assertEqual(state1["status"], "active")
                self.assertEqual(state2["object"], "test2")
                self.assertEqual(state2["count"], 42)
            except json.JSONDecodeError as e:
                self.fail(f"Generated file is not valid JSON: {e}")

    def test_handler_with_exception(self):
        """Test handler behavior with exceptions."""
        handler = JSONFileHandler(self.log_file)
        handler.setFormatter(JSONFormatter())
        
        # Create a record that might cause issues
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
        
        # Add a non-serializable object to test error handling
        # Function is not JSON serializable
        record.problematic_field = lambda x: x
        
        # Should not raise an exception
        try:
            handler.emit(record)
            handler.close()
        except Exception as e:
            self.fail(f"Handler should handle exceptions gracefully: {e}")
        
        # Verify that the handler still created a valid file structure
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, 'r') as f:
            content = f.read()
            # Should at least have the basic structure
            self.assertIn('{"logs": [', content)

    def test_handler_file_encoding(self):
        """Test handler with UTF-8 encoding."""
        handler = JSONFileHandler(self.log_file, encoding="utf-8")
        handler.setFormatter(JSONFormatter())
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message with unicode: éñç",
            args=(),
            exc_info=None
        )
        record.created = datetime.now().timestamp()
        record.caller_module = "test_module"
        record.caller_func = "test_function"
        record.caller_lineno = 15
        
        handler.emit(record)
        handler.close()
        
        # Check that unicode is preserved
        with open(self.log_file, 'r', encoding="utf-8") as f:
            content = f.read()
            self.assertIn("éñç", content)

    def test_handler_with_no_records(self):
        """Test handler behavior when no records are emitted."""
        handler = JSONFileHandler(self.log_file)
        handler.setFormatter(JSONFormatter())
        
        # Close without emitting any records
        handler.close()
        
        # Check that file still has valid JSON structure
        with open(self.log_file, 'r') as f:
            content = f.read()
            try:
                parsed = json.loads(content)
                self.assertIn("logs", parsed)
                self.assertIn("state", parsed)
                self.assertIn("diagnostics_state", parsed)
                self.assertEqual(len(parsed["logs"]), 0)  # No logs emitted
            except json.JSONDecodeError as e:
                self.fail(f"Generated file is not valid JSON: {e}")


if __name__ == '__main__':
    unittest.main()
