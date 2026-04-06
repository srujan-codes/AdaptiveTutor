# AdaptiveTutor — Sprint 1 Plan

> **Sprint Goal:** Build the foundational backend and frontend scaffolding, implement core learning flow (generate lesson → take quiz → get results), and deploy to staging.
>
> **Sprint Duration:** 2 weeks
> **Start Date:** 2026-04-06
> **End Date:** 2026-04-19

---

## Ticket Legend

| Status | Meaning |
|--------|---------|
| `To Do` | Not started |
| `In Progress` | Actively being worked on |
| `In Review` | Complete, awaiting code review |
| `Done` | Reviewed and merged |
| `Blocked` | Cannot proceed — see blockers |

---

## Sprint 1 Tickets

### Infrastructure & Setup

---

#### [TICKET-001] Backend Project Scaffold
- **Assigned to:** DevOps Engineer
- **Status:** To Do
- **Priority:** P0 — Critical
- **Description:** Initialize the backend Python project with FastAPI. Create `requirements.txt` with all pinned dependencies, `backend/.env.example` with documented env vars, and `backend/config.py` for settings management via pydantic-settings.
- **Acceptance Criteria:**
  - [ ] `requirements.txt` exists with all dependencies pinned to exact versions
  - [ ] `.env.example` lists every required env var with placeholder and comment
  - [ ] `config.py` loads all settings via pydantic-settings
  - [ ] `pip install -r requirements.txt` succeeds cleanly
  - [ ] `uvicorn backend.main:app` starts without errors

---

#### [TICKET-002] Frontend Project Scaffold
- **Assigned to:** DevOps Engineer
- **Status:** To Do
- **Priority:** P0 — Critical
- **Description:** Initialize the frontend project using Vite + React. Set up Tailwind CSS, PostCSS, React Router, and Axios. Create `vercel.json` for deployment config.
- **Acceptance Criteria:**
  - [ ] `npm install` succeeds cleanly
  - [ ] `npm run dev` starts the Vite dev server
  - [ ] Tailwind CSS classes render correctly
  - [ ] React Router is configured with placeholder routes
  - [ ] `vercel.json` has correct build and route configuration

---

#### [TICKET-003] Database Setup & Models
- **Assigned to:** Architect
- **Status:** To Do
- **Priority:** P0 — Critical
- **Description:** Create SQLAlchemy models for all 5 data entities (User, Session, LessonContent, QuizQuestion, PerformanceRecord) as defined in `ARCHITECTURE.md`. Set up database connection in `backend/database/connection.py`. Initialize Alembic for migrations.
- **Acceptance Criteria:**
  - [ ] All 5 SQLAlchemy models match `ARCHITECTURE.md` exactly
  - [ ] Pydantic schemas exist for all request/response shapes
  - [ ] `connection.py` provides engine, SessionLocal, and Base
  - [ ] Alembic is configured and initial migration works
  - [ ] SQLite works in dev, PostgreSQL connection string configurable for prod

---

### Authentication

---

#### [TICKET-004] JWT Authentication Service
- **Assigned to:** Backend Lead
- **Status:** To Do
- **Priority:** P0 — Critical
- **Dependencies:** TICKET-003
- **Description:** Implement JWT-based auth in `backend/services/auth_service.py`. Create password hashing (bcrypt), token creation, and token verification. Build the `get_current_user` dependency.
- **Acceptance Criteria:**
  - [ ] Passwords are hashed with bcrypt before storage
  - [ ] JWT tokens are created with HS256, 24h expiry, and `sub` claim
  - [ ] Token verification decodes and validates expiry
  - [ ] `get_current_user` dependency returns User or raises 401
  - [ ] No secrets hardcoded — all via environment variables

---

#### [TICKET-005] Auth Endpoints
- **Assigned to:** Backend Lead
- **Status:** To Do
- **Priority:** P0 — Critical
- **Dependencies:** TICKET-003, TICKET-004
- **Description:** Implement `POST /auth/register`, `POST /auth/login`, and `GET /auth/me` endpoints in `backend/routers/auth.py`, matching the contracts in `ARCHITECTURE.md`.
- **Acceptance Criteria:**
  - [ ] `POST /auth/register` creates user, returns user + token
  - [ ] `POST /auth/register` returns 409 if email/username taken
  - [ ] `POST /auth/login` returns user + token for valid credentials
  - [ ] `POST /auth/login` returns 401 for invalid credentials
  - [ ] `GET /auth/me` returns current user when token is valid
  - [ ] All error responses match the standard error format

