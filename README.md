# Friday.ai - AI Project Lifecycle Platform

<div align="center">

![Friday.ai Architecture](docs/architecture.svg)

**A full-stack platform to plan, run, track, and report AI research projects end-to-end.**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

</div>

---

## Overview

Friday.ai is built around a practical AI project lifecycle:

1. Problem statement research (review -> proposal -> update cycle)
2. Baseline experiment to validate hypothesis (SEH)
3. Reproduce current solutions
4. Run smallest partial experiments
5. Run benchmark evaluations
6. Create result tables from steps 4 and 5
7. Scale successful experiments
8. Final evaluation, collation, discussion, and LaTeX-ready reporting

This repository currently contains:
- A FastAPI backend with authentication, lifecycle management, experiment tracking, and run logging
- A React + TypeScript frontend with login/signup and a lifecycle dashboard
- Documentation + architecture diagram

The backend also **expands the original partial backend** from
[`paritosh5feb/friday.com`](https://github.com/paritosh5feb/friday.com),
including project -> experiment -> run -> run-params/run-metrics tracking.

---

## Key Features

### Authentication
- Signup / Login with JWT
- Protected APIs with bearer token auth
- `/api/auth/me` profile endpoint

### Lifecycle-aware Project Management
- Create projects
- Auto-initialize lifecycle stages for each project
- Update stage status and notes (`pending`, `in_progress`, `completed`, `blocked`)
- Lifecycle summary endpoint for scale/final-eval readiness checks

### Experiment + Run Tracking (Expanded from `friday.com`)
- Experiment CRUD per project
- Run creation and status transitions (`queued`, `running`, `completed`, `failed`)
- Per-run parameter logging
- Step-wise run metric logging
- Run detail endpoint with params + metrics for reproducibility

### Evaluation + Reporting
- Benchmark logging
- Result table storage (markdown)
- Final report entries with discussion/evaluation and LaTeX snippet fields

---

## Architecture

### High-level components
- **Frontend (React + TS):** auth screens + project lifecycle dashboard
- **Backend (FastAPI):** auth, projects, lifecycle, experiments, runs, benchmarks, tables, reports
- **Database (SQLite):** persistent storage through SQLAlchemy models

### Data flow
`React UI -> REST API -> FastAPI services -> SQLAlchemy ORM -> SQLite`

---

## Project Structure

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

---

## Getting Started

### Prerequisites
- Python 3.11+ (3.12 recommended)
- Node.js 18+

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend URL: `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

Set API URL if needed:

```bash
echo "VITE_API_BASE_URL=http://localhost:8000/api" > frontend/.env
```

---

## API Reference (Implemented)

### Health / utility
- `GET /`
- `GET /health`
- `GET /db-check`

### Auth
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Projects + lifecycle
- `POST /api/projects`
- `GET /api/projects`
- `GET /api/projects/paginated`
- `GET /api/projects/{project_id}`
- `PATCH /api/projects/{project_id}`
- `GET /api/projects/{project_id}/stages`
- `PATCH /api/stages/{stage_id}`
- `GET /api/projects/{project_id}/lifecycle-summary`

### Experiments
- `GET /api/projects/{project_id}/experiments`
- `POST /api/projects/{project_id}/experiments`
- `PATCH /api/experiments/{experiment_id}`
- `DELETE /api/experiments/{experiment_id}`

### Runs (expanded from friday.com logic)
- `GET /api/projects/{project_id}/runs`
- `POST /api/runs`
- `PATCH /api/runs/{run_id}/start`
- `PATCH /api/runs/{run_id}/finish`
- `POST /api/runs/{run_id}/params`
- `POST /api/runs/{run_id}/metrics`
- `GET /api/runs/{run_id}/metrics`
- `GET /api/runs/{run_id}`

### Benchmarks / Tables / Reports
- `GET /api/projects/{project_id}/benchmarks`
- `POST /api/projects/{project_id}/benchmarks`
- `GET /api/projects/{project_id}/tables`
- `POST /api/projects/{project_id}/tables`
- `GET /api/projects/{project_id}/reports`
- `POST /api/projects/{project_id}/reports`
- `PATCH /api/reports/{report_id}`

---

## Notes

- Password hashing uses `passlib` with `pbkdf2_sha256`.
- A lightweight startup migration is included for legacy local DBs (adds `projects.description` when missing).
- Frontend is intentionally simple and functional, focused on lifecycle execution workflow.
