"""
Logging configuration for MCP Server
"""

import logging
import structlog
from pathlib import Path
from typing import Optional

from .settings import settings


def setup_logging(
    log_level: str = settings.log_level,
    log_format: str = settings.log_format,
    log_file: Optional[str] = settings.log_file
) -> None:
    """
    Set up structured logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Logging format ('json' or 'text')
        log_file: Optional log file path
    """
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if log_format == "json" else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",
        handlers=_create_handlers(log_file, log_format)
    )
    
    # Set log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def _create_handlers(log_file: Optional[str], log_format: str) -> list:
    """Create logging handlers"""
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    handlers.append(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        handlers.append(file_handler)
    
    return handlers


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a logger instance"""
    return structlog.get_logger(name)