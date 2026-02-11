"""Lifecycle step management service."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.lifecycle import (
    LifecycleStep, StepStatus,
    ResearchPaper, Experiment, BenchmarkResult, ResultTable, LatexReport,
)
from app.models.project import Project
from app.schemas.lifecycle import (
    LifecycleStepUpdate,
    ResearchPaperCreate, ResearchPaperUpdate,
    ExperimentCreate, ExperimentUpdate,
    BenchmarkResultCreate, BenchmarkResultUpdate,
    ResultTableCreate, ResultTableUpdate,
    LatexReportCreate, LatexReportUpdate,
)


class LifecycleService:
    """Service for managing lifecycle steps and related entities."""

    # ==================== Lifecycle Steps ====================

    @staticmethod
    def get_lifecycle_steps(db: Session, project_id: int) -> List[LifecycleStep]:
        """Get all lifecycle steps for a project."""
        return (
            db.query(LifecycleStep)
            .filter(LifecycleStep.project_id == project_id)
            .order_by(LifecycleStep.step_number)
            .all()
        )

    @staticmethod
    def get_lifecycle_step(db: Session, project_id: int, step_number: int) -> LifecycleStep:
        """Get a specific lifecycle step."""
        step = (
            db.query(LifecycleStep)
            .filter(
                LifecycleStep.project_id == project_id,
                LifecycleStep.step_number == step_number,
            )
            .first()
        )
        if not step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lifecycle step {step_number} not found",
            )
        return step

    @staticmethod
    def update_lifecycle_step(
        db: Session, project_id: int, step_number: int, update_data: LifecycleStepUpdate
    ) -> LifecycleStep:
        """Update a lifecycle step."""
        step = LifecycleService.get_lifecycle_step(db, project_id, step_number)
        update_dict = update_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(step, key, value)

        # Auto-set timestamps
        if update_data.status == "in_progress" and not step.started_at:
            step.started_at = datetime.utcnow()
        if update_data.status == "completed":
            step.completed_at = datetime.utcnow()
            step.progress_percentage = 100

        step.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(step)

        # Update project current_step if advancing
        if update_data.status == "completed":
            project = db.query(Project).filter(Project.id == project_id).first()
            if project and project.current_step == step_number and step_number < 9:
                project.current_step = step_number + 1
                project.status = "in_progress"
                db.commit()

        return step

    # ==================== Research Papers (Step 1) ====================

    @staticmethod
    def create_research_paper(
        db: Session, project_id: int, paper_data: ResearchPaperCreate
    ) -> ResearchPaper:
        """Create a new research paper entry."""
        paper = ResearchPaper(
            project_id=project_id,
            **paper_data.model_dump(),
        )
        db.add(paper)
        db.commit()
        db.refresh(paper)
        return paper

    @staticmethod
    def get_research_papers(db: Session, project_id: int) -> List[ResearchPaper]:
        """Get all research papers for a project."""
        return (
            db.query(ResearchPaper)
            .filter(ResearchPaper.project_id == project_id)
            .order_by(ResearchPaper.created_at.desc())
            .all()
        )

    @staticmethod
    def get_research_paper(db: Session, paper_id: int, project_id: int) -> ResearchPaper:
        """Get a specific research paper."""
        paper = (
            db.query(ResearchPaper)
            .filter(ResearchPaper.id == paper_id, ResearchPaper.project_id == project_id)
            .first()
        )
        if not paper:
            raise HTTPException(status_code=404, detail="Research paper not found")
        return paper

    @staticmethod
    def update_research_paper(
        db: Session, paper_id: int, project_id: int, update_data: ResearchPaperUpdate
    ) -> ResearchPaper:
        """Update a research paper."""
        paper = LifecycleService.get_research_paper(db, paper_id, project_id)
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(paper, key, value)
        paper.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(paper)
        return paper

    @staticmethod
    def delete_research_paper(db: Session, paper_id: int, project_id: int) -> None:
        """Delete a research paper."""
        paper = LifecycleService.get_research_paper(db, paper_id, project_id)
        db.delete(paper)
        db.commit()

    # ==================== Experiments (Steps 2, 3, 4, 7) ====================

    @staticmethod
    def create_experiment(
        db: Session, project_id: int, experiment_data: ExperimentCreate
    ) -> Experiment:
        """Create a new experiment."""
        experiment = Experiment(
            project_id=project_id,
            **experiment_data.model_dump(),
        )
        db.add(experiment)
        db.commit()
        db.refresh(experiment)
        return experiment

    @staticmethod
    def get_experiments(
        db: Session, project_id: int, experiment_type: Optional[str] = None
    ) -> List[Experiment]:
        """Get experiments for a project, optionally filtered by type."""
        query = db.query(Experiment).filter(Experiment.project_id == project_id)
        if experiment_type:
            query = query.filter(Experiment.experiment_type == experiment_type)
        return query.order_by(Experiment.created_at.desc()).all()

    @staticmethod
    def get_experiment(db: Session, experiment_id: int, project_id: int) -> Experiment:
        """Get a specific experiment."""
        experiment = (
            db.query(Experiment)
            .filter(Experiment.id == experiment_id, Experiment.project_id == project_id)
            .first()
        )
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        return experiment

    @staticmethod
    def update_experiment(
        db: Session, experiment_id: int, project_id: int, update_data: ExperimentUpdate
    ) -> Experiment:
        """Update an experiment."""
        experiment = LifecycleService.get_experiment(db, experiment_id, project_id)
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(experiment, key, value)

        # Auto-set timestamps
        if update_data.status == "running" and not experiment.started_at:
            experiment.started_at = datetime.utcnow()
        if update_data.status in ("completed", "failed"):
            experiment.completed_at = datetime.utcnow()

        experiment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(experiment)
        return experiment

    @staticmethod
    def delete_experiment(db: Session, experiment_id: int, project_id: int) -> None:
        """Delete an experiment."""
        experiment = LifecycleService.get_experiment(db, experiment_id, project_id)
        db.delete(experiment)
        db.commit()

    # ==================== Benchmark Results (Step 5) ====================

    @staticmethod
    def create_benchmark_result(
        db: Session, project_id: int, benchmark_data: BenchmarkResultCreate
    ) -> BenchmarkResult:
        """Create a new benchmark result."""
        benchmark = BenchmarkResult(
            project_id=project_id,
            **benchmark_data.model_dump(),
        )
        db.add(benchmark)
        db.commit()
        db.refresh(benchmark)
        return benchmark

    @staticmethod
    def get_benchmark_results(db: Session, project_id: int) -> List[BenchmarkResult]:
        """Get all benchmark results for a project."""
        return (
            db.query(BenchmarkResult)
            .filter(BenchmarkResult.project_id == project_id)
            .order_by(BenchmarkResult.created_at.desc())
            .all()
        )

    @staticmethod
    def get_benchmark_result(db: Session, benchmark_id: int, project_id: int) -> BenchmarkResult:
        """Get a specific benchmark result."""
        benchmark = (
            db.query(BenchmarkResult)
            .filter(BenchmarkResult.id == benchmark_id, BenchmarkResult.project_id == project_id)
            .first()
        )
        if not benchmark:
            raise HTTPException(status_code=404, detail="Benchmark result not found")
        return benchmark

    @staticmethod
    def update_benchmark_result(
        db: Session, benchmark_id: int, project_id: int, update_data: BenchmarkResultUpdate
    ) -> BenchmarkResult:
        """Update a benchmark result."""
        benchmark = LifecycleService.get_benchmark_result(db, benchmark_id, project_id)
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(benchmark, key, value)
        benchmark.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(benchmark)
        return benchmark

    @staticmethod
    def delete_benchmark_result(db: Session, benchmark_id: int, project_id: int) -> None:
        """Delete a benchmark result."""
        benchmark = LifecycleService.get_benchmark_result(db, benchmark_id, project_id)
        db.delete(benchmark)
        db.commit()

    # ==================== Result Tables (Step 6) ====================

    @staticmethod
    def create_result_table(
        db: Session, project_id: int, table_data: ResultTableCreate
    ) -> ResultTable:
        """Create a new result table."""
        table = ResultTable(
            project_id=project_id,
            **table_data.model_dump(),
        )
        db.add(table)
        db.commit()
        db.refresh(table)
        return table

    @staticmethod
    def get_result_tables(db: Session, project_id: int) -> List[ResultTable]:
        """Get all result tables for a project."""
        return (
            db.query(ResultTable)
            .filter(ResultTable.project_id == project_id)
            .order_by(ResultTable.created_at.desc())
            .all()
        )

    @staticmethod
    def get_result_table(db: Session, table_id: int, project_id: int) -> ResultTable:
        """Get a specific result table."""
        table = (
            db.query(ResultTable)
            .filter(ResultTable.id == table_id, ResultTable.project_id == project_id)
            .first()
        )
        if not table:
            raise HTTPException(status_code=404, detail="Result table not found")
        return table

    @staticmethod
    def update_result_table(
        db: Session, table_id: int, project_id: int, update_data: ResultTableUpdate
    ) -> ResultTable:
        """Update a result table."""
        table = LifecycleService.get_result_table(db, table_id, project_id)
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(table, key, value)
        table.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(table)
        return table

    @staticmethod
    def delete_result_table(db: Session, table_id: int, project_id: int) -> None:
        """Delete a result table."""
        table = LifecycleService.get_result_table(db, table_id, project_id)
        db.delete(table)
        db.commit()

    # ==================== Auto-generate Result Tables ====================

    @staticmethod
    def auto_generate_result_table(db: Session, project_id: int) -> ResultTable:
        """Auto-generate a comparison table from experiments and benchmarks."""
        experiments = (
            db.query(Experiment)
            .filter(Experiment.project_id == project_id, Experiment.results.isnot(None))
            .all()
        )
        benchmarks = (
            db.query(BenchmarkResult)
            .filter(BenchmarkResult.project_id == project_id, BenchmarkResult.metrics.isnot(None))
            .all()
        )

        # Collect all metric names
        all_metrics = set()
        for exp in experiments:
            if exp.results:
                all_metrics.update(exp.results.keys())
        for bench in benchmarks:
            if bench.metrics:
                all_metrics.update(bench.metrics.keys())

        headers = ["Name", "Type"] + sorted(all_metrics)
        rows = []

        for exp in experiments:
            row = [exp.name, f"Experiment ({exp.experiment_type})"]
            for metric in sorted(all_metrics):
                val = exp.results.get(metric, "-") if exp.results else "-"
                row.append(str(val))
            rows.append(row)

        for bench in benchmarks:
            row = [bench.benchmark_name, "Benchmark" + (" (baseline)" if bench.is_baseline else "")]
            for metric in sorted(all_metrics):
                val = bench.metrics.get(metric, "-") if bench.metrics else "-"
                row.append(str(val))
            rows.append(row)

        table = ResultTable(
            project_id=project_id,
            title="Auto-generated Comparison Table",
            description="Automatically generated from experiments and benchmark results",
            table_data={"headers": headers, "rows": rows},
            table_type="comparison",
        )
        db.add(table)
        db.commit()
        db.refresh(table)
        return table

    # ==================== LaTeX Reports (Step 9) ====================

    @staticmethod
    def create_latex_report(
        db: Session, project_id: int, report_data: LatexReportCreate
    ) -> LatexReport:
        """Create a new LaTeX report."""
        report = LatexReport(
            project_id=project_id,
            **report_data.model_dump(),
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def get_latex_reports(db: Session, project_id: int) -> List[LatexReport]:
        """Get all LaTeX reports for a project."""
        return (
            db.query(LatexReport)
            .filter(LatexReport.project_id == project_id)
            .order_by(LatexReport.created_at.desc())
            .all()
        )

    @staticmethod
    def get_latex_report(db: Session, report_id: int, project_id: int) -> LatexReport:
        """Get a specific LaTeX report."""
        report = (
            db.query(LatexReport)
            .filter(LatexReport.id == report_id, LatexReport.project_id == project_id)
            .first()
        )
        if not report:
            raise HTTPException(status_code=404, detail="LaTeX report not found")
        return report

    @staticmethod
    def update_latex_report(
        db: Session, report_id: int, project_id: int, update_data: LatexReportUpdate
    ) -> LatexReport:
        """Update a LaTeX report."""
        report = LifecycleService.get_latex_report(db, report_id, project_id)
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(report, key, value)
        report.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def delete_latex_report(db: Session, report_id: int, project_id: int) -> None:
        """Delete a LaTeX report."""
        report = LifecycleService.get_latex_report(db, report_id, project_id)
        db.delete(report)
        db.commit()
