from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        messages: list[dict],
        model: str,
        tools: list[dict] | None = None,
    ) -> str:
        """Generate a response from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            model: The model identifier to use.
            tools: Optional list of tool definitions for function calling.

        Returns:
            The generated text response.
        """
        ...


__all__ = ["BaseLLMProvider"]
