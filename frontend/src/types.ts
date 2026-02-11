export type LifecycleStatus = "pending" | "in_progress" | "completed" | "blocked";
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
