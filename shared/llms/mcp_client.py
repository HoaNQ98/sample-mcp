"""MCP client that uses an LLM to call MCP tools."""

import json
import logging
from typing import Any, Dict, List, Optional, Union

import httpx

from shared.llms.client import LLMClient

logger = logging.getLogger(__name__)


class MCPToolClient:
    """Client for calling MCP tools."""

    def __init__(
        self,
        base_url: str,
        llm_client: LLMClient,
        timeout: float = 30.0,
    ):
        """Initialize the MCP tool client.
        
        Args:
            base_url: The base URL of the MCP server.
            llm_client: The LLM client to use.
            timeout: The timeout for HTTP requests in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.llm_client = llm_client
        self.timeout = timeout
        self.http_client = httpx.AsyncClient(timeout=timeout)
        logger.info(f"Initialized MCP tool client with base URL: {base_url}")
        
        # Cache for tool definitions
        self._tools_cache = None
    
    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get the available tools from the MCP server.
        
        Returns:
            A list of tool definitions.
        """
        if self._tools_cache is not None:
            return self._tools_cache
        
        try:
            response = await self.http_client.get(f"{self.base_url}/info")
            response.raise_for_status()
            
            data = response.json()
            
            # Check for tools in different response structures
            if "data" in data and "tools" in data["data"]:
                # Structure: {"data": {"tools": [...]}}
                self._tools_cache = data["data"]["tools"]
                return self._tools_cache
            elif "tools" in data:
                # Structure: {"tools": [...]}
                self._tools_cache = data["tools"]
                return self._tools_cache
            
            logger.warning("No tools found in MCP server response")
            return []
        except Exception as e:
            logger.error(f"Error getting tools: {e}", exc_info=True)
            return []
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Call an MCP tool directly.
        
        Args:
            tool_name: The name of the tool to call.
            arguments: The arguments to pass to the tool.
            
        Returns:
            The tool response.
        """
        try:
            logger.info(f"Calling tool {tool_name} with arguments: {arguments}")
            
            response = await self.http_client.post(
                f"{self.base_url}/mcp/tool/{tool_name}",
                json=arguments,
            )
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Tool response: {result}")
            
            if not result.get("success", False):
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Tool call failed: {error_msg}")
                raise ValueError(f"Tool call failed: {error_msg}")
            
            return result.get("data", {})
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}", exc_info=True)
            raise
    
    async def call_resource(self, uri: str) -> Dict[str, Any]:
        """Call an MCP resource.
        
        Args:
            uri: The URI of the resource to call.
            
        Returns:
            The resource response.
        """
        try:
            logger.info(f"Calling resource {uri}")
            
            # Ensure the URI starts with a slash
            if not uri.startswith("/"):
                uri = f"/{uri}"
            
            response = await self.http_client.get(
                f"{self.base_url}/mcp/resource{uri}",
            )
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Resource response: {result}")
            
            if not result.get("success", False):
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Resource call failed: {error_msg}")
                raise ValueError(f"Resource call failed: {error_msg}")
            
            return result.get("data", {})
        except Exception as e:
            logger.error(f"Error calling resource {uri}: {e}", exc_info=True)
            raise
    
    async def _format_tools_for_llm(self) -> List[Dict[str, Any]]:
        """Format the tools for the LLM.
        
        Returns:
            A list of tool definitions formatted for the LLM.
        """
        tools = await self.get_tools()
        
        llm_tools = []
        for tool in tools:
            llm_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", {}),
                }
            }
            llm_tools.append(llm_tool)
        
        return llm_tools
    
    async def process_with_llm(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Process a prompt with the LLM and call MCP tools as needed.
        
        Args:
            prompt: The prompt to process.
            system_message: Optional system message to provide context.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.
            
        Returns:
            A dictionary containing the LLM response and any tool results.
        """
        # Format the tools for the LLM
        llm_tools = await self._format_tools_for_llm()
        
        if not llm_tools:
            logger.warning("No tools available for the LLM")
            # Fall back to regular text generation if no tools are available
            text = await self.llm_client.generate(
                prompt=prompt,
                system_message=system_message,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return {"response": text, "tool_results": None}
        
        # Generate text with tool calling capabilities
        llm_response = await self.llm_client.generate_with_tools(
            prompt=prompt,
            tools=llm_tools,
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # Process any tool calls
        tool_results = None
        if llm_response.get("tool_calls"):
            tool_results = []
            
            for tool_call in llm_response["tool_calls"]:
                if tool_call["type"] == "function":
                    function = tool_call["function"]
                    tool_name = function["name"]
                    
                    try:
                        # Parse the arguments
                        arguments = json.loads(function["arguments"])
                        
                        # Call the tool
                        result = await self.call_tool(tool_name, arguments)
                        
                        tool_results.append({
                            "tool_name": tool_name,
                            "arguments": arguments,
                            "result": result,
                            "error": None,
                        })
                    except Exception as e:
                        logger.error(f"Error calling tool {tool_name}: {e}", exc_info=True)
                        tool_results.append({
                            "tool_name": tool_name,
                            "arguments": json.loads(function["arguments"]) if function["arguments"] else {},
                            "result": None,
                            "error": str(e),
                        })
        
        return {
            "response": llm_response.get("content"),
            "tool_results": tool_results,
        }
