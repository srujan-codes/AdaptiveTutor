"""
Performance router — GET /performance, GET /performance/insights.

Handles performance history retrieval and AI-generated insights.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.performance_analyzer import PerformanceAnalyzerAgent
from database.connection import get_db
from models.performance import (
    PerformanceInsightsResponse,
    PerformanceRecord,
    PerformanceRecordItem,
    PerformanceResponse,
)
from models.user import User
from services.auth_service import get_current_user
from services.claude_client import AIGenerationError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/performance", tags=["Performance"])


@router.get(
    "",
    response_model=PerformanceResponse,
    summary="Get performance history",
)
async def get_performance(
    topic: str | None = Query(None, description="Filter by topic"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PerformanceResponse:
    """
    Get the current user's performance history with summary stats.

    Supports optional topic filtering and pagination via limit.
    """
    # Build query
    query = (
        select(PerformanceRecord)
        .where(PerformanceRecord.user_id == current_user.id)
        .order_by(PerformanceRecord.created_at.desc())
    )
    if topic:
        query = query.where(PerformanceRecord.topic == topic)
    query = query.limit(limit)

    result = await db.execute(query)
    records = result.scalars().all()

    # Calculate summary stats
    total_result = await db.execute(
        select(func.count(PerformanceRecord.id)).where(
            PerformanceRecord.user_id == current_user.id
        )
    )
    total_sessions = total_result.scalar() or 0

    avg_result = await db.execute(
        select(func.avg(PerformanceRecord.score)).where(
            PerformanceRecord.user_id == current_user.id
        )
    )
    average_score = float(avg_result.scalar() or 0.0)

    # Best topic (highest average score with >=2 sessions)
    best_topic = await _get_extreme_topic(db, current_user.id, best=True)
    weakest_topic = await _get_extreme_topic(db, current_user.id, best=False)

    return PerformanceResponse(
        records=[
            PerformanceRecordItem.model_validate(r) for r in records
        ],
        total_sessions=total_sessions,
        average_score=round(average_score, 2),
        best_topic=best_topic,
        weakest_topic=weakest_topic,
    )


@router.get(
    "/insights",
    response_model=PerformanceInsightsResponse,
    summary="Get AI-generated performance insights",
)
async def get_performance_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PerformanceInsightsResponse:
    """
    Get AI-generated performance insights using the Performance Analyzer Agent.

    Requires at least 3 completed sessions.
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
            detail="At least 3 completed sessions are required for insights.",
        )

    # Prepare data for the agent
    total_sessions = len(records)
    average_score = sum(r.score for r in records) / total_sessions

    formatted_records = []
    for r in records:
        date_str = r.created_at.strftime("%Y-%m-%d") if r.created_at else "unknown"
        formatted_records.append({
            "topic": r.topic,
            "difficulty": r.difficulty,
            "score": r.score,
            "date": date_str,
        })

    # Call Performance Analyzer Agent
    try:
        agent = PerformanceAnalyzerAgent()
        insights = await agent.run(
            username=current_user.username,
            total_sessions=total_sessions,
            average_score=average_score,
            performance_records=formatted_records,
        )
    except AIGenerationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI analysis failed. Please try again.",
        )
    except Exception as e:
        logger.error("Performance analysis error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during analysis.",
        )

    return PerformanceInsightsResponse(**insights)


async def _get_extreme_topic(
    db: AsyncSession, user_id: str, best: bool = True
) -> str | None:
    """
    Get the user's best or weakest topic (by average score, min 2 sessions).
    """
    order = func.avg(PerformanceRecord.score).desc() if best else func.avg(PerformanceRecord.score).asc()

    result = await db.execute(
        select(
            PerformanceRecord.topic,
            func.avg(PerformanceRecord.score).label("avg_score"),
        )
        .where(PerformanceRecord.user_id == user_id)
        .group_by(PerformanceRecord.topic)
        .having(func.count(PerformanceRecord.id) >= 2)
        .order_by(order)
        .limit(1)
    )
    row = result.first()
    return row[0] if row else None
