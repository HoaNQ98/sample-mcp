"""Base LLM client interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class LLMClient(ABC):
    """Base LLM client interface."""

    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
