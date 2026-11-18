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

                self.assertIn(len(geometry.vertices), (8, 24))
                self.assertEqual(len(geometry.triangles), 36)
                self.assertIn("run_id", result["run"])

                # Test CAD exports
                step_res = api.export_step(project.project_id)
                self.assertTrue(Path(step_res.path).exists())
                self.assertGreater(Path(step_res.path).stat().st_size, 0)

                stl_res = api.export_stl(project.project_id)
                self.assertTrue(Path(stl_res.path).exists())
                self.assertGreater(Path(stl_res.path).stat().st_size, 0)
        finally:
            api.store = original_store
