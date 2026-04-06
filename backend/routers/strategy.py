"""
Strategy router — GET /strategy/next-topic.

Recommends the next topic using the Strategy Planner Agent.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.performance_analyzer import PerformanceAnalyzerAgent
from agents.strategy_planner import StrategyPlannerAgent
from database.connection import get_db
from models.performance import PerformanceRecord, StrategyResponse
from models.user import User
from services.auth_service import get_current_user
from services.claude_client import AIGenerationError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/strategy", tags=["Strategy"])


@router.get(
    "/next-topic",
    response_model=StrategyResponse,
    summary="Get AI-recommended next topic",
)
async def get_next_topic(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StrategyResponse:
    """
    Get AI-recommended next topic using the Strategy Planner Agent.

    Requires at least 3 completed sessions for data-driven recommendations.
    """
    # Get all performance records
    result = await db.execute(
        select(PerformanceRecord)
        .where(PerformanceRecord.user_id == current_user.id)
        .order_by(PerformanceRecord.created_at.desc())
    )
    records = result.scalars().all()

    if len(records) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 3 completed sessions are required for strategy recommendations.",
        )

    total_sessions = len(records)
    average_score = sum(r.score for r in records) / total_sessions

    # Aggregate topic-level stats
    topic_result = await db.execute(
        select(
            PerformanceRecord.topic,
            func.max(PerformanceRecord.score).label("best_score"),
            func.count(PerformanceRecord.id).label("times_studied"),
            func.max(PerformanceRecord.created_at).label("last_date"),
        )
        .where(PerformanceRecord.user_id == current_user.id)
        .group_by(PerformanceRecord.topic)
    )
    topic_rows = topic_result.all()

    topic_scores = []
    for row in topic_rows:
        last_date = row.last_date.strftime("%Y-%m-%d") if row.last_date else "unknown"
        topic_scores.append({
            "topic": row.topic,
            "best_score": row.best_score,
            "times_studied": row.times_studied,
            "last_date": last_date,
        })

    # Get performance insights first (strengths, weaknesses, trend)
    strengths = []
    weaknesses = []
    trend = "stable"

    try:
        formatted_records = []
        for r in records:
            date_str = r.created_at.strftime("%Y-%m-%d") if r.created_at else "unknown"
            formatted_records.append({
                "topic": r.topic,
                "difficulty": r.difficulty,
                "score": r.score,
                "date": date_str,
            })

        analyzer = PerformanceAnalyzerAgent()
        insights = await analyzer.run(
            username=current_user.username,
            total_sessions=total_sessions,
            average_score=average_score,
            performance_records=formatted_records,
        )
        strengths = insights.get("strengths", [])
        weaknesses = insights.get("weaknesses", [])
        trend = insights.get("trends", "stable")
    except Exception as e:
        logger.warning("Performance analysis failed for strategy, using defaults: %s", str(e))

    # Call Strategy Planner Agent
    try:
        planner = StrategyPlannerAgent()
        strategy = await planner.run(
            username=current_user.username,
            current_difficulty=current_user.current_difficulty,
            total_sessions=total_sessions,
            topic_scores=topic_scores,
            strengths=strengths,
            weaknesses=weaknesses,
            trend=trend,
        )
    except AIGenerationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI strategy planning failed. Please try again.",
        )
    except Exception as e:
        logger.error("Strategy planning error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during strategy planning.",
        )

    return StrategyResponse(**strategy)
