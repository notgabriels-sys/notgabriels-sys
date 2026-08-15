# Gabriel García Alonso

Berlin-based sound engineer, music producer, and hardware-live performer. I
build local-first tools for the practical work around independent music:
preparing a release, checking delivery material, reviewing artwork, and making
handoffs easier to understand.

## Current direction

**[Releaseforge](https://github.com/notgabriels-sys/releaseforge/pull/1)** is
the flagship work in progress: a local release-proof workflow for the point
before a distributor upload or delivery handoff. It keeps measured file facts,
supplied declarations, open evidence, and captured revision changes visibly
separate in a portable offline packet.

The goal is not another cloud catalogue or a false compliance badge. It is a
clearer answer to a practical question: *what was reviewed, what is only
declared, and what changed before this handoff?*

## Safe synthetic workflow starter

The suite also contains a one-command, fully synthetic integration walk-through
for the Releaseforge → Coverforge → Releaseforge handoff path. It is useful
when evaluating the workflow before any genuine artwork, audio, or release
folder is involved:

```bash
python3 scripts/release_workflow_demo.py /path/to/new-synthetic-workflow
```

It requires local `releaseforge` and `coverforge` binaries and never installs,
uploads, or deletes anything. Read the exact prerequisites, output tree, and
limits in [the synthetic workflow starter guide](docs/RELEASE_WORKFLOW_STARTER.md).

This integration currently depends on the companion-manifest work under review
in [Releaseforge PR #1](https://github.com/notgabriels-sys/releaseforge/pull/1)
and [Coverforge PR #3](https://github.com/notgabriels-sys/albumdesign/pull/3).
It is a draft workflow demonstration, not a claim that either feature is
merged, installed, or available from the default branches.

## A focused toolchain

The tools below cover different parts of one release workflow. They remain
local-first and make their limits explicit.

- **[Coverforge](https://github.com/notgabriels-sys/albumdesign)** — preflights
  release artwork and exports a per-platform delivery pack from an approved
  master.
- **[Mastergate](https://github.com/notgabriels-sys/mastergate)** — measures a
  declared batch of PCM WAV files against a delivery contract and writes a
  portable evidence pack.
- **[Releaseledger](https://github.com/notgabriels-sys/releaseledger)** —
  checks declared release metadata and prepares a reviewable handoff dossier.
- **[Sleeveproof](https://github.com/notgabriels-sys/sleeveproof)** — turns a
  batch of cover-art variants into labelled contact sheets for selection and
  review.

## Artist and label work

- **Hologram People** — solo hardware-live project.
- **Lack of Fate** — hardware-live duo with Carlos García Alonso.
- **Fate Through** — independent label and creative platform.

## Working principles

- Start with the files and facts that actually exist on the owner's machine.
- Distinguish verified measurements from declarations, approvals, and unknowns.
- Make a portable record for a collaborator without uploading raw source media.
- Treat a passing local check as evidence of a narrow check, never as proof of
  rights, approval, platform acceptance, or public release status.

I am consolidating this work around release handoff and delivery evidence rather
than turning every useful internal utility into a separate product.
