"""Models package — re-exports all SQLAlchemy models and Pydantic schemas."""

from backend.models.lesson import LessonContent, LessonGenerateRequest, LessonResponse
from backend.models.performance import (
    PerformanceInsightsResponse,
    PerformanceRecord,
    PerformanceRecordItem,
    PerformanceResponse,
    StrategyResponse,
)
from backend.models.quiz import (
    QuestionResult,
    QuizGenerateRequest,
    QuizQuestion,
    QuizQuestionFullResponse,
    QuizQuestionResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
)
from backend.models.session import Session, SessionCreate, SessionResponse
from backend.models.user import (
    AuthResponse,
    DifficultyLevel,
    User,
    UserCreate,
    UserLogin,
    UserResponse,
)

__all__ = [
    # ORM Models
    "User",
    "Session",
    "LessonContent",
    "QuizQuestion",
    "PerformanceRecord",
    # User schemas
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "AuthResponse",
    "DifficultyLevel",
    # Session schemas
    "SessionCreate",
    "SessionResponse",
    # Lesson schemas
    "LessonGenerateRequest",
    "LessonResponse",
    # Quiz schemas
    "QuizGenerateRequest",
    "QuizQuestionResponse",
    "QuizQuestionFullResponse",
    "QuizSubmitRequest",
    "QuizSubmitResponse",
    "QuestionResult",
    # Performance schemas
    "PerformanceRecordItem",
    "PerformanceResponse",
    "PerformanceInsightsResponse",
    "StrategyResponse",
]
