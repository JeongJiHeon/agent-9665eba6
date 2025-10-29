"""Logging utilities."""

import sys
from pathlib import Path
from loguru import logger
from app.config import settings


def setup_logging():
    """Configure application logging."""
    
    # Remove default handler
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )
    
    # File handler
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        settings.LOG_FILE,
        rotation="500 MB",
        retention="10 days",
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        serialize=False,
    )
    
    logger.info("Logging configured successfully")


def get_logger(name: str):
    """
    Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)
