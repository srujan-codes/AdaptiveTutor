"""
Claude API client wrapper (now powered by Groq).

Provides a reusable async wrapper around the Groq Python SDK with:
  - Automatic retry (1 retry, 1s delay)
  - JSON response parsing and validation
  - Structured error handling
"""

import asyncio
import json
import logging
import re

import groq

from config import settings

logger = logging.getLogger(__name__)


class AIGenerationError(Exception):
    """Raised when AI content generation fails after retries."""

    def __init__(self, message: str = "AI generation failed"):
        self.message = message
        super().__init__(self.message)


class ClaudeClient:
    """
    Async wrapper for the Groq API (Class kept named ClaudeClient for backwards compatibility).

    All agent calls must go through this client — no direct API calls elsewhere.
    """

    def __init__(self) -> None:
        """Initialize the async Groq client."""
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is not set — AI features will fail.")
        self._client = groq.AsyncGroq(api_key=settings.GROQ_API_KEY)
        self._model = settings.CLAUDE_MODEL

    async def send_message(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> dict:
        """
        Send a message to Groq and return the parsed JSON response.

        Args:
            system_prompt: The system prompt defining agent behavior.
            user_message: The user message with specific request data.
            max_tokens: Maximum tokens in the response.
            temperature: Sampling temperature (0.0-1.0).

        Returns:
            Parsed JSON dict from the AI's response.

        Raises:
            AIGenerationError: If the API call or JSON parsing fails after retry.
        """
        system_prompt += "\n\nIMPORTANT: You must return ONLY raw, unformatted, single-line JSON. Do NOT include control characters like newlines or tabs."
        last_error: Exception | None = None

        for attempt in range(2):  # Initial attempt + 1 retry
            try:
                if attempt > 0:
                    logger.info("Retrying AI API call (attempt %d)...", attempt + 1)
                    await asyncio.sleep(1)  # 1 second backoff

                response = await self._client.chat.completions.create(
                    model=self._model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                )

                # Extract text content from response
                raw_text = response.choices[0].message.content

                # Parse JSON from the response
                parsed = self._parse_json(raw_text)
                return parsed

            except groq.APIError as e:
                last_error = e
                logger.error(
                    "AI API error (attempt %d): %s", attempt + 1, str(e)
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
        Parse JSON from the AI's response text.

        Handles cases where it wraps JSON in markdown code blocks.

        Args:
            raw_text: Raw text from the response.

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
        # Remove control characters but preserve the JSON structure
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        # Replace literal newlines inside strings with \n escape
        try:
            return json.loads(text)
        except Exception:
            # Last resort: extract JSON object
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', match.group())
                return json.loads(cleaned)
            raise


# ─── Singleton Instance ──────────────────────────────────────

_client_instance: ClaudeClient | None = None


def get_claude_client() -> ClaudeClient:
    """Get or create the singleton ClaudeClient instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = ClaudeClient()
    return _client_instance
