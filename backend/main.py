import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database.connection import engine, Base

# Import the 5 specific domain routers directly
from routers import auth, lessons, quizzes, performance, strategy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On startup trigger the SQLAlchemy database builds via the Base schema map.
    Dispose engines efficiently on termination.
    """
    logger.info("Initializing database schema...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
    
    yield
    
    logger.info("Shutting down database connection mapping.")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://adaptive-tutor-ashy.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception occurred at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": "An unexpected error occurred."}
    )

# Include the routers exactly as mapped out by the individual APIRouter definitions
# The individual routers already contain their own namespace prefixes (e.g. `/auth`)
API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(lessons.router, prefix=API_PREFIX)
app.include_router(quizzes.router, prefix=API_PREFIX)
app.include_router(performance.router, prefix=API_PREFIX)
app.include_router(strategy.router, prefix=API_PREFIX)

@app.get("/health", tags=["health"])
async def health_check():
    """Simple ping-pong healthcheck."""
    return {"status": "ok", "app": settings.APP_NAME}
