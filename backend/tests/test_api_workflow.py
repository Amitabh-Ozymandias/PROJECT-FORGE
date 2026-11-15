import tempfile
import unittest
from pathlib import Path

import backend.app.main as api
from backend.app.projects import ProjectStore
from backend.app.schemas import ProjectCreate


class LocalApiWorkflowTests(unittest.TestCase):
    def test_create_preview_and_static_run(self) -> None:
        original_store = api.store
        try:
            with tempfile.TemporaryDirectory() as directory:
                api.store = ProjectStore(Path(directory))
                project = api.create_project(ProjectCreate(name="API smoke"))
                geometry = api.project_geometry(project.project_id)
                result = api.run_static_analysis(project.project_id)

                self.assertEqual(len(geometry.vertices), 8)
                self.assertEqual(len(geometry.triangles), 36)
                self.assertIn("run_id", result["run"])
        finally:
            api.store = original_store