---

### AI Agent Integration

---

#### [TICKET-006] Claude API Client Wrapper
- **Assigned to:** Backend Lead
- **Status:** To Do
- **Priority:** P0 — Critical
- **Description:** Build `backend/services/claude_client.py` — a reusable async wrapper around the Anthropic Python SDK. Handle retries (1 retry with 1s backoff), JSON response parsing, and structured error handling.
- **Acceptance Criteria:**
  - [ ] Async client initialized with API key from env
  - [ ] Single `send_message(system_prompt, user_message, max_tokens, temperature)` method
  - [ ] Automatic retry (1 retry, 1s delay) on failure
  - [ ] JSON parsing of response with validation
  - [ ] Custom `AIGenerationError` exception raised on failure
  - [ ] No raw Anthropic errors leak to callers

---

#### [TICKET-007] Content Generator Agent
- **Assigned to:** Backend Lead
- **Status:** To Do
- **Priority:** P1 — High
- **Dependencies:** TICKET-006
- **Description:** Implement `backend/agents/content_generator.py` using the system prompt from `PROMPTS.md`. Create the agent class that takes topic + difficulty and returns structured lesson content.
- **Acceptance Criteria:**
  - [ ] Uses system prompt from `PROMPTS.md` exactly
  - [ ] Accepts topic and difficulty, returns validated lesson data
  - [ ] Output matches `LessonResponse` schema
  - [ ] Handles JSON parsing failures gracefully

---

#### [TICKET-008] Quiz Agent
- **Assigned to:** Backend Lead
- **Status:** To Do
- **Priority:** P1 — High
- **Dependencies:** TICKET-006
- **Description:** Implement `backend/agents/quiz_agent.py` using the system prompt from `PROMPTS.md`. Takes lesson content and generates exactly 5 MCQ questions.
- **Acceptance Criteria:**
  - [ ] Uses system prompt from `PROMPTS.md` exactly
  - [ ] Accepts lesson content, returns 5 validated questions
  - [ ] Output matches `QuizQuestionResponse` schema
  - [ ] Validates exactly 5 questions, exactly 4 options each

---

#### [TICKET-009] Difficulty Adjuster Agent
- **Assigned to:** Backend Lead
- **Status:** To Do
- **Priority:** P1 — High
- **Dependencies:** TICKET-006
- **Description:** Implement `backend/agents/difficulty_adjuster.py` using the system prompt from `PROMPTS.md`. Takes score + history, returns difficulty adjustment decision.
- **Acceptance Criteria:**
  - [ ] Uses system prompt from `PROMPTS.md` exactly
  - [ ] Accepts score, current difficulty, and history
  - [ ] Returns validated difficulty adjustment decision
  - [ ] Correctly follows the adjustment rules from the prompt

---

#### [TICKET-010] Performance Analyzer Agent
- **Assigned to:** Backend Lead
- **Status:** To Do
- **Priority:** P2 — Medium
- **Dependencies:** TICKET-006
- **Description:** Implement `backend/agents/performance_analyzer.py`. Analyzes score history and returns strengths, weaknesses, trends, and recommendations.
- **Acceptance Criteria:**
  - [ ] Uses system prompt from `PROMPTS.md` exactly
  - [ ] Accepts performance records, returns validated insights
  - [ ] Output matches `PerformanceInsightsResponse` schema

---

#### [TICKET-011] Strategy Planner Agent
- **Assigned to:** Backend Lead
- **Status:** To Do
- **Priority:** P2 — Medium
- **Dependencies:** TICKET-006
- **Description:** Implement `backend/agents/strategy_planner.py`. Recommends next topic based on performance data and learning gaps.
- **Acceptance Criteria:**
  - [ ] Uses system prompt from `PROMPTS.md` exactly
  - [ ] Accepts performance data, returns validated recommendation
  - [ ] Output matches `StrategyResponse` schema

---

### API Endpoints

---

