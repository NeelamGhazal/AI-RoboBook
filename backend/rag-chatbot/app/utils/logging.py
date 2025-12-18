"""
Structured logging configuration using structlog.
Provides JSON logging for production and console logging for development.
"""
import logging
import sys
from typing import Any, Dict

import structlog
from structlog.types import EventDict, Processor

from app.config import settings


def add_log_level(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add log level to event dict."""
    event_dict["level"] = method_name.upper()
    return event_dict


def configure_logging() -> None:
    """Configure structured logging based on settings."""

    # Determine processors based on LOG_JSON setting
    if settings.LOG_JSON:
        # Production: JSON format
        processors: list[Processor] = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: Console format
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.dev.ConsoleRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.LOG_LEVEL)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """Get a configured logger instance."""
    return structlog.get_logger(name)


# Configure logging on module import
configure_logging()
logger = get_logger(__name__)
