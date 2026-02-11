"""Project model for AI research project management."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.PLANNING)
    current_step = Column(Integer, default=1)  # 1-9 lifecycle step
    domain = Column(String(100), nullable=True)  # e.g., NLP, CV, RL
    tags = Column(String(500), nullable=True)  # comma-separated tags
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="projects")
    lifecycle_steps = relationship("LifecycleStep", back_populates="project", cascade="all, delete-orphan")
    research_papers = relationship("ResearchPaper", back_populates="project", cascade="all, delete-orphan")
    experiments = relationship("Experiment", back_populates="project", cascade="all, delete-orphan")
    benchmark_results = relationship("BenchmarkResult", back_populates="project", cascade="all, delete-orphan")
    result_tables = relationship("ResultTable", back_populates="project", cascade="all, delete-orphan")
    latex_reports = relationship("LatexReport", back_populates="project", cascade="all, delete-orphan")
