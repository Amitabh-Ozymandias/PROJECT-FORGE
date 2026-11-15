from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
from uuid import uuid4

from forge_lab.model import Design

from .schemas import ProjectCreate, ProjectDocument, ProjectSummary


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def default_design(design_id: str) -> dict:
    return {
        "design_id": design_id,
        "part": {"length_m": 0.18, "width_m": 0.032, "height_m": 0.012},
        "material": {
            "name": "6061-T6 aluminium",
            "youngs_modulus_pa": 68_900_000_000,
            "yield_strength_pa": 276_000_000,
            "density_kg_m3": 2700,
        },
        "load_case": {"name": "rated end load", "end_force_n": 850},
        "constraints": {
            "minimum_factor_of_safety": 2.0,
            "maximum_tip_deflection_m": 0.0015,
            "minimum_width_m": 0.02,
            "maximum_width_m": 0.08,
            "minimum_height_m": 0.006,
            "maximum_height_m": 0.05,
            "manufacturing_increment_m": 0.001,
        },
    }


class ProjectStore:
    """Local, human-readable .forge project documents; no cloud service required."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[ProjectSummary]:
        projects: list[ProjectSummary] = []
        for manifest in self.root.glob("*/project.forge.json"):
            payload = self._read(manifest)
            projects.append(ProjectSummary(**{key: payload[key] for key in ProjectSummary.model_fields}))
        return sorted(projects, key=lambda item: item.updated_at, reverse=True)

    def create(self, request: ProjectCreate) -> ProjectDocument:
        project_id = str(uuid4())
        design = request.design or default_design(project_id)
        Design.from_dict(design)
        now = utc_now()
        document = ProjectDocument(
            project_id=project_id,
            name=request.name.strip(),
            created_at=now,
            updated_at=now,
            design=design,
        )
        self._write(document)
        return document

    def get(self, project_id: str) -> ProjectDocument:
        path = self._manifest_path(project_id)
        if not path.is_file():
            raise FileNotFoundError(project_id)
        return ProjectDocument(**self._read(path))

    def update_design(self, project_id: str, design: dict) -> ProjectDocument:
        document = self.get(project_id)
        Design.from_dict(design)
        updated = document.model_copy(update={"design": design, "updated_at": utc_now()})
        self._write(updated)
        return updated

    def save_run(self, project_id: str, run: dict) -> Path:
        project_dir = self._manifest_path(project_id).parent
        if not project_dir.is_dir():
            raise FileNotFoundError(project_id)
        runs_dir = project_dir / "runs"
        runs_dir.mkdir(exist_ok=True)
        path = runs_dir / f"{run['run_id']}.json"
        path.write_text(json.dumps(run, indent=2), encoding="utf-8")
        return path

    def _manifest_path(self, project_id: str) -> Path:
        return self.root / project_id / "project.forge.json"

    @staticmethod
    def _read(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def _write(self, document: ProjectDocument) -> None:
        path = self._manifest_path(document.project_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(document.model_dump_json(indent=2), encoding="utf-8")
