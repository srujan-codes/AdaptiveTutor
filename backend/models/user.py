"""
User model — SQLAlchemy ORM + Pydantic schemas.
Matches ARCHITECTURE.md User specification.
"""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import String, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.connection import Base


class User(Base):
    """SQLAlchemy User model."""

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
        SAEnum("beginner", "intermediate", "advanced", name="difficulty_level"),
        default="beginner",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    sessions = relationship("Session", back_populates="user", lazy="selectin")
    performance_records = relationship(
        "PerformanceRecord", back_populates="user", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"


# --- Pydantic Schemas ---


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: str = Field(..., max_length=255, description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Display name")
    password: str = Field(..., min_length=8, description="Plaintext password")


class UserResponse(BaseModel):
    """Schema for user data returned to client."""

    id: str
    email: str
    username: str
    current_difficulty: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Schema for login request."""

    email: str
    password: str


class AuthResponse(BaseModel):
    """Schema for auth responses (login/register)."""

    user: UserResponse
    access_token: str
