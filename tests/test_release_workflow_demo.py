import sys
import tempfile
import unittest
from pathlib import Path

from scripts.release_workflow_demo import WorkflowError, plan_workflow, resolve_executable


class WorkflowPlanTests(unittest.TestCase):
    def setUp(self):
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary_directory.name)

    def tearDown(self):
        self._temporary_directory.cleanup()

    def test_plan_uses_fresh_destination_and_literal_command_vectors(self):
        root = self.root / "workflow"

        plan = plan_workflow(
            root,
            releaseforge_bin=sys.executable,
            coverforge_bin=sys.executable,
        )

        self.assertEqual(plan.destination, root.resolve())
        self.assertFalse(root.exists())
        self.assertEqual(
            plan.commands[0],
            (str(Path(sys.executable).resolve()), "demo", str(root.resolve() / "releaseforge-demo")),
        )
        self.assertEqual(
            plan.commands[1][1:3],
            ("build", str(plan.release_demo / "release-v1" / "artwork" / "final-cover.jpg")),
        )
        self.assertNotIn("shell", plan.__dict__)

    def test_plan_refuses_existing_destination(self):
        root = self.root / "workflow"
        root.mkdir()

        with self.assertRaisesRegex(WorkflowError, "already exists"):
            plan_workflow(root, releaseforge_bin=sys.executable, coverforge_bin=sys.executable)

    def test_resolve_executable_rejects_an_unavailable_command(self):
        with self.assertRaisesRegex(WorkflowError, "not available"):
            resolve_executable("not-a-real-release-workflow-binary", "Releaseforge")
