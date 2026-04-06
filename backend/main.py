"""
AdaptiveTutor — FastAPI Application Entry Point

Start with: uvicorn backend.main:app --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.database.connection import init_db

# Import routers
from backend.routers import auth, lessons, quizzes, performance, strategy


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup: initialize database tables
    await init_db()
    yield
    # Shutdown: cleanup if needed


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered adaptive tutoring platform",
    lifespan=lifespan,
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Health Check ---
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {"status": "healthy", "version": settings.APP_VERSION}


# --- Register Routers ---
API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])
app.include_router(lessons.router, prefix=f"{API_PREFIX}/lessons", tags=["Lessons"])
app.include_router(quizzes.router, prefix=f"{API_PREFIX}/quizzes", tags=["Quizzes"])
app.include_router(
    performance.router, prefix=f"{API_PREFIX}/performance", tags=["Performance"]
)
app.include_router(
    strategy.router, prefix=f"{API_PREFIX}/strategy", tags=["Strategy"]
)
