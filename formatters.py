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
        
        # Add any extra fields that were passed, filtering out
        # non-serializable objects
        for key, value in record.__dict__.items():
            if (key not in log_entry and
                    not key.startswith('_') and
                    key != "msg" and
                    self._is_json_serializable(value)):
                log_entry[key] = value
                
        return json.dumps(log_entry, ensure_ascii=False)


class HumanReadableFormatter(logging.Formatter):
    """Human-readable formatter for console output."""
    
    def format(self, record):
        # Format extra fields if present
        extra_fields = []
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info', 'caller_module', 'caller_func', 
                          'caller_lineno', 'taskName'] and not key.startswith('_'):
                extra_fields.append(f"{key}={value}")
        
        extra_str = f" [{', '.join(extra_fields)}]" if extra_fields else ""
        
        return (f"{datetime.fromtimestamp(record.created).strftime('%H:%M:%S')} "
                f"[{record.levelname}] "
                f"{getattr(record, 'caller_module', 'unknown')}.{getattr(record, 'caller_func', 'unknown')}:"
                f"{getattr(record, 'caller_lineno', 0)} - "
                f"{record.getMessage()}{extra_str}")
