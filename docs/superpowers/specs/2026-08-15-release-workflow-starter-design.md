# Release Workflow Starter design

## Goal

Make the relationship between the two flagship local tools immediately
testable: one command should create a completely synthetic Releaseforge demo,
build a Coverforge delivery capture from that demo's cover, and write an
aligned local handoff packet. This is an onboarding and integration check, not
a release service, uploader, or readiness decision.

## User and problem

An artist, engineer, label operator, or evaluator can understand each tool in
isolation but has no short, reproducible proof that their captures work
together. Manually translating three CLI commands, paths, and output
boundaries is an unnecessary first-use hurdle. A user needs a safe way to see
the exact end-to-end shape before using any genuine release assets.

## Decision

Add a dependency-free Python entry script:

```text
python3 scripts/release_workflow_demo.py DESTINATION
```

It accepts optional executable overrides:

```text
--releaseforge-bin PATH_OR_COMMAND
--coverforge-bin PATH_OR_COMMAND
```

The command will be documented in the suite README and a dedicated operator
guide. It intentionally does not install packages, clone repositories, fetch
from the network, read user media, or hide the underlying child-tool output.

## Workflow contract

`DESTINATION` must not exist. Once accepted, the starter will execute only
argument-vector subprocess calls, never a shell string:

1. `releaseforge demo DESTINATION/releaseforge-demo`
2. `coverforge build DESTINATION/releaseforge-demo/release-v1/artwork/final-cover.jpg --name synthetic-cover -o DESTINATION/coverforge-packet`
3. `releaseforge handoff DESTINATION/releaseforge-demo/proof-v1 --coverforge DESTINATION/coverforge-packet/manifest.json --output DESTINATION/release-handoff`

The first command creates every media asset and proof capture from synthetic
data. The second receives only the synthetic cover written by the first. The
third reads only the generated proof and manifest captures.

On success the starter validates that the handoff directory contains exactly
`RELEASE_HANDOFF.md`, `RELEASE_HANDOFF.json`, and `RELEASE_HANDOFF.html`. It
also validates schema version 1, an empty handoff finding list, and the
Coverforge linkage state `aligned`. It prints locations and a narrow summary.
Those checks establish only that this selected synthetic capture relationship
aligned locally. They do not establish rights, approval, ownership, current
file status, distributor acceptance, platform compliance, public release
readiness, or successful delivery.

## Inputs, outputs, and failure behavior

- Executable values resolve either as an executable path or a command available
  on `PATH`; an unavailable value fails before the destination is created.
- An existing destination fails before any child command runs.
- A child-command nonzero exit stops the workflow. Any synthetic files already
  created are deliberately retained for local diagnosis; the script never
  deletes or changes them.
- A missing expected child output or malformed handoff JSON fails with an
  actionable local error.
- The script writes no document of its own and does not copy source media;
  child-tool output is the complete result.

## Implementation shape

Create `scripts/release_workflow_demo.py` with small testable units for
executable resolution, fresh-destination planning, vector-command construction,
subprocess execution, and handoff validation. Make `scripts/` importable so a
standard-library `unittest` suite can import the module without adding a
dependency. `main()` returns `0` on a verified synthetic workflow and `2` on
operator, executable, subprocess, or output-validation errors.

Create `tests/test_release_workflow_demo.py` using a supplied runner function
to assert exact argument vectors and to synthesize minimal child outputs. This
unit suite proves that the starter cannot use a shell command, cannot run child
tools for an existing destination, and rejects an unaligned or malformed
handoff packet. A separate clean temporary virtual environment will install
the current Releaseforge and Coverforge worktrees and run the script against
the real two binaries.

## Documentation and scope

The suite README will add one clearly labelled **synthetic workflow starter**
section, while `docs/RELEASE_WORKFLOW_STARTER.md` will state prerequisites,
commands, expected directory tree, and limitations. It must state that the
current integration depends on the companion-manifest work under review in
Releaseforge PR #1 and Coverforge PR #3; the guide will not present draft work
as a merged public release.

No cloud account, UI, service tier, billing, analytics, upload, real artwork,
real audio, or metadata-destination claim is in scope.

## Acceptance criteria

1. A fresh destination with working local `releaseforge` and `coverforge`
   binaries produces the documented synthetic directory tree and an aligned
   three-file handoff packet.
2. The script invokes child tools through literal argument vectors and never
   through a shell.
3. Existing destinations and unresolved executables fail without starting the
   workflow.
4. Malformed, incomplete, or non-aligned handoff output fails visibly rather
   than being called a successful demo.
5. Standard-library unit tests and a clean installed-binary integration smoke
   test pass without touching user-provided artwork or media.
