import json
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.release_workflow_demo import (
    WorkflowError,
    plan_workflow,
    resolve_executable,
    run_workflow,
    validate_handoff,
)


def write_handoff(packet: Path, *, findings: list[object], state: str) -> None:
    packet.mkdir(parents=True)
    (packet / "RELEASE_HANDOFF.md").write_text("synthetic", encoding="utf-8")
    (packet / "RELEASE_HANDOFF.html").write_text("synthetic", encoding="utf-8")
    (packet / "RELEASE_HANDOFF.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "findings": findings,
                "coverforge": {"linkage": {"state": state}},
            }
        ),
        encoding="utf-8",
    )


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


class WorkflowExecutionTests(unittest.TestCase):
    def setUp(self):
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary_directory.name)

    def tearDown(self):
        self._temporary_directory.cleanup()

    def test_run_workflow_runs_fixed_vectors_and_validates_an_aligned_handoff(self):
        plan = plan_workflow(
            self.root / "workflow",
            releaseforge_bin=sys.executable,
            coverforge_bin=sys.executable,
        )
        calls: list[tuple[str, ...]] = []

        def runner(command: tuple[str, ...]) -> None:
            calls.append(command)
            if command[1] == "demo":
                cover = plan.release_demo / "release-v1" / "artwork" / "final-cover.jpg"
                cover.parent.mkdir(parents=True)
                cover.write_bytes(b"synthetic")
                (plan.release_demo / "proof-v1").mkdir()
                (plan.release_demo / "proof-v1" / "RELEASE_PROOF.json").write_text(
                    "{}", encoding="utf-8"
                )
            elif command[1] == "build":
                plan.coverforge_packet.mkdir()
                (plan.coverforge_packet / "manifest.json").write_text("{}", encoding="utf-8")
            else:
                write_handoff(plan.handoff_packet, findings=[], state="aligned")

        result = run_workflow(plan, runner=runner)

        self.assertEqual(calls, list(plan.commands))
        self.assertEqual(result.coverforge_state, "aligned")

    def test_validate_handoff_rejects_non_aligned_capture(self):
        packet = self.root / "handoff"
        write_handoff(packet, findings=[], state="needs_evidence")

        with self.assertRaisesRegex(WorkflowError, "not aligned"):
            validate_handoff(packet)

    def test_validate_handoff_rejects_an_unexpected_file(self):
        packet = self.root / "handoff"
        write_handoff(packet, findings=[], state="aligned")
        (packet / "unexpected.txt").write_text("unexpected", encoding="utf-8")

        with self.assertRaisesRegex(WorkflowError, "expected exactly"):
            validate_handoff(packet)

    def test_validate_handoff_rejects_findings(self):
        packet = self.root / "handoff"
        write_handoff(packet, findings=[{"state": "needs_evidence"}], state="aligned")

        with self.assertRaisesRegex(WorkflowError, "contains findings"):
            validate_handoff(packet)
