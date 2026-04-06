"""
AdaptiveTutor — FastAPI Application Entry Point.

Configures CORS, lifespan events (DB table creation),
and mounts all API routers under /api/v1.

Run with: uvicorn backend.main:app --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import get_settings
from backend.database.connection import Base, engine
from backend.routers import auth, lessons, performance, quizzes, strategy
from backend.services.claude_client import AIGenerationError

settings = get_settings()

# ─── Logging ─────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ─── Lifespan ────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.

    Startup: Create all database tables (if they don't exist).
    Shutdown: Dispose of the database engine.
    """
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified.")

    yield

    # Shutdown
    await engine.dispose()
    logger.info("Database engine disposed. Goodbye.")


# ─── App ─────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered adaptive tutoring API with 5 specialized Claude agents.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ─── CORS ────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Global Exception Handlers ───────────────────────────────


@app.exception_handler(AIGenerationError)
async def ai_generation_error_handler(
    request: Request, exc: AIGenerationError
) -> JSONResponse:
    """Handle AI generation failures with structured error response."""
    logger.error("AI Generation Error: %s", exc.message)
    return JSONResponse(
        status_code=500,
        content={
            "error": "AI_GENERATION_FAILED",
            "detail": "AI content generation failed. Please try again later.",
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all handler for unhandled exceptions."""
    logger.error("Unhandled exception: %s", str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "detail": "An internal server error occurred.",
        },
    )


# ─── Routers ─────────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(lessons.router, prefix=API_PREFIX)
app.include_router(quizzes.router, prefix=API_PREFIX)
app.include_router(performance.router, prefix=API_PREFIX)
app.include_router(strategy.router, prefix=API_PREFIX)


# ─── Health Check ─────────────────────────────────────────────


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint for deployment monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint — redirects to docs."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
