# Release Workflow Starter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provide one safe, dependency-free command that proves the synthetic
Releaseforge-to-Coverforge-to-Releaseforge handoff path works locally.

**Architecture:** A standard-library script plans a fresh destination and
resolves two explicit local executables, then invokes three fixed argument
vectors without a shell. It validates the generated handoff packet before it
reports success. Unit tests inject a runner so they verify the exact vectors and
error behavior without installing or executing either companion project.

**Tech Stack:** Python 3.11+ standard library (`argparse`, `dataclasses`,
`json`, `pathlib`, `shutil`, `subprocess`, `unittest`); current local
Releaseforge and Coverforge binaries for the final synthetic integration smoke.

## Global Constraints

- Work only in the isolated `codex/release-workflow-starter` worktree.
- `DESTINATION` must be absent before planning; never delete a user path.
- Resolve binaries as a concrete executable path or a command on `PATH`; never
  invoke a shell or interpolate a command string.
- Run exactly the documented synthetic child-command sequence and inspect no
  user-selected artwork, audio, metadata, or credentials.
- Stop after a child failure; retain generated synthetic diagnostic files and
  do not clean them up automatically.
- Call success only after the handoff has exactly three expected files, schema
  version `1`, no top-level findings, and Coverforge linkage state `aligned`.
- Do not claim rights, ownership, approval, delivery, distributor acceptance,
  platform compliance, or public-release readiness.
- The guide must call out its dependency on Releaseforge PR #1 and Coverforge
  PR #3 while those changes remain under review.

---

### Task 1: Establish the safe workflow planner

**Files:**
- Create: `scripts/__init__.py`
- Create: `scripts/release_workflow_demo.py`
- Create: `tests/__init__.py`
- Create: `tests/test_release_workflow_demo.py`

**Interfaces:**
- Produces `WorkflowError(ValueError)` for local operator and output errors.
- Produces `WorkflowPlan` with `destination`, `releaseforge_bin`,
  `coverforge_bin`, `release_demo`, `coverforge_packet`, `handoff_packet`, and
  `commands` fields.
- Produces `resolve_executable(value: str, label: str) -> str` and
  `plan_workflow(destination: Path | str, *, releaseforge_bin: str,
  coverforge_bin: str) -> WorkflowPlan`.
- Consumed by Task 2 for child execution and Task 3 for the CLI.

- [ ] **Step 1: Write the failing planner tests**

```python
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
            (sys.executable, "demo", str(root.resolve() / "releaseforge-demo")),
        )
        self.assertEqual(plan.commands[1][1:3], ("build", str(plan.release_demo / "release-v1" / "artwork" / "final-cover.jpg")))
        self.assertNotIn("shell", plan.__dict__)

    def test_plan_refuses_existing_destination_before_child_execution(self):
        root = self.root / "workflow"
        root.mkdir()
        with self.assertRaisesRegex(WorkflowError, "already exists"):
            plan_workflow(root, releaseforge_bin=sys.executable, coverforge_bin=sys.executable)

    def test_resolve_executable_rejects_an_unavailable_command(self):
        with self.assertRaisesRegex(WorkflowError, "not available"):
            resolve_executable("not-a-real-release-workflow-binary", "Releaseforge")
```

- [ ] **Step 2: Run the planner tests and verify the expected red failure**

Run:

```bash
python3 -m unittest tests.test_release_workflow_demo.WorkflowPlanTests -v
```

Expected: import failure because `scripts.release_workflow_demo` does not exist.

- [ ] **Step 3: Implement the minimal safe planner**

```python
@dataclass(frozen=True)
class WorkflowPlan:
    destination: Path
    releaseforge_bin: str
    coverforge_bin: str
    release_demo: Path
    coverforge_packet: Path
    handoff_packet: Path
    commands: tuple[tuple[str, ...], ...]


def plan_workflow(destination: Path | str, *, releaseforge_bin: str, coverforge_bin: str) -> WorkflowPlan:
    root = Path(destination).expanduser().resolve()
    if root.exists():
        raise WorkflowError(f"workflow destination already exists: {root.name}")
    releaseforge = resolve_executable(releaseforge_bin, "Releaseforge")
    coverforge = resolve_executable(coverforge_bin, "Coverforge")
    demo = root / "releaseforge-demo"
    cover = demo / "release-v1" / "artwork" / "final-cover.jpg"
    packet = root / "coverforge-packet"
    handoff = root / "release-handoff"
    return WorkflowPlan(
        destination=root,
        releaseforge_bin=releaseforge,
        coverforge_bin=coverforge,
        release_demo=demo,
        coverforge_packet=packet,
        handoff_packet=handoff,
        commands=(
            (releaseforge, "demo", str(demo)),
            (coverforge, "build", str(cover), "--name", "synthetic-cover", "-o", str(packet)),
            (releaseforge, "handoff", str(demo / "proof-v1"), "--coverforge", str(packet / "manifest.json"), "--output", str(handoff)),
        ),
    )
```

