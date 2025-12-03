"""
Centralized Logging Configuration

This module provides consistent logging across all MetaMind modules.
Replace print statements with logger calls for better control and debugging.

Usage:
    from logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("Processing dashboard %d", dashboard_id)
    logger.error("Failed to extract: %s", error)
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional


# Default log format - clean and minimal
DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log levels mapping
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Global state
_initialized = False
_log_dir: Optional[Path] = None


def _get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def _get_log_dir() -> Path:
    """Get or create the logs directory."""
    global _log_dir
    if _log_dir is None:
        _log_dir = Path(os.getenv("LOGS_DIR", _get_project_root() / "logs"))
        _log_dir.mkdir(parents=True, exist_ok=True)
    return _log_dir


def setup_logging(
    level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    filename_prefix: str = "metamind"
) -> None:
    """
    Configure logging for the entire application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to write logs to file
        log_to_console: Whether to output logs to console
        filename_prefix: Prefix for log file names
    """
    global _initialized
    
    if _initialized:
        return
    
    # Get log level from environment or parameter
    log_level_str = os.getenv("LOG_LEVEL", level).upper()
    log_level = LOG_LEVELS.get(log_level_str, logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT)
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        log_dir = _get_log_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"{filename_prefix}_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    
    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given module name.
    
    Args:
        name: Module name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    # Ensure logging is initialized
    if not _initialized:
        setup_logging()
    
    return logging.getLogger(name)


class LogContext:
    """
    Context manager for logging with additional context.
    
    Usage:
        with LogContext(logger, "Processing dashboard", dashboard_id=476):
            # ... processing code ...
    """
    
    def __init__(self, logger: logging.Logger, message: str, **context):
        self.logger = logger
        self.message = message
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
        self.logger.info(f"START: {self.message} [{context_str}]")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        elapsed = time.time() - self.start_time
        context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
        
        if exc_type is None:
            self.logger.info(f"DONE: {self.message} [{context_str}] ({elapsed:.2f}s)")
        else:
            self.logger.error(
                f"FAILED: {self.message} [{context_str}] ({elapsed:.2f}s) - {exc_val}"
            )
        
        return False  # Don't suppress exceptions

