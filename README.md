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

## A focused toolchain

The tools below cover different parts of one release workflow. They remain
local-first and make their limits explicit.

- **[Coverforge](https://github.com/notgabriels-sys/albumdesign)** — preflights
  release artwork and exports a per-platform delivery pack from an approved
  master.
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

## Client Workflow Check (draft integration)

The hub also contains a small local check for the point before work begins: it
records the declared status returned by **Mixintake** and **Scopequote** in one
path-free review packet. It does not turn an intake into a price, a quote into
an agreement, or a local check into evidence of a real-world client outcome.

```sh
python3 scripts/client_workflow_check.py INTAKE.toml QUOTE.toml \
  --output NEW_CLIENT_WORKFLOW_REVIEW
```

See [the Client Workflow Check guide](docs/CLIENT_WORKFLOW_CHECK.md) for the
required local executables, exit statuses, and boundaries. Its companion
client-review changes currently remain in draft PRs:
[Mixintake PR #2](https://github.com/notgabriels-sys/mixintake/pull/2) and
[Scopequote PR #2](https://github.com/notgabriels-sys/scopequote/pull/2).
