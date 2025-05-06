from functools import lru_cache

from shared.config import BaseSettings, get_base_settings
from shared.config.base_settings import setup_logging


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    APP_NAME: str = "sample-mcp"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Sample MCP server with clean architecture"
    
    # MCP settings
    MCP_ENABLED: bool = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    # Start with base settings
    base_settings = get_base_settings()
    
    # Create service settings
    settings = Settings()
    
    # Update with service-specific settings
    settings_dict = settings.dict()
    for key, value in settings_dict.items():
        if hasattr(base_settings, key):
            setattr(base_settings, key, value)
    
    return base_settings


def setup_app_logging() -> None:
    """Set up application logging."""
    settings = get_settings()
    setup_logging(settings)
