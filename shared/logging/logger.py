"""Logging module for the application."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Set up logging configuration.

    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file (if None, logs to console only)
        log_format: The format of the log messages
        max_bytes: Maximum size of the log file before rotation
        backup_count: Number of backup files to keep
    """
    # Convert log level string to logging level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add file handler if log_file is specified
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Add rotating file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: The name of the logger

    Returns:
        A logger instance
    """
    return logging.getLogger(name)
