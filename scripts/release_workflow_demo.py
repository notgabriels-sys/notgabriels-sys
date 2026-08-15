"""Plan a safe, synthetic Releaseforge and Coverforge workflow demonstration."""

from __future__ import annotations

import os
import shutil
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


class WorkflowError(ValueError):
    """A local synthetic workflow cannot be planned safely."""


@dataclass(frozen=True)
class WorkflowPlan:
    """All local paths and literal child-command vectors for one workflow run."""

    destination: Path
    releaseforge_bin: str
    coverforge_bin: str
    release_demo: Path
    coverforge_packet: Path
    handoff_packet: Path
    commands: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class WorkflowResult:
    """Verified locations from one completed synthetic workflow."""

    destination: Path
    release_demo: Path
    coverforge_packet: Path
    handoff_packet: Path
    coverforge_state: str


EXPECTED_HANDOFF_FILES = {
    "RELEASE_HANDOFF.html",
    "RELEASE_HANDOFF.json",
    "RELEASE_HANDOFF.md",
}


def resolve_executable(value: str, label: str) -> str:
    """Resolve one explicit executable path or a command on PATH."""
    if not isinstance(value, str) or not value.strip():
        raise WorkflowError(f"{label} executable is not available")

    requested = value.strip()
    if Path(requested).is_absolute() or "/" in requested:
        candidate = Path(requested).expanduser().resolve()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
        raise WorkflowError(f"{label} executable is not available: {requested}")

    found = shutil.which(requested)
    if found is None:
        raise WorkflowError(f"{label} executable is not available: {requested}")
    return str(Path(found).resolve())


def plan_workflow(
    destination: Path | str,
    *,
    releaseforge_bin: str,
    coverforge_bin: str,
) -> WorkflowPlan:
    """Create a no-write plan for the documented synthetic workflow."""
    root = Path(destination).expanduser().resolve()
    if root.exists():
        raise WorkflowError(f"workflow destination already exists: {root.name}")

    releaseforge = resolve_executable(releaseforge_bin, "Releaseforge")
    coverforge = resolve_executable(coverforge_bin, "Coverforge")
    release_demo = root / "releaseforge-demo"
    coverforge_packet = root / "coverforge-packet"
    handoff_packet = root / "release-handoff"
    cover = release_demo / "release-v1" / "artwork" / "final-cover.jpg"

    return WorkflowPlan(
        destination=root,
        releaseforge_bin=releaseforge,
        coverforge_bin=coverforge,
        release_demo=release_demo,
        coverforge_packet=coverforge_packet,
        handoff_packet=handoff_packet,
        commands=(
            (releaseforge, "demo", str(release_demo)),
            (
                coverforge,
                "build",
                str(cover),
                "--name",
                "synthetic-cover",
                "-o",
                str(coverforge_packet),
            ),
            (
                releaseforge,
                "handoff",
                str(release_demo / "proof-v1"),
                "--coverforge",
                str(coverforge_packet / "manifest.json"),
                "--output",
                str(handoff_packet),
            ),
        ),
    )


def _run_command(command: tuple[str, ...]) -> None:
    """Run one literal child-command vector without a shell."""
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as error:
        raise WorkflowError(f"child command failed with exit status {error.returncode}") from error


def _require_file(path: Path, description: str) -> None:
    if not path.is_file():
        raise WorkflowError(f"{description} was not created")


def validate_handoff(packet: Path) -> str:
    """Validate the narrow successful outcome expected from the synthetic run."""
    if not packet.is_dir():
        raise WorkflowError("handoff packet was not created")

    actual = {item.name for item in packet.iterdir()}
    if actual != EXPECTED_HANDOFF_FILES:
        raise WorkflowError("handoff packet expected exactly the required three files")

    try:
        payload = json.loads((packet / "RELEASE_HANDOFF.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise WorkflowError("handoff packet JSON is unreadable") from error

    if not isinstance(payload, dict):
        raise WorkflowError("handoff packet JSON has unexpected shape")
    if payload.get("schema_version") != 1:
        raise WorkflowError("handoff packet has unsupported schema version")
    if payload.get("findings") != []:
        raise WorkflowError("handoff packet contains findings")

    coverforge = payload.get("coverforge")
    if not isinstance(coverforge, dict):
        raise WorkflowError("handoff packet has no Coverforge capture")
    linkage = coverforge.get("linkage")
    if not isinstance(linkage, dict):
        raise WorkflowError("handoff packet has no Coverforge linkage")
    state = linkage.get("state")
    if state != "aligned":
        raise WorkflowError("Coverforge capture relationship is not aligned")
    return state


def run_workflow(
    plan: WorkflowPlan,
    *,
    runner: Callable[[tuple[str, ...]], None] = _run_command,
) -> WorkflowResult:
    """Execute the fixed synthetic sequence and validate its final packet."""
    plan.destination.mkdir(parents=True, exist_ok=False)

    runner(plan.commands[0])
    _require_file(
        plan.release_demo / "release-v1" / "artwork" / "final-cover.jpg",
        "synthetic demo cover",
    )
    _require_file(plan.release_demo / "proof-v1" / "RELEASE_PROOF.json", "synthetic proof packet")

    runner(plan.commands[1])
    _require_file(plan.coverforge_packet / "manifest.json", "Coverforge manifest")

    runner(plan.commands[2])
    state = validate_handoff(plan.handoff_packet)
    return WorkflowResult(
        destination=plan.destination,
        release_demo=plan.release_demo,
        coverforge_packet=plan.coverforge_packet,
        handoff_packet=plan.handoff_packet,
        coverforge_state=state,
    )
