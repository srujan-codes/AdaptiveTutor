"""
PerformanceRecord model — SQLAlchemy ORM and Pydantic schemas.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.connection import Base


class PerformanceRecord(Base):
    """SQLAlchemy model for tracking user quiz performance."""
    __tablename__ = "performance_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sessions.id"), nullable=False, index=True
    )
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="performance_records")
    session = relationship("Session", back_populates="performance_record")


# ─── Pydantic Schemas ────────────────────────────────────────


class PerformanceRecordItem(BaseModel):
    """Schema for a single performance record."""
    id: str
    topic: str
    difficulty: str
    score: int
    time_spent_seconds: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PerformanceResponse(BaseModel):
    """Schema for overall performance summary."""
    records: list[PerformanceRecordItem]
    total_sessions: int
    average_score: float
    best_topic: str | None
    weakest_topic: str | None


class PerformanceInsightsResponse(BaseModel):
    """Schema for AI-generated performance insights."""
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    trends: str
    recommendations: list[str]


class StrategyResponse(BaseModel):
    """Schema for AI-generated next-topic recommendation."""
    recommended_topic: str
    reason: str
    suggested_difficulty: str
    alternatives: list[str]
    study_plan: str
