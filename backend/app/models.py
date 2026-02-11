from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    objective = Column(Text, nullable=False)
    hypothesis = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="projects")
    lifecycle_stages = relationship(
        "LifecycleStage",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="LifecycleStage.stage_number",
    )
    experiments = relationship("Experiment", back_populates="project", cascade="all, delete-orphan")
    benchmarks = relationship("Benchmark", back_populates="project", cascade="all, delete-orphan")
    result_tables = relationship("ResultTable", back_populates="project", cascade="all, delete-orphan")
    final_reports = relationship("FinalReport", back_populates="project", cascade="all, delete-orphan")


class LifecycleStage(Base):
    __tablename__ = "lifecycle_stages"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    stage_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    guidance = Column(Text, nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    notes = Column(Text, default="", nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="lifecycle_stages")


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    hypothesis = Column(Text, default="", nullable=False)
    setup_notes = Column(Text, default="", nullable=False)
    result_summary = Column(Text, default="", nullable=False)
    metric_name = Column(String(255), default="", nullable=False)
    metric_value = Column(Float, nullable=True)
    status = Column(String(50), default="planned", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="experiments")
    benchmarks = relationship("Benchmark", back_populates="experiment")


class Benchmark(Base):
    __tablename__ = "benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id", ondelete="SET NULL"), nullable=True, index=True)
    dataset = Column(String(255), nullable=False)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Float, nullable=False)
    notes = Column(Text, default="", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="benchmarks")
    experiment = relationship("Experiment", back_populates="benchmarks")


class ResultTable(Base):
    __tablename__ = "result_tables"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    table_markdown = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="result_tables")


class FinalReport(Base):
    __tablename__ = "final_reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    discussion = Column(Text, default="", nullable=False)
    evaluation_summary = Column(Text, default="", nullable=False)
    latex_snippet = Column(Text, default="", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="final_reports")
