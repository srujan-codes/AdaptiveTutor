"""
Content Generator Agent.

Generates a structured lesson given a topic and difficulty level.
Uses the exact system prompt from PROMPTS.md.
"""

import logging
from typing import Any

from agents.base import BaseAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert educational content creator for AdaptiveTutor. Generate a single, comprehensive lesson on a given topic at a specified difficulty level.

DIFFICULTY LEVELS:
- beginner: No prior knowledge assumed. Simple language, analogies, concrete examples. ~400 words.
- intermediate: Basic familiarity assumed. More detail, nuances, related concepts. ~600 words.
- advanced: Strong foundation assumed. Deep theory, edge cases, trade-offs. ~800 words.

OUTPUT FORMAT — valid JSON only:
{
  "title": "Clear, descriptive lesson title",
  "content": "Full lesson in Markdown (use ##, ###, bullets, code blocks, bold/italic). End with a Summary section.",
  "key_concepts": ["concept_1", "concept_2", "concept_3", "concept_4", "concept_5"],
  "estimated_duration_minutes": <integer>
}

RULES:
1. Exactly 5 key concepts. 2. Factually accurate. 3. Match length to difficulty.
4. At least 2 examples/analogies. 5. End with Summary section. 6. No quiz questions.
7. Return ONLY valid JSON — no text outside the JSON."""


class ContentGeneratorAgent(BaseAgent):
    """Generates structured lesson content from a topic and difficulty level."""

    SYSTEM_PROMPT = SYSTEM_PROMPT
    MAX_TOKENS = 2048
    TEMPERATURE = 0.7

    def format_user_message(self, **kwargs: Any) -> str:
        """
        Build the user message for content generation.

        Required kwargs:
            topic (str): The lesson topic.
            difficulty (str): "beginner" | "intermediate" | "advanced"
        """
        topic = kwargs["topic"]
        difficulty = kwargs["difficulty"]
        return (
            f"Generate a lesson on the following topic at the specified difficulty level.\n"
            f"Topic: {topic}\n"
            f"Difficulty: {difficulty}"
        )

    def parse_response(self, data: dict) -> dict:
        """
        Validate the content generator response.

        Ensures:
            - title, content, key_concepts, estimated_duration_minutes exist
            - key_concepts has exactly 5 items
            - estimated_duration_minutes is an integer
        """
        # Validate required fields
        required_fields = ["title", "content", "key_concepts", "estimated_duration_minutes"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Validate key_concepts
        key_concepts = data["key_concepts"]
        if not isinstance(key_concepts, list) or len(key_concepts) != 5:
            logger.warning(
                "Expected 5 key_concepts, got %d. Adjusting.",
                len(key_concepts) if isinstance(key_concepts, list) else 0,
            )
            # Pad or truncate to 5
            if isinstance(key_concepts, list):
                while len(key_concepts) < 5:
                    key_concepts.append(f"Concept {len(key_concepts) + 1}")
                key_concepts = key_concepts[:5]
            else:
                key_concepts = [f"Concept {i}" for i in range(1, 6)]
            data["key_concepts"] = key_concepts

        # Ensure duration is an int
        data["estimated_duration_minutes"] = int(data["estimated_duration_minutes"])

        return data
