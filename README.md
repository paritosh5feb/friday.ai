# Friday.ai

Friday.ai is an AI project management platform built around a practical research-to-report lifecycle.
It helps teams plan, execute, evaluate, and document AI experiments with a structured workflow from
problem discovery to LaTeX-ready final reporting.

## Core Lifecycle Built into the Product

Each project is automatically initialized with 8 lifecycle stages:

1. **Problem statement research**
   - Literature review loop (review -> proposal -> update)
   - Open problem statement tracking
2. **Establish baseline experiments (SEH validation)**
3. **Reproduce current solutions**
4. **Run smallest partial experiment**
5. **Benchmark evaluations**
6. **Create result tables for stages 4 and 5**
7. **Scale experiments after quality checks**
8. **Final evaluation, collation, discussion, and LaTeX report preparation**

## Architecture

![Friday.ai Architecture](docs/architecture.svg)

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, SQLite, JWT authentication, bcrypt password hashing
- **Frontend:** React + TypeScript + Vite
- **Auth:** Signup/Login + token-based session handling
- **Storage:** Local SQLite database (`backend/friday_ai.db`)

## Repository Structure

```text
.
├── backend
│   ├── app
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── lifecycle.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── security.py
│   └── requirements.txt
├── frontend
│   ├── src
│   │   ├── api.ts
│   │   ├── auth.tsx
│   │   ├── App.tsx
│   │   ├── components/ProtectedRoute.tsx
│   │   └── pages/{LoginPage,SignupPage,DashboardPage}.tsx
│   └── package.json
└── docs
    └── architecture.svg
```

## Features Implemented

### Authentication

- User signup
- User login
- Current user endpoint (`/api/auth/me`)
- JWT-protected project and experiment APIs

### Lifecycle-Aware Project Management

- Create and list projects
- Auto-generate all lifecycle stages when a new project is created
- Update stage status (`pending`, `in_progress`, `completed`, `blocked`) and notes

### Experiment and Evaluation Tracking

- Create/list/delete experiments with:
  - kind (`baseline`, `reproduction`, `partial`, `benchmark`, `scaled`, `final`)
  - setup notes, hypothesis, result summary
  - metric name and value
- Create/list benchmark records linked to projects (optionally to experiments)
- Create/list markdown result tables
- Create/list final reports with:
  - discussion
  - evaluation summary
  - LaTeX snippet

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`

### Useful API Paths

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET/POST /api/projects`
- `GET /api/projects/{project_id}`
- `PATCH /api/stages/{stage_id}`
- `GET/POST /api/projects/{project_id}/experiments`
- `DELETE /api/experiments/{experiment_id}`
- `GET/POST /api/projects/{project_id}/benchmarks`
- `GET/POST /api/projects/{project_id}/tables`
- `GET/POST /api/projects/{project_id}/reports`

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

If needed, set custom API URL:

```bash
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env
```

## How the Product Supports Your AI Workflow

- **Research loop** is represented in stage 1 notes and status progression.
- **Baseline, reproduction, and smallest experiments** are logged using experiment kinds.
- **Benchmark evaluations** have their own structured records for metric comparison.
- **Table generation** supports markdown-based result tables for stage 6.
- **Scale-up decisions and final discussions** are captured in late-stage notes and reports.
- **LaTeX report creation** is supported by dedicated report fields for raw LaTeX snippets.

## Next Enhancements (Optional)

- File uploads for paper PDFs and dataset artifacts
- Auto-generated charts from benchmark tables
- Team roles and collaboration comments
- Export full project as PDF/LaTeX bundle