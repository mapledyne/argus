"""Core logging functions for the diagnostics system."""

import atexit
import json
import logging
import os
import string
import sys
import time
import warnings
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from pathlib import Path

from .formatters import HumanReadableFormatter, JSONFormatter
from .handlers import JSONFileHandler

# region logging functions


def log(level: int, message: str, **extra_fields) -> None:
    """Basic logging function that handles caller information. Typically
    the other helper fuctions (```debug```, ```info```, etc) are better to use,
    but for custom levels, this function can be used.

    Args:
        level: The logging level of the message.
        message: The message to log.
        **extra_fields: Additional fields to log.

    Returns:
        None

    Example:
        >>> import argus
        >>> argus.log(argus.DEBUG, "This is a debug message")
        >>> argus.log(argus.INFO, "This is an info message")
        >>> argus.log(argus.WARNING, "This is a warning message", user_id=123, ip="192.168.1.1")
    """
    from .__init__ import logger  # pylint: disable=C0415
    if level < logger.level:
        return
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
        message = string.Template(message).safe_substitute(extra_fields)
    logger._log(level, message, args=(), extra=extra)  # pylint: disable=W0212


def debug(message: str, **extra_fields) -> None:
    """Log a debug message.

    Args:
        message: The message to log.
        **extra_fields: Additional fields to log.

    Returns:
        None

    Example:
        >>> import argus
        >>> argus.debug("This is a debug message")
        >>> argus.debug("This is a debug message", user_id=123, ip="192.168.1.1")
    """
    log(logging.DEBUG, message, **extra_fields)


def info(message: str, **extra_fields) -> None:
    """Log an info message.

    Args:
        message: The message to log.
        **extra_fields: Additional fields to log.

    Returns:
        None

    Example:
        >>> import argus
        >>> argus.info("This is an info message")
        >>> argus.info("This is an info message", user_id=123, ip="192.168.1.1")
    """
    log(logging.INFO, message, **extra_fields)


def warning(message: str, **extra_fields) -> None:
    """Log a warning message.

    **Note:**  If warning_type is provided, this message will raise a
    warning of warning_type (see [python warnings](https://docs.python.org/3/library/warnings.html)
    for categories/types) in addition to logging it.

    Args:
        message: The message to log.
        **extra_fields: Additional fields to log.

    Returns:
        None

    Example:
        >>> import argus
        >>> argus.warning("This is a warning message")
        >>> argus.warning("This is a warning message", user_id=123, ip="192.168.1.1")
        >>> argus.warning("This is a warning message", warning_type=SyntaxWarning)
    """
    warning_type = extra_fields.pop('warning_type', None)
    log(logging.WARNING, message, **extra_fields)
    if warning_type:
        warnings.warn(message, warning_type, stacklevel=3)


def error(message: str, **extra_fields) -> None:
    """Log an error message.

    **Note:**  If error_type is provided, this message will raise an exception
    of that type after logging, passing the message as the exception message.

    Args:
        message: The message to log.
        **extra_fields: Additional fields to log.

    Returns:
        None

    Example:
        >>> import argus
        >>> argus.error("This is an error message")
        >>> argus.error("This is an error message", user_id=123, ip="192.168.1.1")
        >>> argus.error("Invalid value", error_type=ValueError)
    """
    error_type = extra_fields.pop('error_type', None)
    log(logging.ERROR, message, **extra_fields)
    if error_type:
        raise error_type(message)


def critical(message: str, **extra_fields) -> None:
    """Log a critical message.

    **Note:**  If error_type is provided, this message will raise an exception
    of that type after logging, passing the message as the exception message.

    Args:
        message: The message to log.
        **extra_fields: Additional fields to log.

    Returns:
        None

    Example:
        >>> import argus
        >>> argus.critical("This is a critical message")
        >>> argus.critical("This is a critical message", user_id=123, ip="192.168.1.1")
        >>> argus.critical("Invalid value", error_type=ValueError)
    """
    error_type = extra_fields.pop('error_type', None)
    log(logging.CRITICAL, message, **extra_fields)
    if error_type:
        raise error_type(message)

# endregion logging functions

# region Decorators to auto-log