`resolve_executable()` must use `Path.is_file()` and `os.access(path,
os.X_OK)` for a supplied path, otherwise `shutil.which()`. It returns the
resolved executable string and raises `WorkflowError` for blank or unavailable
values.

- [ ] **Step 4: Run the planner tests and verify green**

Run:

```bash
python3 -m unittest tests.test_release_workflow_demo.WorkflowPlanTests -v
```

Expected: all planner tests pass and no destination is created.

- [ ] **Step 5: Commit the planner**

```bash
git add scripts/__init__.py scripts/release_workflow_demo.py tests/__init__.py tests/test_release_workflow_demo.py
git commit -m "feat: plan synthetic release workflow demo"
```

### Task 2: Execute and verify the synthetic workflow

**Files:**
- Modify: `scripts/release_workflow_demo.py`
- Modify: `tests/test_release_workflow_demo.py`

**Interfaces:**
- Consumes `WorkflowPlan` from Task 1.
- Produces `WorkflowResult` with the three generated packet locations and a
  narrow `coverforge_state` string.
- Produces `run_workflow(plan: WorkflowPlan, *, runner: Callable[[tuple[str, ...]], None]) -> WorkflowResult` and
  `validate_handoff(packet: Path) -> str`.
- Consumed by Task 3's command-line `main()`.

- [ ] **Step 1: Write the failing execution and validation tests**

```python
def test_run_workflow_runs_fixed_vectors_and_validates_an_aligned_handoff(self):
    plan = plan_workflow(self.root / "workflow", releaseforge_bin=sys.executable, coverforge_bin=sys.executable)
    calls: list[tuple[str, ...]] = []

    def runner(command: tuple[str, ...]) -> None:
        calls.append(command)
        if command[1] == "demo":
            (plan.release_demo / "release-v1" / "artwork").mkdir(parents=True)
            (plan.release_demo / "release-v1" / "artwork" / "final-cover.jpg").write_bytes(b"synthetic")
            (plan.release_demo / "proof-v1").mkdir()
        elif command[1] == "build":
            plan.coverforge_packet.mkdir()
            (plan.coverforge_packet / "manifest.json").write_text("{}", encoding="utf-8")
        else:
            plan.handoff_packet.mkdir()
            for name in ("RELEASE_HANDOFF.md", "RELEASE_HANDOFF.html"):
                (plan.handoff_packet / name).write_text("synthetic", encoding="utf-8")
            (plan.handoff_packet / "RELEASE_HANDOFF.json").write_text(
                json.dumps({"schema_version": 1, "findings": [], "coverforge": {"linkage": {"state": "aligned"}}}),
                encoding="utf-8",
            )

    result = run_workflow(plan, runner=runner)
    self.assertEqual(calls, list(plan.commands))
    self.assertEqual(result.coverforge_state, "aligned")

def test_validate_handoff_rejects_non_aligned_capture(self):
    packet = self.root / "handoff"
    write_handoff(packet, findings=[], state="needs_evidence")
    with self.assertRaisesRegex(WorkflowError, "not aligned"):
        validate_handoff(packet)
```

Implement `write_handoff()` as a test-local helper that creates exactly the
three required files. Also include a test that adding an unexpected fourth file
raises `WorkflowError` with `expected exactly` in its message.

- [ ] **Step 2: Run the execution tests and verify red**

Run:

```bash
python3 -m unittest tests.test_release_workflow_demo.WorkflowExecutionTests -v
```

Expected: import error for `run_workflow` and `validate_handoff`.

- [ ] **Step 3: Implement literal-vector execution and packet validation**

