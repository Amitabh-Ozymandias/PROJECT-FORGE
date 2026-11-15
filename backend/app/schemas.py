from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    design: dict[str, Any] | None = None


class ProjectUpdate(BaseModel):
    design: dict[str, Any]


class ProjectSummary(BaseModel):
    project_id: str
    name: str
    created_at: str
    updated_at: str


class ProjectDocument(ProjectSummary):
    design: dict[str, Any]


class GeometryPreview(BaseModel):
    generator: str
    vertices: list[list[float]]
    triangles: list[int]
    dimensions_m: dict[str, float]
