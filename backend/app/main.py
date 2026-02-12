from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, func, inspect, or_, text
from sqlalchemy.orm import Session, selectinload

from .config import settings
from .database import Base, engine, get_db
from .dependencies import get_current_user
from .lifecycle import LIFECYCLE_TEMPLATE, LIFECYCLE_STATUSES
from .models import (
    Benchmark,
    Experiment,
    FinalReport,
    LifecycleStage,
    ProjectMember,
    ProjectPage,
    Project,
    ResultTable,
    Run,
    RunMetric,
    RunParam,
    Task,
    User,
)
from .permissions import has_scope, normalize_member_scopes, parse_scopes, serialize_scopes
from .schemas import (
    BenchmarkCreate,
    BenchmarkRead,
    ExperimentCreate,
    ExperimentRead,
    ExperimentUpdate,
    FinalReportCreate,
    FinalReportRead,
    FinalReportUpdate,
    LifecycleStageRead,
    LifecycleStageUpdate,
    KanbanBoardResponse,
    ProjectMemberCreate,
    ProjectMemberRead,
    ProjectMemberUpdate,
    ProjectPageCreate,
    ProjectPageRead,
    ProjectPageUpdate,
    ProjectCreate,
    ProjectDetail,
    ProjectLifecycleSummary,
    ProjectListResponse,
    ProjectRead,
    RunComparisonItem,
    RunComparisonResponse,
    ProjectUpdate,
    ResultTableCreate,
    ResultTableRead,
    RunCreate,
    RunDetailRead,
    RunFinish,
    RunMetricCreate,
    RunMetricRead,
    RunParamCreate,
    RunParamRead,
    RunRead,
    TaskCreate,
    TaskRead,
    TaskUpdate,
    Token,
    UserCreate,
    UserLogin,
    UserRead,
)
from .security import create_access_token, hash_password, verify_password


Base.metadata.create_all(bind=engine)


