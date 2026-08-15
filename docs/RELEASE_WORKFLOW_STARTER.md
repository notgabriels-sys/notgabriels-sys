# Synthetic Release Workflow Starter

This guide runs one completely local, synthetic workflow through the two
flagship tools:

```text
Releaseforge demo → Coverforge delivery capture → Releaseforge handoff
```

Use it to see the capture relationship and generated packet shape before you
point either tool at genuine artwork, audio, metadata, or a release folder.

## Prerequisites

- Python 3.11 or newer to run this repository's script.
- A local `releaseforge` executable containing the companion-handoff work.
- A local `coverforge` executable containing portable manifest capture.
- A destination directory name that does not already exist.

The starter does not install Python packages, clone repositories, contact a
service, or download media. At the time this guide was written, the required
companion-manifest work is under review in
[Releaseforge PR #1](https://github.com/notgabriels-sys/releaseforge/pull/1)
and [Coverforge PR #3](https://github.com/notgabriels-sys/albumdesign/pull/3).
Use local checkouts or installed binaries that contain those changes; do not
assume the default branches already provide them.

## Run

If both binaries are available on your `PATH`:

```bash
python3 scripts/release_workflow_demo.py /path/to/new-synthetic-workflow
```

Or name the two exact local executables:

```bash
python3 scripts/release_workflow_demo.py /path/to/new-synthetic-workflow \
  --releaseforge-bin /path/to/releaseforge-venv/bin/releaseforge \
  --coverforge-bin /path/to/coverforge-venv/bin/coverforge
```

The supplied destination must be new. This is deliberate: the starter does
not overwrite a previous run or delete anything to make a path available.

## What it creates

All files below originate from the `releaseforge demo` command and the two
subsequent local commands. The starter itself does not copy originals or add
its own report.

```text
new-synthetic-workflow/
├── releaseforge-demo/
│   ├── release-v1/              synthetic cover, WAV, and release.toml
│   ├── release-v2/              a second synthetic revision
│   ├── proof-v1/                Releaseforge proof packet for v1
│   ├── proof-v2/                Releaseforge proof packet for v2
│   └── START_HERE.md
├── coverforge-packet/           rendered cover variants and manifest.json
└── release-handoff/
    ├── RELEASE_HANDOFF.md
    ├── RELEASE_HANDOFF.json
    └── RELEASE_HANDOFF.html
```

Internally, the starter runs these literal argument-vector commands, never a
shell command:

```text
releaseforge demo DESTINATION/releaseforge-demo
coverforge build DESTINATION/releaseforge-demo/release-v1/artwork/final-cover.jpg --name synthetic-cover -o DESTINATION/coverforge-packet
releaseforge handoff DESTINATION/releaseforge-demo/proof-v1 --coverforge DESTINATION/coverforge-packet/manifest.json --output DESTINATION/release-handoff
```

## What success means

The starter succeeds only when the handoff directory contains exactly the
three named handoff files, the JSON reports schema version 1 with no top-level
findings, and the captured Coverforge linkage state is `aligned`.

That is deliberately narrow. It means the selected local, synthetic
Releaseforge proof and Coverforge manifest aligned in the relationship that
Releaseforge can inspect.

## What success does not mean

It does not establish ownership, approval, rights, current-file verification,
technical suitability for a particular destination, distribution, delivery,
platform acceptance, platform compliance, public-release readiness, or any
external event. It does not use genuine media, so it cannot validate your real
release.

## Failure behavior

An unavailable executable, an existing destination, a failed child command,
missing expected output, malformed handoff JSON, non-empty handoff finding
list, or non-aligned capture relationship stops the starter with exit status
`2`.

If a child command has already generated synthetic files when it fails, those
files remain in the requested destination for local diagnosis. The starter
does not automatically delete or overwrite them. Choose a different new
destination for a clean retry.
