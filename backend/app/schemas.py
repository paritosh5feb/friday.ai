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


ProjectRole = Literal["admin", "manager", "researcher", "reviewer", "viewer"]
ProjectScope = Literal[
    "manage_members",
    "manage_lifecycle",
    "manage_experiments",
    "manage_runs",
    "manage_tasks",
    "manage_pages",
]


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


class ProjectMemberCreate(BaseModel):
    email: EmailStr
    role: ProjectRole = "researcher"
    scopes: list[ProjectScope] | None = None


class ProjectMemberUpdate(BaseModel):
    role: ProjectRole | None = None
    scopes: list[ProjectScope] | None = None


class ProjectMemberRead(BaseModel):
    id: int
    project_id: int
    user_id: int
    user_email: EmailStr
    user_full_name: str
    role: ProjectRole
    scopes: list[ProjectScope]
    created_at: datetime


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


TaskStatus = Literal["backlog", "todo", "in_progress", "in_review", "done"]
TaskPriority = Literal["low", "medium", "high", "critical"]


class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str = ""
    status: TaskStatus = "todo"
    priority: TaskPriority = "medium"
    assignee_id: int | None = None
    stage_number: int | None = Field(default=None, ge=1, le=8)
    story_points: int | None = Field(default=None, ge=0)
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: int | None = None
    stage_number: int | None = Field(default=None, ge=1, le=8)
    story_points: int | None = Field(default=None, ge=0)
    due_date: datetime | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee_id: int | None
    assignee_name: str | None = None
    reporter_id: int | None
    reporter_name: str | None = None
    stage_number: int | None
    story_points: int | None
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime


class KanbanBoardResponse(BaseModel):
    project_id: int
    columns: dict[TaskStatus, list[TaskRead]]


class ProjectPageCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    content: str = ""
    parent_page_id: int | None = None


class ProjectPageUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    content: str | None = None
    parent_page_id: int | None = None


class ProjectPageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    content: str
    parent_page_id: int | None
    author_id: int | None
    author_name: str | None = None
    updated_by_id: int | None
    updated_by_name: str | None = None
    created_at: datetime
    updated_at: datetime


class RunComparisonItem(BaseModel):
    run_id: int
    experiment_id: int
    experiment_title: str
    status: RunStatus
    selected_metric: float | None
    metrics: dict[str, float]
    params: dict[str, str]
    started_at: datetime
    finished_at: datetime | None


class RunComparisonResponse(BaseModel):
    project_id: int
    metric_key: str | None
    items: list[RunComparisonItem]
    best_run_id: int | None
    best_metric_value: float | None


class ProjectLifecycleSummary(BaseModel):
    project_id: int
    stage_status_counts: dict[str, int]
    experiment_counts_by_kind: dict[str, int]
    run_status_counts: dict[str, int]
    benchmarks_logged: int
    result_tables_created: int
    final_reports_created: int
    task_status_counts: dict[str, int]
    documentation_pages_created: int
    ready_to_scale: bool
    ready_for_final_evaluation: bool
