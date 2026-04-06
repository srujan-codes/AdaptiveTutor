# Sprint 2 Frontend Review 🚀

Welcome to the Sprint 2 Frontend Review for **AdaptiveTutor**. As the Tech Lead, I am thrilled to walk you through our newly minted, fully functional React Single Page Application (SPA). The UI is complete, seamlessly wired up, and ready to teach!

---

## 1. 📊 What Was Built

The **Frontend Lead** finished all tickets (TICKET-015 through TICKET-019), building out a full Vite + React 18 architecture powered by TailwindCSS v4. 

**Infrastructure & Context State**:
- Configured Axios within `client.js` using global request/response interceptors to effortlessly manage `Bearer` authentication tokens.
- Established `AuthContext.jsx` as the central state provider for user context and hydration checks upon page reloads.
- Built a router shield inside `App.jsx` dividing `<ProtectedRoute>` domains from `<PublicRoute>` gateways.

**Components Built**:
- `Navbar.jsx`: Persistent global navigator displaying real-time user difficulty.
- `TopicSelector.jsx`: Dynamic topic and difficulty input terminal bridging directly to the AI Content generation.
- `ScoreChart.jsx`: Integrated `recharts` for scalable visual graph rendering.
- `InsightsPanel.jsx`: A mapped dashboard to compartmentalize text-heavy AI observations.

---

## 2. 🎨 UI & Page Overview

We applied a modern, "Glassmorphism" design system utilizing overlapping gradients, blurred borders, and animated interaction highlights to ensure a premium User Experience.

- **`Landing.jsx`**: Visually impactful hero layout that establishes the "Learn Anything" promise. Outlines the 5 Claude Agents before driving users towards registration.
- **`Login.jsx`**: Minimalist modal handling both Login and Registration paths. Contains inline error validation and password visibility toggles.
- **`Dashboard.jsx`**: The engine payload. Highlights recent historical sessions, general stats, and enables input for the user's next topic of study. Unlocks "AI Recommended Next Topic" logic dynamically after completing 3 sessions.
- **`Lesson.jsx`**: Uses `react-markdown` to format the Claude-generated content beautifully inline. Translates technical Markdown into readable text, complete with badge highlighting on key concepts.
- **`Quiz.jsx`**: Traps user workflow until they respond to all 5 generated Multiple Choice Questions. Uses a progress meter tracker and conditionally scales color depending on success or failure of each question upon submission.
- **`Performance.jsx`**: Maps the `ScoreChart` graph against the deeper `InsightsPanel`. If users haven't completed 3 sessions, an aesthetically pleasing "Locked" state blocks out the AI recommendation components to avoid jarring crashes.

---

## 3. 🔌 API Integration Connections

Our client bridges directly to localhost `8000/8001` via Vite proxies during development.

*   **Auth Services**: `POST /auth/register` and `POST /auth/login` map to our AuthContext wrappers payload. `GET /auth/me` resolves gracefully on the `useEffect` DOM hydration pass.
*   **Lesson Services**: Generates topics out of the dashboard via `POST /lessons/generate`, fetching isolated lessons cleanly using `GET /lessons/{lesson_id}`.
*   **Quiz Services**: Fires `POST /quizzes/generate` to lock down questions, stripping answers. Forces exactly 5 array indices to append accurately via `POST /quizzes/submit`.
*   **Performance Services**: Pulls the historic ledger by calling `GET /performance` and extracts qualitative insights asynchronously utilizing `GET /performance/insights`.
*   **Strategy Services**: Unlocks via `GET /strategy/next-topic` directly informing the Dashboard and Performance recommendation calls to action.

---

## 4. ⚠️ Known Risks & Architecture Flags

While stable, our Frontend implementation carries specific tolerances:

1.   **Asynchronous UX Drag**: Calls to Anthropic AI, especially via the Content Generator and Performance Agent endpoints, carry high latencies (~10-25 seconds). We've aggressively implemented `Loading Spinners` natively blocking click interactions to prevent double-firing queries during these API wait times.
2.   **Token Drops**: The JWT 401 loop requires manual interception; our `axios.interceptor` handles this cleanly now, but we must be careful with downstream edge behaviors randomly resetting users back to the root `Landing` directory when navigating to protected areas.
3.   **State Dependencies**: The `Quiz.jsx` inherently depends on React Router `Location State` to pull initial questions from the preceding Lesson component without re-pinging the Database payload. This means raw links dynamically pushing directly to `/quiz/{id}` bypass safety constraints unless mitigated properly.

---

## 5. ✅ Definition of Done

How do we securely conclude the Frontend is production ready?

*   All static components deploy without Vite warnings or errors.
*   The `tailwindcss` engine properly prunes dependencies across `import` structures.
*   Routing interceptors block all unathenticated access unconditionally to `/dashboard`, `/lesson`, `/quiz`, and `/performance` spaces.
*   `GET` constraints natively evaluate `< 3 session` errors gracefully across both visual components affected.

---

## 6. 🎯 Sprint 3 Preview (Testing & Deployment)

Next, we shift entirely. With the backend API and frontend SPA completely built, we move to stabilize and deploy:

*   **QA Engineer Pipeline**: Activating unit tests mapping to backend Auth, Lesson, and Quiz endpoint structures utilizing PyTest and Vitest (TICKETs-020 and 021). 
*   **Deployment Operations**: Validating `Render` and `Vercel` infrastructure hosting layers. Finalizing GitHub Continuous Integration (CI) bridges so every branch push natively builds without conflict.
