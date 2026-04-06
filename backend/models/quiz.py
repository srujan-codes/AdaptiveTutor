"""
QuizQuestion model — SQLAlchemy ORM + Pydantic schemas.
Matches ARCHITECTURE.md QuizQuestion specification.
"""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.connection import Base


class QuizQuestion(Base):
    """SQLAlchemy QuizQuestion model — a single MCQ question."""

    __tablename__ = "quiz_questions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    lesson_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("lesson_contents.id"), nullable=False, index=True
    )
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict] = mapped_column(JSON, nullable=False)  # list of 4 strings
    correct_answer: Mapped[str] = mapped_column(
        String(1), nullable=False
    )  # A, B, C, or D
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    lesson = relationship("LessonContent", back_populates="quiz_questions")

    def __repr__(self) -> str:
        return f"<QuizQuestion(id={self.id}, q={self.question_number})>"


# --- Pydantic Schemas ---


class QuizGenerateRequest(BaseModel):
    """Schema for quiz generation request."""

    lesson_id: str = Field(..., description="ID of the lesson to generate quiz for")


class QuizQuestionResponse(BaseModel):
    """Schema for quiz question returned to client (NO correct answer on generate)."""

    id: str
    lesson_id: str
    question_number: int
    question_text: str
    options: list[str]  # Always exactly 4
    # correct_answer and explanation are OMITTED on generate, included on submit results
    correct_answer: str | None = None
    explanation: str | None = None

    model_config = {"from_attributes": True}


class QuizSubmitRequest(BaseModel):
    """Schema for quiz submission."""

    lesson_id: str = Field(..., description="Lesson ID the quiz belongs to")
    answers: list[str] = Field(
        ...,
        min_length=5,
        max_length=5,
        description='List of 5 answers: ["A", "C", "B", "D", "A"]',
    )


class QuestionResult(BaseModel):
    """Result for a single question after submission."""

    question_number: int
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str


class QuizSubmitResponse(BaseModel):
    """Schema for quiz submission response."""

    score: int  # 0-5
    total: int  # Always 5
    percentage: float
    results: list[QuestionResult]
    new_difficulty: str  # Adjusted difficulty for next session
