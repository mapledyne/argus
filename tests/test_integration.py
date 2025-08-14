"""Integration tests for the complete logging system."""

import unittest
import tempfile
import shutil
import json
import warnings
from pathlib import Path

import argus
from argus.log_functions import run_debug_functions
from .test_utils import close_file_handler


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete logging system."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        # Reset logging state for each test
        argus.set_log_directory(None)
        # Clear debug functions between tests
        from argus.log_functions import debug_functions
        debug_functions.clear()
        # Reset logger level to default
        argus.log_level(argus.ERROR)
        # Properly close and clear all logger handlers to ensure clean state
        for handler in argus.logger.handlers[:]:  # Copy list to avoid modification
            if hasattr(handler, 'close'):
                handler.close()
            argus.logger.removeHandler(handler)

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up any file logging
        from argus.log_functions import _file_handler
        if _file_handler:
            _file_handler.close()
        argus.set_log_directory(None)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_logging_workflow(self):
        """Test complete logging workflow with file and console output."""
        # Set up logging
        argus.set_log_directory(self.temp_dir)
        argus.log_level(argus.DEBUG)
        
        # Log various messages
        argus.debug("Debug message", user_id=123)
        argus.info("Info message", action="login")
        
        # Suppress the expected warning for testing
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            argus.warning("Warning message", warning_type=UserWarning)
        
        # Test error logging with exception raising (this is expected behavior)
        with self.assertRaises(ValueError) as context:
            argus.error("Error message", error_type=ValueError)
        self.assertEqual(str(context.exception), "Error message")
        
        # Check that log file was created
        log_files = list(Path(self.temp_dir).glob("*.log"))
        self.assertEqual(len(log_files), 1)
        
        # Close the file handler to ensure JSON structure is completed
        close_file_handler()
        
        # Check log file content
        with open(log_files[0], 'r') as f:
            content = f.read()
            parsed = json.loads(content)
            
            self.assertIn("logs", parsed)
            self.assertIn("state", parsed)
            self.assertIn("diagnostics_state", parsed)
            
            logs = parsed["logs"]
            self.assertEqual(len(logs), 4)
            
            # Check that all messages are present
            messages = [log["message"] for log in logs]
            self.assertIn("Debug message", messages)
            self.assertIn("Info message", messages)
            self.assertIn("Warning message", messages)
            self.assertIn("Error message", messages)
            
            # Check that extra fields are included
            debug_log = next(log for log in logs if log["message"] == "Debug message")
            self.assertIn("extra_data", debug_log)
            self.assertEqual(debug_log["extra_data"]["user_id"], 123)
            
            info_log = next(log for log in logs if log["message"] == "Info message")
            self.assertIn("extra_data", info_log)
            self.assertEqual(info_log["extra_data"]["action"], "login")

    def test_decorators_with_logging(self):
        """Test decorators working with the logging system."""
        argus.set_log_directory(self.temp_dir)
        argus.log_level(argus.DEBUG)
        
        @argus.log_function_call
        @argus.log_timing
        def test_function(x, y):
            return x + y
        
        @argus.deprecated("This function is deprecated")
        def old_function():
            return "old"
        
        # Call functions
        result = test_function(1, 2)
        
        # Suppress the expected deprecation warning for testing
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            old_result = old_function()

        # Check results
        self.assertEqual(result, 3)
        self.assertEqual(old_result, "old")
        
        # Close the file handler to ensure JSON structure is completed
        close_file_handler()
        
        # Check log file
        log_files = list(Path(self.temp_dir).glob("*.log"))
        self.assertEqual(len(log_files), 1)
        
        with open(log_files[0], 'r') as f:
            content = f.read()
            parsed = json.loads(content)
            
            logs = parsed["logs"]
            messages = [log["message"] for log in logs]
            
            # Check for decorator-generated logs
            self.assertTrue(any("Calling function: test_function" in msg 
                              for msg in messages))
            self.assertTrue(any("Function test_function took" in msg 
                              for msg in messages))
            self.assertTrue(any("DEPRECATED: old_function" in msg 
                              for msg in messages))

    def test_debug_function_registration(self):
        """Test debug function registration and execution."""
        argus.set_log_directory(self.temp_dir)
        argus.log_level(argus.DEBUG)
        
        def debug_func1():
            return {"status": "active", "count": 42}
        
        def debug_func2():
            return "Simple string output"
        
        # Register debug functions
        argus.register_debug_function(debug_func1)
        argus.register_debug_function(debug_func2)
        

        
        # Manually run debug functions (normally done at exit)
        run_debug_functions()
        
        # Check log file
        log_files = list(Path(self.temp_dir).glob("*.log"))
        self.assertEqual(len(log_files), 1)
        
        with open(log_files[0], 'r') as f:
            content = f.read()
            parsed = json.loads(content)
            
            # Check that state entries were added
            state = parsed["state"]
            self.assertEqual(len(state), 2)
            
            # Check state content
            state_messages = state  # State entries are already dictionaries
            # Since debug functions are defined inside the test method, 
            # they are class methods and should return the class name
            self.assertTrue(any("TestIntegration" in entry.get("object", "") 
                              for entry in state_messages))
            self.assertTrue(any("TestIntegration" in entry.get("object", "") 
                              for entry in state_messages))

    def test_log_level_filtering(self):
        """Test log level filtering."""
        argus.set_log_directory(self.temp_dir)
        
        # Set to INFO level
        argus.log_level(argus.INFO)
        
        # Log messages at different levels
        argus.debug("Debug message")  # Should be filtered out
        argus.info("Info message")    # Should be included
        argus.warning("Warning message")  # Should be included
        
        # Close the file handler to ensure JSON structure is completed
        close_file_handler()
        
        # Check log file
        log_files = list(Path(self.temp_dir).glob("*.log"))
        self.assertEqual(len(log_files), 1)
        
        with open(log_files[0], 'r') as f:
            content = f.read()
            parsed = json.loads(content)
            
            logs = parsed["logs"]
            messages = [log["message"] for log in logs]
            
            # Debug should be filtered out
            self.assertNotIn("Debug message", messages)
            # Info and warning should be included
            self.assertIn("Info message", messages)
            self.assertIn("Warning message", messages)

    def test_console_and_file_logging(self):
        """Test that both console and file logging work together."""
        argus.set_log_directory(self.temp_dir)
        argus.log_level(argus.INFO)
        
        # Enable console logging
        argus.enable_console_logging()
        
        # Log a message
        argus.info("Test message", user_id=123)
        
        # Close the file handler to ensure JSON structure is completed
        close_file_handler()
        
        # Check file output
        log_files = list(Path(self.temp_dir).glob("*.log"))
        self.assertEqual(len(log_files), 1)
        
        with open(log_files[0], 'r') as f:
            content = f.read()
            parsed = json.loads(content)
            
            logs = parsed["logs"]
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]["message"], "Test message")
            self.assertIn("extra_data", logs[0])
            self.assertEqual(logs[0]["extra_data"]["user_id"], 123)

    def test_module_metadata(self):
        """Test module metadata and version information."""
        self.assertEqual(argus.__version__, "2.0.0")
        self.assertEqual(argus.__author__, "Michael Knowles")
        self.assertEqual(argus.__description__, "A logging module.")

    def test_public_api_availability(self):
        """Test that all public API functions are available."""
        # Core logging functions
        self.assertTrue(hasattr(argus, 'debug'))
        self.assertTrue(hasattr(argus, 'info'))
        self.assertTrue(hasattr(argus, 'warning'))
        self.assertTrue(hasattr(argus, 'error'))
        self.assertTrue(hasattr(argus, 'critical'))
        
        # Decorators
        self.assertTrue(hasattr(argus, 'log_function_call'))
        self.assertTrue(hasattr(argus, 'log_timing'))
        self.assertTrue(hasattr(argus, 'deprecated'))
        
        # Utility functions
        self.assertTrue(hasattr(argus, 'set_log_directory'))
        self.assertTrue(hasattr(argus, 'register_debug_function'))
        self.assertTrue(hasattr(argus, 'max_logs'))
        self.assertTrue(hasattr(argus, 'log_level'))
        self.assertTrue(hasattr(argus, 'enable_console_logging'))
        self.assertTrue(hasattr(argus, 'disable_console_logging'))
        
        # Advanced usage
        self.assertTrue(hasattr(argus, 'logger'))
        self.assertTrue(hasattr(argus, 'DEBUG'))
        self.assertTrue(hasattr(argus, 'INFO'))
        self.assertTrue(hasattr(argus, 'WARNING'))
        self.assertTrue(hasattr(argus, 'ERROR'))
        self.assertTrue(hasattr(argus, 'CRITICAL'))


if __name__ == '__main__':
    unittest.main()
