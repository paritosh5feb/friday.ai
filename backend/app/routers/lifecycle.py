"""Lifecycle management API endpoints.

Manages all 9 lifecycle steps and their associated data:
- Research Papers (Step 1)
- Experiments (Steps 2, 3, 4, 7)
- Benchmark Results (Step 5)
- Result Tables (Step 6)
- LaTeX Reports (Step 9)
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.services.project_service import ProjectService
from app.services.lifecycle_service import LifecycleService
from app.services.latex_service import LatexService
from app.schemas.lifecycle import (
    LifecycleStepResponse, LifecycleStepUpdate,
    ResearchPaperCreate, ResearchPaperUpdate, ResearchPaperResponse,
    ExperimentCreate, ExperimentUpdate, ExperimentResponse,
    BenchmarkResultCreate, BenchmarkResultUpdate, BenchmarkResultResponse,
    ResultTableCreate, ResultTableUpdate, ResultTableResponse,
    LatexReportCreate, LatexReportUpdate, LatexReportResponse,
)

router = APIRouter(prefix="/api/projects/{project_id}", tags=["Lifecycle"])


def _verify_project(project_id: int, current_user: User, db: Session):
    """Helper to verify project ownership."""
    return ProjectService.get_project(db, project_id, current_user.id)


# ==================== Lifecycle Steps ====================

@router.get("/lifecycle", response_model=List[LifecycleStepResponse])
async def get_lifecycle_steps(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all lifecycle steps for a project."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.get_lifecycle_steps(db, project_id)


@router.get("/lifecycle/{step_number}", response_model=LifecycleStepResponse)
async def get_lifecycle_step(
    project_id: int,
    step_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific lifecycle step."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.get_lifecycle_step(db, project_id, step_number)


@router.put("/lifecycle/{step_number}", response_model=LifecycleStepResponse)
async def update_lifecycle_step(
    project_id: int,
    step_number: int,
    update_data: LifecycleStepUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a lifecycle step status and notes."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.update_lifecycle_step(db, project_id, step_number, update_data)


# ==================== Research Papers (Step 1) ====================

@router.post("/papers", response_model=ResearchPaperResponse, status_code=201)
async def create_research_paper(
    project_id: int,
    paper_data: ResearchPaperCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a research paper to the project."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.create_research_paper(db, project_id, paper_data)


@router.get("/papers", response_model=List[ResearchPaperResponse])
async def list_research_papers(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all research papers for a project."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.get_research_papers(db, project_id)


@router.get("/papers/{paper_id}", response_model=ResearchPaperResponse)
async def get_research_paper(
    project_id: int,
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific research paper."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.get_research_paper(db, paper_id, project_id)


@router.put("/papers/{paper_id}", response_model=ResearchPaperResponse)
async def update_research_paper(
    project_id: int,
    paper_id: int,
    update_data: ResearchPaperUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a research paper."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.update_research_paper(db, paper_id, project_id, update_data)


@router.delete("/papers/{paper_id}", status_code=204)
async def delete_research_paper(
    project_id: int,
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a research paper."""
    _verify_project(project_id, current_user, db)
    LifecycleService.delete_research_paper(db, paper_id, project_id)


# ==================== Experiments (Steps 2, 3, 4, 7) ====================