def log_function_call(func: Callable) -> Callable:
    """Decorator to log function calls with arguments and return values.

    Args:
        func: The function to log.

    Returns:
        The wrapped function.

    Example:
        >>> import argus
        >>> @argus.log_function_call
        >>> def my_function(a, b):
        >>>     return a + b
        >>> my_function(1, 2)

        This will log something like the following:
        ```
        14:12:28 [DEBUG] main.py.my_function:200 - Calling function: my_function
        14:12:28 [DEBUG] main.py.my_function:200 - Arguments: (1, 2)
        14:12:28 [DEBUG] main.py.my_function:200 - Keyword arguments: {}
        14:12:28 [DEBUG] main.py.my_function:200 - Function my_function returned: 3
        ```
    """
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
    """Decorator to log function execution time.

    Args:
        func: The function to log.

    Returns:
        The wrapped function.

    Example:
        >>> import argus
        >>> @argus.log_timing
        >>> def my_function(a, b):
        >>>     return a + b
        >>> my_function(1, 2)

        This will log something like the following:
        ```
        14:12:28 [DEBUG] main.py.my_function:200 - Function my_function took 0.00 seconds
        ```

        Note: you can combine this with ```log_function_call``` to get a
        complete log of the function call and timing:

        >>> @argus.log_function_call
        >>> @argus.log_timing
        >>> def my_function(a, b):
        >>>     return a + b
    """
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
    """Decorator to mark functions as deprecated. This will log a warning
    as well as raise a DeprecationWarning within the python warnings system.

    Args:
        message: The message to log when the function is deprecated.

    Returns:
        The wrapped function.

    Example:
        >>> import argus
        >>> @argus.deprecated("This function is deprecated. Use new_function instead.")
        >>> def old_function(a, b):
        >>>     return a + b
        >>> old_function(1, 2)
    """
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


def log_level(new_level: int) -> None:
    """Set the logging level for the logger and all its handlers.

    This function sets the minimum logging level for messages that will be processed.
    Messages below this level will be ignored.

    Args:
        new_level: An integer logging level or one of the following constants:

            ```DEBUG (10), INFO (20), WARNING (30), ERROR (40), or CRITICAL (50)```

    Returns:
        None

    Example:
        >>> import argus
        >>> argus.log_level(argus.DEBUG)  # Show all messages
        >>> argus.log_level(argus.ERROR)  # Only show errors and critical messages
    """
    if new_level < 0 or new_level > 100:
        raise ValueError(f"Invalid log level ({new_level}). Must be between 0 and 100.")
    from .__init__ import logger  # pylint: disable=C0415
    logger.setLevel(new_level)
    for handler in logger.handlers:
        handler.setLevel(new_level)
    # Also update the file handler if it exists
    if _file_handler:
        _file_handler.setLevel(new_level)


def enable_console_logging(display_extra_fields: bool = False) -> None:
    """Enable console logging with human-readable format.

    If argus is not running under a unittest, this will default to enabled
    when your script is run (so this call is usually unneeded). Typical use
    is just to import argus and start logging (usually setting a log file
    if you want things saved). If you want to pause and restart logging, this
    and the related ```disable_console_logging``` can be used.

    Args:
        display_extra_fields: Whether to display extra fields in the console
            output. Defaults to False (off).

    Returns:
        None

    Example:
        >>> import argus
        >>> argus.enable_console_logging()  # Console output is now enabled

        This will log something like the following:
        ```
        21:30:01,229 [INFO] main.py.<module>:99 - Application starting...
        21:30:01,230 [DEBUG] argus.register_debug_function:223 - Registered exit logging function: screen_manager_debug
        21:30:01,230 [INFO] screen.py.initialize:61 - Initializing curses screen.
        21:30:01,231 [DEBUG] screen.py.set_color:35 - Setting color: normal, foreground: 7, background: 0
        21:30:01,232 [DEBUG] screen.py.set_color:50 - Setting background color for normal. Updating screen background and attributes.
        21:30:01,233 [INFO] screen.py.initialize:74 - Curses screen initialized with size: (99, 22)
        ```

        Note that the module, function, and line number are all automatically
        included.
   """
    from .__init__ import logger  # pylint: disable=C0415
    # Remove existing console handlers
    disable_console_logging()

    # Add new console handler with the specified formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(HumanReadableFormatter(display_extra_fields))
    logger.addHandler(console_handler)


