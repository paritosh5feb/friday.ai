from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    created_at: datetime


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    objective: str | None = Field(default=None, min_length=5)
    hypothesis: str | None = Field(default=None, min_length=5)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    objective: str | None = Field(default=None, min_length=5)
    hypothesis: str | None = Field(default=None, min_length=5)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    objective: str
    hypothesis: str
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    items: list[ProjectRead]
    total: int


LifecycleStatus = Literal["pending", "in_progress", "completed", "blocked"]


class LifecycleStageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    stage_number: int
    title: str
    guidance: str
    status: LifecycleStatus
    notes: str
    updated_at: datetime


class LifecycleStageUpdate(BaseModel):
    status: LifecycleStatus | None = None
    notes: str | None = None


ExperimentKind = Literal["baseline", "reproduction", "partial", "benchmark", "scaled", "final"]
ExperimentStatus = Literal["planned", "running", "completed", "failed"]


class ExperimentCreate(BaseModel):
    kind: ExperimentKind = "partial"
    title: str | None = Field(default=None, min_length=2, max_length=255)
    # Compatibility with the partially-built friday.com payload.
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    hypothesis: str = ""
    setup_notes: str = ""
    result_summary: str = ""
    metric_name: str = ""
    metric_value: float | None = None
    status: ExperimentStatus = "planned"

    @model_validator(mode="after")
    def normalize_fields(self) -> "ExperimentCreate":
        if self.title is None and self.name is not None:
            self.title = self.name
        if self.title is None:
            msg = "Either title or name must be provided"
            raise ValueError(msg)
        if self.description and not self.setup_notes:
            self.setup_notes = self.description
        return self


class ExperimentUpdate(BaseModel):
    kind: ExperimentKind | None = None
    title: str | None = Field(default=None, min_length=2, max_length=255)
    hypothesis: str | None = None
    setup_notes: str | None = None
    result_summary: str | None = None
    metric_name: str | None = None
    metric_value: float | None = None
    status: ExperimentStatus | None = None


class ExperimentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    kind: ExperimentKind
    title: str
    hypothesis: str
    setup_notes: str
    result_summary: str
    metric_name: str
    metric_value: float | None
    status: ExperimentStatus
    created_at: datetime
    updated_at: datetime


class BenchmarkCreate(BaseModel):
    experiment_id: int | None = None
    dataset: str = Field(min_length=1, max_length=255)
    metric_name: str = Field(min_length=1, max_length=255)
    metric_value: float
    notes: str = ""


class BenchmarkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    experiment_id: int | None
    dataset: str
    metric_name: str
    metric_value: float
    notes: str
    created_at: datetime


class ResultTableCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    table_markdown: str = Field(min_length=3)


class ResultTableRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    table_markdown: str
    created_at: datetime


class FinalReportCreate(BaseModel):
    discussion: str = ""
    evaluation_summary: str = ""
    latex_snippet: str = ""


class FinalReportUpdate(BaseModel):
    discussion: str | None = None
    evaluation_summary: str | None = None
    latex_snippet: str | None = None


class FinalReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    discussion: str
    evaluation_summary: str
    latex_snippet: str
    created_at: datetime
    updated_at: datetime


class ProjectDetail(ProjectRead):
    lifecycle_stages: list[LifecycleStageRead]
    experiments: list[ExperimentRead]
    benchmarks: list[BenchmarkRead]
    result_tables: list[ResultTableRead]
    final_reports: list[FinalReportRead]


RunStatus = Literal["queued", "running", "completed", "failed"]


class RunCreate(BaseModel):
    experiment_id: int
    status: RunStatus = "queued"


class RunFinish(BaseModel):
    status: Literal["completed", "failed"]


class RunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    experiment_id: int
    status: RunStatus
    started_at: datetime
    finished_at: datetime | None


class RunParamCreate(BaseModel):
    key: str = Field(min_length=1, max_length=255)
    value: str = Field(min_length=1, max_length=1024)


class RunParamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: int
    key: str
    value: str


class RunMetricCreate(BaseModel):
    key: str = Field(min_length=1, max_length=255)
    value: float
    step: int = Field(ge=0)


class RunMetricRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: int
    key: str
    value: float
    step: int
    timestamp: datetime


class RunDetailRead(RunRead):
    params: list[RunParamRead]
    metrics: list[RunMetricRead]


class ProjectLifecycleSummary(BaseModel):
    project_id: int
    stage_status_counts: dict[str, int]
    experiment_counts_by_kind: dict[str, int]
    run_status_counts: dict[str, int]
    benchmarks_logged: int
    result_tables_created: int
    final_reports_created: int
    ready_to_scale: bool
    ready_for_final_evaluation: bool
