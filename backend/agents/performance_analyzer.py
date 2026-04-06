"""
Performance Analyzer Agent.

Analyzes score history and provides insights on strengths,
weaknesses, and trends.
Uses the exact system prompt from PROMPTS.md.
"""

import logging
from typing import Any

from agents.base import BaseAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a learning analytics engine for AdaptiveTutor. Analyze a student's performance history and generate actionable insights.

ANALYSIS: 1. Strengths (topics ≥4/5 consistent). 2. Weaknesses (topics ≤2/5 consistent).
3. Trends (improving/stable/declining — weight recent sessions more). 4. Recommendations (2-3 specific, actionable).

OUTPUT FORMAT — valid JSON only:
{
  "strengths": ["topic_1", "topic_2"],
  "weaknesses": ["topic_3"],
  "trends": "improving|stable|declining",
  "overall_score": 85,
  "recommendation": "Specific recommendation."
}

RULES:
1. Only valid JSON. 2. Encouraging, never discouraging. 3. Handle sparse data gracefully.
4. Strengths/weaknesses can be empty. 5. Recommendation must be specific, not generic.
6. For struggling students, focus on foundations.
7. Return ONLY a valid JSON object, no markdown, no backticks, no newlines inside strings, no explanatory text."""


class PerformanceAnalyzerAgent(BaseAgent):
    """Analyzes student performance data and generates insights."""

    SYSTEM_PROMPT = SYSTEM_PROMPT
    MAX_TOKENS = 512
    TEMPERATURE = 0.3

    def format_user_message(self, **kwargs: Any) -> str:
        """
        Build the user message for performance analysis.

        Required kwargs:
            username (str): Student's username.
            total_sessions (int): Number of completed sessions.
            average_score (float): Average quiz score out of 5.
            performance_records (list[dict]): List of records with topic, difficulty, score, date.
        """
        username = kwargs["username"]
        total_sessions = kwargs["total_sessions"]
        average_score = kwargs["average_score"]
        records = kwargs["performance_records"]

        records_str = ""
        for r in records:
            records_str += (
                f"{r['topic']} | {r['difficulty']} | "
                f"{r['score']}/5 | {r['date']}\n"
            )

        if not records_str:
            records_str = "No records available."

        return (
            f"Analyze the following student performance data.\n"
            f"Student: {username} | Sessions: {total_sessions} | "
            f"Avg score: {average_score:.1f}/5\n"
            f"History (most recent first):\n"
            f"{records_str}"
            f"Format: [topic] | [difficulty] | [score]/5 | [date]"
        )

    def parse_response(self, data: dict) -> dict:
        """
        Validate the performance analyzer response.

        Ensures:
            - summary is a non-empty string
            - strengths and weaknesses are lists of strings
            - trends is one of: improving, stable, declining
            - recommendations is a list of strings
        """
        valid_trends = {"improving", "stable", "declining"}

        # Extract values, supporting both older schemas and new ones
        trends = str(data.get("trends", "stable")).lower().strip()
        if trends not in valid_trends:
            logger.warning("Invalid trend '%s', defaulting to 'stable'", trends)
            trends = "stable"

        strengths = data.get("strengths", [])
        weaknesses = data.get("weaknesses", [])
        strengths = [str(s) for s in strengths] if isinstance(strengths, list) else []
        weaknesses = [str(w) for w in weaknesses] if isinstance(weaknesses, list) else []

        overall_score = int(data.get("overall_score", 0))
        recommendation = data.get("recommendation")
        if not recommendation:
            recs = data.get("recommendations", [])
            recommendation = " ".join(recs) if isinstance(recs, list) else str(recs)

        summary = data.get("summary", "Performance data is being analyzed.")

        return {
            "summary": str(summary),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "trends": trends,
            "overall_score": overall_score,
            "recommendation": str(recommendation),
            "recommendations": [str(recommendation)] if recommendation else []
        }
