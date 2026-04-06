"""
Session model — SQLAlchemy ORM and Pydantic schemas.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.connection import Base


class Session(Base):
    """SQLAlchemy model for learning sessions."""
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    lesson_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("lesson_contents.id"), nullable=True
    )
    quiz_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    lesson = relationship(
        "LessonContent",
        back_populates="session",
        uselist=False,
        foreign_keys="[LessonContent.session_id]",
    )
    performance_record = relationship(
        "PerformanceRecord", back_populates="session", uselist=False
    )


# ─── Pydantic Schemas ────────────────────────────────────────


class SessionCreate(BaseModel):
    """Schema for creating a new session."""
    topic: str = Field(..., max_length=200)
    difficulty: str  # "beginner" | "intermediate" | "advanced"


class SessionResponse(BaseModel):
    """Schema for session response."""
    id: str
    user_id: str
    topic: str
    difficulty: str
    lesson_id: str | None
    quiz_score: int | None
    started_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
