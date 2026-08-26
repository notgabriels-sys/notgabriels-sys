#!/usr/bin/env python3
"""Create a local, status-only review across Mixintake and Scopequote.

This module deliberately treats the companion tools as independent sources of
declared status.  It passes each selected TOML path only to its corresponding
local checker and stores neither input paths nor input contents in its output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path


EXPECTED_REVIEW_FILES = frozenset(
    {
        "CLIENT_WORKFLOW_REVIEW.md",
        "CLIENT_WORKFLOW_REVIEW.json",
        "manifest.json",
    }
)


class WorkflowError(ValueError):
    """Raised when a status-only client-workflow review cannot be created."""


@dataclass(frozen=True)
class WorkflowPlan:
    """Resolved executable vectors and a fresh destination for one review."""

    destination: Path
    commands: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class ToolOutcome:
    """The recognised, declared state returned by one companion checker."""

    tool: str
    exit_code: int
    declared_state: str
    follow_up: bool


@dataclass(frozen=True)
class WorkflowResult:
    """The three generated local review files and their declared status."""

    destination: Path
    outcomes: tuple[ToolOutcome, ...]
    follow_up: bool
    files: tuple[Path, ...]
    manifest_path: Path


def resolve_executable(value: str, label: str) -> Path:
    """Resolve a trusted local executable path or a command available on PATH.

    An operator who supplies an override is responsible for trusting that local
    executable.  This resolver does not install, download, or inspect tools.
    """

    candidate_value = value.strip()
    if not candidate_value:
        raise WorkflowError(f"{label} executable is not available")

    if "/" in candidate_value or "\\" in candidate_value:
        candidate = Path(candidate_value).expanduser()
    else:
        found = shutil.which(candidate_value)
        if found is None:
            raise WorkflowError(f"{label} executable is not available")
        candidate = Path(found)

    try:
        resolved = candidate.resolve(strict=True)
    except OSError as error:
        raise WorkflowError(f"{label} executable is not available") from error

    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise WorkflowError(f"{label} executable is not available")
    return resolved


def _readable_input(value: str | Path, label: str) -> Path:
    """Validate metadata only; selected TOML content remains child-tool data."""

    try:
        resolved = Path(value).expanduser().resolve(strict=True)
    except OSError as error:
        raise WorkflowError(f"{label} input is not a readable regular file") from error

    if not resolved.is_file() or not os.access(resolved, os.R_OK):
        raise WorkflowError(f"{label} input is not a readable regular file")
    return resolved


def plan_workflow(
    intake_path: str | Path,
    quote_path: str | Path,
    destination: str | Path,
    *,
    mixintake_bin: str = "mixintake",
    scopequote_bin: str = "scopequote",
) -> WorkflowPlan:
    """Create literal child command vectors for a destination that is unused."""

    destination_path = Path(destination).expanduser().resolve()
    if destination_path.exists():
        raise WorkflowError("workflow destination already exists")

    intake_input = _readable_input(intake_path, "Mixintake")
    quote_input = _readable_input(quote_path, "Scopequote")
    mixintake_executable = resolve_executable(mixintake_bin, "Mixintake")
    scopequote_executable = resolve_executable(scopequote_bin, "Scopequote")

    return WorkflowPlan(
        destination=destination_path,
        commands=(
            (str(mixintake_executable), "check", str(intake_input)),
            (str(scopequote_executable), "check", str(quote_input)),
        ),
    )


def _run_command(command: Sequence[str]) -> int:
    """Run one literal local command while discarding child console output."""

    try:
        completed = subprocess.run(
            command,
            check=False,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as error:
        raise WorkflowError("child check could not start") from error
    return completed.returncode


def _outcome_for(tool: str, exit_code: int) -> ToolOutcome:
    if type(exit_code) is not int or exit_code not in {0, 2}:
        raise WorkflowError(f"{tool} check did not return a recognised declared status")

    if tool == "Mixintake":
        if exit_code == 0:
            return ToolOutcome(
                tool=tool,
                exit_code=exit_code,
                declared_state="declared sources and deliverables are settled",
                follow_up=False,
            )
        return ToolOutcome(
            tool=tool,
            exit_code=exit_code,
            declared_state="declared source or deliverable follow-up remains",
            follow_up=True,
        )

    if exit_code == 0:
        return ToolOutcome(
            tool=tool,
            exit_code=exit_code,
            declared_state="quote is declared human-reviewed",
            follow_up=False,
        )
    return ToolOutcome(
        tool=tool,
        exit_code=exit_code,
        declared_state="quote declaration remains a draft",
        follow_up=True,
    )


def _outcome_records(outcomes: Sequence[ToolOutcome]) -> list[dict[str, object]]:
    return [
        {
            "tool": outcome.tool,
            "exit_code": outcome.exit_code,
            "declared_state": outcome.declared_state,
            "follow_up": outcome.follow_up,
        }
        for outcome in outcomes
    ]


def _review_boundary() -> str:
    return (
        "This local review records only two declared check outcomes. It does not "
        "establish material receipt, commercial terms, work scheduling, invoicing, "
        "money status, transfer of assets, client consent, or clearance for a real "
        "client workflow. Human action remains required."
    )


def _render_markdown(outcomes: Sequence[ToolOutcome], follow_up: bool) -> str:
    rows = "\n".join(
        f"| {outcome.tool} | {outcome.exit_code} | {outcome.declared_state} | "
        f"{'Yes' if outcome.follow_up else 'No'} |"
        for outcome in outcomes
    )
    summary = (
        "At least one declared follow-up remains. Human action is required before "
        "relying on this record."
        if follow_up
        else "Both tools reported settled declarations. Human action is still "
        "required; this record does not establish readiness for a real client workflow."
    )
    return "\n".join(
        (
            "# Client Workflow Review",
            "",
            "> LOCAL DECLARATION REVIEW — HUMAN CHECK REQUIRED",
            "",
            "## Recorded outcomes",
            "",
            "| Check | Exit status | Declared state | Follow-up |",
            "| --- | ---: | --- | --- |",
            rows,
            "",
            "## Interpretation",
            "",
            summary,
            "",
            "## Boundary",
            "",
            _review_boundary(),
            "",
        )
    )


def _render_review_json(outcomes: Sequence[ToolOutcome], follow_up: bool) -> str:
    payload = {
        "schema_version": 1,
        "review_type": "local declaration status only",
        "declaration_follow_up": follow_up,
        "outcomes": _outcome_records(outcomes),
        "boundary": _review_boundary(),
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _file_record(path: Path) -> dict[str, object]:
    content = path.read_bytes()
    return {
        "path": path.name,
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def _render_manifest(outcomes: Sequence[ToolOutcome], follow_up: bool, files: Sequence[Path]) -> str:
    payload = {
        "schema_version": 1,
        "tool": "client-workflow-check",
        "declaration_follow_up": follow_up,
        "outcomes": _outcome_records(outcomes),
        "files": [_file_record(path) for path in files],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def run_workflow(
    plan: WorkflowPlan,
    *,
    runner: Callable[[Sequence[str]], int] = _run_command,
) -> WorkflowResult:
    """Run recognised child checks, then write the status-only review packet."""

    outcomes = tuple(
        _outcome_for(tool, runner(command))
        for tool, command in zip(("Mixintake", "Scopequote"), plan.commands, strict=True)
    )
    follow_up = any(outcome.follow_up for outcome in outcomes)

    try:
        plan.destination.mkdir(parents=True, exist_ok=False)
    except FileExistsError as error:
        raise WorkflowError("workflow destination already exists") from error

    markdown_path = plan.destination / "CLIENT_WORKFLOW_REVIEW.md"
    review_json_path = plan.destination / "CLIENT_WORKFLOW_REVIEW.json"
    manifest_path = plan.destination / "manifest.json"
    markdown_path.write_text(_render_markdown(outcomes, follow_up), encoding="utf-8")
    review_json_path.write_text(_render_review_json(outcomes, follow_up), encoding="utf-8")
    manifest_path.write_text(
        _render_manifest(outcomes, follow_up, (markdown_path, review_json_path)),
        encoding="utf-8",
    )

    return WorkflowResult(
        destination=plan.destination,
        outcomes=outcomes,
        follow_up=follow_up,
        files=(markdown_path, review_json_path, manifest_path),
        manifest_path=manifest_path,
    )


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a path-free local review of Mixintake and Scopequote statuses."
    )
    parser.add_argument("intake", help="Existing TOML declaration for Mixintake.")
    parser.add_argument("quote", help="Existing TOML declaration for Scopequote.")
    parser.add_argument("--output", required=True, help="A new directory for the local review packet.")
    parser.add_argument(
        "--mixintake-bin",
        default="mixintake",
        help="Trusted local Mixintake executable path or command name.",
    )
    parser.add_argument(
        "--scopequote-bin",
        default="scopequote",
        help="Trusted local Scopequote executable path or command name.",
    )
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    args = parse_arguments(arguments)
    try:
        plan = plan_workflow(
            args.intake,
            args.quote,
            args.output,
            mixintake_bin=args.mixintake_bin,
            scopequote_bin=args.scopequote_bin,
        )
        result = run_workflow(plan)
    except WorkflowError as error:
        print(f"workflow error: {error}", file=sys.stderr)
        return 1

    print(f"Local client workflow review written: {result.destination.name}")
    return 2 if result.follow_up else 0


if __name__ == "__main__":
    raise SystemExit(main())