def disable_console_logging() -> None:
    """Disable console logging.

    Removes all console handlers from the logger and  stops all console
    logging output while preserving file logging if enabled.

    Returns:
        None

    Example:
        >>> import argus
        >>> argus.disable_console_logging()  # Console output is now disabled
    """
    from .__init__ import logger  # pylint: disable=C0415
    # Copy to avoid modification during iteration
    for handler in logger.handlers[:]:
        if (isinstance(handler, logging.StreamHandler) and
                not isinstance(handler, logging.FileHandler)):
            logger.removeHandler(handler)

# endregion logging management

# region log directory management


def get_log_file() -> str | None:
    """Get the current log file.

    Returns:
        The current log file path or None if no log file is set.

    Example:
        >>> import argus
        >>> argus.get_log_file()  # Returns the current log file path
    """
    if not _log_file:
        return None
    return _log_file


def set_log_directory(directory: str | None, prefix: str = "") -> None:
    """Set the log directory and configure file logging.

    Args:
        directory: The directory to log to. If None, file logging is disabled.
        prefix: A prefix to add to the log file name. Defaults to empty string.

    Returns:
        None

    Example:
        >>> import argus
        >>> argus.set_log_directory("logs")  # Logs to logs/YYYY-MM-DD_HH-MM-SS.log
        >>> argus.set_log_directory("logs", "my_app")  # Logs to logs/my_app_YYYY-MM-DD_HH-MM-SS.log
    """
    from .__init__ import logger  # pylint: disable=C0415
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


def max_logs(log_max: int = -1) -> None:
    """Set the maximum number of log files to keep in the log directory.

    Args:
        log_max: Maximum number of log files to retain. Use -1 to keep
            unlimited logs.

    Returns:
        None

    When the number of log files exceeds this limit, the oldest logs are deleted.
    The limit is enforced immediately when set and each time a new log is created.
    """
    global _max_logs  # pylint: disable=global-statement
    if log_max < 1:
        _max_logs = -1
        return
    if log_max == 0:    # keeping 0 logs can cause confusion with the current log
        warning("Can't set max_logs to 0, setting to 1 instead")
        log_max = 1
    _max_logs = log_max
    _cleanup_logs()


# endregion log directory management

# region atexit functions to report state on exit

def register_debug_function(func: Callable, log_limit: int = -1) -> None:
    """Register a function to be called at exit for debugging. This allows
    objects and other resources to report their state at the end of the
    program. In the debug log, this will be shown as a separate "state" list
    in the JSON.

    Callable functions should return a dictionary of key/value pairs of state
    values to be logged, or a string message which will be logged as
    {"message": <string message>}.

    Use log_limit to control if you want this state recorded based on the
    active log level in use at application exit.

    Args:
        func: The function to call at exit.
        log_limit: The logging level to use for the function's output.
            Defaults to DEBUG.

    Returns:
        None

    Example:
        >>> import argus
        >>> def final_state():
        >>>     return {"user": "guest", "ip": "192.168.1.1", "session_id": "1234567890"}
        >>> argus.register_debug_function(final_state)

    """
    if log_limit < 0:
        log_limit = logging.DEBUG
    debug_functions.append((func, log_limit))
    debug(f"Registered exit logging function: {func.__name__}")


@atexit.register
def run_debug_functions() -> None:
    """Execute all registered debug functions and log their output."""
    from .__init__ import logger  # pylint: disable=C0415
    if len(debug_functions) == 0:
        return
    info("Running registered exit logging functions...")
    for func, log_limit in debug_functions:
        if log_limit < logger.level:
            continue
        if "." in func.__qualname__:
            object_name = func.__qualname__.split(".")[0]
        else:
            object_name = func.__name__

        output = func()
        if isinstance(output, str):
            output = {"message": output}
        if not isinstance(output, dict):
            error(f"Debug function {object_name} returned an invalid type: "
                  f"{type(output)}. Function must return a dict or str.")
            continue
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
    from .__init__ import __version__, logger  # pylint: disable=C0415

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


# Initialize console logging only if not running under unittest
if 'unittest' not in sys.modules:
    enable_console_logging()

# endregion Global variables and setup
