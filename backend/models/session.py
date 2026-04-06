"""
Session model — SQLAlchemy ORM + Pydantic schemas.
Matches ARCHITECTURE.md Session specification.
"""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.connection import Base


class Session(Base):
    """SQLAlchemy Session model — represents a single learning session."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    difficulty: Mapped[str] = mapped_column(
        SAEnum("beginner", "intermediate", "advanced", name="difficulty_level"),
        nullable=False,
    )
    lesson_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("lesson_contents.id"), nullable=True
    )
    quiz_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user = relationship("User", back_populates="sessions")
    lesson = relationship("LessonContent", back_populates="session", uselist=False)
    performance_record = relationship(
        "PerformanceRecord", back_populates="session", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, topic={self.topic})>"


# --- Pydantic Schemas ---


class SessionCreate(BaseModel):
    """Schema for creating a new session."""

    topic: str = Field(..., max_length=200, description="Topic to study")
    difficulty: str = Field(
        ..., pattern="^(beginner|intermediate|advanced)$", description="Difficulty level"
    )


class SessionResponse(BaseModel):
    """Schema for session data returned to client."""

    id: str
    user_id: str
    topic: str
    difficulty: str
    lesson_id: str | None
    quiz_score: int | None
    started_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
