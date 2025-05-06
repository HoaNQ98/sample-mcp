"""LLM configuration settings."""

import os
from typing import Optional

from pydantic import ConfigDict, Field, BaseModel
from pydantic_settings import BaseSettings


class LLMSettings(BaseSettings):
    """LLM configuration settings."""
    
    # OpenAI settings
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API key",
    )
    OPENAI_ORGANIZATION: Optional[str] = Field(
        default=None,
        description="OpenAI organization ID",
    )
    OPENAI_MODEL: str = Field(
        default="gpt-4o",
        description="OpenAI model to use",
    )
    
    # LLM general settings
    LLM_PROVIDER: str = Field(
        default="openai",
        description="LLM provider to use (openai)",
    )
    LLM_TEMPERATURE: float = Field(
        default=0.7,
        description="Temperature for LLM generation",
    )
    LLM_MAX_TOKENS: Optional[int] = Field(
        default=None,
        description="Maximum tokens for LLM generation",
    )
    
    # MCP client settings
    MCP_BASE_URL: str = Field(
        default="http://localhost:8000",
        description="Base URL for the MCP server",
    )
    MCP_TIMEOUT: float = Field(
        default=30.0,
        description="Timeout for MCP requests in seconds",
    )
    
    class Config:
        """Pydantic config."""
        
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in the environment
    


def get_llm_settings() -> LLMSettings:
    """Get LLM settings.
    
    Returns:
        LLM settings.
    """
    return LLMSettings()
