"""Utility functions for the diagnostics logging system."""

import atexit
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, List

# Global variables
timestamp: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
_max_logs: int = -1
_log_directory: Optional[str] = None
_file_handler: Optional[logging.FileHandler] = None
debug_functions: List[Callable] = []

# Configure a dedicated logger for DebugManager
logger: logging.Logger = logging.getLogger("DebugManager")
logger.setLevel(logging.ERROR)


def _running_under_unittest() -> bool:
    """Check if the code is being run under a unittest."""
    return 'unittest' in sys.modules


def current_log_dir() -> str:
    """Get the current log directory path."""
    return f"{_log_directory}\\{timestamp}"


def get_log_directory() -> Optional[str]:
    """Get the current log directory."""
    return _log_directory


def set_log_directory(directory: Optional[str]) -> None:
    """Set the log directory and configure file logging."""
    global _file_handler, _log_directory

    if directory is None:
        if _file_handler:
            logging.getLogger().removeHandler(_file_handler)
            _file_handler.close()
            _file_handler = None
            from log_functions import info
            info("File logging disabled.")
        _log_directory = None
        return
    if not os.path.exists(directory):
        os.makedirs(directory)
    _log_directory = directory

    log_file_path = os.path.join(_log_directory, f"{timestamp}.log")
    if _file_handler:
        logger.removeHandler(_file_handler)
        _file_handler.close()

    from handlers import JSONFileHandler
    from formatters import JSONFormatter
    _file_handler = JSONFileHandler(log_file_path, encoding="utf-8")
    _file_handler.setFormatter(JSONFormatter())
    _file_handler.setLevel(logger.level)
    logger.addHandler(_file_handler)

    from log_functions import info
    info(f"File logging enabled. Logs are saved to: {log_file_path}")


def register_debug_function(func: Callable, log_limit: int = logging.DEBUG) -> None:
    """Register a function to be called at exit for debugging."""
    if callable(func):
        debug_functions.append((func, log_limit))
        from log_functions import debug
        debug(f"Registered exit logging function: {func.__name__}")
    else:
        from log_functions import warning
        warning(f"Attempted to register a non-callable object: {func}")


@atexit.register
def run_debug_functions() -> None:
    """Execute all registered debug functions and log their output."""
    if len(debug_functions) == 0:
        return
    from log_functions import info
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
    # structure
    if _file_handler:
        _file_handler.close()


def _diagnostics_state() -> str:
    """Get the current diagnostics state as JSON string."""
    try:
        from __init__ import __version__
    except ImportError:
        __version__ = "unknown"
    
    diag_state = {
        "log_directory": _log_directory,
        "max_logs": _max_logs,
        "log_level": logger.level,
        "log_level_name": logging.getLevelName(logger.level),
        "timestamp": timestamp,
        "diagnostics_version": __version__,
    }
    return json.dumps(diag_state, ensure_ascii=False)


def _cleanup_logs() -> None:
    """Remove old log files, keeping only the latest as specified by max_logs."""
    if _max_logs < 1:
        return
    log_files = sorted(
        [d for d in Path(_log_directory).iterdir() if d.name.endswith(".log")],
        key=lambda d: d.name
    )
    keep_count = len(log_files) - _max_logs
    if keep_count > 0:
        excess_logs = log_files[:keep_count]
        for old_log in excess_logs:
            old_log.unlink()
            from log_functions import info
            info(f"Removed old log file: {old_log}")


def max_logs(val: int) -> None:
    """Set the maximum number of log files to keep."""
    global _max_logs
    if val < 1:
        _max_logs = -1
        return

    _max_logs = val
    _cleanup_logs()


def log_level(val: int) -> None:
    """Set the logging level for the logger and all its handlers."""
    logger.setLevel(val)
    for handler in logger.handlers:
        handler.setLevel(val)


def enable_console_logging() -> None:
    """Enable console logging with human-readable format."""
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            return
    console_handler = logging.StreamHandler()
    from formatters import HumanReadableFormatter
    console_handler.setFormatter(HumanReadableFormatter())
    logger.addHandler(console_handler)


def disable_console_logging() -> None:
    """Disable console logging."""
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            logger.removeHandler(handler)


# Initialize console logging if not running under unittest
if not _running_under_unittest():
    enable_console_logging()
logger.propagate = False
