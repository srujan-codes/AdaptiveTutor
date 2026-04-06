# AdaptiveTutor — Team & Agent Definitions

> 6-person senior development team. Each member owns a domain and is accountable for its quality.

---

## Team Roster

| # | Role | Domain | Primary Files |
|---|------|--------|--------------|
| 1 | Architect | System design, API contracts, data models | `ARCHITECTURE.md`, `backend/models/`, `backend/database/` |
| 2 | Backend Lead | FastAPI server, endpoints, Claude API integration | `backend/main.py`, `backend/routers/`, `backend/agents/`, `backend/services/` |
| 3 | Frontend Lead | React UI, pages, components, styling | `frontend/src/` |
| 4 | DevOps Engineer | Dependencies, env config, CI/CD, deployment | `requirements.txt`, `.env.example`, `vercel.json`, Render config |
| 5 | QA Engineer | Tests, edge cases, API response validation | `backend/tests/`, `frontend/tests/` |
| 6 | Tech Lead / Scrum Master | Sprint planning, coordination, code review | `SPRINT.md`, `PROGRESS.md`, all org files |

---

## 1. Architect

**Owner:** System design & data layer

### Responsibilities
- Define and maintain `ARCHITECTURE.md` — the single source of truth for API contracts and data models.
- Design the database schema (SQLAlchemy models) and manage migrations (Alembic).
- Define the data flow between the 5 AI agents.
- Review all PRs that touch models, schemas, or agent interfaces.
- Ensure consistency between frontend expectations and backend contracts.

### Key Deliverables
- [ ] `ARCHITECTURE.md` with all API contracts and data models
- [ ] SQLAlchemy model files in `backend/models/`
- [ ] Database connection setup in `backend/database/`
- [ ] Alembic migration configuration

### Rules
- No endpoint may be implemented until its contract exists in `ARCHITECTURE.md`.
- All models must use Pydantic for serialization and SQLAlchemy for persistence.
- Schema changes require a migration file — never modify the DB directly.

---

## 2. Backend Lead

**Owner:** FastAPI server & AI agent integration

### Responsibilities
- Build and maintain the FastAPI application (`main.py`).
- Implement all API endpoints in `backend/routers/`.
- Integrate the 5 AI agents via the Anthropic Claude API.
- Build the Claude API client wrapper in `backend/services/claude_client.py`.
- Implement authentication (JWT) in `backend/services/auth_service.py`.

### Key Deliverables
- [ ] FastAPI app with CORS, middleware, and error handling
- [ ] All router files with endpoint implementations
- [ ] All 5 agent implementations in `backend/agents/`
- [ ] Claude API client service
- [ ] JWT authentication service

### Rules
- Every endpoint must match the contract in `ARCHITECTURE.md` exactly.
- All agent calls must go through `claude_client.py` — no direct API calls in routers.
- Use `async def` for all endpoints. Use `asyncio` for concurrent agent calls where possible.
- Every endpoint must have proper error handling with structured error responses.

---

## 3. Frontend Lead

**Owner:** React UI & user experience

### Responsibilities
- Build the React + Vite + Tailwind application.
- Implement all pages: Landing, Dashboard, Lesson, Quiz, Performance, Login.
- Build reusable components: Navbar, LessonCard, QuizForm, ScoreChart, InsightsPanel, TopicSelector.
- Implement client-side routing (React Router).
- Build the API client layer in `frontend/src/api/client.js`.
- Implement auth context and protected routes.

### Key Deliverables
- [ ] Vite + React + Tailwind project scaffold
- [ ] All page components
- [ ] All shared UI components
- [ ] API client with error handling
- [ ] Auth flow (login, logout, token management)
- [ ] Responsive design (mobile-first)

### Rules
- All styling via Tailwind CSS utility classes — no inline styles, no CSS modules.
- Components must be functional (hooks, not class components).
- API calls only through `client.js` — no raw `fetch` in components.
- Loading and error states are required for every async operation.

---

## 4. DevOps Engineer

**Owner:** Infrastructure, dependencies & deployment

### Responsibilities
- Manage `requirements.txt` (backend) and `package.json` (frontend).
- Create and maintain `.env.example` with all required environment variables.
- Configure Vercel deployment for the frontend (`vercel.json`).
- Configure Render deployment for the backend.
- Set up environment-specific configurations (dev, staging, prod).

### Key Deliverables
- [ ] `backend/requirements.txt` with pinned versions
- [ ] `backend/.env.example` with all env vars documented
- [ ] `frontend/vercel.json` with build and route config
- [ ] Render deployment configuration (`render.yaml`)
- [ ] README with setup and deployment instructions

### Rules
- All dependencies must have pinned versions (e.g., `fastapi==0.109.0`, not `fastapi`).
- No secrets in code or config files — everything via environment variables.
- `.env.example` must list every env var with a placeholder value and description comment.
- Deployment configs must handle CORS and API proxying correctly.

---

## 5. QA Engineer

**Owner:** Testing & quality assurance

### Responsibilities
- Write unit tests for all backend endpoints (`pytest`).
- Write unit tests for frontend components (`vitest`).
- Validate all API responses match `ARCHITECTURE.md` contracts.
- Test edge cases: empty inputs, invalid tokens, rate limits, large payloads.
- Verify the AI agent pipeline end-to-end.

### Key Deliverables
- [ ] Backend test suite in `backend/tests/`
- [ ] Frontend test suite in `frontend/tests/`
- [ ] API contract validation tests
- [ ] Edge case test coverage
- [ ] Test documentation (what's covered, what's manual)

### Rules
- Every endpoint must have at least 3 test cases: happy path, validation error, auth error.
- Tests must be independent — no shared state between test functions.
- Mock the Claude API in tests — never make real API calls in CI.
- Test names must be descriptive: `test_generate_lesson_returns_400_for_invalid_topic`.

---

## 6. Tech Lead / Scrum Master

**Owner:** Coordination, planning & quality

### Responsibilities
- Create and maintain `SPRINT.md` with ticket definitions and assignments.
- Maintain `PROGRESS.md` with daily updates.
- Review all code and documentation for consistency.
- Resolve blockers and coordinate between team members.
- Ensure all agents follow the rules in `CLAUDE.md`.
- Make architectural decisions when the Architect needs tiebreaking.

### Key Deliverables
- [ ] All 6 organisation files (this is Sprint 0)
- [ ] Sprint planning with prioritized, well-defined tickets
- [ ] Daily standup summaries in `PROGRESS.md`
- [ ] Code review feedback

### Rules
- No ticket goes to "Done" without code review.
- Blockers must be documented in `PROGRESS.md` within 24 hours.
- Sprint scope changes require explicit justification in `SPRINT.md`.
- The Tech Lead has final say on architectural disputes.

---

## Collaboration Protocol

```
1. Agent reads CLAUDE.md              (mandatory first step)
2. Agent reads their ticket in SPRINT.md
3. Agent reads relevant section of ARCHITECTURE.md
4. Agent does the work
5. Agent updates ticket status in SPRINT.md
6. Agent logs progress in PROGRESS.md
7. Tech Lead reviews
```
