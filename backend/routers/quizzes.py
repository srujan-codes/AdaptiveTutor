"""
Quizzes router — POST /quizzes/generate, POST /quizzes/submit.

Handles quiz generation from lesson content and answer submission
with scoring, difficulty adjustment, and performance recording.
"""

import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.difficulty_adjuster import DifficultyAdjusterAgent
from backend.agents.quiz_agent import QuizAgent
from backend.database.connection import get_db
from backend.models.lesson import LessonContent
from backend.models.performance import PerformanceRecord
from backend.models.quiz import (
    QuestionResult,
    QuizGenerateRequest,
    QuizQuestion,
    QuizQuestionResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
)
from backend.models.session import Session
from backend.models.user import User
from backend.services.auth_service import get_current_user
from backend.services.claude_client import AIGenerationError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.post(
    "/generate",
    summary="Generate quiz questions from a lesson",
)
async def generate_quiz(
    payload: QuizGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Generate 5 MCQ questions from a lesson using the Quiz Agent.

    Returns questions WITHOUT correct_answer and explanation (anti-cheat).
    """
    # Find the lesson (with ownership check)
    result = await db.execute(
        select(LessonContent)
        .join(Session, LessonContent.session_id == Session.id)
        .where(
            LessonContent.id == payload.lesson_id,
            Session.user_id == current_user.id,
        )
    )
    lesson = result.scalar_one_or_none()

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found.",
        )

    # Check if quiz already exists for this lesson
    existing = await db.execute(
        select(QuizQuestion).where(QuizQuestion.lesson_id == lesson.id)
    )
    existing_questions = existing.scalars().all()

    if existing_questions:
        # Return existing quiz (without answers)
        return {
            "questions": [
                QuizQuestionResponse(
                    id=q.id,
                    lesson_id=q.lesson_id,
                    question_number=q.question_number,
                    question_text=q.question_text,
                    options=q.options,
                ).model_dump()
                for q in sorted(existing_questions, key=lambda x: x.question_number)
            ]
        }

    # Call Quiz Agent
    try:
        agent = QuizAgent()
        result_data = await agent.run(
            title=lesson.title,
            difficulty=lesson.difficulty,
            key_concepts=lesson.key_concepts,
            content=lesson.content,
        )
    except AIGenerationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI quiz generation failed. Please try again.",
        )
    except Exception as e:
        logger.error("Unexpected error in quiz generation: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during quiz generation.",
        )

    # Save questions to DB
    questions = []
    for q_data in result_data["questions"]:
        question = QuizQuestion(
            lesson_id=lesson.id,
            question_number=q_data["question_number"],
            question_text=q_data["question_text"],
            options_json=json.dumps(q_data["options"]),
            correct_answer=q_data["correct_answer"],
            explanation=q_data["explanation"],
        )
        db.add(question)
        questions.append(question)

    await db.flush()

    logger.info(
        "Quiz generated for lesson '%s' (user: %s)",
        lesson.title,
        current_user.username,
    )

    # Return without correct_answer and explanation
    return {
        "questions": [
            QuizQuestionResponse(
                id=q.id,
                lesson_id=q.lesson_id,
                question_number=q.question_number,
                question_text=q.question_text,
                options=q.options,
            ).model_dump()
            for q in questions
        ]
    }


@router.post(
    "/submit",
    response_model=QuizSubmitResponse,
    summary="Submit quiz answers and get results",
)
async def submit_quiz(
    payload: QuizSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizSubmitResponse:
    """
    Submit quiz answers, get results, and trigger difficulty adjustment.

    Side effects:
    1. Creates a PerformanceRecord.
    2. Calls the Difficulty Adjuster Agent.
    3. Updates User.current_difficulty if changed.
    4. Marks the Session as completed.
    """
    # Validate answers
    if len(payload.answers) != 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exactly 5 answers required.",
        )

    valid_letters = {"A", "B", "C", "D"}
    for i, ans in enumerate(payload.answers):
        if ans.upper() not in valid_letters:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Answer {i+1} must be A, B, C, or D.",
            )

    # Find the lesson (with ownership check)
    result = await db.execute(
        select(LessonContent)
        .join(Session, LessonContent.session_id == Session.id)
        .where(
            LessonContent.id == payload.lesson_id,
            Session.user_id == current_user.id,
        )
    )
    lesson = result.scalar_one_or_none()

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found.",
        )

    # Get quiz questions
    result = await db.execute(
        select(QuizQuestion)
        .where(QuizQuestion.lesson_id == lesson.id)
        .order_by(QuizQuestion.question_number)
    )
    questions = result.scalars().all()

    if len(questions) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No quiz found for this lesson. Generate a quiz first.",
        )

    # Score the quiz
    score = 0
    results = []
    for i, question in enumerate(questions[:5]):
        user_answer = payload.answers[i].upper()
        is_correct = user_answer == question.correct_answer
        if is_correct:
            score += 1

        results.append(
            QuestionResult(
                question_number=question.question_number,
                user_answer=user_answer,
                correct_answer=question.correct_answer,
                is_correct=is_correct,
                explanation=question.explanation,
            )
        )

    # Get the session
    result = await db.execute(
        select(Session).where(Session.id == lesson.session_id)
    )
    session = result.scalar_one_or_none()

    # Calculate time spent
    time_spent = 0
    if session and session.started_at:
        now = datetime.now(timezone.utc)
        # Handle naive datetimes from SQLite
        started = session.started_at
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        time_spent = int((now - started).total_seconds())

    # Call Difficulty Adjuster Agent
    new_difficulty = current_user.current_difficulty
    try:
        # Get recent performance history
        history_result = await db.execute(
            select(PerformanceRecord)
            .where(PerformanceRecord.user_id == current_user.id)
            .order_by(PerformanceRecord.created_at.desc())
            .limit(5)
        )
        recent_records = history_result.scalars().all()

        score_history = [r.score for r in recent_records]
        difficulty_history = [r.difficulty for r in recent_records]

        adjuster = DifficultyAdjusterAgent()
        adjustment = await adjuster.run(
            current_difficulty=current_user.current_difficulty,
            score=score,
            score_history=score_history,
            difficulty_history=difficulty_history,
        )
        new_difficulty = adjustment["new_difficulty"]

    except AIGenerationError:
        logger.warning("Difficulty adjuster failed, maintaining current level.")
    except Exception as e:
        logger.error("Difficulty adjustment error: %s", str(e))

    # Update user difficulty if changed
    if new_difficulty != current_user.current_difficulty:
        current_user.current_difficulty = new_difficulty
        db.add(current_user)

    # Create PerformanceRecord
    perf_record = PerformanceRecord(
        user_id=current_user.id,
        session_id=lesson.session_id,
        topic=lesson.topic,
        difficulty=lesson.difficulty,
        score=score,
        time_spent_seconds=time_spent,
    )
    db.add(perf_record)

    # Mark session as completed
    if session:
        session.quiz_score = score
        session.completed_at = datetime.now(timezone.utc)
        db.add(session)

    await db.flush()

    percentage = (score / 5) * 100

    logger.info(
        "Quiz submitted: user=%s, topic=%s, score=%d/5 (%.0f%%), new_difficulty=%s",
        current_user.username,
        lesson.topic,
        score,
        percentage,
        new_difficulty,
    )

    return QuizSubmitResponse(
        score=score,
        total=5,
        percentage=percentage,
        results=results,
        new_difficulty=new_difficulty,
    )
