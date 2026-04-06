"""
QuizQuestion model — SQLAlchemy ORM and Pydantic schemas.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.connection import Base


class QuizQuestion(Base):
    """SQLAlchemy model for quiz questions."""
    __tablename__ = "quiz_questions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    lesson_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("lesson_contents.id"), nullable=False, index=True
    )
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    # Store options as JSON string
    options_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    correct_answer: Mapped[str] = mapped_column(String(1), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    lesson = relationship("LessonContent", back_populates="quiz_questions")

    @property
    def options(self) -> list[str]:
        """Deserialize options from JSON string."""
        import json
        try:
            return json.loads(self.options_json)
        except (json.JSONDecodeError, TypeError):
            return []

    @options.setter
    def options(self, value: list[str]) -> None:
        """Serialize options to JSON string."""
        import json
        self.options_json = json.dumps(value)


# ─── Pydantic Schemas ────────────────────────────────────────


class QuizGenerateRequest(BaseModel):
    """Schema for requesting quiz generation."""
    lesson_id: str


class QuizQuestionResponse(BaseModel):
    """Schema for a quiz question (returned to client)."""
    id: str
    lesson_id: str
    question_number: int
    question_text: str
    options: list[str]

    model_config = {"from_attributes": True}


class QuizQuestionFullResponse(BaseModel):
    """Full quiz question including answer and explanation (for results)."""
    id: str
    lesson_id: str
    question_number: int
    question_text: str
    options: list[str]
    correct_answer: str
    explanation: str

    model_config = {"from_attributes": True}


class QuizSubmitRequest(BaseModel):
    """Schema for submitting quiz answers."""
    lesson_id: str
    answers: list[str] = Field(..., min_length=5, max_length=5)


class QuestionResult(BaseModel):
    """Result for a single question after submission."""
    question_number: int
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str


class QuizSubmitResponse(BaseModel):
    """Schema for quiz submission response."""
    score: int
    total: int
    percentage: float
    results: list[QuestionResult]
    new_difficulty: str
