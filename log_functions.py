"""Core logging functions for the diagnostics system."""

import logging
import os
import warnings
import time
from utils import logger
from functools import wraps
from typing import Callable


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
        **extra_fields
    }
    logger._log(level, message, args=(), extra=extra)


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


# REGION Decorators to auto-log

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

# END REGION Decorators