@router.post("/experiments", response_model=ExperimentResponse, status_code=201)
async def create_experiment(
    project_id: int,
    experiment_data: ExperimentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new experiment."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.create_experiment(db, project_id, experiment_data)


@router.get("/experiments", response_model=List[ExperimentResponse])
async def list_experiments(
    project_id: int,
    experiment_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List experiments, optionally filtered by type (baseline, reproduction, partial, scaled)."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.get_experiments(db, project_id, experiment_type)


@router.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    project_id: int,
    experiment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific experiment."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.get_experiment(db, experiment_id, project_id)


@router.put("/experiments/{experiment_id}", response_model=ExperimentResponse)
async def update_experiment(
    project_id: int,
    experiment_id: int,
    update_data: ExperimentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an experiment."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.update_experiment(db, experiment_id, project_id, update_data)


@router.delete("/experiments/{experiment_id}", status_code=204)
async def delete_experiment(
    project_id: int,
    experiment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an experiment."""
    _verify_project(project_id, current_user, db)
    LifecycleService.delete_experiment(db, experiment_id, project_id)


# ==================== Benchmark Results (Step 5) ====================

@router.post("/benchmarks", response_model=BenchmarkResultResponse, status_code=201)
async def create_benchmark_result(
    project_id: int,
    benchmark_data: BenchmarkResultCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new benchmark result."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.create_benchmark_result(db, project_id, benchmark_data)


@router.get("/benchmarks", response_model=List[BenchmarkResultResponse])
async def list_benchmark_results(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all benchmark results for a project."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.get_benchmark_results(db, project_id)


@router.get("/benchmarks/{benchmark_id}", response_model=BenchmarkResultResponse)
async def get_benchmark_result(
    project_id: int,
    benchmark_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific benchmark result."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.get_benchmark_result(db, benchmark_id, project_id)


@router.put("/benchmarks/{benchmark_id}", response_model=BenchmarkResultResponse)
async def update_benchmark_result(
    project_id: int,
    benchmark_id: int,
    update_data: BenchmarkResultUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a benchmark result."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.update_benchmark_result(db, benchmark_id, project_id, update_data)


@router.delete("/benchmarks/{benchmark_id}", status_code=204)
async def delete_benchmark_result(
    project_id: int,
    benchmark_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a benchmark result."""
    _verify_project(project_id, current_user, db)
    LifecycleService.delete_benchmark_result(db, benchmark_id, project_id)


# ==================== Result Tables (Step 6) ====================

@router.post("/tables", response_model=ResultTableResponse, status_code=201)
async def create_result_table(
    project_id: int,
    table_data: ResultTableCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new result table."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.create_result_table(db, project_id, table_data)


@router.post("/tables/auto-generate", response_model=ResultTableResponse, status_code=201)
async def auto_generate_result_table(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Auto-generate a comparison table from experiments and benchmarks."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.auto_generate_result_table(db, project_id)


@router.get("/tables", response_model=List[ResultTableResponse])
async def list_result_tables(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all result tables for a project."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.get_result_tables(db, project_id)


@router.get("/tables/{table_id}", response_model=ResultTableResponse)
async def get_result_table(
    project_id: int,
    table_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific result table."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.get_result_table(db, table_id, project_id)


@router.put("/tables/{table_id}", response_model=ResultTableResponse)
async def update_result_table(
    project_id: int,
    table_id: int,
    update_data: ResultTableUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a result table."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.update_result_table(db, table_id, project_id, update_data)


@router.delete("/tables/{table_id}", status_code=204)
async def delete_result_table(
    project_id: int,
    table_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a result table."""
    _verify_project(project_id, current_user, db)
    LifecycleService.delete_result_table(db, table_id, project_id)


# ==================== LaTeX Reports (Step 9) ====================

@router.post("/reports", response_model=LatexReportResponse, status_code=201)
async def create_latex_report(
    project_id: int,
    report_data: LatexReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new LaTeX report."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.create_latex_report(db, project_id, report_data)


@router.post("/reports/generate", response_model=LatexReportResponse, status_code=201)
async def generate_full_latex_report(
    project_id: int,
    template_type: str = Query("ieee", description="Template: ieee, acm, neurips, custom"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Auto-generate a complete LaTeX report from all project data."""
    project = _verify_project(project_id, current_user, db)
    content = LatexService.generate_full_report(db, project, template_type)

    report_data = LatexReportCreate(
        title=f"{project.title} - Research Report",
        template_type=template_type,
        content=content,
    )
    return LifecycleService.create_latex_report(db, project_id, report_data)


@router.get("/reports", response_model=List[LatexReportResponse])
async def list_latex_reports(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all LaTeX reports for a project."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.get_latex_reports(db, project_id)


@router.get("/reports/{report_id}", response_model=LatexReportResponse)
async def get_latex_report(
    project_id: int,
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific LaTeX report."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.get_latex_report(db, report_id, project_id)


@router.put("/reports/{report_id}", response_model=LatexReportResponse)
async def update_latex_report(
    project_id: int,
    report_id: int,
    update_data: LatexReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a LaTeX report."""
    _verify_project(project_id, current_user, db)
    return LifecycleService.update_latex_report(db, report_id, project_id, update_data)


@router.delete("/reports/{report_id}", status_code=204)
async def delete_latex_report(
    project_id: int,
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a LaTeX report."""
    _verify_project(project_id, current_user, db)
    LifecycleService.delete_latex_report(db, report_id, project_id)
