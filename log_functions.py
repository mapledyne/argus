"""Core logging functions for the diagnostics system."""

import atexit
from collections.abc import Callable
from datetime import datetime
from functools import wraps
import json
import logging
import os
from pathlib import Path
import sys
import time
import warnings

from formatters import HumanReadableFormatter, JSONFormatter
from handlers import JSONFileHandler

# region logging functions


def log(level, message, **extra_fields):
    """Internal logging function that handles caller information."""
    caller_info = logger.findCaller(stack_info=False, stacklevel=3)
    full_path = caller_info[0]
    project_root = os.getcwd()
    relative_path = os.path.relpath(full_path, start=project_root)

    extra = {
        "caller_module": relative_path.replace("\\", "/"),
        "caller_func": caller_info[2],
        "caller_lineno": caller_info[1],
    }

    # Add custom extra fields under a single known key
    if extra_fields:
        extra["extra_data"] = extra_fields

    logger._log(level, message, args=(), extra=extra)  # pylint: disable=W0212


def debug(message, **extra_fields):
    """Log a debug message."""
    log(logging.DEBUG, message, **extra_fields)


def info(message, **extra_fields):
    """Log an info message."""
    log(logging.INFO, message, **extra_fields)


def warning(message, **extra_fields):
    """Log a warning message."""
    warning_type = extra_fields.pop('warning_type', None)
    log(logging.WARNING, message, **extra_fields)
    if warning_type:
        warnings.warn(message, warning_type, stacklevel=3)


def error(message, **extra_fields):
    """Log an error message."""
    error_type = extra_fields.pop('error_type', None)
    log(logging.ERROR, message, **extra_fields)
    if error_type:
        raise error_type(message)


def critical(message, **extra_fields):
    """Log a critical message."""
    error_type = extra_fields.pop('error_type', None)
    log(logging.CRITICAL, message, **extra_fields)
    if error_type:
        raise error_type(message)

# endregion logging functions

# region Decorators to auto-log


def log_function_call(func: Callable) -> Callable:
    """Decorator to log function calls with arguments and return values."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        debug(f"Calling function: {func.__name__}")
        debug(f"Arguments: {args}")
        debug(f"Keyword arguments: {kwargs}")
        try:
            result = func(*args, **kwargs)
            debug(f"Function {func.__name__} returned: {result}")
            return result
        except Exception as e:
            error(f"Function {func.__name__} raised an exception: {e}")
            raise
    return wrapper


def log_timing(func: Callable) -> Callable:
    """Decorator to log function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        info(f"Function {func.__name__} took {elapsed_time:.2f} seconds")
        return result
    return wrapper


