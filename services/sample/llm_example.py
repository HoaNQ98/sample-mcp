"""Example script for using the LLM client with MCP tools."""

import asyncio
import logging
import sys
from typing import Dict, Any

from shared.llms import create_mcp_tool_client
from shared.config import get_llm_settings
from services.sample.config import setup_app_logging

# Set up logging
setup_app_logging()
logger = logging.getLogger(__name__)


async def process_prompt_with_llm(prompt: str) -> Dict[str, Any]:
    """Process a prompt with the LLM and call MCP tools as needed.
    
    Args:
        prompt: The prompt to process.
        
    Returns:
        The LLM response and any tool results.
    """
    settings = get_llm_settings()
    
    # Create the MCP tool client
    mcp_client = await create_mcp_tool_client()
    
    try:
        # Process the prompt with the LLM
        logger.info(f"Processing prompt: {prompt}")
        
        system_message = """You are a helpful assistant that can use tools to help the user.
        You have access to the following tools:
        - get_greeting: Returns a greeting message
        - calculate: Performs a simple calculation
        
        Use these tools when appropriate to help the user.
        """
        
        result = await mcp_client.process_with_llm(
            prompt=prompt,
            system_message=system_message,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
        
        return result
    finally:
        # Close the MCP tool client
        await mcp_client.close()


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python -m services.sample.llm_example <prompt>")
        return
    
    # Get the prompt from the command line arguments
    prompt = " ".join(sys.argv[1:])
    
    try:
        # Process the prompt with the LLM
        result = await process_prompt_with_llm(prompt)
        
        # Print the LLM response
        print("\nLLM Response:")
        print(result["response"])
        
        # Print any tool results
        if result["tool_results"]:
            print("\nTool Results:")
            for tool_result in result["tool_results"]:
                print(f"\nTool: {tool_result['tool_name']}")
                print(f"Arguments: {tool_result['arguments']}")
                if tool_result["error"]:
                    print(f"Error: {tool_result['error']}")
                else:
                    print(f"Result: {tool_result['result']}")
    except Exception as e:
        logger.error(f"Error processing prompt: {e}", exc_info=True)
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
