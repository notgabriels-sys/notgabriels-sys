# Client Workflow Check — implementation plan

> Work on branch codex/client-workflow-check. The behavioral and safety decision is recorded in docs/superpowers/specs/2026-08-15-client-workflow-check-design.md.

## Goal

Create a standard-library hub script that runs Mixintake and Scopequote read-only checks, records only their recognised exit-status meanings in a path-free review packet, and never interprets those statuses as receipt, agreement, payment, or delivery.

## Task 1: Establish the status contract test-first

**Files:**

- Add: scripts/__init__.py
- Add: scripts/client_workflow_check.py
- Add: tests/__init__.py
- Add: tests/test_client_workflow_check.py

1. Add an importable script module with planned dataclasses, a WorkflowError type, and explicit constants for expected output filenames.
2. Add tests for a fresh destination, explicit executable resolution, and literal command vectors:
   - mixintake check INTAKE
   - scopequote check QUOTE
3. Add a test runner seam that returns integer exit codes. Test 0/0 and 2/2 outcomes without launching a shell or actual child process.
4. Run the tests and confirm the missing module/API fails before implementation.

## Task 2: Implement safe execution and output writing

**Files:**

- Modify: scripts/client_workflow_check.py
- Modify: tests/test_client_workflow_check.py

1. Resolve explicit paths or PATH command names to executable files, rejecting unavailable binaries.
2. Build a plan only for a destination that does not exist. Store literal tuple command vectors and no input-content/path fields intended for output.
3. Run child checks with subprocess.run and shell disabled. Capture no child stdout/stderr in generated artifacts. Treat only exits 0 and 2 as understood states; reject all others before the destination is created.
4. Map outcomes to precise declaration-state labels. Calculate a follow-up exit code of 2 when either child returned 2; never label a 0/0 run as client ready.
5. Render a Markdown and JSON review plus a manifest that hashes and counts exactly the two content files. Ensure artifact text does not contain either selected input path or child output.
6. Add tests for unknown exit errors without output creation, expected file set, hashes/byte counts, path-free content, and CLI error/status behavior.

## Task 3: Document a real manual workflow

**Files:**

- Modify: README.md
- Add: docs/CLIENT_WORKFLOW_CHECK.md

1. Add a Client Workflow Check section to the hub profile, explicitly separate from the release workflow.
2. Document prerequisites: local Mixintake and Scopequote executables from their draft branches/PRs, two existing TOML declarations, and a new destination.
3. State the exact command, output tree, child-status mapping, exit behavior, and human-action boundary.
4. State that it does not convert schemas, infer commercial terms, inspect files, transmit data, or enact client/payment actions.
5. Link to Mixintake PR 2 and Scopequote PR 2 as draft dependencies without saying they are merged or default-branch features.

## Task 4: Verify the integration and publish cautiously

**Files:**

- Verify: all changed source, tests, docs, and generated synthetic output

1. Run Python unit tests and compileall. Run git diff --check.
2. In a fresh virtual environment, install Mixintake from the verified client-review branch and Scopequote from its verified client-review branch. Run the hub script with explicit binary overrides, fictional examples, and a new output directory.
3. Verify the wrapper returns 2 for the Scopequote draft while still writing exactly the three expected review files. Verify no selected input path appears in generated JSON/Markdown/manifest.
4. Run a focused security diff review on child-process resolution, literal command vectors, path-free artifact behavior, and absence of external side effects.
5. Push normally and open a draft PR against codex/profile-portfolio. Do not merge, mark ready, or claim an actual client workflow completed.

