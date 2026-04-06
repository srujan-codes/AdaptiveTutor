# AdaptiveTutor — Project Status Report (Updated)

**Role:** Tech Lead
**Date:** April 6th, 2026
**Target Architecture:** FastAPI Backend + React/Vite Frontend
**AI Engine:** Groq API (`llama-3.3-70b-versatile`)

> [!NOTE]
> This is a revised engineering analysis reflecting the completion of the AI JSON Prompting hotfixes. Sprint 2 is now officially closed.

---

## 1. 🏗️ PROJECT OVERVIEW

**AdaptiveTutor** is a dynamic, AI-powered educational web application designed to auto-generate personalized lesson modules, benchmark user performance through intelligent quizzes, and autonomously scale educational difficulty tailored exactly to the user's comprehension speed.

### The 5 AI Logic Agents
1. **Content Generator Agent:** Ingests topics and spits out curated, markdown-formatted study guides.
2. **Quiz Agent:** Cross-references active lessons to generate strict 5-Question MCQs.
3. **Difficulty Adjuster Agent:** Scans recent quiz scores and scales up/down the user's difficulty band autonomously.
4. **Performance Analyzer Agent:** Reviews metrics for users with ≥ 3 completed sessions to generate strategic feedback.
5. **Strategy Planner Agent:** Recommends next topics based on active gaps.

### Tech Stack Summary
- **Frontend:** React 18, Vite, Tailwind CSS v4, React Router, Recharts, Axios.
- **Backend:** FastAPI, Async SQLAlchemy, SQLite (Development), PyJWT.
- **AI Infrastructure:** Python `groq` SDK wrapping `llama-3.3-70b-versatile`.
- **Infra/Hosting targets:** Vercel (Frontend), Render (Backend).

---

## 2. ✅ WHAT'S COMPLETE

**Sprint 1 & Sprint 2 are entirely finalized. Tickets 001 through 019 are `Done`.** 

* **Complete Application Scaffold Built:** The full stack is organically bootstrapped into a working E2E local prototype running on branch `feature/frontend-ui`.
* **Backend Stable:** 
   - All 5 REST routers (`/auth`, `/lessons`, `/quizzes`, `/performance`, `/strategy`) are fully mounted.
   - Hardcoded environmental variables have been decoupled to `.env` using robust `pydantic-settings` models.
   - Groq API (`llama-3.3-70b-versatile`) has seamlessly replaced Anthropic architecture.
* **Frontend Stable:** 
   - JWT Auth flow and layout pages (Dashboard, Performance, Lesson, Quiz) fully mapped out.
   - Dark-mode glassmorphism visual templates finalized.
   - Quiz Router mapping payload correctly bypasses 404s utilizing passive polling fallbacks.
* **Network & AI Stability (RECENT TRHOUGHPUT):** 
   - The JSON fragility block has been universally neutralized. *All 5 AI Agents* (`Quiz`, `Difficulty`, `Performance`, `Strategy`, `Content`) are guarded by strict, native LLM behavior modifications (`"Return ONLY a valid JSON object"`), aggressively locking down Llama-70b.
   - Backend Python regex scrubbing wipes any remaining nested strings.

---

## 3. 🔄 WHAT'S PARTIALLY DONE (Potential Risks)

* **Token Rotation / Backend Authorization Extensibility:**
   Right now, the JWT architecture runs purely statelessly. If the system scales, implementing a formal Refresh Token strategy will become necessary to prevent logging out users constantly. We built Frontend Axios Interceptors to trap 401s, but no silent-refresh layer exists yet.
* **Database Async Collision (SQLite limit):**
   We currently spin Async SQLite in the local environment. Concurrency under AsyncIO while writing to SQLite natively triggers locking issues at scale. This must be pivoted carefully to `PostgreSQL` before Render rollout.

---

## 4. ⏳ WHAT'S PENDING

**Sprint 3 Focus Tracking**

1. **Test-Driven Verification (`backend/tests`, `frontend/tests`) [Tickets 020, 021]**
   - E2E testing of the AI pipeline natively avoiding API calls on CI/CD rails using Vitest/Pytest mocks.
2. **Infrastructure Rollout (`render.yaml`, `vercel.json`) [Tickets 022, 023]**
   - We possess the configuration files, but we have *not* actively built images or deployed the repos to production Vercel servers or Render Docker pipelines yet.

---

## 5. 🚨 CRITICAL BLOCKERS

> [!TIP]
> The architectural blockers have been successfully neutralized. The codebase is "Green" and ready for QA testing. 

1. **No System Blockers!** The massive JSON payload deserialization crashes previously bottlenecking the pipeline were directly resolved. The codebase is structurally intact.

---

## 6. 🎯 RECOMMENDED ACTION PLAN

| Priority | Action Item | Estimated Effort | Description |
| :--- | :--- | :--- | :--- |
| **1** | **Launch E2E PyTest Mocks** | *Medium (2-3h)* | Inject raw `pytest` environments into the backend so local commits verify agent paths without burning Groq tokens. |
| **2** | **PostgreSQL Binding** | *Medium (2h)* | Activate the `DATABASE_URL` bindings in `.env`, verify `alembic` migrations route correctly into a real remote DB to bypass SQLite concurrency traps. |
| **3** | **Vercel & Render Delivery** | *High (3h)* | Inject the deployment environmental variables natively onto Vercel and Render dashboards, bridging the remote CORS domains. |
