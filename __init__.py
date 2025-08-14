"""A comprehensive diagnostics and logging module.

This module provides a logging and diagnostics system.

Key features:
- Flexible logging system with file and console output
- Function call logging and timing decorators
- Debug function registration and execution
- Log rotation and cleanup functionality

The logging system supports both file and console output with customizable log
levels and formats. All logs include detailed caller information (module,
function, line number) for better traceability. Logs to console are human
readable, but the file output is in JSON format.

Example usage:
    >>> import argus as diagnostics
    >>> diagnostics.info("Application started")
    >>> @diagnostics.log_timing
    >>> def my_function():
    ...     pass
"""
import logging

__pdoc__ = {
    '__version__': None,
    '__author__': None,
    '__description__': None
}
# Import core logging functions
from .log_functions import (
    debug, info, warning, error, critical, log,
    log_function_call, log_timing, deprecated,
    set_log_directory,
    get_log_file,
    register_debug_function,
    max_logs,
    log_level,
    enable_console_logging,
    disable_console_logging,
    logger,
    logger_name
)

# Version information

# A weird case where I want to add these variables to __all__ so they can be
# accessed by the logger, but they're not public, as such, and shouldn't be
# included in pydoc. Normally they wouldn't be (the leading _) but because
# they're in __all__, pydoc wants to grab them. The @private is to
# exclude that.
__version__ = "2.0.0"
""" @private """
__author__ = "Michael Knowles"
""" @private """
__description__ = "A logging module."
""" @private """

# Export all public API
__all__ = [
    # Core logging functions
    'debug', 'info', 'warning', 'error', 'critical', 'log',

    # Decorators
    'log_function_call', 'log_timing', 'deprecated',

    # Utility functions
    'set_log_directory', 'get_log_file', 'register_debug_function',
    'max_logs', 'log_level', 'enable_console_logging',
    'disable_console_logging',

    # Advanced usage
    'logger', 'logger_name',

    # Metadata
    '__version__', '__author__', '__description__'
]

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# Add logging level constants to __all__
__all__.extend(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
