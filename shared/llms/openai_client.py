"""OpenAI LLM client implementation."""

import logging
from typing import Any, Dict, List, Optional, Union

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from shared.llms.client import LLMClient

logger = logging.getLogger(__name__)


class OpenAIClient(LLMClient):
    """OpenAI LLM client implementation."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        organization: Optional[str] = None,
    ):
        """Initialize the OpenAI client.
        
        Args:
            api_key: The OpenAI API key.
            model: The model to use.
            organization: Optional organization ID.
        """
        self.client = AsyncOpenAI(
            api_key=api_key,
            organization=organization,
        )
        self.model = model
        logger.info(f"Initialized OpenAI client with model {model}")

    async def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text from a prompt.
        
        Args:
            prompt: The prompt to generate text from.
            system_message: Optional system message to provide context.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.
            
        Returns:
            The generated text.
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        logger.debug(f"Generating text with prompt: {prompt}")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            generated_text = response.choices[0].message.content
            logger.debug(f"Generated text: {generated_text}")
            
            return generated_text
        except Exception as e:
            logger.error(f"Error generating text: {e}", exc_info=True)
            raise

    async def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate text with tool calling capabilities.
        
        Args:
            prompt: The prompt to generate text from.
            tools: The tools available for the model to call.
            system_message: Optional system message to provide context.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.
            
        Returns:
            A dictionary containing the generated text and any tool calls.
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        logger.debug(f"Generating text with tools. Prompt: {prompt}")
        logger.debug(f"Available tools: {tools}")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            message = response.choices[0].message
            
            result = {
                "content": message.content,
                "tool_calls": None,
            }
            
            if message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in message.tool_calls
                ]
                logger.debug(f"Tool calls: {result['tool_calls']}")
            
            return result
        except Exception as e:
            logger.error(f"Error generating text with tools: {e}", exc_info=True)
            raise
