"""
Lessons router — POST /lessons/generate, GET /lessons/{lesson_id}.

Handles lesson generation via the Content Generator Agent
and retrieval of previously generated lessons.
"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.content_generator import ContentGeneratorAgent
from backend.database.connection import get_db
from backend.models.lesson import LessonContent, LessonGenerateRequest, LessonResponse
from backend.models.session import Session
from backend.models.user import DifficultyLevel, User
from backend.services.auth_service import get_current_user
from backend.services.claude_client import AIGenerationError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/lessons", tags=["Lessons"])


@router.post(
    "/generate",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a new lesson",
)
async def generate_lesson(
    payload: LessonGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LessonResponse:
    """
    Generate a new lesson using the Content Generator Agent.

    Flow:
    1. Validate topic and difficulty.
    2. Create a new Session.
    3. Call Content Generator Agent.
    4. Save LessonContent to DB.
    5. Link lesson to session.
    6. Return LessonResponse.
    """
    # Validate difficulty
    valid_difficulties = {d.value for d in DifficultyLevel}
    if payload.difficulty not in valid_difficulties:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid difficulty. Must be one of: {', '.join(valid_difficulties)}",
        )

    # Validate topic
    topic = payload.topic.strip()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic cannot be empty.",
        )

    # Create session
    session = Session(
        user_id=current_user.id,
        topic=topic,
        difficulty=payload.difficulty,
    )
    db.add(session)
    await db.flush()

    # Call Content Generator Agent
    try:
        agent = ContentGeneratorAgent()
        result = await agent.run(topic=topic, difficulty=payload.difficulty)
    except AIGenerationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI content generation failed. Please try again.",
        )
    except Exception as e:
        logger.error("Unexpected error in content generation: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during lesson generation.",
        )

    # Save lesson
    lesson = LessonContent(
        session_id=session.id,
        topic=topic,
        difficulty=payload.difficulty,
        title=result["title"],
        content=result["content"],
        key_concepts_json=json.dumps(result["key_concepts"]),
        estimated_duration_minutes=result["estimated_duration_minutes"],
    )
    db.add(lesson)
    await db.flush()

    # Link lesson to session
    session.lesson_id = lesson.id

    logger.info(
        "Lesson generated: '%s' for user %s (session %s)",
        lesson.title,
        current_user.username,
        session.id,
    )

    return LessonResponse(
        id=lesson.id,
        session_id=lesson.session_id,
        topic=lesson.topic,
        difficulty=lesson.difficulty,
        title=lesson.title,
        content=lesson.content,
        key_concepts=result["key_concepts"],
        estimated_duration_minutes=lesson.estimated_duration_minutes,
        created_at=lesson.created_at,
    )


@router.get(
    "/{lesson_id}",
    response_model=LessonResponse,
    summary="Get a previously generated lesson",
)
async def get_lesson(
    lesson_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LessonResponse:
    """
    Retrieve a previously generated lesson by ID.

    Returns 404 if the lesson doesn't exist or doesn't belong to the user.
    """
    result = await db.execute(
        select(LessonContent)
        .join(Session, LessonContent.session_id == Session.id)
        .where(
            LessonContent.id == lesson_id,
            Session.user_id == current_user.id,
        )
    )
    lesson = result.scalar_one_or_none()

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found.",
        )

    return LessonResponse(
        id=lesson.id,
        session_id=lesson.session_id,
        topic=lesson.topic,
        difficulty=lesson.difficulty,
        title=lesson.title,
        content=lesson.content,
        key_concepts=lesson.key_concepts,
        estimated_duration_minutes=lesson.estimated_duration_minutes,
        created_at=lesson.created_at,
    )
