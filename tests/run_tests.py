#!/usr/bin/env python3
"""Test runner for the argus logging module."""

import sys
import unittest
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import argus
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests import (
    test_log_functions,
    test_decorators,
    test_utils,
    test_formatters,
    test_handlers,
    test_integration
)


def run_all_tests():
    """Run all test suites."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test modules
    test_modules = [
        test_log_functions,
        test_decorators,
        test_utils,
        test_formatters,
        test_handlers,
        test_integration
    ]
    
    for module in test_modules:
        suite.addTests(loader.loadTestsFromModule(module))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_specific_tests(test_names):
    """Run specific test modules or classes."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_name in test_names:
        if test_name == "log_functions":
            suite.addTests(loader.loadTestsFromModule(test_log_functions))
        elif test_name == "decorators":
            suite.addTests(loader.loadTestsFromModule(test_decorators))
        elif test_name == "utils":
            suite.addTests(loader.loadTestsFromModule(test_utils))
        elif test_name == "formatters":
            suite.addTests(loader.loadTestsFromModule(test_formatters))
        elif test_name == "handlers":
            suite.addTests(loader.loadTestsFromModule(test_handlers))
        elif test_name == "integration":
            suite.addTests(loader.loadTestsFromModule(test_integration))
        else:
            print(f"Unknown test module: {test_name}")
            return False
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def main():
    """Main function for running tests."""
    parser = argparse.ArgumentParser(description="Run argus module tests")
    parser.add_argument(
        "--tests",
        nargs="+",
        choices=["log_functions", "decorators", "utils", "formatters", 
                "handlers", "integration"],
        help="Specific test modules to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print("Running argus module tests...")
        print("=" * 50)
    
    if args.tests:
        success = run_specific_tests(args.tests)
    else:
        success = run_all_tests()
    
    if args.verbose:
        print("=" * 50)
        if success:
            print("All tests passed! ✅")
        else:
            print("Some tests failed! ❌")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
