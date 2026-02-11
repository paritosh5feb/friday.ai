"""Models for AI Project Lifecycle management.

Lifecycle Steps:
1. Problem Statement Research - Download papers, create summaries, find open problems
2. Establish Baseline Experiments (SEH) - Validate hypothesis
3. Reproduce Current Solutions - Replicate existing work
4. Partial/Smallest Experiments - Run minimal experiments
5. Benchmark Evaluations - Run standard benchmarks
6. Create Result Tables - Tabulate results from steps 4-5
7. Scale Experiments - Scale up successful small experiments
8. Final Evaluation - Collation, discussion, evaluation
9. LaTeX Report Generation - Create publication-ready reports
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float,
    ForeignKey, Enum as SQLEnum, JSON, Boolean,
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class StepStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    BLOCKED = "blocked"


LIFECYCLE_STEP_NAMES = {
    1: "Problem Statement Research",
    2: "Establish Baseline Experiments (SEH)",
    3: "Reproduce Current Solutions",
    4: "Run Partial/Smallest Experiments",
    5: "Run Benchmark Evaluations",
    6: "Create Result Tables",
    7: "Scale Experiments",
    8: "Final Evaluation & Discussion",
    9: "LaTeX Report Generation",
}

LIFECYCLE_STEP_DESCRIPTIONS = {
    1: "Download research papers (Mendeley), create summaries in Google Docs, find open problem statements. Cycle through review, create proposal, and update.",
    2: "Establish baseline experiments to validate your hypothesis (SEH - Standard Experimental Hypothesis).",
    3: "Reproduce current state-of-the-art solutions to understand existing approaches.",
    4: "Start running partial experiments of the smallest possible experiment to validate approach.",
    5: "Run comprehensive benchmark evaluations against standard datasets and metrics.",
    6: "Create tables summarizing results from partial experiments and benchmark evaluations.",
    7: "If results look promising, scale up the small experiments to full-scale runs.",
    8: "Evaluation, collation, discussion, and evaluation of final results across all experiments.",
    9: "Generate publication-ready LaTeX reports with all results, tables, and analysis.",
}


class LifecycleStep(Base):
    __tablename__ = "lifecycle_steps"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    step_number = Column(Integer, nullable=False)  # 1-9
    step_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(StepStatus), default=StepStatus.NOT_STARTED)
    notes = Column(Text, nullable=True)
    progress_percentage = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="lifecycle_steps")


class ResearchPaper(Base):
    """Research papers for Step 1 - Problem Statement Research."""
    __tablename__ = "research_papers"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(500), nullable=False)
    authors = Column(String(500), nullable=True)
    abstract = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    source_url = Column(String(1000), nullable=True)
    doi = Column(String(255), nullable=True)
    year = Column(Integer, nullable=True)
    venue = Column(String(255), nullable=True)  # Conference/Journal name
    open_problems = Column(Text, nullable=True)  # JSON list of open problems found
    proposal_notes = Column(Text, nullable=True)
    review_status = Column(String(50), default="pending")  # pending, reviewed, proposal_created
    file_path = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="research_papers")


class Experiment(Base):
    """Experiments for Steps 2-4, 7 - Baseline, Reproduction, Partial, Scaled experiments."""
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    experiment_type = Column(String(50), nullable=False)  # baseline, reproduction, partial, scaled
    description = Column(Text, nullable=True)
    hypothesis = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)
    dataset = Column(String(255), nullable=True)
    model_architecture = Column(String(255), nullable=True)
    hyperparameters = Column(JSON, nullable=True)
    results = Column(JSON, nullable=True)  # {"metric_name": value}
    status = Column(String(50), default="planned")  # planned, running, completed, failed
    conclusion = Column(Text, nullable=True)
    log_output = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="experiments")


class BenchmarkResult(Base):
    """Benchmark evaluation results for Step 5."""
    __tablename__ = "benchmark_results"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    benchmark_name = Column(String(255), nullable=False)
    dataset = Column(String(255), nullable=True)
    model_name = Column(String(255), nullable=True)
    metrics = Column(JSON, nullable=True)  # {"accuracy": 0.95, "f1": 0.93, ...}
    environment = Column(Text, nullable=True)  # Hardware/software config
    notes = Column(Text, nullable=True)
    is_baseline = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="benchmark_results")


class ResultTable(Base):
    """Result tables for Step 6 - Tabulated results."""
    __tablename__ = "result_tables"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    table_data = Column(JSON, nullable=True)  # {"headers": [...], "rows": [[...]]}
    table_type = Column(String(50), default="comparison")  # comparison, ablation, summary
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="result_tables")


class LatexReport(Base):
    """LaTeX reports for Step 9."""
    __tablename__ = "latex_reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    template_type = Column(String(50), default="ieee")  # ieee, acm, neurips, custom
    content = Column(Text, nullable=True)  # Full LaTeX content
    compiled_pdf_path = Column(String(1000), nullable=True)
    status = Column(String(50), default="draft")  # draft, review, final
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="latex_reports")
