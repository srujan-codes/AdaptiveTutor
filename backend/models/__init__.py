# Models package — re-exports all models and schemas for easy imports
from backend.models.user import User, UserCreate, UserResponse
from backend.models.session import Session, SessionCreate, SessionResponse
from backend.models.lesson import LessonContent, LessonGenerateRequest, LessonResponse
from backend.models.quiz import (
    QuizQuestion,
    QuizGenerateRequest,
    QuizQuestionResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
    QuestionResult,
)
from backend.models.performance import (
    PerformanceRecord,
    PerformanceRecordItem,
    PerformanceResponse,
    PerformanceInsightsResponse,
    StrategyResponse,
)

__all__ = [
    # SQLAlchemy Models
    "User",
    "Session",
    "LessonContent",
    "QuizQuestion",
    "PerformanceRecord",
    # User Schemas
    "UserCreate",
    "UserResponse",
    # Session Schemas
    "SessionCreate",
    "SessionResponse",
    # Lesson Schemas
    "LessonGenerateRequest",
    "LessonResponse",
    # Quiz Schemas
    "QuizGenerateRequest",
    "QuizQuestionResponse",
    "QuizSubmitRequest",
    "QuizSubmitResponse",
    "QuestionResult",
    # Performance Schemas
    "PerformanceRecordItem",
    "PerformanceResponse",
    "PerformanceInsightsResponse",
    "StrategyResponse",
]
