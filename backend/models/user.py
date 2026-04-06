"""
User model — SQLAlchemy ORM and Pydantic schemas.
"""

import enum
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.connection import Base


class DifficultyLevel(str, enum.Enum):
    """Enumeration of difficulty levels."""
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class User(Base):
    """SQLAlchemy model for users."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    current_difficulty: Mapped[str] = mapped_column(
        String(20), default=DifficultyLevel.beginner.value, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    sessions = relationship("Session", back_populates="user", lazy="selectin")
    performance_records = relationship(
        "PerformanceRecord", back_populates="user", lazy="selectin"
    )


# ─── Pydantic Schemas ────────────────────────────────────────


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: str = Field(..., max_length=255)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: str
    password: str


class UserResponse(BaseModel):
    """Schema for user response (no password)."""
    id: str
    email: str
    username: str
    current_difficulty: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Schema for auth responses (register + login)."""
    user: UserResponse
    access_token: str
