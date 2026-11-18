import type { Design, Geometry, Project, SimulationRun } from "./types";

const endpoint = "http://127.0.0.1:8000/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${endpoint}${path}`, { headers: { "Content-Type": "application/json" }, ...options });
  if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? `Request failed (${response.status})`);
  return response.json() as Promise<T>;
}

export const api = {
  listProjects: () => request<Array<Pick<Project, "project_id" | "name" | "created_at" | "updated_at">>>("/projects"),
  createProject: (name: string) => request<Project>("/projects", { method: "POST", body: JSON.stringify({ name }) }),
  getProject: (id: string) => request<Project>(`/projects/${id}`),
  saveDesign: (id: string, design: Design) => request<Project>(`/projects/${id}`, { method: "PUT", body: JSON.stringify({ design }) }),
  geometry: (id: string) => request<Geometry>(`/projects/${id}/geometry`),
  runStatic: (id: string) => request<{ run: SimulationRun }>(`/projects/${id}/runs/static`, { method: "POST" }),
  exportStepUrl: (id: string) => `${endpoint}/projects/${id}/export/step`,
  exportStlUrl: (id: string) => `${endpoint}/projects/${id}/export/stl`,
};
