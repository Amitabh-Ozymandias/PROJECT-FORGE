from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from forge_lab.model import Design
from forge_lab.simulation import CantileverBeamSolver

from .geometry import CadQueryGeometryService
from .projects import ProjectStore
from .schemas import GeometryPreview, ProjectCreate, ProjectDocument, ProjectSummary, ProjectUpdate


def project_root() -> Path:
    configured = os.environ.get("FORGE_PROJECT_ROOT")
    return Path(configured) if configured else Path.cwd() / "projects"


store = ProjectStore(project_root())
geometry = CadQueryGeometryService()
solver = CantileverBeamSolver()
app = FastAPI(title="FORGE Local Engineering API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    # "null" is the origin used by Electron's packaged file renderer. The API is
    # loopback-only and Electron keeps Node integration disabled in the renderer.
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "null"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ready",
        "project_root": str(store.root),
        "capabilities": {"cadquery": geometry.cadquery_available, "gmsh": False, "calculix": False},
    }


@app.get("/api/projects", response_model=list[ProjectSummary])
def list_projects() -> list[ProjectSummary]:
    return store.list()


@app.post("/api/projects", response_model=ProjectDocument, status_code=201)
def create_project(request: ProjectCreate) -> ProjectDocument:
    try:
        return store.create(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/projects/{project_id}", response_model=ProjectDocument)
def get_project(project_id: str) -> ProjectDocument:
    try:
        return store.get(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@app.put("/api/projects/{project_id}", response_model=ProjectDocument)
def update_project(project_id: str, request: ProjectUpdate) -> ProjectDocument:
    try:
        return store.update_design(project_id, request.design)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/projects/{project_id}/geometry", response_model=GeometryPreview)
def project_geometry(project_id: str) -> GeometryPreview:
    try:
        project = store.get(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
    return geometry.preview(Design.from_dict(project.design))


@app.post("/api/projects/{project_id}/runs/static")
def run_static_analysis(project_id: str) -> dict:
    try:
        project = store.get(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
    run = solver.simulate(Design.from_dict(project.design)).to_dict()
    path = store.save_run(project_id, run)
    return {"run": run, "path": str(path)}
