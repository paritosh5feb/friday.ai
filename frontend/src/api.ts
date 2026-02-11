import type {
  AuthToken,
  Benchmark,
  Experiment,
  FinalReport,
  LifecycleStage,
  Project,
  ProjectDetail,
  ResultTable,
  User,
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

type RequestOptions = Omit<RequestInit, "body"> & { body?: unknown };

async function request<T>(path: string, options: RequestOptions = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers ?? {});
  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const payload = await response.json();
      if (typeof payload?.detail === "string") {
        detail = payload.detail;
      }
    } catch {
      // Keep fallback detail string when response body is not JSON.
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const api = {
  signup: (email: string, fullName: string, password: string) =>
    request<AuthToken>("/auth/signup", { method: "POST", body: { email, full_name: fullName, password } }),

  login: (email: string, password: string) =>
    request<AuthToken>("/auth/login", { method: "POST", body: { email, password } }),

  me: (token: string) => request<User>("/auth/me", { method: "GET" }, token),

  listProjects: (token: string) => request<Project[]>("/projects", { method: "GET" }, token),

  createProject: (token: string, payload: { name: string; objective: string; hypothesis: string }) =>
    request<ProjectDetail>("/projects", { method: "POST", body: payload }, token),

  getProject: (token: string, projectId: number) => request<ProjectDetail>(`/projects/${projectId}`, { method: "GET" }, token),

  updateStage: (
    token: string,
    stageId: number,
    payload: {
      status?: LifecycleStage["status"];
      notes?: string;
    },
  ) => request<LifecycleStage>(`/stages/${stageId}`, { method: "PATCH", body: payload }, token),

  createExperiment: (
    token: string,
    projectId: number,
    payload: {
      kind: Experiment["kind"];
      title: string;
      hypothesis: string;
      setup_notes: string;
      result_summary: string;
      metric_name: string;
      metric_value: number | null;
      status: Experiment["status"];
    },
  ) => request<Experiment>(`/projects/${projectId}/experiments`, { method: "POST", body: payload }, token),

  deleteExperiment: (token: string, experimentId: number) =>
    request<void>(`/experiments/${experimentId}`, { method: "DELETE" }, token),

  createBenchmark: (
    token: string,
    projectId: number,
    payload: {
      experiment_id: number | null;
      dataset: string;
      metric_name: string;
      metric_value: number;
      notes: string;
    },
  ) => request<Benchmark>(`/projects/${projectId}/benchmarks`, { method: "POST", body: payload }, token),

  createTable: (
    token: string,
    projectId: number,
    payload: {
      title: string;
      table_markdown: string;
    },
  ) => request<ResultTable>(`/projects/${projectId}/tables`, { method: "POST", body: payload }, token),

  createReport: (
    token: string,
    projectId: number,
    payload: {
      discussion: string;
      evaluation_summary: string;
      latex_snippet: string;
    },
  ) => request<FinalReport>(`/projects/${projectId}/reports`, { method: "POST", body: payload }, token),
};
