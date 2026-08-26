from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import client_workflow_check
from scripts.client_workflow_check import (
    EXPECTED_REVIEW_FILES,
    WorkflowError,
    WorkflowResult,
    main,
    plan_workflow,
    resolve_executable,
    run_workflow,
)


class ClientWorkflowCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.intake = self.root / "private-intake.toml"
        self.quote = self.root / "private-quote.toml"
        self.intake.write_text("title = 'Private intake'\n", encoding="utf-8")
        self.quote.write_text("reference = 'Private quote'\n", encoding="utf-8")
        self.destination = self.root / "client-workflow-review"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def plan(self, destination: Path | None = None):
        return plan_workflow(
            self.intake,
            self.quote,
            destination or self.destination,
            mixintake_bin=sys.executable,
            scopequote_bin=sys.executable,
        )

    def sequenced_runner(self, *exit_codes: int):
        calls: list[tuple[str, ...]] = []
        remaining = iter(exit_codes)

        def runner(command: tuple[str, ...]) -> int:
            calls.append(command)
            return next(remaining)

        return runner, calls

    def test_resolves_an_explicit_trusted_executable(self) -> None:
        resolved = resolve_executable(sys.executable, "Mixintake")

        self.assertEqual(resolved, Path(sys.executable).resolve())

    def test_rejects_an_unavailable_executable_without_exposing_value(self) -> None:
        with self.assertRaisesRegex(WorkflowError, "Mixintake executable is not available"):
            resolve_executable("definitely-not-a-client-tool", "Mixintake")

    def test_plan_uses_literal_check_vectors_and_keeps_destination_absent(self) -> None:
        plan = self.plan()

        executable = str(Path(sys.executable).resolve())
        self.assertEqual(
            plan.commands,
            (
                (executable, "check", str(self.intake.resolve())),
                (executable, "check", str(self.quote.resolve())),
            ),
        )
        self.assertFalse(self.destination.exists())

    def test_settled_statuses_write_exact_path_free_packet(self) -> None:
        plan = self.plan()
        runner, calls = self.sequenced_runner(0, 0)

        result = run_workflow(plan, runner=runner)

        self.assertEqual(calls, list(plan.commands))
        self.assertFalse(result.follow_up)
        self.assertEqual({path.name for path in result.files}, EXPECTED_REVIEW_FILES)
        self.assertEqual({path.name for path in self.destination.iterdir()}, EXPECTED_REVIEW_FILES)

        markdown = (self.destination / "CLIENT_WORKFLOW_REVIEW.md").read_text(encoding="utf-8")
        review = json.loads((self.destination / "CLIENT_WORKFLOW_REVIEW.json").read_text(encoding="utf-8"))
        manifest = json.loads((self.destination / "manifest.json").read_text(encoding="utf-8"))
        combined = json.dumps([markdown, review, manifest], sort_keys=True)

        self.assertNotIn(str(self.intake), combined)
        self.assertNotIn(str(self.quote), combined)
        self.assertNotIn("untrusted child output", combined)
        self.assertIn("human action", markdown.lower())
        self.assertIn("not establish", markdown.lower())
        self.assertFalse(review["declaration_follow_up"])
        self.assertEqual([outcome["exit_code"] for outcome in review["outcomes"]], [0, 0])

        records = {record["path"]: record for record in manifest["files"]}
        self.assertEqual(set(records), {"CLIENT_WORKFLOW_REVIEW.md", "CLIENT_WORKFLOW_REVIEW.json"})
        for filename, record in records.items():
            content = (self.destination / filename).read_bytes()
            self.assertEqual(record["bytes"], len(content))
            self.assertEqual(record["sha256"], hashlib.sha256(content).hexdigest())

    def test_two_follow_up_statuses_write_packet_and_are_reported(self) -> None:
        plan = self.plan()
        runner, _ = self.sequenced_runner(2, 2)

        result = run_workflow(plan, runner=runner)

        self.assertTrue(result.follow_up)
        self.assertEqual(result.outcomes[0].declared_state, "declared source or deliverable follow-up remains")
        self.assertEqual(result.outcomes[1].declared_state, "quote declaration remains a draft")
        review = json.loads((self.destination / "CLIENT_WORKFLOW_REVIEW.json").read_text(encoding="utf-8"))
        self.assertTrue(review["declaration_follow_up"])

    def test_actual_child_console_output_is_discarded(self) -> None:
        child = self.root / "trusted-child-checker.py"
        child.write_text(
            "#!" + sys.executable + "\n"
            "import sys\n"
            "print('untrusted child output: ' + sys.argv[-1])\n"
            "raise SystemExit(0)\n",
            encoding="utf-8",
        )
        child.chmod(child.stat().st_mode | 0o111)
        plan = plan_workflow(
            self.intake,
            self.quote,
            self.destination,
            mixintake_bin=str(child),
            scopequote_bin=str(child),
        )

        run_workflow(plan)

        combined = "\n".join(
            path.read_text(encoding="utf-8") for path in self.destination.iterdir()
        )
        self.assertNotIn("untrusted child output", combined)
        self.assertNotIn(str(self.intake), combined)
        self.assertNotIn(str(self.quote), combined)

    def test_unrecognised_child_exit_creates_no_destination(self) -> None:
        plan = self.plan()
        runner, _ = self.sequenced_runner(0, 1)

        with self.assertRaisesRegex(WorkflowError, "recognised declared status"):
            run_workflow(plan, runner=runner)

        self.assertFalse(self.destination.exists())

    def test_existing_destination_is_never_overwritten(self) -> None:
        self.destination.mkdir()
        marker = self.destination / "keep.txt"
        marker.write_text("do not overwrite", encoding="utf-8")

        with self.assertRaisesRegex(WorkflowError, "workflow destination already exists"):
            self.plan()

        self.assertEqual(marker.read_text(encoding="utf-8"), "do not overwrite")

    def test_main_returns_follow_up_status_without_printing_inputs(self) -> None:
        plan = self.plan()
        result = WorkflowResult(
            destination=self.destination,
            outcomes=(),
            follow_up=True,
            files=(),
            manifest_path=self.destination / "manifest.json",
        )
        stdout = io.StringIO()
        with (
            mock.patch.object(client_workflow_check, "plan_workflow", return_value=plan),
            mock.patch.object(client_workflow_check, "run_workflow", return_value=result),
            contextlib.redirect_stdout(stdout),
        ):
            exit_code = main(
                [
                    str(self.intake),
                    str(self.quote),
                    "--output",
                    str(self.destination),
                    "--mixintake-bin",
                    sys.executable,
                    "--scopequote-bin",
                    sys.executable,
                ]
            )

        self.assertEqual(exit_code, 2)
        self.assertNotIn(str(self.intake), stdout.getvalue())
        self.assertNotIn(str(self.quote), stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
