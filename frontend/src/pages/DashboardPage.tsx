import { FormEvent, useEffect, useMemo, useState } from "react";

import { api } from "../api";
import { useAuth } from "../auth";
import type {
  ExperimentKind,
  ExperimentStatus,
  Project,
  ProjectDetail,
  ProjectMember,
  ProjectPage,
  ProjectRole,
  RunComparison,
  TaskItem,
  TaskPriority,
  TaskStatus,
} from "../types";

const lifecycleStatuses = ["pending", "in_progress", "completed", "blocked"] as const;
const experimentKinds: ExperimentKind[] = ["baseline", "reproduction", "partial", "benchmark", "scaled", "final"];
const experimentStatuses: ExperimentStatus[] = ["planned", "running", "completed", "failed"];
const roles: ProjectRole[] = ["admin", "manager", "researcher", "reviewer", "viewer"];
const taskStatuses: TaskStatus[] = ["backlog", "todo", "in_progress", "in_review", "done"];
const taskPriorities: TaskPriority[] = ["low", "medium", "high", "critical"];

export function DashboardPage() {
  const { token, user, logout } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [selectedProject, setSelectedProject] = useState<ProjectDetail | null>(null);
  const [members, setMembers] = useState<ProjectMember[]>([]);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [pages, setPages] = useState<ProjectPage[]>([]);
  const [runComparison, setRunComparison] = useState<RunComparison | null>(null);
  const [runMetricKey, setRunMetricKey] = useState("accuracy");
  const [stageNotes, setStageNotes] = useState<Record<number, string>>({});
  const [stageStatuses, setStageStatuses] = useState<Record<number, (typeof lifecycleStatuses)[number]>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  const [projectObjective, setProjectObjective] = useState("");
  const [projectHypothesis, setProjectHypothesis] = useState("");

  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<ProjectRole>("researcher");

  const [taskTitle, setTaskTitle] = useState("");
  const [taskDescription, setTaskDescription] = useState("");
  const [taskStatus, setTaskStatus] = useState<TaskStatus>("todo");
  const [taskPriority, setTaskPriority] = useState<TaskPriority>("medium");
  const [taskAssigneeId, setTaskAssigneeId] = useState<string>("");
  const [taskStageNumber, setTaskStageNumber] = useState<string>("");
  const [taskStoryPoints, setTaskStoryPoints] = useState<string>("");
  const [taskDueDate, setTaskDueDate] = useState("");

  const [pageTitle, setPageTitle] = useState("");
  const [pageContent, setPageContent] = useState("");
  const [pageParentId, setPageParentId] = useState<string>("");

  const [experimentKind, setExperimentKind] = useState<ExperimentKind>("baseline");
  const [experimentTitle, setExperimentTitle] = useState("");
  const [experimentHypothesis, setExperimentHypothesis] = useState("");
  const [experimentSetup, setExperimentSetup] = useState("");
  const [experimentResult, setExperimentResult] = useState("");
  const [experimentMetricName, setExperimentMetricName] = useState("");
  const [experimentMetricValue, setExperimentMetricValue] = useState("");
  const [experimentStatus, setExperimentStatus] = useState<ExperimentStatus>("planned");

  const [benchmarkExperimentId, setBenchmarkExperimentId] = useState<string>("");
  const [benchmarkDataset, setBenchmarkDataset] = useState("");
  const [benchmarkMetricName, setBenchmarkMetricName] = useState("");
  const [benchmarkMetricValue, setBenchmarkMetricValue] = useState("");
  const [benchmarkNotes, setBenchmarkNotes] = useState("");

  const [tableTitle, setTableTitle] = useState("");
  const [tableMarkdown, setTableMarkdown] = useState("");

  const [reportDiscussion, setReportDiscussion] = useState("");
  const [reportEvaluation, setReportEvaluation] = useState("");
  const [reportLatex, setReportLatex] = useState("");

  const selectedProjectName = useMemo(
    () => projects.find((project) => project.id === selectedProjectId)?.name ?? "No project selected",
    [projects, selectedProjectId],
  );

  const tasksByStatus = useMemo(() => {
    const grouped: Record<TaskStatus, TaskItem[]> = {
      backlog: [],
      todo: [],
      in_progress: [],
      in_review: [],
      done: [],
    };
    tasks.forEach((task) => grouped[task.status].push(task));
    return grouped;
  }, [tasks]);

  useEffect(() => {
    if (!token) return;
    void loadProjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function loadProjects() {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const list = await api.listProjects(token);
      setProjects(list);
      if (list.length > 0) {
        const nextProjectId = selectedProjectId && list.some((p) => p.id === selectedProjectId) ? selectedProjectId : list[0].id;
        setSelectedProjectId(nextProjectId);
        await loadProjectWorkspace(nextProjectId);
      } else {
        setSelectedProjectId(null);
        setSelectedProject(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load projects");
    } finally {
      setLoading(false);
    }
  }

  async function loadProjectWorkspace(projectId: number) {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const [detail, team, projectTasks, docs, comparison] = await Promise.all([
        api.getProject(token, projectId),
        api.listMembers(token, projectId),
        api.listTasks(token, projectId),
        api.listPages(token, projectId),
        api.getRunComparison(token, projectId, runMetricKey || undefined),
      ]);
      setSelectedProject(detail);
      setMembers(team);
      setTasks(projectTasks);
      setPages(docs);
      setRunComparison(comparison);

      const nextNotes: Record<number, string> = {};
      const nextStatuses: Record<number, (typeof lifecycleStatuses)[number]> = {};
      detail.lifecycle_stages.forEach((stage) => {
        nextNotes[stage.id] = stage.notes;
        nextStatuses[stage.id] = stage.status;
      });
      setStageNotes(nextNotes);
      setStageStatuses(nextStatuses);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load project details");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateProject(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const project = await api.createProject(token, {
        name: projectName,
        description: projectDescription,
        objective: projectObjective,
        hypothesis: projectHypothesis,
      });
      setProjectName("");
      setProjectDescription("");
      setProjectObjective("");
      setProjectHypothesis("");
      setProjects((prev) => [project, ...prev]);
      setSelectedProjectId(project.id);
      await loadProjectWorkspace(project.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create project");
    } finally {
      setLoading(false);
    }
  }

  async function handleStageUpdate(stageId: number) {
    if (!token || !selectedProject) return;
    setLoading(true);
    setError(null);
    try {
      await api.updateStage(token, stageId, {
        status: stageStatuses[stageId],
        notes: stageNotes[stageId],
      });
      await loadProjectWorkspace(selectedProject.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update stage");
    } finally {
      setLoading(false);
    }
  }

  async function handleInviteMember(event: FormEvent) {
    event.preventDefault();
    if (!token || !selectedProject) return;
    setLoading(true);
    setError(null);
    try {
      await api.addMember(token, selectedProject.id, { email: inviteEmail, role: inviteRole });
      setInviteEmail("");
      setInviteRole("researcher");
      await loadProjectWorkspace(selectedProject.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to add member");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateTask(event: FormEvent) {
    event.preventDefault();
    if (!token || !selectedProject) return;
    setLoading(true);
    setError(null);
    try {
      await api.createTask(token, selectedProject.id, {
        title: taskTitle,
        description: taskDescription,
        status: taskStatus,
        priority: taskPriority,
        assignee_id: taskAssigneeId ? Number(taskAssigneeId) : null,
        stage_number: taskStageNumber ? Number(taskStageNumber) : null,
        story_points: taskStoryPoints ? Number(taskStoryPoints) : null,
        due_date: taskDueDate ? new Date(taskDueDate).toISOString() : null,
      });
      setTaskTitle("");
      setTaskDescription("");
      setTaskStatus("todo");
      setTaskPriority("medium");
      setTaskAssigneeId("");
      setTaskStageNumber("");
      setTaskStoryPoints("");
      setTaskDueDate("");
      await loadProjectWorkspace(selectedProject.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create task");
    } finally {
      setLoading(false);
    }
  }

  async function moveTask(task: TaskItem, newStatus: TaskStatus) {
    if (!token || !selectedProject) return;
    setLoading(true);
    setError(null);
    try {
      await api.updateTask(token, task.id, { status: newStatus });
      await loadProjectWorkspace(selectedProject.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update task");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreatePage(event: FormEvent) {
    event.preventDefault();
    if (!token || !selectedProject) return;
    setLoading(true);
    setError(null);
    try {
      await api.createPage(token, selectedProject.id, {
        title: pageTitle,
        content: pageContent,
        parent_page_id: pageParentId ? Number(pageParentId) : null,
      });
      setPageTitle("");
      setPageContent("");
      setPageParentId("");
      await loadProjectWorkspace(selectedProject.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create page");
    } finally {
      setLoading(false);
    }
  }

  async function refreshRunComparison(event: FormEvent) {
    event.preventDefault();
    if (!token || !selectedProject) return;
    setLoading(true);
    setError(null);
    try {
      const comparison = await api.getRunComparison(token, selectedProject.id, runMetricKey || undefined);
      setRunComparison(comparison);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load run comparison");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateExperiment(event: FormEvent) {
    event.preventDefault();
    if (!token || !selectedProject) return;
    setLoading(true);
    setError(null);
    try {
      await api.createExperiment(token, selectedProject.id, {
        kind: experimentKind,
        title: experimentTitle,
        hypothesis: experimentHypothesis,
        setup_notes: experimentSetup,
        result_summary: experimentResult,
        metric_name: experimentMetricName,
        metric_value: experimentMetricValue.length > 0 ? Number(experimentMetricValue) : null,
        status: experimentStatus,
      });
      setExperimentTitle("");
      setExperimentHypothesis("");
      setExperimentSetup("");
      setExperimentResult("");
      setExperimentMetricName("");
      setExperimentMetricValue("");
      setExperimentStatus("planned");
      await loadProjectWorkspace(selectedProject.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create experiment");
    } finally {
      setLoading(false);
    }
  }

  async function handleDeleteExperiment(experimentId: number) {
    if (!token || !selectedProject) return;
    setLoading(true);
    setError(null);
    try {
      await api.deleteExperiment(token, experimentId);
      await loadProjectWorkspace(selectedProject.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to delete experiment");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateBenchmark(event: FormEvent) {
    event.preventDefault();
    if (!token || !selectedProject) return;
    setLoading(true);
    setError(null);
    try {
      await api.createBenchmark(token, selectedProject.id, {
        experiment_id: benchmarkExperimentId ? Number(benchmarkExperimentId) : null,
        dataset: benchmarkDataset,
        metric_name: benchmarkMetricName,
        metric_value: Number(benchmarkMetricValue),
        notes: benchmarkNotes,
      });
      setBenchmarkExperimentId("");
      setBenchmarkDataset("");
      setBenchmarkMetricName("");
      setBenchmarkMetricValue("");
      setBenchmarkNotes("");
      await loadProjectWorkspace(selectedProject.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create benchmark");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateTable(event: FormEvent) {
    event.preventDefault();
    if (!token || !selectedProject) return;
    setLoading(true);
    setError(null);
    try {
      await api.createTable(token, selectedProject.id, {
        title: tableTitle,
        table_markdown: tableMarkdown,
      });
      setTableTitle("");
      setTableMarkdown("");
      await loadProjectWorkspace(selectedProject.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create result table");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateReport(event: FormEvent) {
    event.preventDefault();
    if (!token || !selectedProject) return;
    setLoading(true);
    setError(null);
    try {
      await api.createReport(token, selectedProject.id, {
        discussion: reportDiscussion,
        evaluation_summary: reportEvaluation,
        latex_snippet: reportLatex,
      });
      setReportDiscussion("");
      setReportEvaluation("");
      setReportLatex("");
      await loadProjectWorkspace(selectedProject.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create report");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="dashboard-layout">
      <aside className="sidebar card">
        <h2>Friday.ai</h2>
        <p className="muted">{user?.full_name}</p>
        <button type="button" className="secondary" onClick={logout}>
          Logout
        </button>

        <hr />

        <h3>Projects</h3>
        <div className="project-list">
          {projects.map((project) => (
            <button
              key={project.id}
              type="button"
              className={`project-list-item ${selectedProjectId === project.id ? "active" : ""}`}
              onClick={() => {
                setSelectedProjectId(project.id);
                void loadProjectWorkspace(project.id);
              }}
            >
              <span>{project.name}</span>
            </button>
          ))}
          {projects.length === 0 && <p className="muted small">No projects yet.</p>}
        </div>

        <hr />

        <h3>Create Project</h3>
        <form className="stacked-form" onSubmit={handleCreateProject}>
          <label>
            Name
            <input value={projectName} onChange={(e) => setProjectName(e.target.value)} minLength={2} required />
          </label>
          <label>
            Description
            <textarea value={projectDescription} onChange={(e) => setProjectDescription(e.target.value)} />
          </label>
          <label>
            Objective
            <textarea
              value={projectObjective}
              onChange={(e) => setProjectObjective(e.target.value)}
              minLength={5}
              required
            />
          </label>
          <label>
            Hypothesis
            <textarea
              value={projectHypothesis}
              onChange={(e) => setProjectHypothesis(e.target.value)}
              minLength={5}
              required
            />
          </label>
          <button type="submit" disabled={loading}>
            Add Project
          </button>
        </form>
      </aside>

      <main className="content">
        <section className="card">
          <h1>{selectedProjectName}</h1>
          {selectedProject && (
            <>
              <p>
                <strong>Description:</strong> {selectedProject.description || "No description yet."}
              </p>
              <p>
                <strong>Objective:</strong> {selectedProject.objective}
              </p>
              <p>
                <strong>Hypothesis:</strong> {selectedProject.hypothesis}
              </p>
            </>
          )}
          {error && <p className="error-text">{error}</p>}
          {loading && <p className="muted">Syncing...</p>}
        </section>

        {selectedProject ? (
          <>
            <section className="card">
              <h2>Team & Access Control (Jira-style)</h2>
              <form className="grid-form" onSubmit={handleInviteMember}>
                <label>
                  User Email
                  <input type="email" value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)} required />
                </label>
                <label>
                  Role
                  <select value={inviteRole} onChange={(e) => setInviteRole(e.target.value as ProjectRole)}>
                    {roles.map((role) => (
                      <option key={role} value={role}>
                        {role}
                      </option>
                    ))}
                  </select>
                </label>
                <button type="submit" disabled={loading}>
                  Add Member
                </button>
              </form>
              <div className="list">
                {members.map((member) => (
                  <article key={member.id} className="list-item">
                    <div>
                      <strong>{member.user_full_name}</strong> ({member.user_email})
                      <p className="muted small">
                        Role: {member.role} | Scopes: {member.scopes.join(", ") || "view only"}
                      </p>
                    </div>
                  </article>
                ))}
                {members.length === 0 && <p className="muted small">No members yet.</p>}
              </div>
            </section>

            <section className="card">
              <h2>Lifecycle Stages</h2>
              <div className="stages-grid">
                {selectedProject.lifecycle_stages.map((stage) => (
                  <article key={stage.id} className="stage-card">
                    <h3>
                      {stage.stage_number}. {stage.title}
                    </h3>
                    <p className="muted">{stage.guidance}</p>
                    <label>
                      Status
                      <select
                        value={stageStatuses[stage.id] ?? stage.status}
                        onChange={(e) =>
                          setStageStatuses((prev) => ({
                            ...prev,
                            [stage.id]: e.target.value as (typeof lifecycleStatuses)[number],
                          }))
                        }
                      >
                        {lifecycleStatuses.map((stageStatus) => (
                          <option key={stageStatus} value={stageStatus}>
                            {stageStatus}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      Notes
                      <textarea
                        value={stageNotes[stage.id] ?? ""}
                        onChange={(e) =>
                          setStageNotes((prev) => ({
                            ...prev,
                            [stage.id]: e.target.value,
                          }))
                        }
                      />
                    </label>
                    <button type="button" onClick={() => void handleStageUpdate(stage.id)} disabled={loading}>
                      Save Stage
                    </button>
                  </article>
                ))}
              </div>
            </section>

            <section className="card">
              <h2>Kanban Tasks (Jira-style Execution)</h2>
              <form className="grid-form" onSubmit={handleCreateTask}>
                <label>
                  Task Title
                  <input value={taskTitle} onChange={(e) => setTaskTitle(e.target.value)} required />
                </label>
                <label>
                  Description
                  <textarea value={taskDescription} onChange={(e) => setTaskDescription(e.target.value)} />
                </label>
                <label>
                  Status
                  <select value={taskStatus} onChange={(e) => setTaskStatus(e.target.value as TaskStatus)}>
                    {taskStatuses.map((statusValue) => (
                      <option key={statusValue} value={statusValue}>
                        {statusValue}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Priority
                  <select value={taskPriority} onChange={(e) => setTaskPriority(e.target.value as TaskPriority)}>
                    {taskPriorities.map((priority) => (
                      <option key={priority} value={priority}>
                        {priority}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Assignee
                  <select value={taskAssigneeId} onChange={(e) => setTaskAssigneeId(e.target.value)}>
                    <option value="">Unassigned</option>
                    {members.map((member) => (
                      <option key={member.user_id} value={member.user_id}>
                        {member.user_full_name}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Lifecycle Stage
                  <input
                    type="number"
                    min={1}
                    max={8}
                    value={taskStageNumber}
                    onChange={(e) => setTaskStageNumber(e.target.value)}
                  />
                </label>
                <label>
                  Story Points
                  <input type="number" min={0} value={taskStoryPoints} onChange={(e) => setTaskStoryPoints(e.target.value)} />
                </label>
                <label>
                  Due Date
                  <input type="datetime-local" value={taskDueDate} onChange={(e) => setTaskDueDate(e.target.value)} />
                </label>
                <button type="submit" disabled={loading}>
                  Create Task
                </button>
              </form>

              <div className="kanban-grid">
                {taskStatuses.map((statusValue) => (
                  <article key={statusValue} className="kanban-column">
                    <h3>{statusValue}</h3>
                    {tasksByStatus[statusValue].map((task) => (
                      <div key={task.id} className="kanban-card">
                        <strong>{task.title}</strong>
                        <p className="muted small">{task.description || "No description"}</p>
                        <p className="small">
                          Priority: <span className={`chip chip-${task.priority}`}>{task.priority}</span>
                        </p>
                        <p className="small">Assignee: {task.assignee_name ?? "Unassigned"}</p>
                        <label>
                          Move
                          <select value={task.status} onChange={(e) => void moveTask(task, e.target.value as TaskStatus)}>
                            {taskStatuses.map((nextStatus) => (
                              <option key={nextStatus} value={nextStatus}>
                                {nextStatus}
                              </option>
                            ))}
                          </select>
                        </label>
                      </div>
                    ))}
                    {tasksByStatus[statusValue].length === 0 && <p className="muted small">No tasks</p>}
                  </article>
                ))}
              </div>
            </section>

            <section className="card">
              <h2>Experiments</h2>
              <form className="grid-form" onSubmit={handleCreateExperiment}>
                <label>
                  Kind
                  <select value={experimentKind} onChange={(e) => setExperimentKind(e.target.value as ExperimentKind)}>
                    {experimentKinds.map((kind) => (
                      <option key={kind} value={kind}>
                        {kind}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Title
                  <input value={experimentTitle} onChange={(e) => setExperimentTitle(e.target.value)} required />
                </label>
                <label>
                  Status
                  <select value={experimentStatus} onChange={(e) => setExperimentStatus(e.target.value as ExperimentStatus)}>
                    {experimentStatuses.map((statusValue) => (
                      <option key={statusValue} value={statusValue}>
                        {statusValue}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Hypothesis
                  <textarea value={experimentHypothesis} onChange={(e) => setExperimentHypothesis(e.target.value)} />
                </label>
                <label>
                  Setup
                  <textarea value={experimentSetup} onChange={(e) => setExperimentSetup(e.target.value)} />
                </label>
                <label>
                  Result Summary
                  <textarea value={experimentResult} onChange={(e) => setExperimentResult(e.target.value)} />
                </label>
                <label>
                  Metric Name
                  <input value={experimentMetricName} onChange={(e) => setExperimentMetricName(e.target.value)} />
                </label>
                <label>
                  Metric Value
                  <input
                    type="number"
                    step="any"
                    value={experimentMetricValue}
                    onChange={(e) => setExperimentMetricValue(e.target.value)}
                  />
                </label>
                <button type="submit" disabled={loading}>
                  Add Experiment
                </button>
              </form>
              <div className="list">
                {selectedProject.experiments.map((experiment) => (
                  <article key={experiment.id} className="list-item">
                    <div>
                      <strong>{experiment.title}</strong> ({experiment.kind}) - {experiment.status}
                      {experiment.metric_name && (
                        <p className="muted">
                          {experiment.metric_name}: {experiment.metric_value ?? "N/A"}
                        </p>
                      )}
                      {experiment.result_summary && <p>{experiment.result_summary}</p>}
                    </div>
                    <button
                      type="button"
                      className="danger"
                      onClick={() => void handleDeleteExperiment(experiment.id)}
                      disabled={loading}
                    >
                      Delete
                    </button>
                  </article>
                ))}
                {selectedProject.experiments.length === 0 && <p className="muted small">No experiments yet.</p>}
              </div>
            </section>

            <section className="card">
              <h2>Runs Comparison (W&B-style)</h2>
              <form className="grid-form" onSubmit={refreshRunComparison}>
                <label>
                  Focus Metric Key
                  <input value={runMetricKey} onChange={(e) => setRunMetricKey(e.target.value)} placeholder="accuracy" />
                </label>
                <button type="submit" disabled={loading}>
                  Refresh Comparison
                </button>
              </form>
              <div className="list">
                {runComparison?.items.map((item) => (
                  <article key={item.run_id} className={`list-item ${runComparison.best_run_id === item.run_id ? "highlight" : ""}`}>
                    <div>
                      <strong>
                        Run #{item.run_id} - {item.experiment_title}
                      </strong>
                      <p className="small">
                        Status: {item.status} | {runComparison.metric_key ?? "metric"}: {item.selected_metric ?? "N/A"}
                      </p>
                      <p className="small">Params: {Object.keys(item.params).length > 0 ? JSON.stringify(item.params) : "none"}</p>
                      <p className="small">Metrics: {Object.keys(item.metrics).length > 0 ? JSON.stringify(item.metrics) : "none"}</p>
                    </div>
                  </article>
                ))}
                {(runComparison?.items.length ?? 0) === 0 && <p className="muted small">No runs to compare yet.</p>}
              </div>
            </section>

            <section className="card">
              <h2>Benchmark Evaluations</h2>
              <form className="grid-form" onSubmit={handleCreateBenchmark}>
                <label>
                  Experiment Link
                  <select value={benchmarkExperimentId} onChange={(e) => setBenchmarkExperimentId(e.target.value)}>
                    <option value="">None</option>
                    {selectedProject.experiments.map((experiment) => (
                      <option key={experiment.id} value={experiment.id}>
                        {experiment.title}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Dataset
                  <input value={benchmarkDataset} onChange={(e) => setBenchmarkDataset(e.target.value)} required />
                </label>
                <label>
                  Metric Name
                  <input value={benchmarkMetricName} onChange={(e) => setBenchmarkMetricName(e.target.value)} required />
                </label>
                <label>
                  Metric Value
                  <input
                    type="number"
                    step="any"
                    value={benchmarkMetricValue}
                    onChange={(e) => setBenchmarkMetricValue(e.target.value)}
                    required
                  />
                </label>
                <label>
                  Notes
                  <textarea value={benchmarkNotes} onChange={(e) => setBenchmarkNotes(e.target.value)} />
                </label>
                <button type="submit" disabled={loading}>
                  Add Benchmark
                </button>
              </form>
              <div className="list">
                {selectedProject.benchmarks.map((benchmark) => (
                  <article key={benchmark.id} className="list-item">
                    <div>
                      <strong>{benchmark.dataset}</strong> - {benchmark.metric_name}: {benchmark.metric_value}
                      {benchmark.notes && <p>{benchmark.notes}</p>}
                    </div>
                  </article>
                ))}
                {selectedProject.benchmarks.length === 0 && <p className="muted small">No benchmarks yet.</p>}
              </div>
            </section>

            <section className="card">
              <h2>Result Tables (Stage 6)</h2>
              <form className="stacked-form" onSubmit={handleCreateTable}>
                <label>
                  Table Title
                  <input value={tableTitle} onChange={(e) => setTableTitle(e.target.value)} required />
                </label>
                <label>
                  Markdown Table
                  <textarea value={tableMarkdown} onChange={(e) => setTableMarkdown(e.target.value)} required />
                </label>
                <button type="submit" disabled={loading}>
                  Save Table
                </button>
              </form>
              <div className="list">
                {selectedProject.result_tables.map((table) => (
                  <article key={table.id} className="list-item">
                    <div>
                      <strong>{table.title}</strong>
                      <pre>{table.table_markdown}</pre>
                    </div>
                  </article>
                ))}
                {selectedProject.result_tables.length === 0 && <p className="muted small">No result tables yet.</p>}
              </div>
            </section>

            <section className="card">
              <h2>Knowledge Pages (Confluence-style)</h2>
              <form className="grid-form" onSubmit={handleCreatePage}>
                <label>
                  Title
                  <input value={pageTitle} onChange={(e) => setPageTitle(e.target.value)} required />
                </label>
                <label>
                  Parent Page
                  <select value={pageParentId} onChange={(e) => setPageParentId(e.target.value)}>
                    <option value="">Top-level page</option>
                    {pages.map((page) => (
                      <option key={page.id} value={page.id}>
                        {page.title}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Content
                  <textarea value={pageContent} onChange={(e) => setPageContent(e.target.value)} />
                </label>
                <button type="submit" disabled={loading}>
                  Create Page
                </button>
              </form>
              <div className="list">
                {pages.map((page) => (
                  <article key={page.id} className="list-item">
                    <div>
                      <strong>{page.title}</strong>
                      {page.parent_page_id && <p className="small muted">Parent: #{page.parent_page_id}</p>}
                      <p>{page.content || "No content yet."}</p>
                      <p className="small muted">
                        Updated by {page.updated_by_name ?? "Unknown"} at {new Date(page.updated_at).toLocaleString()}
                      </p>
                    </div>
                  </article>
                ))}
                {pages.length === 0 && <p className="muted small">No project pages yet.</p>}
              </div>
            </section>

            <section className="card">
              <h2>Final Evaluation & LaTeX Report (Stage 8)</h2>
              <form className="stacked-form" onSubmit={handleCreateReport}>
                <label>
                  Discussion
                  <textarea value={reportDiscussion} onChange={(e) => setReportDiscussion(e.target.value)} />
                </label>
                <label>
                  Evaluation Summary
                  <textarea value={reportEvaluation} onChange={(e) => setReportEvaluation(e.target.value)} />
                </label>
                <label>
                  LaTeX Snippet
                  <textarea value={reportLatex} onChange={(e) => setReportLatex(e.target.value)} />
                </label>
                <button type="submit" disabled={loading}>
                  Save Report
                </button>
              </form>
              <div className="list">
                {selectedProject.final_reports.map((report) => (
                  <article key={report.id} className="list-item">
                    <div>
                      <strong>Updated: {new Date(report.updated_at).toLocaleString()}</strong>
                      {report.discussion && <p>{report.discussion}</p>}
                      {report.evaluation_summary && <p>{report.evaluation_summary}</p>}
                      {report.latex_snippet && <pre>{report.latex_snippet}</pre>}
                    </div>
                  </article>
                ))}
                {selectedProject.final_reports.length === 0 && <p className="muted small">No reports yet.</p>}
              </div>
            </section>
          </>
        ) : (
          <section className="card">
            <p className="muted">Create a project to start mapping your AI lifecycle workflow.</p>
          </section>
        )}
      </main>
    </div>
  );
}
