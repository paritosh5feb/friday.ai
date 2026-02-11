"""Pydantic schemas for lifecycle step operations."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Lifecycle Step Schemas
class LifecycleStepResponse(BaseModel):
    id: int
    project_id: int
    step_number: int
    step_name: str
    description: Optional[str] = None
    status: str
    notes: Optional[str] = None
    progress_percentage: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LifecycleStepUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)


# Research Paper Schemas (Step 1)
class ResearchPaperCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    authors: Optional[str] = None
    abstract: Optional[str] = None
    summary: Optional[str] = None
    source_url: Optional[str] = None
    doi: Optional[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    open_problems: Optional[str] = None
    proposal_notes: Optional[str] = None


class ResearchPaperUpdate(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    abstract: Optional[str] = None
    summary: Optional[str] = None
    source_url: Optional[str] = None
    doi: Optional[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    open_problems: Optional[str] = None
    proposal_notes: Optional[str] = None
    review_status: Optional[str] = None


class ResearchPaperResponse(BaseModel):
    id: int
    project_id: int
    title: str
    authors: Optional[str] = None
    abstract: Optional[str] = None
    summary: Optional[str] = None
    source_url: Optional[str] = None
    doi: Optional[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    open_problems: Optional[str] = None
    proposal_notes: Optional[str] = None
    review_status: str
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Experiment Schemas (Steps 2, 3, 4, 7)
class ExperimentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    experiment_type: str  # baseline, reproduction, partial, scaled
    description: Optional[str] = None
    hypothesis: Optional[str] = None
    methodology: Optional[str] = None
    dataset: Optional[str] = None
    model_architecture: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = None


class ExperimentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    hypothesis: Optional[str] = None
    methodology: Optional[str] = None
    dataset: Optional[str] = None
    model_architecture: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    results: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    conclusion: Optional[str] = None
    log_output: Optional[str] = None


class ExperimentResponse(BaseModel):
    id: int
    project_id: int
    name: str
    experiment_type: str
    description: Optional[str] = None
    hypothesis: Optional[str] = None
    methodology: Optional[str] = None
    dataset: Optional[str] = None
    model_architecture: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    results: Optional[Dict[str, Any]] = None
    status: str
    conclusion: Optional[str] = None
    log_output: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Benchmark Result Schemas (Step 5)
class BenchmarkResultCreate(BaseModel):
    benchmark_name: str = Field(..., min_length=1, max_length=255)
    dataset: Optional[str] = None
    model_name: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    environment: Optional[str] = None
    notes: Optional[str] = None
    is_baseline: bool = False


class BenchmarkResultUpdate(BaseModel):
    benchmark_name: Optional[str] = None
    dataset: Optional[str] = None
    model_name: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    environment: Optional[str] = None
    notes: Optional[str] = None
    is_baseline: Optional[bool] = None


class BenchmarkResultResponse(BaseModel):
    id: int
    project_id: int
    benchmark_name: str
    dataset: Optional[str] = None
    model_name: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    environment: Optional[str] = None
    notes: Optional[str] = None
    is_baseline: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Result Table Schemas (Step 6)
class ResultTableCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    table_data: Optional[Dict[str, Any]] = None
    table_type: str = "comparison"


class ResultTableUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    table_data: Optional[Dict[str, Any]] = None
    table_type: Optional[str] = None


class ResultTableResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    table_data: Optional[Dict[str, Any]] = None
    table_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# LaTeX Report Schemas (Step 9)
class LatexReportCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    template_type: str = "ieee"
    content: Optional[str] = None


class LatexReportUpdate(BaseModel):
    title: Optional[str] = None
    template_type: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None


class LatexReportResponse(BaseModel):
    id: int
    project_id: int
    title: str
    template_type: str
    content: Optional[str] = None
    compiled_pdf_path: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
