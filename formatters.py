"""Formatters for the diagnostics logging system."""

import json
import logging
from datetime import datetime


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
        return (f"{timestamp} [{record.levelname}] "
                f"{caller_module}.{caller_func}:{caller_lineno} - "
                f"{record.getMessage()}{extra_str}")
