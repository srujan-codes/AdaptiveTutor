# AdaptiveTutor — Master Context File

> **Every agent MUST read this file first before doing any work.**

## Project Overview

| Field | Detail |
|-------|--------|
| **Project Name** | AdaptiveTutor |
| **Goal** | Build a personalized, AI-powered adaptive tutoring web application that tailors lesson content, quizzes, and study strategies to each learner's performance in real time. |
| **Description** | AdaptiveTutor uses a team of 5 specialized AI agents (powered by Anthropic's Claude API) to generate lessons, create quizzes, adjust difficulty, analyze performance, and recommend study strategies. The system continuously adapts to the learner — making education truly personalized. |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + Vite + Tailwind CSS | Single-page application with responsive UI |
| **Backend** | Python 3.11 + FastAPI | REST API server, business logic, agent orchestration |
| **AI Engine** | Anthropic Claude API (claude-sonnet-4-20250514) | Powers all 5 AI agents |
| **Database** | SQLite (dev) → PostgreSQL (prod) | User data, sessions, performance records |
| **ORM** | SQLAlchemy 2.0 + Alembic | Database models and migrations |
| **Auth** | JWT (PyJWT) | Stateless authentication |
| **Deployment — Frontend** | Vercel | Static site hosting with CI/CD |
| **Deployment — Backend** | Render | Python web service hosting |
| **Testing** | Pytest (backend) + Vitest (frontend) | Unit and integration tests |

---

## The 5 AI Agents

Each agent is a specialized Claude prompt that performs one function in the learning pipeline.

| # | Agent Name | Responsibility |
|---|-----------|---------------|
| 1 | **Content Generator Agent** | Generates a structured lesson given a topic and difficulty level (beginner / intermediate / advanced). |
| 2 | **Quiz Agent** | Creates 5 multiple-choice questions (MCQs) based on the lesson content just delivered. |
| 3 | **Difficulty Adjuster Agent** | Evaluates the learner's quiz score and decides whether to increase, maintain, or decrease the difficulty level for the next lesson. |
| 4 | **Performance Analyzer Agent** | Analyzes the learner's score history across sessions and produces insights (strengths, weaknesses, trends). |
| 5 | **Strategy Planner Agent** | Recommends the next topic to study based on performance data, learning goals, and knowledge gaps. |

### Agent Pipeline Flow

```
User selects topic
        │
        ▼
┌─────────────────────┐
│ Content Generator    │──── generates lesson ────►  Lesson displayed to user
│ Agent                │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Quiz Agent           │──── generates 5 MCQs ────►  Quiz displayed to user
└─────────────────────┘
        │
        ▼
   User submits quiz
        │
        ▼
┌─────────────────────┐
│ Difficulty Adjuster  │──── adjusts level ────────►  Stored for next lesson
│ Agent                │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Performance Analyzer │──── analyzes history ─────►  Insights shown to user
│ Agent                │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Strategy Planner     │──── recommends next ──────►  Suggested topics shown
│ Agent                │                                to user
└─────────────────────┘
```

---

## Folder Structure

```
AdaptiveTutor/
├── CLAUDE.md                # This file — master context
├── AGENTS.md                # Team member definitions
├── ARCHITECTURE.md          # Technical design & API contracts
├── PROMPTS.md               # AI agent system prompts
├── SPRINT.md                # Sprint plan & tickets
├── PROGRESS.md              # Daily progress log
│
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment & app configuration
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment variable template
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User model
│   │   ├── session.py       # Session model
│   │   ├── lesson.py        # LessonContent model
│   │   ├── quiz.py          # QuizQuestion model
│   │   └── performance.py   # PerformanceRecord model
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # Auth endpoints
│   │   ├── lessons.py       # Lesson endpoints
│   │   ├── quizzes.py       # Quiz endpoints
│   │   ├── performance.py   # Performance endpoints
│   │   └── strategy.py      # Strategy endpoints
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py          # Base agent class
│   │   ├── content_generator.py
│   │   ├── quiz_agent.py
│   │   ├── difficulty_adjuster.py
│   │   ├── performance_analyzer.py
│   │   └── strategy_planner.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── claude_client.py # Anthropic API wrapper
│   │   └── auth_service.py  # JWT auth logic
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py    # DB engine & session factory
│   │   └── migrations/      # Alembic migrations
│   └── tests/
│       ├── __init__.py
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
    ├── vercel.json           # Vercel deployment config
    ├── public/
    │   └── favicon.ico
    ├── src/
    │   ├── main.jsx          # React entry point
    │   ├── App.jsx           # Root component & routing
    │   ├── index.css         # Global styles & Tailwind imports
    │   ├── api/
    │   │   └── client.js     # Axios/fetch API wrapper
    │   ├── components/
    │   │   ├── Layout.jsx
    │   │   ├── Navbar.jsx
    │   │   ├── LessonCard.jsx
    │   │   ├── QuizForm.jsx
    │   │   ├── ScoreChart.jsx
    │   │   ├── InsightsPanel.jsx
    │   │   └── TopicSelector.jsx
    │   ├── pages/
    │   │   ├── Landing.jsx
    │   │   ├── Dashboard.jsx
    │   │   ├── Lesson.jsx
    │   │   ├── Quiz.jsx
    │   │   ├── Performance.jsx
    │   │   └── Login.jsx
    │   ├── hooks/
    │   │   ├── useAuth.js
    │   │   └── useLesson.js
    │   └── context/
    │       └── AuthContext.jsx
    └── tests/
        ├── App.test.jsx
        └── components/
            └── QuizForm.test.jsx
```

---

## Rules Every Agent Must Follow

> These rules are **mandatory** and **non-negotiable**.

### 1. Always Read `CLAUDE.md` First
Before starting any work, every agent must read this file to understand the project context, tech stack, and folder structure.

### 2. Follow API Contracts in `ARCHITECTURE.md`
All endpoints, request/response shapes, and data models are defined in `ARCHITECTURE.md`. Never deviate from the contracts without explicit Tech Lead approval.

### 3. Update `PROGRESS.md` After Completing Work
After finishing any ticket or meaningful unit of work, the agent must append an entry to `PROGRESS.md` documenting:
- What was completed
- Any issues encountered
- What's next

### 4. Follow the Ticket System
Only work on tickets assigned to you in `SPRINT.md`. Update ticket status as you progress:
- `To Do` → `In Progress` → `Done`

### 5. Code Quality Standards
- **Backend**: Type hints on all functions. Docstrings on all public functions. Pydantic models for all request/response schemas.
- **Frontend**: PropTypes or TypeScript-style JSDoc on all components. No inline styles — use Tailwind classes.
- **Both**: No hardcoded secrets. All config via environment variables.

### 6. Git Commit Convention
```
[TICKET-XXX] type: description

Types: feat, fix, refactor, test, docs, chore
Example: [TICKET-003] feat: add lesson generation endpoint
```

### 7. Error Handling
- Backend: Always return structured error responses `{ "error": string, "detail": string }`.
- Frontend: Show user-friendly error messages. Log technical details to console.

### 8. No Breaking Changes Without Coordination
If your work would change an API contract or data model, flag it in `PROGRESS.md` and notify the Tech Lead before proceeding.
