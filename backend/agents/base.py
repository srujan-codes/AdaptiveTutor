"""
BaseAgent — Abstract base class for all AI agents.
All 5 agents inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """
    Abstract base class for AdaptiveTutor AI agents.

    Each agent must define:
    - SYSTEM_PROMPT: The exact system prompt from PROMPTS.md
    - MAX_TOKENS: Maximum response tokens
    - TEMPERATURE: Response temperature
    - execute(): The main entry point
    """

    SYSTEM_PROMPT: str = ""
    MAX_TOKENS: int = 512
    TEMPERATURE: float = 0.5

    def __init__(self, claude_client):
        """
        Initialize agent with a Claude API client.

        Args:
            claude_client: Instance of ClaudeClient from services/claude_client.py
        """
        self.client = claude_client

    @abstractmethod
    async def execute(self, **kwargs) -> dict[str, Any]:
        """
        Execute the agent's task.

        Returns:
            Parsed JSON response from Claude as a dict.

        Raises:
            AIGenerationError: If Claude API call fails after retry.
        """
        ...

    def _build_user_message(self, **kwargs) -> str:
        """
        Build the user message from template variables.
        Subclasses should override this with their specific template.
        """
        raise NotImplementedError
