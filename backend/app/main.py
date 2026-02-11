from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, selectinload

from .config import settings
from .database import Base, engine, get_db
from .dependencies import get_current_user
from .lifecycle import LIFECYCLE_TEMPLATE, LIFECYCLE_STATUSES
from .models import Benchmark, Experiment, FinalReport, LifecycleStage, Project, ResultTable, User
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
    ProjectCreate,
    ProjectDetail,
    ProjectRead,
    ProjectUpdate,
    ResultTableCreate,
    ResultTableRead,
    Token,
    UserCreate,
    UserLogin,
    UserRead,
)
from .security import create_access_token, hash_password, verify_password


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_owned_project_or_404(db: Session, user: User, project_id: int) -> Project:
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.owner_id == user.id)
        .options(
            selectinload(Project.lifecycle_stages),
            selectinload(Project.experiments),
            selectinload(Project.benchmarks),
            selectinload(Project.result_tables),
            selectinload(Project.final_reports),
        )
        .first()
    )
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


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
    project = Project(
        owner_id=current_user.id,
        name=payload.name,
        objective=payload.objective,
        hypothesis=payload.hypothesis,
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

    db.commit()
    return get_owned_project_or_404(db=db, user=current_user, project_id=project.id)


@app.get(f"{settings.api_prefix}/projects", response_model=list[ProjectRead])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectRead]:
    return (
        db.query(Project)
        .filter(Project.owner_id == current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )


@app.get(f"{settings.api_prefix}/projects/{{project_id}}", response_model=ProjectDetail)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectDetail:
    return get_owned_project_or_404(db=db, user=current_user, project_id=project_id)


@app.patch(f"{settings.api_prefix}/projects/{{project_id}}", response_model=ProjectDetail)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectDetail:
    project = get_owned_project_or_404(db=db, user=current_user, project_id=project_id)

    if payload.name is not None:
        project.name = payload.name
    if payload.objective is not None:
        project.objective = payload.objective
    if payload.hypothesis is not None:
        project.hypothesis = payload.hypothesis

    db.commit()
    return get_owned_project_or_404(db=db, user=current_user, project_id=project_id)


@app.get(f"{settings.api_prefix}/projects/{{project_id}}/stages", response_model=list[LifecycleStageRead])
def list_stages(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LifecycleStageRead]:
    project = get_owned_project_or_404(db=db, user=current_user, project_id=project_id)
    return project.lifecycle_stages


@app.patch(f"{settings.api_prefix}/stages/{{stage_id}}", response_model=LifecycleStageRead)
def update_stage(
    stage_id: int,
    payload: LifecycleStageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LifecycleStageRead:
    stage = (
        db.query(LifecycleStage)
        .join(Project, Project.id == LifecycleStage.project_id)
        .filter(LifecycleStage.id == stage_id, Project.owner_id == current_user.id)
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
    get_owned_project_or_404(db=db, user=current_user, project_id=project_id)
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
    get_owned_project_or_404(db=db, user=current_user, project_id=project_id)
    experiment = Experiment(project_id=project_id, **payload.model_dump())
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
    experiment = (
        db.query(Experiment)
        .join(Project, Project.id == Experiment.project_id)
        .filter(Experiment.id == experiment_id, Project.owner_id == current_user.id)
        .first()
    )
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found")

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
    experiment = (
        db.query(Experiment)
        .join(Project, Project.id == Experiment.project_id)
        .filter(Experiment.id == experiment_id, Project.owner_id == current_user.id)
        .first()
    )
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found")
    db.delete(experiment)
    db.commit()
    return None


@app.get(f"{settings.api_prefix}/projects/{{project_id}}/benchmarks", response_model=list[BenchmarkRead])
def list_benchmarks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BenchmarkRead]:
    get_owned_project_or_404(db=db, user=current_user, project_id=project_id)
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
    get_owned_project_or_404(db=db, user=current_user, project_id=project_id)

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
    get_owned_project_or_404(db=db, user=current_user, project_id=project_id)
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
    get_owned_project_or_404(db=db, user=current_user, project_id=project_id)
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
    get_owned_project_or_404(db=db, user=current_user, project_id=project_id)
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
    get_owned_project_or_404(db=db, user=current_user, project_id=project_id)
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
    report = (
        db.query(FinalReport)
        .join(Project, Project.id == FinalReport.project_id)
        .filter(FinalReport.id == report_id, Project.owner_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(report, field, value)

    db.commit()
    db.refresh(report)
    return report
