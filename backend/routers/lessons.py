"""
Lessons router — POST /lessons/generate, GET /lessons/{lesson_id}
Implements ARCHITECTURE.md Lessons endpoints.
"""

from fastapi import APIRouter

router = APIRouter()


# TODO: [TICKET-012] Implement lesson endpoints
# POST /generate — LessonGenerateRequest → LessonResponse
# GET /{lesson_id} — → LessonResponse | 404