def run_lightweight_migrations() -> None:
    inspector = inspect(engine)
    if inspector.has_table("projects"):
        project_columns = {column["name"] for column in inspector.get_columns("projects")}
        if "description" not in project_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE projects ADD COLUMN description TEXT NOT NULL DEFAULT ''"))
    if inspector.has_table("project_members"):
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT OR IGNORE INTO project_members (project_id, user_id, role, scopes, created_at)
                    SELECT p.id, p.owner_id, 'admin',
                           'manage_members,manage_lifecycle,manage_experiments,manage_runs,manage_tasks,manage_pages',
                           CURRENT_TIMESTAMP
                    FROM projects p
                    """
                )
            )


run_lightweight_migrations()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_scope_or_403(member: ProjectMember | None, scope: str) -> None:
    if not has_scope(member, scope):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Missing scope: {scope}")


def ensure_owner_membership(db: Session, project: Project) -> ProjectMember:
    owner_member = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project.id, ProjectMember.user_id == project.owner_id)
        .first()
    )
    if owner_member:
        return owner_member

    owner_member = ProjectMember(
        project_id=project.id,
        user_id=project.owner_id,
        role="admin",
        scopes=serialize_scopes(normalize_member_scopes(role="admin", requested_scopes=None)),
    )
    db.add(owner_member)
    db.commit()
    db.refresh(owner_member)
    return owner_member


def get_project_with_member_or_404(db: Session, user: User, project_id: int) -> tuple[Project, ProjectMember | None]:
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .options(
            selectinload(Project.lifecycle_stages),
            selectinload(Project.experiments).selectinload(Experiment.runs),
            selectinload(Project.benchmarks),
            selectinload(Project.result_tables),
            selectinload(Project.final_reports),
            selectinload(Project.members).selectinload(ProjectMember.user),
        )
        .first()
    )
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if user.id == project.owner_id:
        return project, None

    membership = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project.id, ProjectMember.user_id == user.id)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return project, membership


def get_owned_project_or_404(db: Session, user: User, project_id: int) -> Project:
    project, _ = get_project_with_member_or_404(db=db, user=user, project_id=project_id)
    return project


def get_experiment_with_member_or_404(
    db: Session,
    user: User,
    experiment_id: int,
) -> tuple[Experiment, ProjectMember | None]:
    experiment = db.query(Experiment).options(selectinload(Experiment.runs)).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found")
    _, membership = get_project_with_member_or_404(db=db, user=user, project_id=experiment.project_id)
    return experiment, membership


def get_owned_experiment_or_404(db: Session, user: User, experiment_id: int) -> Experiment:
    experiment, _ = get_experiment_with_member_or_404(db=db, user=user, experiment_id=experiment_id)
    return experiment


def get_run_with_member_or_404(db: Session, user: User, run_id: int) -> tuple[Run, ProjectMember | None]:
    run = (
        db.query(Run)
        .options(selectinload(Run.params), selectinload(Run.metrics), selectinload(Run.experiment))
        .filter(Run.id == run_id)
        .first()
    )
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    _, membership = get_project_with_member_or_404(db=db, user=user, project_id=run.experiment.project_id)
    return run, membership


def get_owned_run_or_404(db: Session, user: User, run_id: int) -> Run:
    run, _ = get_run_with_member_or_404(db=db, user=user, run_id=run_id)
    return run


def serialize_member(member: ProjectMember) -> ProjectMemberRead:
    return ProjectMemberRead(
        id=member.id,
        project_id=member.project_id,
        user_id=member.user_id,
        user_email=member.user.email,
        user_full_name=member.user.full_name,
        role=member.role,
        scopes=parse_scopes(member.scopes),
        created_at=member.created_at,
    )


def serialize_task(task: Task) -> TaskRead:
    return TaskRead(
        id=task.id,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        assignee_id=task.assignee_id,
        assignee_name=task.assignee.full_name if task.assignee else None,
        reporter_id=task.reporter_id,
        reporter_name=task.reporter.full_name if task.reporter else None,
        stage_number=task.stage_number,
        story_points=task.story_points,
        due_date=task.due_date,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def serialize_page(page: ProjectPage) -> ProjectPageRead:
    return ProjectPageRead(
        id=page.id,
        project_id=page.project_id,
        title=page.title,
        content=page.content,
        parent_page_id=page.parent_page_id,
        author_id=page.author_id,
        author_name=page.author.full_name if page.author else None,
        updated_by_id=page.updated_by_id,
        updated_by_name=page.updated_by.full_name if page.updated_by else None,
        created_at=page.created_at,
        updated_at=page.updated_at,
    )


def ensure_assignee_in_project(db: Session, project: Project, assignee_id: int | None) -> None:
    if assignee_id is None:
        return
    if assignee_id == project.owner_id:
        return
    membership = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project.id, ProjectMember.user_id == assignee_id)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee is not a project member")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    # Preserved for compatibility with the friday.com backend style.
    return {"creator": "Paritosh", "service": settings.app_name}


@app.get("/db-check")
def db_check(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"db": "connected"}


@app.post(f"{settings.api_prefix}/auth/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)) -> Token:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(subject=user.email)
    return Token(access_token=token)


@app.post(f"{settings.api_prefix}/auth/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token(subject=user.email)
    return Token(access_token=token)


@app.get(f"{settings.api_prefix}/auth/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user


@app.post(f"{settings.api_prefix}/projects", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectDetail:
    objective = payload.objective or payload.description or "Objective to be refined through literature review."
    hypothesis = payload.hypothesis or "Hypothesis to validate during baseline and reproduction experiments."
    project = Project(
        owner_id=current_user.id,
        name=payload.name,
        description=payload.description or "",
        objective=objective,
        hypothesis=hypothesis,
    )
    db.add(project)
    db.flush()

    for stage in LIFECYCLE_TEMPLATE:
        db.add(
            LifecycleStage(
                project_id=project.id,
                stage_number=stage["stage_number"],
                title=stage["title"],
                guidance=stage["guidance"],
            )
        )
    db.add(
        ProjectMember(
            project_id=project.id,
            user_id=current_user.id,
            role="admin",
            scopes=serialize_scopes(normalize_member_scopes(role="admin", requested_scopes=None)),
        )
    )

    db.commit()
    return get_owned_project_or_404(db=db, user=current_user, project_id=project.id)


@app.get(f"{settings.api_prefix}/projects", response_model=list[ProjectRead])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectRead]:
    return (
        db.query(Project)
        .outerjoin(
            ProjectMember,
            and_(ProjectMember.project_id == Project.id, ProjectMember.user_id == current_user.id),
        )
        .filter(or_(Project.owner_id == current_user.id, ProjectMember.user_id == current_user.id))
        .distinct()
        .order_by(Project.created_at.desc())
        .all()
    )


@app.get(f"{settings.api_prefix}/projects/paginated", response_model=ProjectListResponse)
def list_projects_paginated(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectListResponse:
    project_ids = (
        db.query(Project.id)
        .outerjoin(
            ProjectMember,
            and_(ProjectMember.project_id == Project.id, ProjectMember.user_id == current_user.id),
        )
        .filter(or_(Project.owner_id == current_user.id, ProjectMember.user_id == current_user.id))
        .distinct()
        .subquery()
    )
    total = db.query(func.count()).select_from(project_ids).scalar() or 0
    projects = (
        db.query(Project)
        .outerjoin(
            ProjectMember,
            and_(ProjectMember.project_id == Project.id, ProjectMember.user_id == current_user.id),
        )
        .filter(or_(Project.owner_id == current_user.id, ProjectMember.user_id == current_user.id))
        .distinct()
        .order_by(Project.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return ProjectListResponse(items=projects, total=total)


@app.get(f"{settings.api_prefix}/projects/{{project_id}}", response_model=ProjectDetail)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectDetail:
    project, _ = get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    ensure_owner_membership(db=db, project=project)
    return project


@app.patch(f"{settings.api_prefix}/projects/{{project_id}}", response_model=ProjectDetail)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectDetail:
    project, member = get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    require_scope_or_403(member=member, scope="manage_members")

    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    if payload.objective is not None:
        project.objective = payload.objective
    if payload.hypothesis is not None:
        project.hypothesis = payload.hypothesis

    db.commit()
    return get_owned_project_or_404(db=db, user=current_user, project_id=project_id)


@app.get(f"{settings.api_prefix}/projects/{{project_id}}/members", response_model=list[ProjectMemberRead])
def list_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectMemberRead]:
    project, _ = get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    ensure_owner_membership(db=db, project=project)
    members = (
        db.query(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .filter(ProjectMember.project_id == project.id)
        .order_by(ProjectMember.created_at.asc())
        .all()
    )
    return [serialize_member(member) for member in members]


@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/members",
    response_model=ProjectMemberRead,
    status_code=status.HTTP_201_CREATED,
)
def add_project_member(
    project_id: int,
    payload: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectMemberRead:
    project, current_member = get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    require_scope_or_403(member=current_member, scope="manage_members")

    invited_user = db.query(User).filter(User.email == payload.email).first()
    if not invited_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    member = (
        db.query(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .filter(ProjectMember.project_id == project.id, ProjectMember.user_id == invited_user.id)
        .first()
    )
    if member:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member")

    member = ProjectMember(
        project_id=project.id,
        user_id=invited_user.id,
        role=payload.role,
        scopes=serialize_scopes(normalize_member_scopes(role=payload.role, requested_scopes=payload.scopes)),
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    member = (
        db.query(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .filter(ProjectMember.id == member.id)
        .first()
    )
    return serialize_member(member)


@app.patch(f"{settings.api_prefix}/projects/{{project_id}}/members/{{member_id}}", response_model=ProjectMemberRead)
def update_project_member(
    project_id: int,
    member_id: int,
    payload: ProjectMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectMemberRead:
    project, current_member = get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    require_scope_or_403(member=current_member, scope="manage_members")

    member = (
        db.query(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .filter(ProjectMember.id == member_id, ProjectMember.project_id == project.id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if member.user_id == project.owner_id and payload.role not in {None, "admin"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner role cannot be changed")

    if payload.role is not None:
        member.role = payload.role
    if payload.scopes is not None:
        member.scopes = serialize_scopes(
            normalize_member_scopes(role=member.role, requested_scopes=payload.scopes),
        )
    elif payload.role is not None:
        member.scopes = serialize_scopes(normalize_member_scopes(role=member.role, requested_scopes=None))

    db.commit()
    db.refresh(member)
    return serialize_member(member)


@app.delete(
    f"{settings.api_prefix}/projects/{{project_id}}/members/{{member_id}}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_project_member(
    project_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    project, current_member = get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    require_scope_or_403(member=current_member, scope="manage_members")
    member = (
        db.query(ProjectMember)
        .filter(ProjectMember.id == member_id, ProjectMember.project_id == project.id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if member.user_id == project.owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner cannot be removed")

    db.delete(member)
    db.commit()
    return None


@app.get(f"{settings.api_prefix}/projects/{{project_id}}/stages", response_model=list[LifecycleStageRead])
def list_stages(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LifecycleStageRead]:
    project, _ = get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    return project.lifecycle_stages


@app.patch(f"{settings.api_prefix}/stages/{{stage_id}}", response_model=LifecycleStageRead)
def update_stage(
    stage_id: int,
    payload: LifecycleStageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LifecycleStageRead:
    project_id = db.query(LifecycleStage.project_id).filter(LifecycleStage.id == stage_id).scalar()
    if project_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")
    project, member = get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    require_scope_or_403(member=member, scope="manage_lifecycle")
    stage = (
        db.query(LifecycleStage)
        .filter(LifecycleStage.id == stage_id, LifecycleStage.project_id == project.id)
        .first()
    )
    if not stage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")

    if payload.status is not None:
        if payload.status not in LIFECYCLE_STATUSES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid stage status")
        stage.status = payload.status
    if payload.notes is not None:
        stage.notes = payload.notes
    db.commit()
    db.refresh(stage)
    return stage


@app.get(f"{settings.api_prefix}/projects/{{project_id}}/experiments", response_model=list[ExperimentRead])
def list_experiments(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ExperimentRead]:
    get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    return (
        db.query(Experiment)
        .filter(Experiment.project_id == project_id)
        .order_by(Experiment.created_at.desc())
        .all()
    )


@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/experiments",
    response_model=ExperimentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_experiment(
    project_id: int,
    payload: ExperimentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExperimentRead:
    _, member = get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    require_scope_or_403(member=member, scope="manage_experiments")
    experiment = Experiment(
        project_id=project_id,
        kind=payload.kind,
        title=payload.title or "",
        hypothesis=payload.hypothesis,
        setup_notes=payload.setup_notes,
        result_summary=payload.result_summary,
        metric_name=payload.metric_name,
        metric_value=payload.metric_value,
        status=payload.status,
    )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


@app.patch(f"{settings.api_prefix}/experiments/{{experiment_id}}", response_model=ExperimentRead)
def update_experiment(
    experiment_id: int,
    payload: ExperimentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExperimentRead:
    experiment, member = get_experiment_with_member_or_404(db=db, user=current_user, experiment_id=experiment_id)
    require_scope_or_403(member=member, scope="manage_experiments")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(experiment, field, value)

    db.commit()
    db.refresh(experiment)
    return experiment


@app.delete(f"{settings.api_prefix}/experiments/{{experiment_id}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experiment(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    experiment, member = get_experiment_with_member_or_404(db=db, user=current_user, experiment_id=experiment_id)
    require_scope_or_403(member=member, scope="manage_experiments")
    db.delete(experiment)
    db.commit()
    return None


@app.get(f"{settings.api_prefix}/projects/{{project_id}}/runs", response_model=list[RunRead])
def list_project_runs(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[RunRead]:
    get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    return (
        db.query(Run)
        .join(Experiment, Experiment.id == Run.experiment_id)
        .filter(Experiment.project_id == project_id)
        .order_by(Run.started_at.desc())
        .all()
    )


@app.post(f"{settings.api_prefix}/runs", response_model=RunRead, status_code=status.HTTP_201_CREATED)
def create_run(
    payload: RunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RunRead:
    experiment, member = get_experiment_with_member_or_404(db=db, user=current_user, experiment_id=payload.experiment_id)
    require_scope_or_403(member=member, scope="manage_runs")

    run = Run(experiment_id=experiment.id, status=payload.status)
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


@app.patch(f"{settings.api_prefix}/runs/{{run_id}}/start", response_model=RunRead)
def start_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RunRead:
    run, member = get_run_with_member_or_404(db=db, user=current_user, run_id=run_id)
    require_scope_or_403(member=member, scope="manage_runs")
    if run.status in {"completed", "failed"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Run already finalized")

    run.status = "running"
    run.started_at = datetime.utcnow()
    db.commit()
    db.refresh(run)
    return run


@app.patch(f"{settings.api_prefix}/runs/{{run_id}}/finish", response_model=RunRead)
def finish_run(
    run_id: int,
    payload: RunFinish,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RunRead:
    run, member = get_run_with_member_or_404(db=db, user=current_user, run_id=run_id)
    require_scope_or_403(member=member, scope="manage_runs")
    run.status = payload.status
    run.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(run)
    return run


@app.post(f"{settings.api_prefix}/runs/{{run_id}}/params", response_model=list[RunParamRead])
def log_run_params(
    run_id: int,
    params: list[RunParamCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[RunParamRead]:
    run, member = get_run_with_member_or_404(db=db, user=current_user, run_id=run_id)
    require_scope_or_403(member=member, scope="manage_runs")
    param_objects = [RunParam(run_id=run.id, key=param.key, value=param.value) for param in params]
    db.add_all(param_objects)
    db.commit()
    for param in param_objects:
        db.refresh(param)
    return param_objects


@app.post(f"{settings.api_prefix}/runs/{{run_id}}/metrics", response_model=RunMetricRead)
def log_run_metric(
    run_id: int,
    metric: RunMetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RunMetricRead:
    run, member = get_run_with_member_or_404(db=db, user=current_user, run_id=run_id)
    require_scope_or_403(member=member, scope="manage_runs")
    metric_obj = RunMetric(run_id=run.id, key=metric.key, value=metric.value, step=metric.step)
    db.add(metric_obj)
    db.commit()
    db.refresh(metric_obj)
    return metric_obj


@app.get(f"{settings.api_prefix}/runs/{{run_id}}/metrics", response_model=list[RunMetricRead])
def get_run_metrics(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[RunMetricRead]:
    run, _ = get_run_with_member_or_404(db=db, user=current_user, run_id=run_id)
    return (
        db.query(RunMetric)
        .filter(RunMetric.run_id == run.id)
        .order_by(RunMetric.step.asc(), RunMetric.timestamp.asc())
        .all()
    )


@app.get(f"{settings.api_prefix}/runs/{{run_id}}", response_model=RunDetailRead)
def get_run_detail(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RunDetailRead:
    run, _ = get_run_with_member_or_404(db=db, user=current_user, run_id=run_id)
    run.metrics = sorted(run.metrics, key=lambda item: (item.step, item.timestamp))
    return run


@app.get(
    f"{settings.api_prefix}/projects/{{project_id}}/run-comparison",
    response_model=RunComparisonResponse,
)
def get_run_comparison(
    project_id: int,
    metric_key: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RunComparisonResponse:
    get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    runs = (
        db.query(Run)
        .join(Experiment, Experiment.id == Run.experiment_id)
        .filter(Experiment.project_id == project_id)
        .options(selectinload(Run.params), selectinload(Run.metrics), selectinload(Run.experiment))
        .order_by(Run.started_at.desc())
        .all()
    )

    items: list[RunComparisonItem] = []
    best_run_id: int | None = None
    best_metric_value: float | None = None
    for run in runs:
        metrics_map: dict[str, float] = {}
        for metric in sorted(run.metrics, key=lambda item: (item.step, item.timestamp)):
            metrics_map[metric.key] = metric.value
        params_map = {param.key: param.value for param in run.params}
        selected_metric = metrics_map.get(metric_key) if metric_key else None
        if selected_metric is not None and (best_metric_value is None or selected_metric > best_metric_value):
            best_metric_value = selected_metric
            best_run_id = run.id

        items.append(
            RunComparisonItem(
                run_id=run.id,
                experiment_id=run.experiment_id,
                experiment_title=run.experiment.title,
                status=run.status,
                selected_metric=selected_metric,
                metrics=metrics_map,
                params=params_map,
                started_at=run.started_at,
                finished_at=run.finished_at,
            )
        )

    return RunComparisonResponse(
        project_id=project_id,
        metric_key=metric_key,
        items=items,
        best_run_id=best_run_id,
        best_metric_value=best_metric_value,
    )


@app.get(f"{settings.api_prefix}/projects/{{project_id}}/tasks", response_model=list[TaskRead])
def list_tasks(
    project_id: int,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TaskRead]:
    get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    query = (
        db.query(Task)
        .options(selectinload(Task.assignee), selectinload(Task.reporter))
        .filter(Task.project_id == project_id)
    )
    if status_filter:
        query = query.filter(Task.status == status_filter)
    tasks = query.order_by(Task.updated_at.desc()).all()
    return [serialize_task(task) for task in tasks]


@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    project_id: int,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    project, member = get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    require_scope_or_403(member=member, scope="manage_tasks")
    ensure_assignee_in_project(db=db, project=project, assignee_id=payload.assignee_id)

    task = Task(
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        assignee_id=payload.assignee_id,
        reporter_id=current_user.id,
        stage_number=payload.stage_number,
        story_points=payload.story_points,
        due_date=payload.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task = (
        db.query(Task)
        .options(selectinload(Task.assignee), selectinload(Task.reporter))
        .filter(Task.id == task.id)
        .first()
    )
    return serialize_task(task)


@app.patch(f"{settings.api_prefix}/tasks/{{task_id}}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    task = (
        db.query(Task)
        .options(selectinload(Task.assignee), selectinload(Task.reporter), selectinload(Task.project))
        .filter(Task.id == task_id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    project, member = get_project_with_member_or_404(db=db, user=current_user, project_id=task.project_id)
    require_scope_or_403(member=member, scope="manage_tasks")
    updates = payload.model_dump(exclude_unset=True)
    if "assignee_id" in updates:
        ensure_assignee_in_project(db=db, project=project, assignee_id=updates["assignee_id"])
    for field, value in updates.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return serialize_task(task)


@app.delete(f"{settings.api_prefix}/tasks/{{task_id}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    _, member = get_project_with_member_or_404(db=db, user=current_user, project_id=task.project_id)
    require_scope_or_403(member=member, scope="manage_tasks")
    db.delete(task)
    db.commit()
    return None


@app.get(
    f"{settings.api_prefix}/projects/{{project_id}}/kanban",
    response_model=KanbanBoardResponse,
)
def get_kanban_board(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> KanbanBoardResponse:
    get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    columns: dict[str, list[TaskRead]] = {status_key: [] for status_key in ["backlog", "todo", "in_progress", "in_review", "done"]}
    tasks = (
        db.query(Task)
        .options(selectinload(Task.assignee), selectinload(Task.reporter))
        .filter(Task.project_id == project_id)
        .order_by(Task.updated_at.desc())
        .all()
    )
    for task in tasks:
        columns.setdefault(task.status, []).append(serialize_task(task))
    return KanbanBoardResponse(project_id=project_id, columns=columns)


@app.get(f"{settings.api_prefix}/projects/{{project_id}}/pages", response_model=list[ProjectPageRead])
def list_pages(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectPageRead]:
    get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    pages = (
        db.query(ProjectPage)
        .options(selectinload(ProjectPage.author), selectinload(ProjectPage.updated_by))
        .filter(ProjectPage.project_id == project_id)
        .order_by(ProjectPage.updated_at.desc())
        .all()
    )
    return [serialize_page(page) for page in pages]


@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/pages",
    response_model=ProjectPageRead,
    status_code=status.HTTP_201_CREATED,
)
def create_page(
    project_id: int,
    payload: ProjectPageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectPageRead:
    _, member = get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    require_scope_or_403(member=member, scope="manage_pages")
    if payload.parent_page_id is not None:
        parent = (
            db.query(ProjectPage)
            .filter(ProjectPage.id == payload.parent_page_id, ProjectPage.project_id == project_id)
            .first()
        )
        if not parent:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent page not found")

    page = ProjectPage(
        project_id=project_id,
        title=payload.title,
        content=payload.content,
        parent_page_id=payload.parent_page_id,
        author_id=current_user.id,
        updated_by_id=current_user.id,
    )
    db.add(page)
    db.commit()
    db.refresh(page)
    page = (
        db.query(ProjectPage)
        .options(selectinload(ProjectPage.author), selectinload(ProjectPage.updated_by))
        .filter(ProjectPage.id == page.id)
        .first()
    )
    return serialize_page(page)


@app.get(f"{settings.api_prefix}/pages/{{page_id}}", response_model=ProjectPageRead)
def get_page(
    page_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectPageRead:
    page = (
        db.query(ProjectPage)
        .options(selectinload(ProjectPage.author), selectinload(ProjectPage.updated_by))
        .filter(ProjectPage.id == page_id)
        .first()
    )
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    get_project_with_member_or_404(db=db, user=current_user, project_id=page.project_id)
    return serialize_page(page)


@app.patch(f"{settings.api_prefix}/pages/{{page_id}}", response_model=ProjectPageRead)
def update_page(
    page_id: int,
    payload: ProjectPageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectPageRead:
    page = (
        db.query(ProjectPage)
        .options(selectinload(ProjectPage.author), selectinload(ProjectPage.updated_by))
        .filter(ProjectPage.id == page_id)
        .first()
    )
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    _, member = get_project_with_member_or_404(db=db, user=current_user, project_id=page.project_id)
    require_scope_or_403(member=member, scope="manage_pages")
    updates = payload.model_dump(exclude_unset=True)
    if "parent_page_id" in updates and updates["parent_page_id"] is not None:
        parent = (
            db.query(ProjectPage)
            .filter(ProjectPage.id == updates["parent_page_id"], ProjectPage.project_id == page.project_id)
            .first()
        )
        if not parent:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent page not found")
        if parent.id == page.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Page cannot be its own parent")

    for field, value in updates.items():
        setattr(page, field, value)
    page.updated_by_id = current_user.id
    db.commit()
    db.refresh(page)
    return serialize_page(page)


@app.delete(f"{settings.api_prefix}/pages/{{page_id}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_page(
    page_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    page = db.query(ProjectPage).filter(ProjectPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    _, member = get_project_with_member_or_404(db=db, user=current_user, project_id=page.project_id)
    require_scope_or_403(member=member, scope="manage_pages")
    db.delete(page)
    db.commit()
    return None


@app.get(f"{settings.api_prefix}/projects/{{project_id}}/benchmarks", response_model=list[BenchmarkRead])
def list_benchmarks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BenchmarkRead]:
    get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    return (
        db.query(Benchmark)
        .filter(Benchmark.project_id == project_id)
        .order_by(Benchmark.created_at.desc())
        .all()
    )


@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/benchmarks",
    response_model=BenchmarkRead,
    status_code=status.HTTP_201_CREATED,
)
def create_benchmark(
    project_id: int,
    payload: BenchmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BenchmarkRead:
    _, member = get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    require_scope_or_403(member=member, scope="manage_experiments")

    if payload.experiment_id is not None:
        experiment = (
            db.query(Experiment)
            .filter(Experiment.id == payload.experiment_id, Experiment.project_id == project_id)
            .first()
        )
        if not experiment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found")

    benchmark = Benchmark(project_id=project_id, **payload.model_dump())
    db.add(benchmark)
    db.commit()
    db.refresh(benchmark)
    return benchmark


@app.get(f"{settings.api_prefix}/projects/{{project_id}}/tables", response_model=list[ResultTableRead])
def list_result_tables(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ResultTableRead]:
    get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    return (
        db.query(ResultTable)
        .filter(ResultTable.project_id == project_id)
        .order_by(ResultTable.created_at.desc())
        .all()
    )


@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/tables",
    response_model=ResultTableRead,
    status_code=status.HTTP_201_CREATED,
)
def create_result_table(
    project_id: int,
    payload: ResultTableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResultTableRead:
    _, member = get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    require_scope_or_403(member=member, scope="manage_experiments")
    table = ResultTable(project_id=project_id, **payload.model_dump())
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


@app.get(f"{settings.api_prefix}/projects/{{project_id}}/reports", response_model=list[FinalReportRead])
def list_reports(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FinalReportRead]:
    get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    return (
        db.query(FinalReport)
        .filter(FinalReport.project_id == project_id)
        .order_by(FinalReport.updated_at.desc())
        .all()
    )


@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/reports",
    response_model=FinalReportRead,
    status_code=status.HTTP_201_CREATED,
)
def create_report(
    project_id: int,
    payload: FinalReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FinalReportRead:
    _, member = get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)
    require_scope_or_403(member=member, scope="manage_pages")
    report = FinalReport(project_id=project_id, **payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@app.patch(f"{settings.api_prefix}/reports/{{report_id}}", response_model=FinalReportRead)
def update_report(
    report_id: int,
    payload: FinalReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FinalReportRead:
    report = db.query(FinalReport).filter(FinalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    _, member = get_project_with_member_or_404(db=db, user=current_user, project_id=report.project_id)
    require_scope_or_403(member=member, scope="manage_pages")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(report, field, value)

    db.commit()
    db.refresh(report)
    return report


@app.get(
    f"{settings.api_prefix}/projects/{{project_id}}/lifecycle-summary",
    response_model=ProjectLifecycleSummary,
)
def get_project_lifecycle_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectLifecycleSummary:
    project, _ = get_project_with_member_or_404(db=db, user=current_user, project_id=project_id)

    stage_status_counts = {status_value: 0 for status_value in LIFECYCLE_STATUSES}
    for stage in project.lifecycle_stages:
        stage_status_counts[stage.status] = stage_status_counts.get(stage.status, 0) + 1

    experiment_counts_by_kind: dict[str, int] = {}
    run_status_counts: dict[str, int] = {"queued": 0, "running": 0, "completed": 0, "failed": 0}
    for experiment in project.experiments:
        experiment_counts_by_kind[experiment.kind] = experiment_counts_by_kind.get(experiment.kind, 0) + 1
        for run in experiment.runs:
            run_status_counts[run.status] = run_status_counts.get(run.status, 0) + 1

    completed_stage_numbers = {stage.stage_number for stage in project.lifecycle_stages if stage.status == "completed"}
    ready_to_scale = {1, 2, 3, 4, 5, 6}.issubset(completed_stage_numbers) and bool(project.result_tables)
    ready_for_final_evaluation = ready_to_scale and 7 in completed_stage_numbers
    task_status_counts: dict[str, int] = {"backlog": 0, "todo": 0, "in_progress": 0, "in_review": 0, "done": 0}
    tasks = db.query(Task).filter(Task.project_id == project.id).all()
    for task in tasks:
        task_status_counts[task.status] = task_status_counts.get(task.status, 0) + 1

    return ProjectLifecycleSummary(
        project_id=project.id,
        stage_status_counts=stage_status_counts,
        experiment_counts_by_kind=experiment_counts_by_kind,
        run_status_counts=run_status_counts,
        benchmarks_logged=len(project.benchmarks),
        result_tables_created=len(project.result_tables),
        final_reports_created=len(project.final_reports),
        task_status_counts=task_status_counts,
        documentation_pages_created=db.query(func.count(ProjectPage.id)).filter(ProjectPage.project_id == project.id).scalar()
        or 0,
        ready_to_scale=ready_to_scale,
        ready_for_final_evaluation=ready_for_final_evaluation,
    )