#### [TICKET-012] Lesson Endpoints
- **Assigned to:** Backend Lead
- **Status:** To Do
- **Priority:** P1 — High
- **Dependencies:** TICKET-003, TICKET-004, TICKET-007
- **Description:** Implement `POST /lessons/generate` and `GET /lessons/{lesson_id}` in `backend/routers/lessons.py`. Lesson generation creates a Session, calls the Content Generator Agent, saves the lesson, and returns it.
- **Acceptance Criteria:**
  - [ ] `POST /lessons/generate` creates session + lesson, returns `LessonResponse`
  - [ ] `GET /lessons/{lesson_id}` returns existing lesson or 404
  - [ ] Both endpoints require auth
  - [ ] Error responses match standard format

---

#### [TICKET-013] Quiz Endpoints
- **Assigned to:** Backend Lead
- **Status:** To Do
- **Priority:** P1 — High
- **Dependencies:** TICKET-003, TICKET-004, TICKET-008, TICKET-009
- **Description:** Implement `POST /quizzes/generate` and `POST /quizzes/submit` in `backend/routers/quizzes.py`. Quiz generation calls Quiz Agent. Submission scores the quiz, calls Difficulty Adjuster, creates PerformanceRecord, and updates user difficulty.
- **Acceptance Criteria:**
  - [ ] `POST /quizzes/generate` returns questions WITHOUT correct answers
  - [ ] `POST /quizzes/submit` scores answers, returns full results with explanations
  - [ ] Submit creates PerformanceRecord and updates user difficulty
  - [ ] Both endpoints require auth
  - [ ] Validates exactly 5 answers on submit

---

#### [TICKET-014] Performance & Strategy Endpoints
- **Assigned to:** Backend Lead
- **Status:** To Do
- **Priority:** P2 — Medium
- **Dependencies:** TICKET-003, TICKET-004, TICKET-010, TICKET-011
- **Description:** Implement `GET /performance`, `GET /performance/insights`, and `GET /strategy/next-topic`.
- **Acceptance Criteria:**
  - [ ] `GET /performance` returns paginated history with stats
  - [ ] `GET /performance/insights` calls Performance Analyzer Agent
  - [ ] `GET /strategy/next-topic` calls Strategy Planner Agent
  - [ ] Insights/strategy require minimum 3 sessions
  - [ ] All endpoints require auth

---

### Frontend Pages

---

#### [TICKET-015] API Client & Auth Context
- **Assigned to:** Frontend Lead
- **Status:** Done
- **Priority:** P0 — Critical
- **Description:** Build `frontend/src/api/client.js` (Axios instance with auth interceptor, base URL config, error handling) and `frontend/src/context/AuthContext.jsx` (login, logout, token persistence, protected route wrapper).
- **Acceptance Criteria:**
  - [x] Axios client auto-attaches Bearer token
  - [x] Client handles 401 by redirecting to login
  - [x] AuthContext provides `user`, `login()`, `logout()`, `isAuthenticated`
  - [x] Token persisted in localStorage
  - [x] Protected route component redirects to login if not authenticated

---

#### [TICKET-016] Landing & Login Pages
- **Assigned to:** Frontend Lead
- **Status:** Done
- **Priority:** P1 — High
- **Dependencies:** TICKET-015
- **Description:** Build `Landing.jsx` (hero section, feature highlights, CTA to register/login) and `Login.jsx` (login form + registration toggle, error display, redirect to dashboard on success).
- **Acceptance Criteria:**
  - [x] Landing page is visually polished, responsive, and has clear CTA
  - [x] Login page supports both login and registration
  - [x] Form validation with error messages
  - [x] Loading states during auth requests
  - [x] Redirects to Dashboard on successful auth


---

#### [TICKET-017] Dashboard Page
- **Assigned to:** Frontend Lead
- **Status:** Done
- **Priority:** P1 — High
- **Dependencies:** TICKET-015
- **Description:** Build `Dashboard.jsx` — the main hub showing: topic selector for new lesson, recent sessions, current difficulty level, quick stats, and recommended next topic (when available).
- **Acceptance Criteria:**
  - [x] TopicSelector component for starting new lessons
  - [x] Shows current difficulty level
  - [x] Displays recent session history
  - [x] Quick stats (total sessions, average score)
  - [x] Responsive layout


---

