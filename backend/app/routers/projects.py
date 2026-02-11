"""Project management API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new AI research project."""
    return ProjectService.create_project(db, project_data, current_user.id)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all projects for the current user."""
    projects = ProjectService.get_projects(db, current_user.id, skip, limit)
    total = ProjectService.get_project_count(db, current_user.id)
    return ProjectListResponse(projects=projects, total=total)


@router.get("/stats")
async def get_project_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get project statistics for dashboard."""
    return ProjectService.get_project_stats(db, current_user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific project by ID."""
    return ProjectService.get_project(db, project_id, current_user.id)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    update_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a project."""
    return ProjectService.update_project(db, project_id, current_user.id, update_data)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a project and all associated data."""
    ProjectService.delete_project(db, project_id, current_user.id)
