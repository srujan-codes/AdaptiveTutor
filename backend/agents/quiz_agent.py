"""
Quiz Agent.

Generates 5 MCQ questions based on lesson content.
Uses the exact system prompt from PROMPTS.md.
"""

import logging
from typing import Any

from agents.base import BaseAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a quiz generation engine for AdaptiveTutor. Create exactly 5 MCQs based on a lesson.

QUESTION MIX: 2 recall/comprehension, 2 application, 1 analysis.
Each question: 4 options (A-D), one correct, plausible distractors, varied correct answer letters.

OUTPUT FORMAT — valid JSON only:
{
  "questions": [
    {
      "question_number": 1,
      "question": "The full question",
      "options": ["A. First", "B. Second", "C. Third", "D. Fourth"],
      "correct_answer": "B",
      "explanation": "Why B is correct and others are wrong."
    }
  ]
}

RULES:
1. Exactly 5 questions. 2. All relate to lesson content. 3. Cover different key concepts.
4. Options prefixed "A. ", "B. ", "C. ", "D. ". 5. correct_answer is just the letter.
6. Explanations are educational. 7. No text outside JSON. 8. Distribute answers across A-D.
9. Return ONLY a valid JSON object, no markdown, no backticks, no newlines inside strings."""


class QuizAgent(BaseAgent):
    """Generates 5 MCQ questions from lesson content."""

    SYSTEM_PROMPT = SYSTEM_PROMPT
    MAX_TOKENS = 2048
    TEMPERATURE = 0.5

    def format_user_message(self, **kwargs: Any) -> str:
        """
        Build the user message for quiz generation.

        Required kwargs:
            title (str): Lesson title.
            difficulty (str): Lesson difficulty.
            key_concepts (list[str]): Key concepts from the lesson.
            content (str): Full lesson content.
        """
        title = kwargs["title"]
        difficulty = kwargs["difficulty"]
        key_concepts = kwargs["key_concepts"]
        content = kwargs["content"]

        concepts_str = ", ".join(key_concepts) if isinstance(key_concepts, list) else key_concepts

        return (
            f"Generate 5 MCQ quiz questions based on the following lesson.\n"
            f"Lesson Title: {title}\n"
            f"Lesson Difficulty: {difficulty}\n"
            f"Key Concepts: {concepts_str}\n"
            f"Lesson Content:\n{content}"
        )

    def parse_response(self, data: dict) -> dict:
        """
        Validate the quiz agent response.

        Ensures:
            - questions list exists with exactly 5 items
            - Each question has required fields
            - Each question has exactly 4 options
            - correct_answer is a single letter A-D
        """
        if "questions" not in data:
            raise ValueError("Missing 'questions' field in response")

        questions = data["questions"]
        if not isinstance(questions, list):
            raise ValueError("'questions' must be a list")

        # Validate we have at least 5 questions (truncate if more)
        if len(questions) < 5:
            raise ValueError(f"Expected 5 questions, got {len(questions)}")
        questions = questions[:5]

        validated = []
        for i, q in enumerate(questions):
            # Validate required fields (allowing question dict mapping)
            question_text = q.get("question") or q.get("question_text")
            if not question_text:
                raise ValueError(f"Question {i+1} missing field: question")
                
            for field in ["options", "correct_answer", "explanation"]:
                if field not in q:
                    raise ValueError(f"Question {i+1} missing field: {field}")

            # Validate options
            options = q["options"]
            if not isinstance(options, list) or len(options) != 4:
                raise ValueError(
                    f"Question {i+1} must have exactly 4 options, got {len(options) if isinstance(options, list) else 'non-list'}"
                )

            # Validate correct_answer
            answer = q["correct_answer"].strip().upper()
            if answer not in ("A", "B", "C", "D"):
                raise ValueError(
                    f"Question {i+1} correct_answer must be A, B, C, or D — got '{answer}'"
                )

            validated.append({
                "question_number": i + 1,
                "question_text": question_text,
                "options": options,
                "correct_answer": answer,
                "explanation": q["explanation"],
            })

        return {"questions": validated}
