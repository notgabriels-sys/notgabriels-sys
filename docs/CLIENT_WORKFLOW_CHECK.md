# Client Workflow Check

`scripts/client_workflow_check.py` is a local, status-only bridge between two
separate early-stage tools:

- **Mixintake** checks declarations about source and deliverable states.
- **Scopequote** checks the declared state of a quote draft.

It is intentionally not a conversion layer. The script does not read, parse,
copy, upload, hash, or write either TOML input. It passes each selected path to
its own local checker, retains only that command's recognised exit status, and
writes a small review packet with no selected paths or child console output.

## Current dependency status

This hub script is an integration for the following companion client-review
work, which is currently still proposed in draft pull requests:

- [Mixintake PR #2](https://github.com/notgabriels-sys/mixintake/pull/2)
- [Scopequote PR #2](https://github.com/notgabriels-sys/scopequote/pull/2)

Check out or install those specific draft branches locally if you want to use
the matching `mixintake` and `scopequote` executables. This document makes no
claim that either feature exists on a default branch.

## Prerequisites

You need all of the following on your own machine:

- An existing Mixintake TOML declaration.
- An existing Scopequote TOML declaration.
- A trusted, executable local `mixintake` command or absolute executable path.
- A trusted, executable local `scopequote` command or absolute executable path.
- A new output directory name that does not yet exist.

The executable overrides are intentional: if you point either option to a
local program, you are choosing to trust that program. This script does not
download, install, or inspect it.

## Run it

From this repository:

```sh
python3 scripts/client_workflow_check.py \
  /path/to/intake.toml \
  /path/to/quote.toml \
  --output /path/to/new-client-workflow-review \
  --mixintake-bin /path/to/mixintake \
  --scopequote-bin /path/to/scopequote
```

If both executable names are already available on `PATH`, the two `--*-bin`
options may be omitted. The script runs the following literal, shell-free
commands:

```text
mixintake check INTAKE.toml
scopequote check QUOTE.toml
```

Child stdout and stderr are discarded. They are not included in the review.

## Output

The output directory is created only after both checks return a recognised
status. It contains exactly these files:

```text
new-client-workflow-review/
├── CLIENT_WORKFLOW_REVIEW.md
├── CLIENT_WORKFLOW_REVIEW.json
└── manifest.json
```

The Markdown and JSON describe only the two declared statuses. `manifest.json`
contains byte counts and SHA-256 values for those two content files. It does
not include either selected input path, TOML content, or child process output.

## Status and exit behavior

| Tool | Child exit | Recorded meaning |
| --- | ---: | --- |
| Mixintake | `0` | Declared sources and deliverables are settled. |
| Mixintake | `2` | Declared source or deliverable follow-up remains. |
| Scopequote | `0` | The quote is declared human-reviewed. |
| Scopequote | `2` | The quote declaration remains a draft. |

The wrapper itself returns:

- `0` when both child checks return `0`.
- `2` when either child check returns `2`; the packet is still written.
- `1` when an executable or input cannot be used, the destination already
  exists, a child cannot start, or a child returns an unrecognised status. In
  that case, no review directory is created by the normal failed-check path.

## Human-action boundary

A status of `0` records a settled declaration from a local checker. It does
not establish material receipt, technical suitability, rights, commercial
terms, work scheduling, invoicing, money status, client consent, transfer of
assets, or clearance to proceed with a real client workflow. Review each of
those matters separately with the people and records involved.

The script deliberately does not:

- Convert schemas or transfer data between the two TOMLs.
- Calculate a fee, tax, deposit, payment, or invoice.
- Inspect source media or make a technical/rights claim about it.
- Send email, open a portal or browser, access a network, upload material, or
  trigger an action in a client or payment system.
