"""Factory for creating LLM clients."""

import logging
from typing import Optional

from shared.config import get_llm_settings
from shared.llms.client import LLMClient
from shared.llms.openai_client import OpenAIClient
from shared.llms.mcp_client import MCPToolClient

logger = logging.getLogger(__name__)


async def create_llm_client() -> LLMClient:
    """Create an LLM client based on the configuration.
    
    Returns:
        An LLM client.
    """
    settings = get_llm_settings()
    
    if settings.LLM_PROVIDER.lower() == "openai":
        logger.info(f"Creating OpenAI client with model {settings.OPENAI_MODEL}")
        return OpenAIClient(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            organization=settings.OPENAI_ORGANIZATION,
        )
    else:
        logger.warning(f"Unknown LLM provider: {settings.LLM_PROVIDER}, falling back to OpenAI")
        return OpenAIClient(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            organization=settings.OPENAI_ORGANIZATION,
        )


async def create_mcp_tool_client(
    base_url: Optional[str] = None,
    timeout: Optional[float] = None,
) -> MCPToolClient:
    """Create an MCP tool client.
    
    Args:
        base_url: Optional base URL for the MCP server. If not provided, the value from the configuration will be used.
        timeout: Optional timeout for HTTP requests in seconds. If not provided, the value from the configuration will be used.
        
    Returns:
        An MCP tool client.
    """
    settings = get_llm_settings()
    
    # Create the LLM client
    llm_client = await create_llm_client()
    
    # Use provided values or fall back to configuration
    base_url = base_url or settings.MCP_BASE_URL
    timeout = timeout or settings.MCP_TIMEOUT
    
    logger.info(f"Creating MCP tool client with base URL: {base_url}")
    return MCPToolClient(
        base_url=base_url,
        llm_client=llm_client,
        timeout=timeout,
    )
