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

# Import core logging functions
from .log_functions import (
    debug, info, warning, error, critical, log, 
    log_function_call, log_timing, deprecated
)

# Import utility functions
from .utils import (
    set_log_directory,
    get_log_directory,
    register_debug_function,
    max_logs,
    log_level,
    enable_console_logging,
    disable_console_logging
)

# Import the logger
from .utils import logger

# Version information
__version__ = "2.0.0"
__author__ = "Michael Knowles"
__description__ = "A logging module."

import logging


# Export all public API
__all__ = [
    # Core logging functions
    'debug', 'info', 'warning', 'error', 'critical', 'log',

    # Decorators
    'log_function_call', 'log_timing', 'deprecated',
    
    # Utility functions
    'set_log_directory', 'get_log_directory', 'register_debug_function',
    'max_logs', 'log_level', 'enable_console_logging',
    'disable_console_logging',
    
    # Advanced usage
    'logger',
    
    # Metadata
    '__version__', '__author__', '__description__'
]

import logging
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# Add logging level constants to __all__
__all__.extend(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
