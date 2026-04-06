"""
Claude API client wrapper.

Provides a reusable async wrapper around the Anthropic Python SDK with:
  - Automatic retry (1 retry, 1s delay)
  - JSON response parsing and validation
  - Structured error handling (never leaks raw Anthropic errors)
"""

import asyncio
import json
import logging

import anthropic

from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AIGenerationError(Exception):
    """Raised when AI content generation fails after retries."""

    def __init__(self, message: str = "AI generation failed"):
        self.message = message
        super().__init__(self.message)


class ClaudeClient:
    """
    Async wrapper for the Anthropic Claude API.

    All agent calls must go through this client — no direct API calls elsewhere.
    """

    def __init__(self) -> None:
        """Initialize the async Anthropic client."""
        if not settings.ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY is not set — AI features will fail.")
        self._client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self._model = settings.CLAUDE_MODEL

    async def send_message(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> dict:
        """
        Send a message to Claude and return the parsed JSON response.

        Args:
            system_prompt: The system prompt defining agent behavior.
            user_message: The user message with specific request data.
            max_tokens: Maximum tokens in the response.
            temperature: Sampling temperature (0.0-1.0).

        Returns:
            Parsed JSON dict from Claude's response.

        Raises:
            AIGenerationError: If the API call or JSON parsing fails after retry.
        """
        last_error: Exception | None = None

        for attempt in range(2):  # Initial attempt + 1 retry
            try:
                if attempt > 0:
                    logger.info("Retrying Claude API call (attempt %d)...", attempt + 1)
                    await asyncio.sleep(1)  # 1 second backoff

                response = await self._client.messages.create(
                    model=self._model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_message}
                    ],
                )

                # Extract text content from response
                raw_text = response.content[0].text

                # Parse JSON from the response
                parsed = self._parse_json(raw_text)
                return parsed

            except anthropic.APIError as e:
                last_error = e
                logger.error(
                    "Claude API error (attempt %d): %s", attempt + 1, str(e)
                )
            except json.JSONDecodeError as e:
                last_error = e
                logger.error(
                    "JSON parse error (attempt %d): %s", attempt + 1, str(e)
                )
            except Exception as e:
                last_error = e
                logger.error(
                    "Unexpected error (attempt %d): %s", attempt + 1, str(e)
                )

        # Both attempts failed
        logger.error(
            "AI generation failed after 2 attempts. Last error: %s", str(last_error)
        )
        raise AIGenerationError(
            f"AI content generation failed. Please try again later."
        )

    def _parse_json(self, raw_text: str) -> dict:
        """
        Parse JSON from Claude's response text.

        Handles cases where Claude wraps JSON in markdown code blocks.

        Args:
            raw_text: Raw text from Claude's response.

        Returns:
            Parsed JSON dictionary.

        Raises:
            json.JSONDecodeError: If JSON parsing fails.
        """
        text = raw_text.strip()

        # Strip markdown code block wrappers if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()
        return json.loads(text)


# ─── Singleton Instance ──────────────────────────────────────

_client_instance: ClaudeClient | None = None


def get_claude_client() -> ClaudeClient:
    """Get or create the singleton ClaudeClient instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = ClaudeClient()
    return _client_instance
