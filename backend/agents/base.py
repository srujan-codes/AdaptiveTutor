"""
Base agent abstract class.

All 5 AI agents inherit from BaseAgent, which provides
the shared Claude API call logic via ClaudeClient.
"""

from abc import ABC, abstractmethod
from typing import Any

from backend.services.claude_client import ClaudeClient, get_claude_client


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.

    Subclasses must define:
        - SYSTEM_PROMPT: The system prompt for this agent.
        - MAX_TOKENS: Maximum response tokens.
        - TEMPERATURE: Sampling temperature.
        - format_user_message(**kwargs): Build the user message.
        - parse_response(data): Validate and transform the response.
    """

    SYSTEM_PROMPT: str = ""
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.7

    def __init__(self, client: ClaudeClient | None = None) -> None:
        """Initialize with an optional ClaudeClient (uses singleton if None)."""
        self._client = client or get_claude_client()

    async def run(self, **kwargs: Any) -> dict:
        """
        Execute the agent pipeline: format message → call Claude → parse response.

        Args:
            **kwargs: Agent-specific parameters passed to format_user_message.

        Returns:
            Parsed and validated response dict.
        """
        user_message = self.format_user_message(**kwargs)
        raw_response = await self._client.send_message(
            system_prompt=self.SYSTEM_PROMPT,
            user_message=user_message,
            max_tokens=self.MAX_TOKENS,
            temperature=self.TEMPERATURE,
        )
        return self.parse_response(raw_response)

    @abstractmethod
    def format_user_message(self, **kwargs: Any) -> str:
        """Build the user message from provided kwargs."""
        ...

    @abstractmethod
    def parse_response(self, data: dict) -> dict:
        """Validate and transform the raw Claude response."""
        ...
