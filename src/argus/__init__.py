"""Argus - An easy logging module.

Argus makes logging easy and powerful. It provides a clean API for logging with
both console and file output, automatic function call tracking, timing decorators,
and more.

Key Features:

    ```
    • Simple logging: info(), debug(), warning(), error(), critical()
    • File and console output with different formats
    • Automatic caller information (file, function, line number)
    • Decorators for function call logging and timing
    • Custom extra data support with clean structure
    • JSON file output for easy parsing
    • Human-readable console output
    ```

Quick Start:

    >>> import argus
    >>> argus.set_log_directory("logs")  # if you want to log to a file
    >>> argus.max_logs(10)               # if you want to limit the number of logs
    >>> argus.log_level(argus.DEBUG)     # set to level you want to see
    >>> argus.info("Hello, world!")
    >>> argus.info("User action", user_id=123, action="login")

    With a couple of environment variables set, you can set up some defaults
    and make this even easier. Either through the regular environment, or
    .env files if you use [dotenv](https://github.com/theskumar/python-dotenv).
    With those defaults set how you like (see below), you can then just do:

    >>> import argus
    >>> argus.info("Application starting")

Log Messages:
    Logs can include both messages and extra data as named parameters. These
    additional parameterscan also be used with the strings. Both of these
    will result in the same logging message, for example:

    >>> argus.info("User logged in: $user from $ip", user=user_id, ip=ip_address)
    >>> argus.info(f"User logged in: {user_id} from {ip_address}", user=user_id, ip=ip_address)

    This allows debug messages to simply be a string template and stored
    centrally, if useful. From a very slight performance perspective, using
    templates is better since the template is only evaluated if the log level
    would report the message, whereas the f-string is evaluated either way.

Defaults:
    Defaults use environment variables, overriding with a .env file if it
    exists and dotenv is installed.
    ```
    • Log level:
        Environment variable LOG_LEVEL or defaults to ERROR if not set

    • Log directory:
        Environment variable LOG_DIRECTORY or defaults to not logging to file

    • Max logs:
        Environment variable MAX_LOGS or defaults to keeping all logs
    ```

Basic Logging:

    >>> argus.debug("Debug info")
    >>> argus.info("Something happened")
    >>> argus.warning("Be careful!")
    >>> argus.error("Something went wrong")
    >>> argus.critical("System failure!")

With Extra Data:

    >>> argus.info("User logged in", user_id=123, ip="192.168.1.1")

Decorators:

    >>> @argus.log_function_call
    >>> def my_function(x, y):
    ...     return x + y

    >>> @argus.log_timing
    >>> def slow_function():
    ...     time.sleep(1)

File Logging to JSON format:

    >>> argus.set_log_directory("logs")
    >>> argus.max_logs(10)  # Will auto-cleanup old logs
"""

import logging
import os

# =============================================================================
# Core Logging Functions
# =============================================================================

from .log_functions import (
    # Basic logging functions
    debug,
    info,
    warning,
    error,
    critical,
    log,

    # Decorators
    log_function_call,
    log_timing,
    deprecated,

    # Configuration functions
    set_log_directory,
    get_log_file,
    log_level,
    max_logs,

    # Console logging control
    enable_console_logging,
    disable_console_logging,

    # Debug function management
    register_debug_function,
)

# =============================================================================
# Module Metadata
# =============================================================================

# Hide metadata from pydoc since it's not part of the public API
__version__ = "2.3.0"
"""@private"""
__author__ = "Michael Knowles"
"""@private"""
__description__ = "A friendly and comprehensive logging and diagnostics module"
"""@private"""

# =============================================================================
# Logging Level Constants
# =============================================================================

# Standard logging levels for easy reference
DEBUG = logging.DEBUG
"""Logging level constant: Debug - Detailed information for diagnosing problems."""

INFO = logging.INFO
"""Logging level constant: Info - General information about program execution."""

WARNING = logging.WARNING
"""Logging level constant: Warning - Indicates a potential problem or unusual situation."""

ERROR = logging.ERROR
"""Logging level constant: Error - A more serious problem that prevents normal operation."""

CRITICAL = logging.CRITICAL
"""Logging level constant: Critical - A critical error that may prevent the program from running."""

# =============================================================================
# Module level variables
# =============================================================================

_default_log_level = int(os.getenv("LOG_LEVEL", str(logging.ERROR)))
_default_log_directory = os.getenv("LOG_DIRECTORY", None)
_default_max_logs = int(os.getenv("MAX_LOGS", "-1"))

try:
    import dotenv
    # use dotenv_values() instead of load_env() to not override anything the
    # main script might want to do.
    _dotenv_vars = dotenv.dotenv_values()
    if "LOG_LEVEL" in _dotenv_vars:
        _default_log_level = int(_dotenv_vars["LOG_LEVEL"])
    if "LOG_DIRECTORY" in _dotenv_vars:
        _default_log_directory = _dotenv_vars["LOG_DIRECTORY"]
    if "MAX_LOGS" in _dotenv_vars:
        _default_max_logs = int(_dotenv_vars["MAX_LOGS"])
except ImportError:
    pass

logger_name: str = "ArgusLogger"
""" ADVANCED: Logger name if wanting to coordinate with other loggers. """
logger: logging.Logger = logging.getLogger(logger_name)
""" ADVANCED: Useful if needing direct access to the logger. """
logger.setLevel(_default_log_level)
logger.propagate = False

if _default_log_directory:
    set_log_directory(_default_log_directory)
    if _default_max_logs:
        max_logs(_default_max_logs)

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # Core logging functions
    'debug',
    'info',
    'warning',
    'error',
    'critical',
    'log',

    # Decorators
    'log_function_call',
    'log_timing',
    'deprecated',

    # Configuration
    'set_log_directory',
    'get_log_file',
    'log_level',
    'max_logs',

    # Console control
    'enable_console_logging',
    'disable_console_logging',

    # Debug functions
    'register_debug_function',

    # Advanced usage
    'logger',
    'logger_name',

    # Logging levels
    'DEBUG',
    'INFO',
    'WARNING',
    'ERROR',
    'CRITICAL',

    # Module metadata
    '__version__',
    '__author__',
    '__description__'
]
