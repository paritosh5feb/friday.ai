export type LifecycleStatus = "pending" | "in_progress" | "completed" | "blocked";
export type ProjectRole = "admin" | "manager" | "researcher" | "reviewer" | "viewer";
export type ProjectScope =
  | "manage_members"
  | "manage_lifecycle"
  | "manage_experiments"
  | "manage_runs"
  | "manage_tasks"
  | "manage_pages";
export type ExperimentKind =
  | "baseline"
  | "reproduction"
  | "partial"
  | "benchmark"
  | "scaled"
  | "final";
export type ExperimentStatus = "planned" | "running" | "completed" | "failed";

export interface User {
  id: number;
  email: string;
  full_name: string;
  created_at: string;
}

export interface Project {
  id: number;
  name: string;
  description: string;
  objective: string;
  hypothesis: string;
  created_at: string;
  updated_at: string;
}

export interface LifecycleStage {
  id: number;
  project_id: number;
  stage_number: number;
  title: string;
  guidance: string;
  status: LifecycleStatus;
  notes: string;
  updated_at: string;
}

export interface Experiment {
  id: number;
  project_id: number;
  kind: ExperimentKind;
  title: string;
  hypothesis: string;
  setup_notes: string;
  result_summary: string;
  metric_name: string;
  metric_value: number | null;
  status: ExperimentStatus;
  created_at: string;
  updated_at: string;
}

export interface Benchmark {
  id: number;
  project_id: number;
  experiment_id: number | null;
  dataset: string;
  metric_name: string;
  metric_value: number;
  notes: string;
  created_at: string;
}

export interface ResultTable {
  id: number;
  project_id: number;
  title: string;
  table_markdown: string;
  created_at: string;
}

export interface FinalReport {
  id: number;
  project_id: number;
  discussion: string;
  evaluation_summary: string;
  latex_snippet: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectDetail extends Project {
  lifecycle_stages: LifecycleStage[];
  experiments: Experiment[];
  benchmarks: Benchmark[];
  result_tables: ResultTable[];
  final_reports: FinalReport[];
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface ProjectMember {
  id: number;
  project_id: number;
  user_id: number;
  user_email: string;
  user_full_name: string;
  role: ProjectRole;
  scopes: ProjectScope[];
  created_at: string;
}

export type TaskStatus = "backlog" | "todo" | "in_progress" | "in_review" | "done";
export type TaskPriority = "low" | "medium" | "high" | "critical";

export interface TaskItem {
  id: number;
  project_id: number;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee_id: number | null;
  assignee_name: string | null;
  reporter_id: number | null;
  reporter_name: string | null;
  stage_number: number | null;
  story_points: number | null;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface KanbanBoard {
  project_id: number;
  columns: Record<TaskStatus, TaskItem[]>;
}

export interface ProjectPage {
  id: number;
  project_id: number;
  title: string;
  content: string;
  parent_page_id: number | null;
  author_id: number | null;
  author_name: string | null;
  updated_by_id: number | null;
  updated_by_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface RunComparisonItem {
  run_id: number;
  experiment_id: number;
  experiment_title: string;
  status: "queued" | "running" | "completed" | "failed";
  selected_metric: number | null;
  metrics: Record<string, number>;
  params: Record<string, string>;
  started_at: string;
  finished_at: string | null;
}

export interface RunComparison {
  project_id: number;
  metric_key: string | null;
  items: RunComparisonItem[];
  best_run_id: number | null;
  best_metric_value: number | null;
}
