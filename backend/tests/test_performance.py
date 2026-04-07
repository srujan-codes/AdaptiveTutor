import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from models.performance import PerformanceRecord
from models.session import Session
import uuid

pytestmark = pytest.mark.asyncio

async def seed_performance_records(db_session: AsyncSession, test_user: dict):
    # Create a couple of sessions and performance records
    for i in range(3):
        session = Session(
            id=str(uuid.uuid4()),
            user_id=test_user["id"],
            topic=f"Topic {i}",
            difficulty="beginner",
            quiz_score=i + 2  # scores: 2, 3, 4
        )
        db_session.add(session)
        
        record = PerformanceRecord(
            id=str(uuid.uuid4()),
            user_id=test_user["id"],
            session_id=session.id,
            topic=f"Topic {i}",
            difficulty="beginner",
            score=i + 2,
            time_spent_seconds=120
        )
        db_session.add(record)
    await db_session.commit()

async def test_get_performance(client: AsyncClient, test_user: dict, db_session: AsyncSession):
    await seed_performance_records(db_session, test_user)

    response = await client.get("/api/v1/performance", headers=test_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert len(data["records"]) == 3
    assert data["total_sessions"] == 3
    # Average score: (2+3+4)/3 = 3.0
    assert data["average_score"] == 3.0

async def test_get_performance_insights(client: AsyncClient, test_user: dict, db_session: AsyncSession, mock_claude):
    await seed_performance_records(db_session, test_user)

    mock_claude.send_message.return_value = {
        "summary": "Good progress",
        "strengths": ["Topic 2"],
        "weaknesses": ["Topic 0"],
        "trends": "improving",
        "recommendations": ["Keep it up"]
    }

    response = await client.get("/api/v1/performance/insights", headers=test_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Good progress"
    assert data["trends"] == "improving"

async def test_get_strategy_next_topic(client: AsyncClient, test_user: dict, db_session: AsyncSession, mock_claude):
    await seed_performance_records(db_session, test_user)

    mock_claude.send_message.return_value = {
        "recommended_topic": "Topic 4",
        "reason": "Good next step",
        "suggested_difficulty": "intermediate",
        "alternatives": ["Topic 5", "Topic 6"],
        "study_plan": "Read first then practice."
    }

    response = await client.get("/api/v1/strategy/next-topic", headers=test_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["recommended_topic"] == "Topic 4"
    assert data["suggested_difficulty"] == "intermediate"
