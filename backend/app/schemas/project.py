"""Pydantic schemas for project-related operations."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    domain: Optional[str] = None
    tags: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    current_step: Optional[int] = None
    domain: Optional[str] = None
    tags: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    current_step: int
    domain: Optional[str] = None
    tags: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
