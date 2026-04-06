"""
LessonContent model — SQLAlchemy ORM and Pydantic schemas.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


class LessonContent(Base):
    """SQLAlchemy model for AI-generated lesson content."""
    __tablename__ = "lesson_contents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sessions.id"), nullable=False, index=True
    )
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # Store key_concepts as JSON string (comma-separated for SQLite compat)
    key_concepts_json: Mapped[str] = mapped_column(
        Text, nullable=False, default="[]"
    )
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    session = relationship(
        "Session",
        back_populates="lesson",
        foreign_keys=[session_id],
    )
    quiz_questions = relationship(
        "QuizQuestion", back_populates="lesson", lazy="selectin"
    )

    @property
    def key_concepts(self) -> list[str]:
        """Deserialize key_concepts from JSON string."""
        import json
        try:
            return json.loads(self.key_concepts_json)
        except (json.JSONDecodeError, TypeError):
            return []

    @key_concepts.setter
    def key_concepts(self, value: list[str]) -> None:
        """Serialize key_concepts to JSON string."""
        import json
        self.key_concepts_json = json.dumps(value)


# ─── Pydantic Schemas ────────────────────────────────────────


class LessonGenerateRequest(BaseModel):
    """Schema for requesting a new lesson."""
    topic: str = Field(..., max_length=200)
    difficulty: str  # "beginner" | "intermediate" | "advanced"


class LessonResponse(BaseModel):
    """Schema for lesson response."""
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
