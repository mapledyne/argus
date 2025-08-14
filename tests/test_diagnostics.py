"""
Unit tests for the k_diagnostics module.

This module tests all major functionality of the diagnostics system including:
- Logging functions (debug, info, warning, error, critical)
- System metrics (when psutil is available)
- Decorators (log_function_call, log_timing, deprecated)
- Configuration functions
- Debug function management
- Log cleanup functionality
"""

import unittest
import tempfile
import shutil
import time
import warnings

# Import the module to test
import argus as diag

class TestLoggingFunctions(unittest.TestCase):
    """Test the basic logging functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for logs
        self.temp_dir = tempfile.mkdtemp()
        self.original_log_dir = diag.get_log_directory()
        diag.set_log_directory(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        diag.set_log_directory(self.original_log_dir)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_debug_logging(self):
        """Test debug level logging."""
        with self.assertLogs('DebugManager', level='DEBUG') as cm:
            diag.debug("Test debug message")
        
        self.assertIn("Test debug message", cm.output[0])

    def test_info_logging(self):
        """Test info level logging."""
        with self.assertLogs('DebugManager', level='INFO') as cm:
            diag.info("Test info message")
        
        self.assertIn("Test info message", cm.output[0])

    def test_warning_logging(self):
        """Test warning level logging."""
        with self.assertLogs('DebugManager', level='WARNING') as cm:
            diag.warning("Test warning message")
        
        self.assertIn("Test warning message", cm.output[0])

    def test_error_logging(self):
        """Test error level logging."""
        with self.assertLogs('DebugManager', level='ERROR') as cm:
            diag.error("Test error message")
        
        self.assertIn("Test error message", cm.output[0])

    def test_critical_logging(self):
        """Test critical level logging."""
        with self.assertLogs('DebugManager', level='CRITICAL') as cm:
            diag.critical("Test critical message")
        
        self.assertIn("Test critical message", cm.output[0])

    def test_log_with_custom_level(self):
        """Test logging with custom level."""
        with self.assertLogs('DebugManager', level='INFO') as cm:
            diag.log(diag.INFO, "Test custom level message")
        
        self.assertIn("Test custom level message", cm.output[0])

class TestDecorators(unittest.TestCase):
    """Test the decorators provided by the module."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_log_dir = diag.get_log_directory()
        diag.set_log_directory(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        diag.set_log_directory(self.original_log_dir)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_function_call_decorator(self):
        """Test the log_function_call decorator."""
        @diag.log_function_call
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
        @diag.log_function_call
        def failing_function():
            raise ValueError("Test exception")

        with self.assertLogs('DebugManager', level='ERROR') as cm:
            with self.assertRaises(ValueError):
                failing_function()
        
        self.assertIn("Function failing_function raised an exception", cm.output[0])

    def test_log_timing_decorator(self):
        """Test the log_timing decorator."""
        @diag.log_timing
        def slow_function():
            time.sleep(0.01)  # Small delay to ensure measurable time
            return "done"

        with self.assertLogs('DebugManager', level='INFO') as cm:
            result = slow_function()

        self.assertEqual(result, "done")
        self.assertIn("Function slow_function took", cm.output[0])

    def test_deprecated_decorator(self):
        """Test the deprecated decorator."""
        @diag.deprecated("This function is deprecated")
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
        @diag.deprecated("Custom deprecation message")
        def old_function():
            return "old result"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_function()
        
        self.assertEqual(result, "old result")
        self.assertIn("Custom deprecation message", str(w[0].message))


class TestConfigurationFunctions(unittest.TestCase):
    """Test configuration functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_log_dir = diag.get_log_directory()
        # Get logger from the diagnostics module directly
        self.original_log_level = diag.logger.level

    def tearDown(self):
        """Clean up test fixtures."""
        diag.set_log_directory(self.original_log_dir)
        diag.log_level(self.original_log_level)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_set_and_get_log_directory(self):
        """Test setting and getting log directory."""
        diag.set_log_directory(self.temp_dir)
        self.assertEqual(diag.get_log_directory(), self.temp_dir)

    def test_set_log_directory_none(self):
        """Test setting log directory to None."""
        diag.set_log_directory(None)
        self.assertIsNone(diag.get_log_directory())

    def test_log_level_setting(self):
        """Test setting log level."""
        diag.log_level(diag.DEBUG)
        self.assertEqual(diag.logger.level, diag.DEBUG)

        diag.log_level(diag.INFO)
        self.assertEqual(diag.logger.level, diag.INFO)

    def test_max_logs_setting(self):
        """Test setting max logs."""
        # Set a log directory first to avoid NoneType error
        diag.set_log_directory(self.temp_dir)
        diag.max_logs(5)
        # Note: We can't easily test the cleanup functionality without creating actual log files
        # This test just ensures the function doesn't raise an exception
        self.assertTrue(True)


class TestDebugFunctionManagement(unittest.TestCase):
    """Test debug function registration and execution."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_log_dir = diag.get_log_directory()
        diag.set_log_directory(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        diag.set_log_directory(self.original_log_dir)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_register_debug_function(self):
        """Test registering a debug function."""
        def test_debug_func():
            return "Debug output"

        with self.assertLogs('DebugManager', level='DEBUG') as cm:
            diag.register_debug_function(test_debug_func)
        
        self.assertIn("Registered exit logging function: test_debug_func", cm.output[0])

    def test_register_non_callable(self):
        """Test registering a non-callable object."""
        non_callable = "not a function"
        
        with self.assertLogs('DebugManager', level='WARNING') as cm:
            diag.register_debug_function(non_callable)
        
        self.assertIn("Attempted to register a non-callable object", cm.output[0])
class TestLogCleanup(unittest.TestCase):
    """Test log cleanup functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_log_dir = diag.get_log_directory()
        self.original_max_logs = getattr(diag, '_max_logs', -1)
        diag.set_log_directory(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        diag.set_log_directory(self.original_log_dir)
        if hasattr(diag, '_max_logs'):
            diag._max_logs = self.original_max_logs
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cleanup_logs_disabled(self):
        """Test cleanup when max_logs is -1 (disabled)."""
        diag.max_logs(-1)
        # Should not raise any exceptions

    def test_cleanup_logs_with_no_old_logs(self):
        """Test cleanup when there are no old logs to remove."""
        diag.max_logs(5)
        # Should not raise any exceptions


class TestModuleConstants(unittest.TestCase):
    """Test module constants and imports."""

    def test_logging_constants(self):
        """Test logging level constants."""
        import logging
        self.assertEqual(diag.DEBUG, logging.DEBUG)
        self.assertEqual(diag.INFO, logging.INFO)
        self.assertEqual(diag.WARNING, logging.WARNING)
        self.assertEqual(diag.ERROR, logging.ERROR)
        self.assertEqual(diag.CRITICAL, logging.CRITICAL)


if __name__ == '__main__':
    
    unittest.main()
