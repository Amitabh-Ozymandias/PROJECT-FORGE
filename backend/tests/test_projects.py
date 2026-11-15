import tempfile
import unittest
from pathlib import Path

from backend.app.projects import ProjectStore
from backend.app.schemas import ProjectCreate


class ProjectStoreTests(unittest.TestCase):
    def test_creates_readable_local_project_and_persists_runs(self) -> None:
        workspace = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(dir=workspace) as directory:
            store = ProjectStore(Path(directory))
            project = store.create(ProjectCreate(name="Bracket"))
            self.assertEqual(store.get(project.project_id).name, "Bracket")
            self.assertEqual(len(store.list()), 1)
            result = store.save_run(project.project_id, {"run_id": "test-run"})
            self.assertTrue(result.is_file())


if __name__ == "__main__":
    unittest.main()