```python
def _run_command(command: tuple[str, ...]) -> None:
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as error:
        raise WorkflowError(f"child command failed with exit status {error.returncode}") from error


EXPECTED_HANDOFF_FILES = {"RELEASE_HANDOFF.md", "RELEASE_HANDOFF.json", "RELEASE_HANDOFF.html"}


def run_workflow(plan: WorkflowPlan, *, runner: Callable[[tuple[str, ...]], None] = _run_command) -> WorkflowResult:
    plan.destination.mkdir(parents=True, exist_ok=False)
    for command in plan.commands:
        runner(command)
    state = validate_handoff(plan.handoff_packet)
    return WorkflowResult(
        destination=plan.destination,
        release_demo=plan.release_demo,
        coverforge_packet=plan.coverforge_packet,
        handoff_packet=plan.handoff_packet,
        coverforge_state=state,
    )


def validate_handoff(packet: Path) -> str:
    if not packet.is_dir():
        raise WorkflowError("handoff packet was not created")
    actual = {item.name for item in packet.iterdir()}
    if actual != EXPECTED_HANDOFF_FILES:
        raise WorkflowError("handoff packet must contain exactly the expected three files")
    payload = json.loads((packet / "RELEASE_HANDOFF.json").read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise WorkflowError("handoff packet has unsupported schema version")
    if payload.get("findings") != []:
        raise WorkflowError("handoff packet contains findings")
    state = payload.get("coverforge", {}).get("linkage", {}).get("state")
    if state != "aligned":
        raise WorkflowError("Coverforge capture relationship is not aligned")
    return state
```

Use a `try`/`except` around JSON decoding and raise `WorkflowError("handoff
packet JSON is unreadable")` from `json.JSONDecodeError`. Do not catch broad
exceptions from a runner because a test failure or programmer error must remain
visible.

- [ ] **Step 4: Run all unit tests and verify green**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: planner, exact-vector, malformed-output, and non-aligned-handoff
tests all pass.

- [ ] **Step 5: Commit execution and validation**

```bash
git add scripts/release_workflow_demo.py tests/test_release_workflow_demo.py
git commit -m "feat: run verified synthetic release workflow"
```

### Task 3: Add the operator CLI and concise docs

**Files:**
- Modify: `scripts/release_workflow_demo.py`
- Modify: `tests/test_release_workflow_demo.py`
- Modify: `README.md`
- Create: `docs/RELEASE_WORKFLOW_STARTER.md`

**Interfaces:**
- Consumes `plan_workflow()` and `run_workflow()` from Tasks 1–2.
- Produces `main(argv: Sequence[str] | None = None) -> int`, executable as
  `python3 scripts/release_workflow_demo.py DESTINATION`.
- Produces one operator guide linked from the repository README.

- [ ] **Step 1: Write the failing CLI tests**

```python
def test_main_returns_usage_error_without_running_for_existing_destination(self):
    destination = self.root / "existing"
    destination.mkdir()
    code = main([
        str(destination),
        "--releaseforge-bin", sys.executable,
        "--coverforge-bin", sys.executable,
    ])
    self.assertEqual(code, 2)

def test_parser_accepts_explicit_binary_overrides(self):
    args = build_parser().parse_args([
        "demo-output",
        "--releaseforge-bin", "/opt/tools/releaseforge",
        "--coverforge-bin", "/opt/tools/coverforge",
    ])
    self.assertEqual(args.releaseforge_bin, "/opt/tools/releaseforge")
    self.assertEqual(args.coverforge_bin, "/opt/tools/coverforge")
```

Capture `stderr` with `contextlib.redirect_stderr` and assert it includes
`workflow error:` for the existing destination case.

- [ ] **Step 2: Run the CLI tests and verify red**

Run:

```bash
python3 -m unittest tests.test_release_workflow_demo.WorkflowCliTests -v
```

Expected: import error for `main` and `build_parser`.

- [ ] **Step 3: Implement the minimal CLI and documentation**

```python
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a synthetic local Releaseforge and Coverforge workflow.")
    parser.add_argument("destination", help="new directory for generated synthetic workflow files")
    parser.add_argument("--releaseforge-bin", default="releaseforge")
    parser.add_argument("--coverforge-bin", default="coverforge")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        plan = plan_workflow(args.destination, releaseforge_bin=args.releaseforge_bin, coverforge_bin=args.coverforge_bin)
        result = run_workflow(plan)
    except WorkflowError as error:
        print(f"workflow error: {error}", file=sys.stderr)
        return 2
    print("Synthetic local workflow complete.")
    print(f"Coverforge linkage: {result.coverforge_state}")
    print(f"Review handoff: {result.handoff_packet}")
    return 0
```