#### [TICKET-018] Lesson & Quiz Pages
- **Assigned to:** Frontend Lead
- **Status:** Done
- **Priority:** P1 — High
- **Dependencies:** TICKET-015
- **Description:** Build `Lesson.jsx` (displays lesson content with Markdown rendering, "Take Quiz" button) and `Quiz.jsx` (displays 5 questions, handles answer selection, submit, and results display).
- **Acceptance Criteria:**
  - [x] Lesson page renders Markdown content properly
  - [x] Shows key concepts and estimated duration
  - [x] Quiz page displays all 5 questions with radio buttons
  - [x] Submit validates all questions answered
  - [x] Results page shows score, correct/incorrect, and explanations
  - [x] Shows new difficulty level after quiz


---

#### [TICKET-019] Performance Page
- **Assigned to:** Frontend Lead
- **Status:** Done
- **Priority:** P2 — Medium
- **Dependencies:** TICKET-015
- **Description:** Build `Performance.jsx` with score history chart (ScoreChart component), AI-generated insights (InsightsPanel), and strategy recommendations.
- **Acceptance Criteria:**
  - [x] Score history displayed as a chart
  - [x] InsightsPanel shows strengths, weaknesses, trends
  - [x] Strategy section shows recommended next topic
  - [x] Handles empty state (no sessions yet)
  - [x] Loading and error states


---

### Testing

---

#### [TICKET-020] Backend Auth & Lesson Tests
- **Assigned to:** QA Engineer
- **Status:** To Do
- **Priority:** P1 — High
- **Dependencies:** TICKET-005, TICKET-012
- **Description:** Write pytest tests for auth endpoints (register, login, me) and lesson endpoints (generate, get). Mock Claude API.
- **Acceptance Criteria:**
  - [ ] 3+ tests per endpoint (happy path, validation error, auth error)
  - [ ] Claude API is mocked — no real API calls
  - [ ] Tests are independent (no shared state)
  - [ ] All tests pass with `pytest`

---

#### [TICKET-021] Backend Quiz & Performance Tests
- **Assigned to:** QA Engineer
- **Status:** To Do
- **Priority:** P2 — Medium
- **Dependencies:** TICKET-013, TICKET-014
- **Description:** Write pytest tests for quiz endpoints and performance/strategy endpoints. Mock Claude API.
- **Acceptance Criteria:**
  - [ ] 3+ tests per endpoint
  - [ ] Quiz submit correctly scores answers and adjusts difficulty
  - [ ] Performance endpoints handle min-session requirements
  - [ ] All tests pass with `pytest`

---

### Deployment

---

#### [TICKET-022] Backend Deployment (Render)
- **Assigned to:** DevOps Engineer
- **Status:** To Do
- **Priority:** P2 — Medium
- **Dependencies:** TICKET-001
- **Description:** Create `render.yaml` for Render deployment. Configure PostgreSQL addon, environment variables, and health check endpoint.
- **Acceptance Criteria:**
  - [ ] `render.yaml` with web service config
  - [ ] PostgreSQL database provisioned
  - [ ] All env vars documented and configurable
  - [ ] Health check endpoint (`GET /health`) returns 200
  - [ ] CORS configured for frontend domain

---

#### [TICKET-023] Frontend Deployment (Vercel)
- **Assigned to:** DevOps Engineer
- **Status:** To Do
- **Priority:** P2 — Medium
- **Dependencies:** TICKET-002
- **Description:** Configure `vercel.json` for frontend deployment. Set up API proxy rewrites, build settings, and environment variables.
- **Acceptance Criteria:**
  - [ ] `vercel.json` has correct build command and output directory
  - [ ] API routes proxied to Render backend URL
  - [ ] SPA fallback configured for React Router
  - [ ] Environment variables for API base URL

---

## Sprint 1 Summary

| Priority | Tickets | Count |
|----------|---------|-------|
| P0 — Critical | TICKET-001 through TICKET-006, TICKET-015 | 7 |
| P1 — High | TICKET-007 through TICKET-009, TICKET-012, TICKET-013, TICKET-016 through TICKET-018, TICKET-020 | 9 |
| P2 — Medium | TICKET-010, TICKET-011, TICKET-014, TICKET-019, TICKET-021 through TICKET-023 | 7 |
| **Total** | | **23** |

### Assignment Summary

| Role | Tickets | Count |
|------|---------|-------|
| DevOps Engineer | 001, 002, 022, 023 | 4 |
| Architect | 003 | 1 |
| Backend Lead | 004–014 | 11 |
| Frontend Lead | 015–019 | 5 |
| QA Engineer | 020, 021 | 2 |