def deprecated(message: str = "This function is deprecated.") -> Callable:
    """Decorator to mark functions as deprecated."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(f"{func.__name__}: {message}",
                          DeprecationWarning, stacklevel=2)
            warning(f"DEPRECATED: {func.__name__}: {message}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# endregion Decorators

# region logging management


def log_level(val: int) -> None:
    """Set the logging level for the logger and all its handlers."""
    logger.setLevel(val)
    for handler in logger.handlers:
        handler.setLevel(val)
    # Also update the file handler if it exists
    if _file_handler:
        _file_handler.setLevel(val)


def enable_console_logging(display_extra_fields: bool = False) -> None:
    """Enable console logging with human-readable format."""
    # Remove existing console handlers
    disable_console_logging()

    # Add new console handler with the specified formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(HumanReadableFormatter(display_extra_fields))
    logger.addHandler(console_handler)


def disable_console_logging() -> None:
    """Disable console logging."""
    # Copy to avoid modification during iteration
    for handler in logger.handlers[:]:
        if (isinstance(handler, logging.StreamHandler) and
                not isinstance(handler, logging.FileHandler)):
            logger.removeHandler(handler)

# endregion logging management

# region log directory management


def get_log_file() -> str | None:
    """Get the current log file."""
    if not _log_file:
        return None
    return _log_file


def set_log_directory(directory: str | None, prefix: str = "") -> None:
    """Set the log directory and configure file logging."""
    global _file_handler, _log_file  # pylint: disable=global-statement

    if not directory:
        if _file_handler:
            logging.getLogger().removeHandler(_file_handler)
            _file_handler.close()
            _file_handler = None
            info("File logging disabled.")

        _log_file = None
        return
    if not os.path.exists(directory):
        os.makedirs(directory)
    prefix = prefix.strip()
    if prefix:
        prefix = f"{prefix}_"

    _log_file = os.path.join(directory, f"{prefix}{timestamp}.log")
    if _file_handler:
        logger.removeHandler(_file_handler)
        _file_handler.close()

    _file_handler = JSONFileHandler(_log_file, encoding="utf-8")
    _file_handler.setFormatter(JSONFormatter())
    _file_handler.setLevel(logger.level)
    logger.addHandler(_file_handler)

    info(f"File logging enabled. Logs are saved to: {_log_file}")


def _cleanup_logs() -> None:
    """Remove old log files, keeping only max_logs entries."""
    if _max_logs < 1:
        return
    log_dir = os.path.dirname(_log_file)
    log_files = sorted(
        [d for d in Path(log_dir).iterdir() if d.name.endswith(".log")],
        key=lambda d: d.name
    )
    keep_count = len(log_files) - _max_logs
    if keep_count > 0:
        excess_logs = log_files[:keep_count]
        for old_log in excess_logs:
            old_log.unlink()
            info(f"Removed old log file: {old_log}")


def max_logs(val: int) -> None:
    """Set the maximum number of log files to keep."""
    global _max_logs  # pylint: disable=global-statement
    if val < 1:
        _max_logs = -1
        return
    if val == 0:    # keeping 0 logs can cause confusion with the current log
        warning("Can't set max_logs to 0, setting to 1 instead")
        val = 1
    _max_logs = val
    _cleanup_logs()


# endregion log directory management

# region atexit functions to report state on exit

def register_debug_function(func: Callable, log_limit: int = -1) -> None:
    """Register a function to be called at exit for debugging."""

    if log_limit < 0:
        log_limit = logging.DEBUG
    debug_functions.append((func, log_limit))
    debug(f"Registered exit logging function: {func.__name__}")


@atexit.register
def run_debug_functions() -> None:
    """Execute all registered debug functions and log their output."""
    if len(debug_functions) == 0:
        return
    info("Running registered exit logging functions...")
    for func, log_limit in debug_functions:
        if log_limit > logger.level:
            continue
        if "." in func.__qualname__:
            object_name = func.__qualname__.split(".")[0]
        else:
            object_name = func.__name__

        output = func()
        if isinstance(output, str):
            output = {"message": output}
        state_entry = {"object": object_name}
        state_entry.update(output)
        entry = json.dumps(state_entry, ensure_ascii=False)
        if _file_handler:
            _file_handler.state_entries.append(entry)

    # Ensure the handler is properly closed to write the final JSON
    if _file_handler:
        _file_handler.close()


def _diagnostics_state() -> str:
    """Get the current diagnostics state as JSON string."""
    try:
        from __init__ import __version__  # pylint: disable=C0415
    except ImportError:
        __version__ = "unknown"

    diag_state = {
        "log_file": _log_file,
        "max_logs": _max_logs,
        "log_level": logger.level,
        "log_level_name": logging.getLevelName(logger.level),
        "timestamp": timestamp,
        "diagnostics_version": __version__,
    }
    return json.dumps(diag_state, ensure_ascii=False)

# endregion atexit functions

# region Global variables and setup


timestamp: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
_max_logs: int = -1
_log_file: str | None = None
_file_handler: logging.FileHandler | None = None
debug_functions: list[Callable] = []
logger_name: str = "ArgusLogger"


# Configure a dedicated logger for ArgusLogger
logger: logging.Logger = logging.getLogger(logger_name)
logger.setLevel(logging.ERROR)


# Initialize console logging only if not running under unittest
if 'unittest' not in sys.modules:
    enable_console_logging()

logger.propagate = False

# endregion Global variables and setup
