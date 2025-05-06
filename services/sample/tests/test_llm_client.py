"""Tests for the LLM client."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from shared.llms.client import LLMClient
from shared.llms.mcp_client import MCPToolClient


class MockLLMClient(LLMClient):
    """Mock LLM client for testing."""
    
    def __init__(self):
        """Initialize the mock LLM client."""
        self.generate = AsyncMock()
        self.generate_with_tools = AsyncMock()


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    return MockLLMClient()


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client."""
    mock_client = MagicMock()
    mock_client.get = AsyncMock()
    mock_client.post = AsyncMock()
    mock_client.aclose = AsyncMock()
    return mock_client


@pytest.mark.asyncio
async def test_mcp_tool_client_process_with_llm_no_tool_calls(mock_llm_client, mock_http_client):
    """Test processing a prompt with the LLM when no tool calls are made."""
    # Arrange
    with patch("httpx.AsyncClient", return_value=mock_http_client):
        mcp_client = MCPToolClient(
            base_url="http://localhost:8000",
            llm_client=mock_llm_client,
        )
        
        # Mock the get_tools method to return some tools
        mcp_client.get_tools = AsyncMock(return_value=[
            {
                "name": "get_greeting",
                "description": "Returns a greeting message",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the person to greet"
                        }
                    },
                    "required": ["name"]
                }
            }
        ])
        
        # Mock the LLM response
        mock_llm_client.generate_with_tools.return_value = {
            "content": "Hello! How can I help you today?",
            "tool_calls": None
        }
        
        # Act
        result = await mcp_client.process_with_llm(
            prompt="Hello",
            system_message="You are a helpful assistant."
        )
        
        # Assert
        assert result["response"] == "Hello! How can I help you today?"
        assert result["tool_results"] is None
        
        # Verify the LLM was called with the correct arguments
        mock_llm_client.generate_with_tools.assert_called_once()
        args, kwargs = mock_llm_client.generate_with_tools.call_args
        assert kwargs["prompt"] == "Hello"
        assert kwargs["system_message"] == "You are a helpful assistant."
        assert len(kwargs["tools"]) == 1
        assert kwargs["tools"][0]["function"]["name"] == "get_greeting"


@pytest.mark.asyncio
async def test_mcp_tool_client_process_with_llm_with_tool_calls(mock_llm_client, mock_http_client):
    """Test processing a prompt with the LLM when tool calls are made."""
    # Arrange
    with patch("httpx.AsyncClient", return_value=mock_http_client):
        mcp_client = MCPToolClient(
            base_url="http://localhost:8000",
            llm_client=mock_llm_client,
        )
        
        # Mock the get_tools method to return some tools
        mcp_client.get_tools = AsyncMock(return_value=[
            {
                "name": "get_greeting",
                "description": "Returns a greeting message",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the person to greet"
                        }
                    },
                    "required": ["name"]
                }
            }
        ])
        
        # Mock the LLM response with a tool call
        mock_llm_client.generate_with_tools.return_value = {
            "content": "I'll get a greeting for you.",
            "tool_calls": [
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "get_greeting",
                        "arguments": json.dumps({"name": "John"})
                    }
                }
            ]
        }
        
        # Mock the call_tool method
        mcp_client.call_tool = AsyncMock(return_value={
            "greeting": "Hello, John! Welcome to the MCP sample service.",
            "timestamp": "2023-05-06T12:34:56.789012"
        })
        
        # Act
        result = await mcp_client.process_with_llm(
            prompt="Get a greeting for John",
            system_message="You are a helpful assistant."
        )
        
        # Assert
        assert result["response"] == "I'll get a greeting for you."
        assert result["tool_results"] is not None
        assert len(result["tool_results"]) == 1
        assert result["tool_results"][0]["tool_name"] == "get_greeting"
        assert result["tool_results"][0]["arguments"] == {"name": "John"}
        assert result["tool_results"][0]["result"]["greeting"] == "Hello, John! Welcome to the MCP sample service."
        
        # Verify the LLM was called with the correct arguments
        mock_llm_client.generate_with_tools.assert_called_once()
        
        # Verify the tool was called with the correct arguments
        mcp_client.call_tool.assert_called_once_with("get_greeting", {"name": "John"})


@pytest.mark.asyncio
async def test_mcp_tool_client_process_with_llm_tool_call_error(mock_llm_client, mock_http_client):
    """Test processing a prompt with the LLM when a tool call fails."""
    # Arrange
    with patch("httpx.AsyncClient", return_value=mock_http_client):
        mcp_client = MCPToolClient(
            base_url="http://localhost:8000",
            llm_client=mock_llm_client,
        )
        
        # Mock the get_tools method to return some tools
        mcp_client.get_tools = AsyncMock(return_value=[
            {
                "name": "get_greeting",
                "description": "Returns a greeting message",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the person to greet"
                        }
                    },
                    "required": ["name"]
                }
            }
        ])
        
        # Mock the LLM response with a tool call
        mock_llm_client.generate_with_tools.return_value = {
            "content": "I'll get a greeting for you.",
            "tool_calls": [
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "get_greeting",
                        "arguments": json.dumps({"name": "John"})
                    }
                }
            ]
        }
        
        # Mock the call_tool method to raise an exception
        mcp_client.call_tool = AsyncMock(side_effect=ValueError("Tool call failed"))
        
        # Act
        result = await mcp_client.process_with_llm(
            prompt="Get a greeting for John",
            system_message="You are a helpful assistant."
        )
        
        # Assert
        assert result["response"] == "I'll get a greeting for you."
        assert result["tool_results"] is not None
        assert len(result["tool_results"]) == 1
        assert result["tool_results"][0]["tool_name"] == "get_greeting"
        assert result["tool_results"][0]["arguments"] == {"name": "John"}
        assert result["tool_results"][0]["result"] is None
        assert result["tool_results"][0]["error"] == "Tool call failed"
        
        # Verify the LLM was called with the correct arguments
        mock_llm_client.generate_with_tools.assert_called_once()
        
        # Verify the tool was called with the correct arguments
        mcp_client.call_tool.assert_called_once_with("get_greeting", {"name": "John"})


@pytest.mark.asyncio
async def test_mcp_tool_client_process_with_llm_no_tools_available(mock_llm_client, mock_http_client):
    """Test processing a prompt with the LLM when no tools are available."""
    # Arrange
    with patch("httpx.AsyncClient", return_value=mock_http_client):
        mcp_client = MCPToolClient(
            base_url="http://localhost:8000",
            llm_client=mock_llm_client,
        )
        
        # Mock the get_tools method to return no tools
        mcp_client.get_tools = AsyncMock(return_value=[])
        
        # Mock the LLM response
        mock_llm_client.generate.return_value = "Hello! How can I help you today?"
        
        # Act
        result = await mcp_client.process_with_llm(
            prompt="Hello",
            system_message="You are a helpful assistant."
        )
        
        # Assert
        assert result["response"] == "Hello! How can I help you today?"
        assert result["tool_results"] is None
        
        # Verify the LLM was called with the correct arguments
        mock_llm_client.generate.assert_called_once_with(
            prompt="Hello",
            system_message="You are a helpful assistant.",
            temperature=0.7,
            max_tokens=None
        )
