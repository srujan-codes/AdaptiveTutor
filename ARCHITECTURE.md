# AdaptiveTutor — Architecture & Technical Design

> Single source of truth for API contracts, data models, and system design.
> All agents must implement to these exact specifications.

---

## Table of Contents

1. [Folder Structure](#folder-structure)
2. [Data Models](#data-models)
3. [API Endpoints](#api-endpoints)
4. [AI Agent Flow](#ai-agent-flow)
5. [Authentication](#authentication)
6. [Error Handling](#error-handling)

---

## Folder Structure

```
AdaptiveTutor/
├── backend/
│   ├── main.py                      # FastAPI app, CORS, lifespan
│   ├── config.py                    # Settings via pydantic-settings
│   ├── requirements.txt
│   ├── .env.example
│   ├── models/
│   │   ├── __init__.py              # Re-exports all models
│   │   ├── user.py                  # User SQLAlchemy + Pydantic
│   │   ├── session.py               # Session SQLAlchemy + Pydantic
│   │   ├── lesson.py                # LessonContent SQLAlchemy + Pydantic
│   │   ├── quiz.py                  # QuizQuestion SQLAlchemy + Pydantic
│   │   └── performance.py           # PerformanceRecord SQLAlchemy + Pydantic
│   ├── routers/
│   │   ├── auth.py                  # POST /auth/register, /auth/login
│   │   ├── lessons.py               # POST /lessons/generate, GET /lessons/{id}
│   │   ├── quizzes.py               # POST /quizzes/generate, POST /quizzes/submit
│   │   ├── performance.py           # GET /performance, GET /performance/insights
│   │   └── strategy.py              # GET /strategy/next-topic
│   ├── agents/
│   │   ├── base.py                  # BaseAgent abstract class
│   │   ├── content_generator.py     # ContentGeneratorAgent
│   │   ├── quiz_agent.py            # QuizAgent
│   │   ├── difficulty_adjuster.py   # DifficultyAdjusterAgent
│   │   ├── performance_analyzer.py  # PerformanceAnalyzerAgent
│   │   └── strategy_planner.py      # StrategyPlannerAgent
│   ├── services/
│   │   ├── claude_client.py         # Anthropic SDK wrapper
│   │   └── auth_service.py          # JWT create/verify
│   ├── database/
│   │   ├── connection.py            # Engine, SessionLocal, Base
│   │   └── migrations/              # Alembic
│   └── tests/
│       ├── conftest.py              # Fixtures: test client, test DB, mock Claude
│       ├── test_auth.py
│       ├── test_lessons.py
│       ├── test_quizzes.py
│       ├── test_performance.py
│       └── test_agents.py
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── vercel.json
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx
    │   ├── index.css
    │   ├── api/client.js
    │   ├── components/
    │   ├── pages/
    │   ├── hooks/
    │   └── context/
    └── tests/
```

---

## Data Models

### User

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| `id` | UUID | PK, auto-generated | Unique user identifier |
| `email` | string | Unique, indexed, max 255 | User's email address |
| `username` | string | Unique, indexed, max 50 | Display name |
| `hashed_password` | string | — | Bcrypt-hashed password |
| `current_difficulty` | enum | `beginner` / `intermediate` / `advanced`, default `beginner` | Current learning level |
| `created_at` | datetime | auto, UTC | Account creation timestamp |
| `updated_at` | datetime | auto, UTC | Last update timestamp |

```python
# Pydantic Schemas
class UserCreate(BaseModel):
    email: str
    username: str
    password: str  # plaintext, hashed before storage

class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    current_difficulty: str
    created_at: datetime
```

---

### Session

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| `id` | UUID | PK, auto-generated | Session identifier |
| `user_id` | UUID | FK → User.id | Owner of this session |
| `topic` | string | max 200 | Topic being studied |
| `difficulty` | enum | `beginner` / `intermediate` / `advanced` | Difficulty for this session |
| `lesson_id` | UUID | FK → LessonContent.id, nullable | Generated lesson |
| `quiz_score` | integer | nullable, 0-5 | Score on the quiz (out of 5) |
| `started_at` | datetime | auto, UTC | Session start |
| `completed_at` | datetime | nullable, UTC | Session completion |

```python
class SessionCreate(BaseModel):
    topic: str
    difficulty: str  # "beginner" | "intermediate" | "advanced"

class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    topic: str
    difficulty: str
    lesson_id: UUID | None
    quiz_score: int | None
    started_at: datetime
    completed_at: datetime | None
```

---

### LessonContent

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| `id` | UUID | PK, auto-generated | Lesson identifier |
| `session_id` | UUID | FK → Session.id | Parent session |
| `topic` | string | max 200 | Lesson topic |
| `difficulty` | enum | `beginner` / `intermediate` / `advanced` | Lesson difficulty |
| `title` | string | max 300 | AI-generated lesson title |
| `content` | text | — | Full lesson content (Markdown) |
| `key_concepts` | JSON | list of strings | Key concepts covered |
| `estimated_duration_minutes` | integer | — | Estimated reading time |
| `created_at` | datetime | auto, UTC | Generation timestamp |

```python
class LessonGenerateRequest(BaseModel):
    topic: str
    difficulty: str  # "beginner" | "intermediate" | "advanced"

class LessonResponse(BaseModel):
    id: UUID
    session_id: UUID
    topic: str
    difficulty: str
    title: str
    content: str
    key_concepts: list[str]
    estimated_duration_minutes: int
    created_at: datetime
```

---

### QuizQuestion

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| `id` | UUID | PK, auto-generated | Question identifier |
| `lesson_id` | UUID | FK → LessonContent.id | Parent lesson |
| `question_number` | integer | 1-5 | Order in quiz |
| `question_text` | string | — | The question |
| `options` | JSON | list of 4 strings | Answer choices (A-D) |
| `correct_answer` | string | A / B / C / D | The correct option |
| `explanation` | string | — | Why the answer is correct |
| `created_at` | datetime | auto, UTC | Generation timestamp |

```python
class QuizGenerateRequest(BaseModel):
    lesson_id: UUID

class QuizQuestionResponse(BaseModel):
    id: UUID
    lesson_id: UUID
    question_number: int
    question_text: str
    options: list[str]  # Always exactly 4 options
    correct_answer: str  # "A" | "B" | "C" | "D"
    explanation: str

class QuizSubmitRequest(BaseModel):
    lesson_id: UUID
    answers: list[str]  # List of 5 answers: ["A", "C", "B", "D", "A"]

class QuizSubmitResponse(BaseModel):
    score: int  # 0-5
    total: int  # Always 5
    percentage: float
    results: list[QuestionResult]
    new_difficulty: str  # Adjusted difficulty for next session

class QuestionResult(BaseModel):
    question_number: int
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str
```

---

### PerformanceRecord

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| `id` | UUID | PK, auto-generated | Record identifier |
| `user_id` | UUID | FK → User.id | Owner |
| `session_id` | UUID | FK → Session.id | Related session |
| `topic` | string | max 200 | Topic studied |
| `difficulty` | enum | `beginner` / `intermediate` / `advanced` | Difficulty level |
| `score` | integer | 0-5 | Quiz score |
| `time_spent_seconds` | integer | — | Time from session start to quiz submit |
| `created_at` | datetime | auto, UTC | Record timestamp |

```python
class PerformanceResponse(BaseModel):
    records: list[PerformanceRecordItem]
    total_sessions: int
    average_score: float
    best_topic: str | None
    weakest_topic: str | None

class PerformanceRecordItem(BaseModel):
    id: UUID
    topic: str
    difficulty: str
    score: int
    time_spent_seconds: int
    created_at: datetime

class PerformanceInsightsResponse(BaseModel):
    summary: str             # AI-generated natural language summary
    strengths: list[str]     # Topics the user excels at
    weaknesses: list[str]    # Topics needing improvement
    trends: str              # "improving" | "stable" | "declining"
    recommendations: list[str]  # Actionable suggestions
```

---

## API Endpoints

Base URL: `/api/v1`

### Authentication — `/api/v1/auth`

#### `POST /auth/register`
Register a new user.

| | Detail |
|---|--------|
| **Auth** | None |
| **Request** | `UserCreate` |
| **Response** | `{ "user": UserResponse, "access_token": string }` |
| **Errors** | `400` email/username taken, `422` validation error |

#### `POST /auth/login`
Authenticate and receive a JWT.

| | Detail |
|---|--------|
| **Auth** | None |
| **Request** | `{ "email": string, "password": string }` |
| **Response** | `{ "user": UserResponse, "access_token": string }` |
| **Errors** | `401` invalid credentials |

#### `GET /auth/me`
Get current user profile.

| | Detail |
|---|--------|
| **Auth** | Bearer token |
| **Response** | `UserResponse` |
| **Errors** | `401` invalid/expired token |

---

### Lessons — `/api/v1/lessons`

#### `POST /lessons/generate`
Generate a new lesson using the Content Generator Agent.

| | Detail |
|---|--------|
| **Auth** | Bearer token |
| **Request** | `LessonGenerateRequest` |
| **Response** | `LessonResponse` |
| **Errors** | `400` invalid topic/difficulty, `401` unauthorized, `500` AI generation failure |

#### `GET /lessons/{lesson_id}`
Retrieve a previously generated lesson.

| | Detail |
|---|--------|
| **Auth** | Bearer token |
| **Response** | `LessonResponse` |
| **Errors** | `401` unauthorized, `404` not found |

---

### Quizzes — `/api/v1/quizzes`

#### `POST /quizzes/generate`
Generate 5 MCQ questions from a lesson using the Quiz Agent.

| | Detail |
|---|--------|
| **Auth** | Bearer token |
| **Request** | `QuizGenerateRequest` |
| **Response** | `{ "questions": list[QuizQuestionResponse] }` (without `correct_answer` and `explanation`) |
| **Errors** | `400` invalid lesson_id, `401` unauthorized, `404` lesson not found, `500` AI failure |

> **Note:** The response for `POST /quizzes/generate` intentionally omits `correct_answer` and `explanation` to prevent cheating. These are only revealed after submission.

#### `POST /quizzes/submit`
Submit quiz answers, get results, and trigger difficulty adjustment.

| | Detail |
|---|--------|
| **Auth** | Bearer token |
| **Request** | `QuizSubmitRequest` |
| **Response** | `QuizSubmitResponse` |
| **Errors** | `400` invalid answers format, `401` unauthorized, `404` lesson not found |

**Side effects:**
1. Creates a `PerformanceRecord`.
2. Calls the Difficulty Adjuster Agent.
3. Updates `User.current_difficulty` if changed.
4. Marks the `Session` as completed.

---

### Performance — `/api/v1/performance`

#### `GET /performance`
Get the user's performance history.

| | Detail |
|---|--------|
| **Auth** | Bearer token |
| **Query Params** | `topic` (optional), `limit` (default 20, max 100) |
| **Response** | `PerformanceResponse` |
| **Errors** | `401` unauthorized |

#### `GET /performance/insights`
Get AI-generated performance insights using the Performance Analyzer Agent.

| | Detail |
|---|--------|
| **Auth** | Bearer token |
| **Response** | `PerformanceInsightsResponse` |
| **Errors** | `401` unauthorized, `400` not enough data (min 3 sessions), `500` AI failure |

---

### Strategy — `/api/v1/strategy`

#### `GET /strategy/next-topic`
Get AI-recommended next topic using the Strategy Planner Agent.

| | Detail |
|---|--------|
| **Auth** | Bearer token |
| **Response** | `StrategyResponse` |
| **Errors** | `401` unauthorized, `400` not enough data, `500` AI failure |

```python
class StrategyResponse(BaseModel):
    recommended_topic: str
    reason: str                  # Why this topic was recommended
    suggested_difficulty: str    # Recommended difficulty level
    alternatives: list[str]     # 2-3 alternative topic suggestions
    study_plan: str             # Brief study plan description
```

---

## AI Agent Flow

### Complete Learning Session Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         USER STARTS SESSION                             │
│                    POST /lessons/generate                                │
│                    { topic, difficulty }                                 │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   1. CONTENT GENERATOR AGENT │
              │                              │
              │   Input:  topic, difficulty   │
              │   Output: lesson content      │
              │           (Markdown + key     │
              │            concepts)          │
              └──────────────┬───────────────┘
                             │
                             │  Lesson saved to DB
                             │  Returned to user
                             │
                             ▼
                   User reads lesson...
                             │
                             ▼
              ┌──────────────────────────────┐
              │   2. QUIZ AGENT              │
              │      POST /quizzes/generate  │
              │                              │
              │   Input:  lesson content,    │
              │           key concepts       │
              │   Output: 5 MCQ questions    │
              └──────────────┬───────────────┘
                             │
                             │  Questions shown to user
                             │  (without answers)
                             │
                             ▼
                   User answers quiz...
                             │
                             ▼
              ┌──────────────────────────────┐
              │   3. DIFFICULTY ADJUSTER     │
              │      (triggered by           │
              │       POST /quizzes/submit)  │
              │                              │
              │   Input:  score (0-5),       │
              │           current difficulty,│
              │           recent history     │
              │   Output: new difficulty     │
              │           level              │
              └──────────────┬───────────────┘
                             │
                             │  User difficulty updated
                             │  PerformanceRecord created
                             │
                             ▼
              ┌──────────────────────────────┐
              │   4. PERFORMANCE ANALYZER    │
              │      GET /performance/       │
              │          insights            │
              │                              │
              │   Input:  all user scores,   │
              │           topics, history    │
              │   Output: strengths,         │
              │           weaknesses,        │
              │           trends             │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   5. STRATEGY PLANNER        │
              │      GET /strategy/          │
              │          next-topic          │
              │                              │
              │   Input:  performance data,  │
              │           past topics,       │
              │           difficulty level   │
              │   Output: recommended topic, │
              │           study plan         │
              └──────────────────────────────┘
                             │
                             ▼
              User selects next topic → cycle repeats
```

### Agent Dependencies

```
Content Generator ← (no dependencies — first in pipeline)
Quiz Agent ← depends on Content Generator output (lesson content)
Difficulty Adjuster ← depends on Quiz submission (score) + user history
Performance Analyzer ← depends on accumulated PerformanceRecords
Strategy Planner ← depends on Performance Analyzer insights + topic history
```

---

## Authentication

### JWT Configuration

| Setting | Value |
|---------|-------|
| Algorithm | HS256 |
| Token lifetime | 24 hours |
| Header format | `Authorization: Bearer <token>` |
| Payload claims | `sub` (user_id as string), `exp`, `iat` |

### Auth Middleware

All endpoints except `/auth/register` and `/auth/login` require a valid JWT.

```python
# Dependency injection pattern
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Decode JWT, fetch user from DB, raise 401 if invalid."""
    ...
```

---

## Error Handling

### Standard Error Response

All errors return this shape:

```json
{
  "error": "ERROR_CODE",
  "detail": "Human-readable description of what went wrong."
}
```

### Error Codes

| HTTP Status | Error Code | When |
|-------------|-----------|------|
| 400 | `BAD_REQUEST` | Invalid input data |
| 401 | `UNAUTHORIZED` | Missing/invalid/expired token |
| 403 | `FORBIDDEN` | Valid token but insufficient permissions |
| 404 | `NOT_FOUND` | Resource doesn't exist |
| 409 | `CONFLICT` | Duplicate resource (e.g., email taken) |
| 422 | `VALIDATION_ERROR` | Request body fails Pydantic validation |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error (including AI agent failures) |

### AI Agent Error Handling

When a Claude API call fails:
1. Retry once with exponential backoff (1 second delay).
2. If retry fails, return `500` with error code `AI_GENERATION_FAILED`.
3. Log the full error details server-side.
4. Never expose raw Claude API errors to the client.
