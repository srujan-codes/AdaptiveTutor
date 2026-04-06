"""
LessonContent model — SQLAlchemy ORM + Pydantic schemas.
Matches ARCHITECTURE.md LessonContent specification.
"""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.connection import Base


class LessonContent(Base):
    """SQLAlchemy LessonContent model — AI-generated lesson."""

    __tablename__ = "lesson_contents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sessions.id"), nullable=False, index=True
    )
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    difficulty: Mapped[str] = mapped_column(
        SAEnum("beginner", "intermediate", "advanced", name="difficulty_level"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    key_concepts: Mapped[dict] = mapped_column(JSON, nullable=False)
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    session = relationship("Session", back_populates="lesson")
    quiz_questions = relationship(
        "QuizQuestion", back_populates="lesson", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<LessonContent(id={self.id}, title={self.title})>"


# --- Pydantic Schemas ---


class LessonGenerateRequest(BaseModel):
    """Schema for lesson generation request."""

    topic: str = Field(..., max_length=200, description="Topic to generate lesson for")
    difficulty: str = Field(
        ..., pattern="^(beginner|intermediate|advanced)$", description="Difficulty level"
    )


class LessonResponse(BaseModel):
    """Schema for lesson data returned to client."""

    id: str
    session_id: str
    topic: str
    difficulty: str
    title: str
    content: str
    key_concepts: list[str]
    estimated_duration_minutes: int
    created_at: datetime

    model_config = {"from_attributes": True}
