"""Plan a safe, synthetic Releaseforge and Coverforge workflow demonstration."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path


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
