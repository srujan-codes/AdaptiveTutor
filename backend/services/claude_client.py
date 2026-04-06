"""
Claude API Client — async wrapper around the Anthropic Python SDK.
Implementation: TICKET-006
"""

# TODO: [TICKET-006] Implement ClaudeClient
# - Initialize async Anthropic client from env
# - send_message(system_prompt, user_message, max_tokens, temperature) → dict
# - Retry logic: 1 retry, 1s exponential backoff
# - JSON response parsing with validation
# - Custom AIGenerationError exception
# - Never expose raw Anthropic errors


class AIGenerationError(Exception):
    """Raised when Claude API call fails after retry."""

    pass
