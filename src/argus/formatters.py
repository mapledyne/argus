"""Formatters for the diagnostics logging system."""

import json
import logging
from datetime import datetime
from enum import Enum


class ANSIColors(Enum):
    """ANSI colors for console output."""
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    LIGHT_YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def _is_json_serializable(self, obj):
        """Check if an object is JSON serializable."""
        try:
            json.dumps(obj)
            return True
        except (TypeError, ValueError):
            return False

    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "caller_module": getattr(record, "caller_module", "unknown"),
            "caller_func": getattr(record, "caller_func", "unknown"),
            "caller_lineno": getattr(record, "caller_lineno", 0),
            "logger": record.name,
        }

        # Add extra_data if present (custom fields passed by user)
        extra_data = getattr(record, "extra_data", None)
        if extra_data and isinstance(extra_data, dict):
            # Filter out non-serializable objects from extra_data
            serializable_extra = {}
            for key, value in extra_data.items():
                if self._is_json_serializable(value):
                    serializable_extra[key] = value
            if serializable_extra:
                log_entry["extra_data"] = serializable_extra

        return json.dumps(log_entry, ensure_ascii=False)


class HumanReadableFormatter(logging.Formatter):
    """Human-readable formatter for console output."""

    def __init__(self, display_extra_fields: bool = False):
        super().__init__()
        self.display_extra_fields = display_extra_fields

    def format(self, record):
        extra_str = ""
        if self.display_extra_fields:
            # Format extra_data if present
            extra_data = getattr(record, "extra_data", None)
            if extra_data and isinstance(extra_data, dict):
                extra_fields = []
                for key, value in extra_data.items():
                    extra_fields.append(f"{key}={value}")
                if extra_fields:
                    extra_str = f" [{', '.join(extra_fields)}]"

        caller_module = getattr(record, 'caller_module', 'unknown')
        caller_func = getattr(record, 'caller_func', 'unknown')
        caller_lineno = getattr(record, 'caller_lineno', 0)

        timestamp = datetime.fromtimestamp(record.created).strftime(
            '%H:%M:%S')
        level_color = ANSIColors.PURPLE.value
        level_name = record.levelname
        match level_name:
            case "DEBUG" | "INFO":
                level_color = ANSIColors.GREEN.value
            case "WARNING":
                level_color = ANSIColors.YELLOW.value
            case "ERROR" | "CRITICAL":
                level_color = ANSIColors.RED.value
        
        return (f"{timestamp} {level_color}[{level_name}]{ANSIColors.END.value} "
                f"{caller_module}.{caller_func}:{caller_lineno} - "
                f"{ANSIColors.BLUE.value}{record.getMessage()}"
                f"{ANSIColors.END.value}{extra_str}")
