# AdaptiveTutor

AdaptiveTutor is a personalized, AI-powered adaptive tutoring web application that tailors lesson content, quizzes, and study strategies to each learner's performance in real time using a team of 5 specialized AI agents.

## Running Locally

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables (create a `.env` file based on `.env.example`):
   ```
   GROQ_API_KEY=your_groq_api_key
   SECRET_KEY=your_jwt_secret_key
   DATABASE_URL=sqlite:///./test.db  # Use SQLite for local dev
   ```
5. Run the server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Configure environment variables (create a `.env` file):
   ```
   VITE_API_URL=http://localhost:8000/api/v1
   ```
4. Start the development server:
   ```bash
   npm run dev
   ```

## Deployment Guide

We use **Vercel** for the frontend and **Render** for the backend.

### Required Environment Variables

**Backend (Render):**
- `GROQ_API_KEY`: Your Groq API key for powering the AI agents.
- `JWT_SECRET_KEY`: A secure random string for signing JWT tokens.
- `DATABASE_URL`: The PostgreSQL database connection string.

**Frontend (Vercel):**
- `VITE_API_URL`: The URL of your deployed backend API (e.g., `https://adaptivetutor-backend.onrender.com/api/v1`).

### Deploying the Backend to Render

1. Create a new Web Service on [Render](https://render.com/).
2. Connect your GitHub repository.
3. Configure the service:
   - **Root Directory:** `backend`
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT` (The `render.yaml` and `Procfile` are already configured for this).
4. Add the required environment variables in the Render dashboard.
5. Deploy the application.

### Deploying the Frontend to Vercel

1. Create a new Project on [Vercel](https://vercel.com/).
2. Connect your GitHub repository.
3. Configure the project:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Add the `VITE_API_URL` environment variable pointing to your deployed Render service.
5. Deploy the application. (The `vercel.json` already contains rules for SPA routing).