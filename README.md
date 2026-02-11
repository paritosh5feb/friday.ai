# Friday.AI - AI Project Management Platform

<div align="center">

![Friday.AI](docs/architecture.svg)

**A comprehensive, full-stack platform for managing the complete AI research project lifecycle -- from problem statement research to publication-ready LaTeX reports.**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)](https://reactjs.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## Table of Contents

- [Overview](#overview)
- [AI Research Lifecycle](#ai-research-lifecycle)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Docker Setup](#docker-setup)
- [API Documentation](#api-documentation)
- [Screenshots & UI](#screenshots--ui)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Friday.AI** is an intelligent project management platform designed specifically for AI/ML researchers and teams. It provides a structured, step-by-step workflow that guides researchers through the entire lifecycle of an AI research project -- from initial literature review to the final publication-ready LaTeX report.

The platform is built around a **9-step AI Research Lifecycle** that encodes best practices for conducting rigorous, reproducible AI research.

---

## AI Research Lifecycle

Friday.AI implements a carefully designed 9-step lifecycle for AI research projects:

```
Step 1: Problem Statement Research
   |    -> Download papers (Mendeley), create summaries
   |    -> Find open problem statements
   |    -> CYCLE: Review -> Create Proposal -> Update
   v
Step 2: Establish Baseline Experiments (SEH)
   |    -> Validate your Standard Experimental Hypothesis
   v
Step 3: Reproduce Current Solutions
   |    -> Replicate state-of-the-art results
   v
Step 4: Run Partial / Smallest Experiments
   |    -> Quick validation at minimal scale
   v
Step 5: Run Benchmark Evaluations
   |    -> Standard datasets and metrics
   v
Step 6: Create Result Tables
   |    -> Tabulate results from Steps 4-5
   |    -> Auto-generate comparison tables
   v
Step 7: Scale Experiments
   |    -> Full-scale runs if results are promising
   v
Step 8: Final Evaluation & Discussion
   |    -> Collation, analysis, discussion of all results
   v
Step 9: LaTeX Report Generation
        -> Publication-ready reports (IEEE, ACM, NeurIPS)
        -> One-click auto-generation from all project data
```

Each step has its own dedicated UI with status tracking, progress monitoring, and data management capabilities.

---

## Features

### Authentication & User Management
- JWT-based authentication (signup/login)
- Secure password hashing with bcrypt
- Protected routes and API endpoints
- User profile management

### Project Management
- Create, read, update, delete AI research projects
- Project status tracking (Planning, In Progress, Completed, On Hold, Archived)
- Domain categorization (NLP, CV, RL, etc.)
- Tag-based organization
- Dashboard with project statistics

### Step 1: Problem Statement Research
- Research paper management (title, authors, abstract, DOI, venue)
- Paper summaries and open problem identification
- Proposal notes with review workflow (Pending -> Reviewed -> Proposal Created)
- Source URL linking (arXiv, Mendeley, etc.)

### Step 2-4, 7: Experiment Management
- Full experiment CRUD for baseline, reproduction, partial, and scaled experiments
- Hypothesis documentation
- Methodology tracking
- Dataset and model architecture logging
- Hyperparameter storage (JSON)
- Results tracking with metrics (JSON)
- Experiment status (Planned -> Running -> Completed/Failed)
- Conclusion documentation

### Step 5: Benchmark Evaluations
- Benchmark result tracking with multiple metrics
- Baseline marking for comparison
- Environment/hardware documentation
- Metrics visualization

### Step 6: Result Tables
- Manual table creation with custom headers and rows
- **Auto-generation** of comparison tables from experiments and benchmarks
- Table types: Comparison, Ablation Study, Summary

### Step 8: Final Evaluation
- Collated results overview across all experiments and benchmarks
- Summary statistics (total experiments, completed, failed, benchmarks)
- Experiment conclusions aggregation
- Discussion framework with guided prompts

### Step 9: LaTeX Report Generation
- **One-click auto-generation** from all project data
- Multiple templates: IEEE Conference, ACM SIGCONF, NeurIPS, Custom Article
- Proper LaTeX formatting with `booktabs` tables
- Automatic bibliography generation from research papers
- Copy to clipboard and download as `.tex` file
- Draft -> Review -> Final status workflow

### Modern UI/UX
- Responsive design (desktop + mobile)
- Interactive lifecycle progress sidebar
- Collapsible sidebar navigation
- Search and filter capabilities
- Real-time status updates
- Beautiful gradient-based auth pages

---

## Architecture

```
friday.ai/
├── backend/                    # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── config.py          # Application settings
│   │   ├── database.py        # SQLAlchemy database configuration
│   │   ├── models/            # SQLAlchemy ORM models
│   │   │   ├── user.py        # User model
│   │   │   ├── project.py     # Project model with status enum
│   │   │   └── lifecycle.py   # All lifecycle entities (9 models)
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   │   ├── user.py        # Auth schemas
│   │   │   ├── project.py     # Project CRUD schemas
│   │   │   └── lifecycle.py   # Lifecycle entity schemas
│   │   ├── routers/           # API route handlers
│   │   │   ├── auth.py        # POST /signup, /login, GET /me
│   │   │   ├── projects.py    # Project CRUD + stats
│   │   │   └── lifecycle.py   # All lifecycle endpoints
│   │   ├── services/          # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── project_service.py
│   │   │   ├── lifecycle_service.py
│   │   │   └── latex_service.py  # LaTeX report generator
│   │   ├── middleware/        # Auth middleware
│   │   └── utils/             # Security utilities
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # React + Vite Frontend
│   ├── src/
│   │   ├── App.jsx            # Root component with routing
│   │   ├── main.jsx           # Entry point
│   │   ├── index.css          # TailwindCSS + custom styles
│   │   ├── api/
│   │   │   └── client.js      # Axios API client with interceptors
│   │   ├── context/
│   │   │   └── AuthContext.jsx # Authentication state management
│   │   ├── components/
│   │   │   ├── Layout.jsx     # Main layout with sidebar
│   │   │   ├── LifecycleProgress.jsx  # Interactive step display
│   │   │   └── ProtectedRoute.jsx
│   │   └── pages/
│   │       ├── Login.jsx      # Login page
│   │       ├── Signup.jsx     # Registration page
│   │       ├── Dashboard.jsx  # Stats and overview
│   │       ├── Projects.jsx   # Project list
│   │       ├── NewProject.jsx # Create project
│   │       ├── ProjectDetail.jsx  # Project view with lifecycle
│   │       └── lifecycle/     # 9 lifecycle step pages
│   │           ├── StepHeader.jsx
│   │           ├── ProblemResearch.jsx
│   │           ├── BaselineExperiment.jsx
│   │           ├── ReproduceSolutions.jsx
│   │           ├── PartialExperiments.jsx
│   │           ├── BenchmarkEvaluations.jsx
│   │           ├── ResultTables.jsx
│   │           ├── ScaleExperiments.jsx
│   │           ├── FinalEvaluation.jsx
│   │           └── LatexReport.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── nginx.conf
│
├── docs/
│   └── architecture.svg       # Architecture diagram
├── docker-compose.yml
├── .gitignore
└── README.md
```

### Data Flow

```
Browser (React SPA)
    |
    | HTTP/REST (JSON)
    |
    v
FastAPI Backend
    |
    |--- Auth Router (/api/auth/*)
    |--- Project Router (/api/projects/*)
    |--- Lifecycle Router (/api/projects/{id}/lifecycle/*)
    |       |--- Papers (/papers/*)
    |       |--- Experiments (/experiments/*)
    |       |--- Benchmarks (/benchmarks/*)
    |       |--- Tables (/tables/*)
    |       |--- Reports (/reports/*)
    |
    v
Service Layer (Business Logic)
    |
    v
SQLAlchemy ORM
    |
    v
SQLite Database
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 | UI Components & SPA |
| | Vite 6 | Build tool & dev server |
| | TailwindCSS 3.4 | Utility-first styling |
| | React Router DOM 6 | Client-side routing |
| | Axios | HTTP client |
| | Lucide React | Icon library |
| **Backend** | Python 3.12 | Server language |
| | FastAPI 0.115 | REST API framework |
| | SQLAlchemy 2.0 | ORM & database toolkit |
| | Pydantic 2.10 | Data validation |
| | Python-Jose | JWT token management |
| | Passlib + bcrypt | Password hashing |
| **Database** | SQLite | Lightweight relational DB |
| **DevOps** | Docker | Containerization |
| | Docker Compose | Multi-container orchestration |
| | Nginx | Frontend serving & reverse proxy |

---

## Getting Started

### Prerequisites

- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **Docker** (optional, for containerized deployment)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API Docs (Swagger): `http://localhost:8000/api/docs`
- API Docs (ReDoc): `http://localhost:8000/api/redoc`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

> Note: The Vite dev server proxies `/api` requests to `http://localhost:8000` automatically.

### Docker Setup

```bash
# Build and start all services
docker-compose up --build

# Services:
# - Frontend: http://localhost:5173
# - Backend:  http://localhost:8000
```

---

## API Documentation

### Authentication

| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/auth/me` | Get current user info |

### Projects

| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/api/projects` | Create new project |
| GET | `/api/projects` | List user's projects |
| GET | `/api/projects/stats` | Get project statistics |
| GET | `/api/projects/{id}` | Get project details |
| PUT | `/api/projects/{id}` | Update project |
| DELETE | `/api/projects/{id}` | Delete project |

### Lifecycle Steps

| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/api/projects/{id}/lifecycle` | Get all 9 steps |
| GET | `/api/projects/{id}/lifecycle/{step}` | Get specific step |
| PUT | `/api/projects/{id}/lifecycle/{step}` | Update step status/notes |

### Research Papers (Step 1)

| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/api/projects/{id}/papers` | Add paper |
| GET | `/api/projects/{id}/papers` | List papers |
| PUT | `/api/projects/{id}/papers/{pid}` | Update paper |
| DELETE | `/api/projects/{id}/papers/{pid}` | Delete paper |

### Experiments (Steps 2, 3, 4, 7)

| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/api/projects/{id}/experiments` | Create experiment |
| GET | `/api/projects/{id}/experiments` | List experiments (filter by type) |
| PUT | `/api/projects/{id}/experiments/{eid}` | Update experiment |
| DELETE | `/api/projects/{id}/experiments/{eid}` | Delete experiment |

### Benchmarks (Step 5)

| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/api/projects/{id}/benchmarks` | Add benchmark result |
| GET | `/api/projects/{id}/benchmarks` | List benchmarks |
| PUT | `/api/projects/{id}/benchmarks/{bid}` | Update benchmark |
| DELETE | `/api/projects/{id}/benchmarks/{bid}` | Delete benchmark |

### Result Tables (Step 6)

| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/api/projects/{id}/tables` | Create table |
| POST | `/api/projects/{id}/tables/auto-generate` | Auto-generate from data |
| GET | `/api/projects/{id}/tables` | List tables |
| PUT | `/api/projects/{id}/tables/{tid}` | Update table |
| DELETE | `/api/projects/{id}/tables/{tid}` | Delete table |

### LaTeX Reports (Step 9)

| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/api/projects/{id}/reports` | Create report |
| POST | `/api/projects/{id}/reports/generate` | Auto-generate full report |
| GET | `/api/projects/{id}/reports` | List reports |
| PUT | `/api/projects/{id}/reports/{rid}` | Update report |
| DELETE | `/api/projects/{id}/reports/{rid}` | Delete report |

### Utility

| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/lifecycle-info` | Get lifecycle step descriptions |

---

## Database Schema

```
users
  ├── id (PK)
  ├── email (unique)
  ├── username (unique)
  ├── full_name
  ├── hashed_password
  ├── is_active
  └── timestamps

projects
  ├── id (PK)
  ├── title
  ├── description
  ├── status (planning|in_progress|completed|on_hold|archived)
  ├── current_step (1-9)
  ├── domain
  ├── tags
  ├── owner_id (FK -> users)
  └── timestamps

lifecycle_steps
  ├── id (PK)
  ├── project_id (FK -> projects)
  ├── step_number (1-9)
  ├── step_name
  ├── status (not_started|in_progress|in_review|completed|blocked)
  ├── progress_percentage (0-100)
  ├── notes
  └── timestamps

research_papers
  ├── id (PK)
  ├── project_id (FK -> projects)
  ├── title, authors, abstract, summary
  ├── source_url, doi, year, venue
  ├── open_problems, proposal_notes
  ├── review_status (pending|reviewed|proposal_created)
  └── timestamps

experiments
  ├── id (PK)
  ├── project_id (FK -> projects)
  ├── name, experiment_type (baseline|reproduction|partial|scaled)
  ├── hypothesis, methodology, description
  ├── dataset, model_architecture
  ├── hyperparameters (JSON), results (JSON)
  ├── status (planned|running|completed|failed)
  ├── conclusion, log_output
  └── timestamps

benchmark_results
  ├── id (PK)
  ├── project_id (FK -> projects)
  ├── benchmark_name, dataset, model_name
  ├── metrics (JSON)
  ├── environment, notes, is_baseline
  └── timestamps

result_tables
  ├── id (PK)
  ├── project_id (FK -> projects)
  ├── title, description
  ├── table_data (JSON: {headers, rows})
  ├── table_type (comparison|ablation|summary)
  └── timestamps

latex_reports
  ├── id (PK)
  ├── project_id (FK -> projects)
  ├── title
  ├── template_type (ieee|acm|neurips|custom)
  ├── content (full LaTeX source)
  ├── status (draft|review|final)
  └── timestamps
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./friday_ai.db` | Database connection string |
| `SECRET_KEY` | *(set in config)* | JWT signing secret |
| `CORS_ORIGINS` | `localhost:5173,3000` | Allowed CORS origins |
| `UPLOAD_DIR` | `./uploads` | File upload directory |
| `REPORT_DIR` | `./generated_reports` | Generated reports directory |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**Built with purpose for AI researchers**

*Friday.AI - Because every great research project deserves a structured workflow.*

</div>
