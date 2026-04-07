import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from database.connection import get_db

pytestmark = pytest.mark.asyncio

async def test_register_success(client: AsyncClient, db_session: AsyncSession):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "StrongPassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["username"] == "newuser"

async def test_register_duplicate_email(client: AsyncClient, test_user: dict):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",  # this should conflict with test_user
            "username": "anotheruser",
            "password": "StrongPassword123"
        }
    )
    assert response.status_code == 409
    data = response.json()
    assert "detail" in data

async def test_login_success(client: AsyncClient, test_user: dict):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"

async def test_login_wrong_password(client: AsyncClient, test_user: dict):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword!"
        }
    )
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data

async def test_get_me_success(client: AsyncClient, test_user: dict):
    response = await client.get(
        "/api/v1/auth/me",
        headers=test_user["headers"]
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"

async def test_get_me_fail_without_token(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
