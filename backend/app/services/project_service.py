"""Project management service."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.project import Project, ProjectStatus
from app.models.lifecycle import (
    LifecycleStep, StepStatus,
    LIFECYCLE_STEP_NAMES, LIFECYCLE_STEP_DESCRIPTIONS,
)
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:

    @staticmethod
    def create_project(db: Session, project_data: ProjectCreate, owner_id: int) -> Project:
        """Create a new project with all 9 lifecycle steps."""
        project = Project(
            title=project_data.title,
            description=project_data.description,
            domain=project_data.domain,
            tags=project_data.tags,
            owner_id=owner_id,
            status=ProjectStatus.PLANNING,
            current_step=1,
        )
        db.add(project)
        db.flush()  # Get the project ID

        # Create all 9 lifecycle steps
        for step_num in range(1, 10):
            step = LifecycleStep(
                project_id=project.id,
                step_number=step_num,
                step_name=LIFECYCLE_STEP_NAMES[step_num],
                description=LIFECYCLE_STEP_DESCRIPTIONS[step_num],
                status=StepStatus.NOT_STARTED,
                progress_percentage=0,
            )
            db.add(step)

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_projects(db: Session, owner_id: int, skip: int = 0, limit: int = 50) -> List[Project]:
        """Get all projects for a user."""
        return (
            db.query(Project)
            .filter(Project.owner_id == owner_id)
            .order_by(Project.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_project_count(db: Session, owner_id: int) -> int:
        """Get total project count for a user."""
        return db.query(Project).filter(Project.owner_id == owner_id).count()

    @staticmethod
    def get_project(db: Session, project_id: int, owner_id: int) -> Project:
        """Get a single project by ID."""
        project = (
            db.query(Project)
            .filter(Project.id == project_id, Project.owner_id == owner_id)
            .first()
        )
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        return project

    @staticmethod
    def update_project(db: Session, project_id: int, owner_id: int, update_data: ProjectUpdate) -> Project:
        """Update a project."""
        project = ProjectService.get_project(db, project_id, owner_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(project, key, value)

        project.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(db: Session, project_id: int, owner_id: int) -> None:
        """Delete a project and all associated data."""
        project = ProjectService.get_project(db, project_id, owner_id)
        db.delete(project)
        db.commit()

    @staticmethod
    def get_project_stats(db: Session, owner_id: int) -> dict:
        """Get project statistics for dashboard."""
        total = db.query(Project).filter(Project.owner_id == owner_id).count()
        planning = db.query(Project).filter(
            Project.owner_id == owner_id, Project.status == ProjectStatus.PLANNING
        ).count()
        in_progress = db.query(Project).filter(
            Project.owner_id == owner_id, Project.status == ProjectStatus.IN_PROGRESS
        ).count()
        completed = db.query(Project).filter(
            Project.owner_id == owner_id, Project.status == ProjectStatus.COMPLETED
        ).count()
        on_hold = db.query(Project).filter(
            Project.owner_id == owner_id, Project.status == ProjectStatus.ON_HOLD
        ).count()

        return {
            "total": total,
            "planning": planning,
            "in_progress": in_progress,
            "completed": completed,
            "on_hold": on_hold,
        }
