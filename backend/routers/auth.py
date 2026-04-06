"""
Auth router — POST /auth/register, POST /auth/login, GET /auth/me.

Handles user registration, login, and current user retrieval.
All responses match ARCHITECTURE.md contracts.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from models.user import (
    AuthResponse,
    User,
    UserCreate,
    UserLogin,
    UserResponse,
)
from services.auth_service import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """
    Register a new user account.

    - Creates a new user with a bcrypt-hashed password.
    - Returns the user profile and a JWT access token.
    - Returns 409 if email or username is already taken.
    """
    # Check email uniqueness
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    # Check username uniqueness
    result = await db.execute(select(User).where(User.username == payload.username))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this username already exists.",
        )

    # Validate difficulty value early
    valid_difficulties = {"beginner", "intermediate", "advanced"}

    # Create user
    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        current_difficulty="beginner",
    )
    db.add(user)
    await db.flush()  # Get the auto-generated ID

    # Create JWT token
    token = create_access_token(user.id)

    logger.info("User registered: %s (%s)", user.username, user.email)

    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=token,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login and get access token",
)
async def login(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """
    Authenticate a user and return a JWT access token.

    - Verifies email and password.
    - Returns 401 for invalid credentials.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Create JWT token
    token = create_access_token(user.id)

    logger.info("User logged in: %s", user.username)

    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=token,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Get the current authenticated user's profile.

    Requires a valid Bearer token.
    """
    return UserResponse.model_validate(current_user)
