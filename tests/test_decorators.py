"""Tests for decorators."""

import unittest
import tempfile
import shutil
import time
import warnings

import argus


class TestDecorators(unittest.TestCase):
    """Test the decorators provided by the module."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_log_dir = argus.get_log_directory()
        argus.set_log_directory(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        argus.set_log_directory(self.original_log_dir)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_function_call_decorator(self):
        """Test the log_function_call decorator."""
        @argus.log_function_call
        def test_function(arg1, arg2, kwarg1="default"):
            return arg1 + arg2

        with self.assertLogs('DebugManager', level='DEBUG') as cm:
            result = test_function(1, 2, kwarg1="test")
        
        self.assertEqual(result, 3)
        log_output = '\n'.join(cm.output)
        self.assertIn("Calling function: test_function", log_output)
        self.assertIn("Arguments: (1, 2)", log_output)
        self.assertIn("Keyword arguments: {'kwarg1': 'test'}", log_output)
        self.assertIn("Function test_function returned: 3", log_output)

    def test_log_function_call_with_exception(self):
        """Test log_function_call decorator with exception handling."""
        @argus.log_function_call
        def failing_function():
            raise ValueError("Test exception")

        with self.assertLogs('DebugManager', level='ERROR') as cm:
            with self.assertRaises(ValueError):
                failing_function()
        
        self.assertIn("Function failing_function raised an exception", cm.output[0])

    def test_log_timing_decorator(self):
        """Test the log_timing decorator."""
        @argus.log_timing
        def slow_function():
            time.sleep(0.01)  # Small delay to ensure measurable time
            return "done"

        with self.assertLogs('DebugManager', level='INFO') as cm:
            result = slow_function()

        self.assertEqual(result, "done")
        self.assertIn("Function slow_function took", cm.output[0])

    def test_log_timing_decorator_fast_function(self):
        """Test the log_timing decorator with a fast function."""
        @argus.log_timing
        def fast_function():
            return "fast"

        with self.assertLogs('DebugManager', level='INFO') as cm:
            result = fast_function()

        self.assertEqual(result, "fast")
        self.assertIn("Function fast_function took", cm.output[0])

    def test_deprecated_decorator(self):
        """Test the deprecated decorator."""
        @argus.deprecated("This function is deprecated")
        def old_function():
            return "old result"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_function()
        
        self.assertEqual(result, "old result")
        self.assertEqual(len(w), 1)
        self.assertIs(w[0].category, DeprecationWarning)
        self.assertIn("deprecated", str(w[0].message))

    def test_deprecated_decorator_custom_message(self):
        """Test deprecated decorator with custom message."""
        @argus.deprecated("Custom deprecation message")
        def old_function():
            return "old result"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_function()
        
        self.assertEqual(result, "old result")
        self.assertIn("Custom deprecation message", str(w[0].message))

    def test_deprecated_decorator_default_message(self):
        """Test deprecated decorator with default message."""
        @argus.deprecated()
        def old_function():
            return "old result"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_function()
        
        self.assertEqual(result, "old result")
        self.assertIn("This function is deprecated", str(w[0].message))

    def test_decorator_preserves_function_metadata(self):
        """Test that decorators preserve function metadata."""
        @argus.log_function_call
        def test_function():
            """Test function docstring."""
            pass

        self.assertEqual(test_function.__name__, "test_function")
        self.assertEqual(test_function.__doc__, "Test function docstring.")


if __name__ == '__main__':
    unittest.main()
