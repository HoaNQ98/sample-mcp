"""Base settings for all services."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class BaseSettings(BaseModel):
    """Base settings for all services."""
    
    # App settings
    APP_NAME: str = "base-service"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Base service"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_base_settings() -> BaseSettings:
    """Get cached base settings."""
    return BaseSettings()


def setup_logging(settings: BaseSettings = None) -> None:
    """Set up application logging."""
    from shared.logging import setup_logging as setup_app_logging
    
    if settings is None:
        settings = get_base_settings()
    
    # Create logs directory if log file is specified
    if settings.LOG_FILE:
        log_file_path = Path(settings.LOG_FILE)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Set up logging
    setup_app_logging(
        log_level=settings.LOG_LEVEL,
        log_file=settings.LOG_FILE,
        log_format=settings.LOG_FORMAT,
    )