In `docs/RELEASE_WORKFLOW_STARTER.md`, include these sections exactly:

1. **Prerequisites**: Python 3.11+, local Releaseforge and Coverforge binaries
   containing the companion-manifest work, no automatic install.
2. **Run**: one default command and one command with absolute binary overrides.
3. **What it creates**: `releaseforge-demo/`, `coverforge-packet/`, and
   `release-handoff/`, all solely from synthetic data.
4. **What success means**: only the local captured Coverforge relationship
   aligned and the handoff had no top-level findings.
5. **What it does not mean**: no ownership, approval, rights, destination,
   distribution, compliance, platform, or public-release claim.
6. **Failure behavior**: no overwrite; partial synthetic output remains after a
   child error for local diagnosis; no automatic deletion.

Add a short README link to this guide directly after the flagship-work section.

- [ ] **Step 4: Run all unit tests and command help**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/release_workflow_demo.py --help
git diff --check
```

Expected: all unit tests pass, help exposes both binary overrides, and no
whitespace errors occur.

- [ ] **Step 5: Commit the interface and documentation**

```bash
git add scripts/release_workflow_demo.py tests/test_release_workflow_demo.py README.md docs/RELEASE_WORKFLOW_STARTER.md
git commit -m "docs: add synthetic release workflow guide"
```

### Task 4: Verify in a clean environment and publish a draft branch

**Files:**
- Verify: `scripts/release_workflow_demo.py`
- Verify: `tests/test_release_workflow_demo.py`
- Verify: `README.md`
- Verify: `docs/RELEASE_WORKFLOW_STARTER.md`

**Interfaces:**
- Consumes the final script through a direct `python3` invocation.
- Requires current local worktrees for Releaseforge and Coverforge only during
  the smoke test; it writes all output into a new temporary directory.

- [ ] **Step 1: Run repository-level verification**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts
git diff --check codex/profile-portfolio..HEAD
git status --short --branch
```

Expected: all standard-library tests pass, scripts compile, no whitespace
errors occur, and only intended committed files are present.

- [ ] **Step 2: Run the clean installed-binary integration smoke**

Run the exact sequence below in new temporary locations:

```bash
python3 -m venv "$TASK_VENV"
"$TASK_VENV/bin/python" -m pip install /Users/notgabriels/Documents/GitHub/releaseforge /Users/notgabriels/Documents/GitHub/albumdesign-contact-sheet
"$TASK_VENV/bin/python" scripts/release_workflow_demo.py "$TASK_OUTPUT" \
  --releaseforge-bin "$TASK_VENV/bin/releaseforge" \
  --coverforge-bin "$TASK_VENV/bin/coverforge"
```

Then assert that `release-handoff/` has exactly the expected three files and
that `RELEASE_HANDOFF.json` has `findings == []` and
`coverforge.linkage.state == "aligned"`. Run a second invocation at the same
destination and assert exit status `2` without overwriting it.

- [ ] **Step 3: Perform a focused diff security review**

Review the final branch diff for these specific surfaces:

- binary resolution and `subprocess.run` argument-vector use;
- fresh-destination checks and no automatic deletion;
- validation of untrusted generated handoff JSON;
- README/guide claims and the explicit draft dependency boundary.

Record the review outcome before publishing. Do not claim zero findings unless
the completed review actually reports zero reportable findings.

- [ ] **Step 4: Push the stacked branch and open a draft PR**

```bash
git push -u origin codex/release-workflow-starter
gh pr create \
  --repo notgabriels-sys/notgabriels-sys \
  --head codex/release-workflow-starter \
  --base codex/profile-portfolio \
  --draft \
  --title "feat: add synthetic release workflow starter"
```

The PR body must state that it is stacked on profile PR #1, that it depends on
the companion-manifest work under review in Releaseforge PR #1 and Coverforge
PR #3, and that it was verified exclusively with generated synthetic media.

- [ ] **Step 5: Verify the live PR state**

Run:

```bash
gh pr view --repo notgabriels-sys/notgabriels-sys --json number,url,state,isDraft,mergeable,baseRefName,headRefName,headRefOid,statusCheckRollup
```

Expected: an open, draft PR from `codex/release-workflow-starter` to
`codex/profile-portfolio`. Do not merge or mark either PR ready.
