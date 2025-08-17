"""
SC4 Python Framework - Python Logger Integration

This module provides Python logging integration with the C++ logging system,
ensuring all output goes to the same log file and console.
"""

import sys
import logging
from typing import Any, TextIO
from io import StringIO


class SC4PythonHandler(logging.Handler):
    """
    Custom logging handler that forwards Python log messages to the C++ logger.
    """
    
    def __init__(self):
        super().__init__()
        self.setFormatter(logging.Formatter(
            '[Python] [%(name)s] [%(levelname)s] %(message)s'
        ))
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record by forwarding it to the C++ logger.
        """
        try:
            msg = self.format(record)
            # Import here to avoid circular imports
            import sc4_native
            
            # Map Python log levels to appropriate C++ log calls
            # We'll expose these functions from C++ to Python
            if hasattr(sc4_native, 'log_message'):
                level_map = {
                    logging.DEBUG: 0,     # LOG_DEBUG
                    logging.INFO: 1,      # LOG_INFO  
                    logging.WARNING: 2,   # LOG_WARN
                    logging.ERROR: 3,     # LOG_ERROR
                    logging.CRITICAL: 4   # LOG_CRITICAL
                }
                cpp_level = level_map.get(record.levelno, 1)  # Default to INFO
                sc4_native.log_message(msg, cpp_level)
            else:
                # Fallback: just print to stderr if C++ logging not available
                print(msg, file=sys.stderr)
                
        except Exception:
            # If C++ logging fails, fall back to stderr
            print(f"[Python] [FALLBACK] {record.getMessage()}", file=sys.stderr)


class SC4PrintCapture:
    """
    Captures print() calls and redirects them to the C++ logger.
    """
    
    def __init__(self, original_stdout: TextIO):
        self.original_stdout = original_stdout
        self.buffer = StringIO()
    
    def write(self, text: str) -> int:
        """Write text to both buffer and original stdout."""
        if text.strip():  # Only log non-empty strings
            try:
                import sc4_native
                if hasattr(sc4_native, 'log_message'):
                    # Log as INFO level
                    sc4_native.log_message(f"[Python] [print] {text.strip()}", 1)
                else:
                    self.original_stdout.write(f"[Python] [print] {text}")
            except Exception:
                self.original_stdout.write(f"[Python] [print] {text}")
        
        return len(text)
    
    def flush(self) -> None:
        """Flush the buffer."""
        self.buffer.flush()
        if hasattr(self.original_stdout, 'flush'):
            self.original_stdout.flush()


def setup_python_logging() -> None:
    """
    Set up Python logging to integrate with the C++ logging system.
    
    This should be called once during Python initialization.
    """
    # Set up the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add our custom handler
    sc4_handler = SC4PythonHandler()
    root_logger.addHandler(sc4_handler)
    
    # Redirect stdout (print statements) to our capture system
    original_stdout = sys.stdout
    sys.stdout = SC4PrintCapture(original_stdout)
    
    # Log that setup is complete
    logging.getLogger('SC4PythonFramework').info("Python logging integration initialized")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a plugin or module.
    
    Args:
        name: Name of the logger (usually plugin name)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"SC4Plugin.{name}")


# Convenience functions for direct logging
def log_debug(message: str) -> None:
    """Log a debug message."""
    logging.getLogger('SC4PythonFramework').debug(message)

def log_info(message: str) -> None:
    """Log an info message."""
    logging.getLogger('SC4PythonFramework').info(message)

def log_warning(message: str) -> None:
    """Log a warning message."""
    logging.getLogger('SC4PythonFramework').warning(message)

def log_error(message: str) -> None:
    """Log an error message."""
    logging.getLogger('SC4PythonFramework').error(message)

def log_critical(message: str) -> None:
    """Log a critical message."""
    logging.getLogger('SC4PythonFramework').critical(message)