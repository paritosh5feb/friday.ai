"""Friday.AI - AI Project Management Platform

Main FastAPI application entry point.
Manages the complete AI research project lifecycle from problem statement
research through LaTeX report generation.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routers import auth, projects, lifecycle

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(lifecycle.router)

# Create upload directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORT_DIR, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/api/lifecycle-info")
async def lifecycle_info():
    """Get information about the AI Project Lifecycle steps."""
    from app.models.lifecycle import LIFECYCLE_STEP_NAMES, LIFECYCLE_STEP_DESCRIPTIONS

    steps = []
    for i in range(1, 10):
        steps.append({
            "step_number": i,
            "name": LIFECYCLE_STEP_NAMES[i],
            "description": LIFECYCLE_STEP_DESCRIPTIONS[i],
        })
    return {"lifecycle_steps": steps}
