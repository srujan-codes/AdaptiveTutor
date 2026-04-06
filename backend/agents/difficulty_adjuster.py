"""
Difficulty Adjuster Agent.

Decides whether to increase, maintain, or decrease difficulty
based on quiz performance and history.
Uses the exact system prompt from PROMPTS.md.
"""

import logging
from typing import Any

from agents.base import BaseAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a difficulty calibration engine for AdaptiveTutor. Decide the next difficulty level based on quiz performance and history.

LEVELS (in order): beginner → intermediate → advanced

RULES:
- 5/5: Increase one level (unless advanced). - 4/5 or 3/5: Maintain. - ≤2/5: Decrease one level (unless beginner).
- 3 consecutive 5/5 at same level → always increase. - 3 consecutive ≤2/5 at same level → always decrease.
- Just increased + scored ≤2/5 → revert immediately. - Only change by ONE level at a time.

OUTPUT FORMAT — valid JSON only:
{
  "new_difficulty": "beginner|intermediate|advanced",
  "reasoning": "1-2 sentence encouraging explanation"
}

Return ONLY a valid JSON object, no markdown, no backticks, no newlines inside strings, no explanatory text."""


class DifficultyAdjusterAgent(BaseAgent):
    """Evaluates quiz performance and adjusts difficulty level."""

    SYSTEM_PROMPT = SYSTEM_PROMPT
    MAX_TOKENS = 256
    TEMPERATURE = 0.1

    def format_user_message(self, **kwargs: Any) -> str:
        """
        Build the user message for difficulty adjustment.

        Required kwargs:
            current_difficulty (str): Current difficulty level.
            score (int): Latest quiz score (0-5).
            score_history (list[int]): Recent scores (last 5, most recent first).
            difficulty_history (list[str]): Recent difficulties (last 5, most recent first).
        """
        current_difficulty = kwargs["current_difficulty"]
        score = kwargs["score"]
        score_history = kwargs.get("score_history", [])
        difficulty_history = kwargs.get("difficulty_history", [])

        history_str = ", ".join(str(s) for s in score_history) if score_history else "No previous scores"
        diff_str = ", ".join(difficulty_history) if difficulty_history else "No previous difficulties"

        return (
            f"Evaluate performance and determine next difficulty.\n"
            f"Current difficulty: {current_difficulty}\n"
            f"Latest quiz score: {score}/5\n"
            f"Recent scores (last 5, most recent first): {history_str}\n"
            f"Recent difficulties (last 5, most recent first): {diff_str}"
        )

    def parse_response(self, data: dict) -> dict:
        """
        Validate the difficulty adjuster response.

        Ensures:
            - new_difficulty is a valid level
            - changed is a boolean
            - reason is a string
        """
        valid_levels = {"beginner", "intermediate", "advanced"}

        new_difficulty = data.get("new_difficulty", "").lower().strip()
        if new_difficulty not in valid_levels:
            logger.warning("Invalid new_difficulty '%s', defaulting to current", new_difficulty)
            new_difficulty = data.get("current_difficulty", "beginner").lower().strip()

        reason = data.get("reasoning") or data.get("reason") or "Maintaining current level."

        return {
            "current_difficulty": data.get("current_difficulty", "beginner"),
            "new_difficulty": new_difficulty,
            "changed": bool(data.get("changed", False)),
            "reason": str(reason),
            "reasoning": str(reason),
        }
