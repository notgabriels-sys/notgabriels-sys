# Client Workflow Check — design

**Date:** 2026-08-15
**Status:** Approved through Gabriel's standing instruction to keep building useful GitHub tools autonomously.

## Problem

Mixintake and Scopequote handle different early client-workflow declarations: source/scope intake and quote preparation. They can be used side by side, but the operator currently has to run both checks separately and mentally translate the exit statuses without a small, shareable record of what was checked and what still needs human work.

Automatically converting an intake into a price or quote would be unsafe: the tools intentionally do not infer fees, tax, agreement, receipt, delivery, or client approval. The useful integration is therefore a narrow status aggregator, not data transformation.

## Decision

Add a standard-library script to the GitHub hub:

    python3 scripts/client_workflow_check.py INTAKE.toml QUOTE.toml --output NEW_DIRECTORY

It runs two existing local read-only checks as literal argument vectors:

    mixintake check INTAKE.toml
    scopequote check QUOTE.toml

The script does not read, parse, copy, upload, hash, or persist either input file. It captures only the child exit statuses and writes a new path-free local review packet after both checks finish with a recognised status.

## User-facing behavior

The new output directory contains:

    client-workflow-review/
    ├── CLIENT_WORKFLOW_REVIEW.md
    ├── CLIENT_WORKFLOW_REVIEW.json
    └── manifest.json

The review packet names only the two tool statuses:

- Mixintake 0 means declared source/deliverable states are settled.
- Mixintake 2 means declared source or deliverable follow-up remains.
- Scopequote 0 means a quote is declared human-reviewed.
- Scopequote 2 means the quote remains a declared draft.

The packet never calls either state client ready, received, approved, agreed, booked, issued, paid, or delivered. It always ends with an explicit human-action boundary.

The parent command returns 0 only when both child checks return 0; it returns 2 when either tool returns its documented follow-up/draft status. Both outcomes can write the review packet. Any other child exit status, unavailable executable, or existing output directory returns 1 or 2 without claiming a completed review.

## Execution and safety

The --mixintake-bin and --scopequote-bin options accept an explicit executable path or command name and default to mixintake and scopequote. The resolver verifies local executability or a PATH lookup before planning. Both child commands run through subprocess.run without a shell. Their stdout/stderr are not copied into the review packet, preventing incidental text or local paths from becoming handoff data.

The destination must not exist. Child checks run before the script creates the destination, so a failed or unrecognised check does not leave an output packet behind. The normal local filesystem race between planning and directory creation remains an operating-system concern; creation uses exist_ok=False so an intervening directory cannot be overwritten.

The script does not install dependencies, open a browser, send email, access a network, receive files, inspect audio, formulate a quote, calculate a fee/tax, issue an invoice, collect payment, or take any action in a client system. A user who explicitly points a binary override at a local executable is responsible for trusting that executable; the script does not download or discover third-party tools beyond PATH lookup.

## Data flow

    operator-selected intake path ──> mixintake check ──> exit status only ─┐
                                                                            ├─> review + manifest
    operator-selected quote path  ──> scopequote check ──> exit status only ─┘

No input path, source/quote content, child console output, client/contact data, or external action result belongs in the review packet. The manifest records SHA-256 and byte counts for the two generated content files only.

## Explicit non-goals

- No schema conversion between Mixintake and Scopequote.
- No rate, tax, deposit, payment, invoice, agreement, or booking inference.
- No source-file/audio access or claim of receipt, quality, rights, or delivery.
- No client portal, email, browser, network, upload, analytics, or user tracking.
- No merging, retargeting, or release claim for the companion draft PRs.

## Acceptance criteria

1. The script uses exact, shell-free check vectors and treats only child exits 0 and 2 as normal declared-state outcomes.
2. It writes exactly two path-free review files plus a hash/byte manifest only into a fresh destination after recognised checks finish.
3. It returns 2 for declared follow-up/draft outcomes without calling them ready, and returns 0 only for settled declared statuses while preserving the human-action boundary.
4. Tests cover planning, trusted executable resolution, command vectors, all status mappings, unrecognised child failures, non-overwriting behavior, artifact hashes, and absent path/child-output leaks.
5. Documentation is clear about prerequisites and the companion work remaining in draft PRs.

