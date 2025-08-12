"""
Argus - A diagnostics and logging module.

This package provides a robust logging and diagnostics system with performance 
monitoring capabilities. It offers a flexible and extensible way to track 
application behavior, system metrics, and debug information.

Quick Start:
    >>> import k_diagnostics as diag
    >>> diag.info("Application started")
    >>> diag.debug(f"Memory usage: {diag.Metrics.memory_usage():.2f} MB")
    
    >>> @diag.log_timing
    >>> def my_function():
    ...     pass

Key Features:
- System metrics collection (memory, CPU, thread count, uptime) [requires psutil]
- Flexible logging system with file and console output
- Function call logging and timing decorators
- Debug function registration and execution
- Log rotation and cleanup functionality
"""

from .diagnostics import (
    # Core logging functions
    debug,
    info,
    warning,
    error,
    critical,
    log,
    
    # System metrics
    Metrics,
    
    # Decorators
    log_function_call,
    log_timing,
    deprecated,
    
    # Configuration functions
    log_level,
    max_logs,
    set_log_directory,
    get_log_directory,
    
    # Debug function management
    register_debug_function,
    run_debug_functions,
    
    # Utility functions
    cleanup_logs,
    running_under_unittest,
    current_log_dir,
    
    # Constants and state
    PSUTIL_AVAILABLE
)

# Convenience imports for common use cases
__all__ = [
    # Logging functions
    'debug', 'info', 'warning', 'error', 'critical', 'log',
    
    # Metrics
    'Metrics',
    
    # Decorators
    'log_function_call', 'log_timing', 'deprecated',
    
    # Configuration
    'log_level', 'max_logs', 'set_log_directory', 'get_log_directory',
    
    # Debug management
    'register_debug_function', 'run_debug_functions',
    
    # Utilities
    'cleanup_logs', 'running_under_unittest', 'current_log_dir',
    
    # State
    'PSUTIL_AVAILABLE',
]

# Version information
__version__ = "1.1.0"
__author__ = "Michael Knowles"
__description__ = "A diagnostics and logging module"

# Convenience aliases for common logging levels
import logging
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# Add logging level constants to __all__
__all__.extend(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
