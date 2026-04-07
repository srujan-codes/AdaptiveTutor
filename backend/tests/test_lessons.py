import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from models.lesson import LessonContent
from database.connection import get_db

pytestmark = pytest.mark.asyncio

async def test_generate_lesson_success(client: AsyncClient, test_user: dict, mock_claude):
    mock_claude.send_message.return_value = {
        "title": "Introduction to Python",
        "content": "Python is a programming language.",
        "key_concepts": ["Variables", "Loops"],
        "estimated_duration_minutes": 10
    }

    response = await client.post(
        "/api/v1/lessons/generate",
        json={"topic": "Python basics", "difficulty": "beginner"},
        headers=test_user["headers"]
    )
    assert response.status_code == 201
    data = response.json()
    assert data["topic"] == "Python basics"
    assert data["title"] == "Introduction to Python"
    assert data["estimated_duration_minutes"] == 10
    assert "id" in data
    assert "session_id" in data

    mock_claude.send_message.assert_called_once()

async def test_get_lesson_success(client: AsyncClient, test_user: dict, mock_claude):
    mock_claude.send_message.return_value = {
        "title": "Introduction to Python",
        "content": "Python is a programming language.",
        "key_concepts": ["Variables", "Loops"],
        "estimated_duration_minutes": 10
    }

    # First generate a lesson
    gen_response = await client.post(
        "/api/v1/lessons/generate",
        json={"topic": "Python basics", "difficulty": "beginner"},
        headers=test_user["headers"]
    )
    lesson_id = gen_response.json()["id"]

    # Now get it
    get_response = await client.get(
        f"/api/v1/lessons/{lesson_id}",
        headers=test_user["headers"]
    )
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == lesson_id
    assert data["title"] == gen_response.json()["title"]

async def test_get_lesson_not_found(client: AsyncClient, test_user: dict):
    fake_id = str(uuid.uuid4())
    get_response = await client.get(
        f"/api/v1/lessons/{fake_id}",
        headers=test_user["headers"]
    )
    assert get_response.status_code == 404
