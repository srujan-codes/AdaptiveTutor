"""
Strategy Planner Agent.

Recommends what the student should study next based on performance
data and knowledge gaps.
Uses the exact system prompt from PROMPTS.md.
"""

import logging
from typing import Any

from backend.agents.base import BaseAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a learning strategy advisor for AdaptiveTutor. Recommend what the student should study next.

PRINCIPLES: 1. Spaced repetition for weak topics. 2. Fill knowledge gaps (prerequisites first).
3. Progressive learning (build on mastery). 4. Variety to maintain engagement. 5. Confidence building after losing streaks.

OUTPUT FORMAT — valid JSON only:
{
  "recommended_topic": "Specific topic name",
  "reason": "2-3 sentences referencing student data.",
  "suggested_difficulty": "beginner|intermediate|advanced",
  "alternatives": ["Alt 1", "Alt 2", "Alt 3"],
  "study_plan": "2-3 sentence concrete plan."
}

RULES:
1. Only valid JSON. 2. Topic must be specific (not just "Python"). 3. Exactly 3 alternatives.
4. Difficulty matches student level + performance. 5. Concrete study plan.
6. New users → foundational popular topic. 7. Never jump 2 difficulty levels.
8. Suggest branching out if student studies only one subject."""


class StrategyPlannerAgent(BaseAgent):
    """Recommends next study topic based on performance data."""

    SYSTEM_PROMPT = SYSTEM_PROMPT
    MAX_TOKENS = 512
    TEMPERATURE = 0.5

    def format_user_message(self, **kwargs: Any) -> str:
        """
        Build the user message for strategy planning.

        Required kwargs:
            username (str): Student's username.
            current_difficulty (str): Current difficulty level.
            total_sessions (int): Number of completed sessions.
            topic_scores (list[dict]): Topics studied with scores.
            strengths (list[str]): Student's strengths.
            weaknesses (list[str]): Student's weaknesses.
            trend (str): Performance trend.
        """
        username = kwargs["username"]
        current_difficulty = kwargs["current_difficulty"]
        total_sessions = kwargs["total_sessions"]
        topic_scores = kwargs.get("topic_scores", [])
        strengths = kwargs.get("strengths", [])
        weaknesses = kwargs.get("weaknesses", [])
        trend = kwargs.get("trend", "stable")

        topics_str = ""
        for t in topic_scores:
            topics_str += (
                f"{t['topic']} | {t['best_score']}/5 | "
                f"{t['times_studied']} | {t['last_date']}\n"
            )

        if not topics_str:
            topics_str = "No topics studied yet."

        strengths_str = ", ".join(strengths) if strengths else "None identified yet"
        weaknesses_str = ", ".join(weaknesses) if weaknesses else "None identified yet"

        return (
            f"Recommend next topic for this student.\n"
            f"Student: {username} | Level: {current_difficulty} | "
            f"Sessions: {total_sessions}\n"
            f"Topics studied:\n"
            f"{topics_str}"
            f"Format: [topic] | [best_score]/5 | [times_studied] | [last_date]\n"
            f"Insights — Strengths: {strengths_str} | "
            f"Weaknesses: {weaknesses_str} | Trend: {trend}"
        )

    def parse_response(self, data: dict) -> dict:
        """
        Validate the strategy planner response.

        Ensures:
            - recommended_topic is a non-empty string
            - suggested_difficulty is a valid level
            - alternatives has exactly 3 items
            - study_plan is a string
        """
        valid_levels = {"beginner", "intermediate", "advanced"}

        recommended_topic = str(data.get("recommended_topic", "Introduction to Programming"))
        reason = str(data.get("reason", "This is a great foundational topic to start with."))
        suggested_difficulty = str(data.get("suggested_difficulty", "beginner")).lower().strip()
        alternatives = data.get("alternatives", [])
        study_plan = str(data.get("study_plan", "Start with the basics and build up gradually."))

        if suggested_difficulty not in valid_levels:
            logger.warning(
                "Invalid suggested_difficulty '%s', defaulting to 'beginner'",
                suggested_difficulty,
            )
            suggested_difficulty = "beginner"

        # Ensure exactly 3 alternatives
        if isinstance(alternatives, list):
            alternatives = [str(a) for a in alternatives]
            while len(alternatives) < 3:
                alternatives.append(f"Alternative topic {len(alternatives) + 1}")
            alternatives = alternatives[:3]
        else:
            alternatives = [
                "Data Structures",
                "Web Development Basics",
                "Algorithm Design",
            ]

        return {
            "recommended_topic": recommended_topic,
            "reason": reason,
            "suggested_difficulty": suggested_difficulty,
            "alternatives": alternatives,
            "study_plan": study_plan,
        }
