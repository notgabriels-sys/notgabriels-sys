# GitHub profile release-workflow launchpad — design

**Date:** 2026-08-15

## Purpose

Turn the `notgabriels-sys` profile repository into the entry point for one
coherent local-first release workflow. A visitor should understand the problem,
see how the core repositories relate, and have one safe path to inspect the
flagship work without being told that an experimental draft is a finished,
hosted, paid, or externally certified product.

## Context

The current profile README accurately introduces Releaseforge and names the
related projects, but it has two adoption gaps:

1. It sends readers to several repository roots without explaining which tool
   to begin with or what each contributes to the final handoff.
2. Releaseforge is currently a draft implementation, so its working branch and
   privacy-minimal synthetic demo need to be visible without implying a release
   has been merged or a service is available.

The Releaseforge draft explicitly defers maintained delivery profiles, accounts,
billing, and team-product work until voluntary real-world pilots establish
value. This change must not jump that gate.

## Decision

Create a small, static profile launchpad composed of two human-readable files:

| File | Responsibility |
| --- | --- |
| `README.md` | Profile-level statement of purpose, focused workflow map, one visible start-here link, and clear state/boundary language. |
| `START_HERE.md` | A short, privacy-safe orientation: where to inspect the current Releaseforge draft, how to run its synthetic demo locally, which related tools feed the handoff, and what not to share. |

No site deployment, tracking, sign-up, analytics, external form, issue creation,
payment flow, user-data upload, or GitHub profile setting change is part of this
work.

## Information architecture

### Profile README

The profile README remains concise. It contains:

1. A plain-language identity and the local-first release-workflow thesis.
2. A `Start here` section that directs visitors to `START_HERE.md`, rather than
   presenting a crowded list of repositories as equally important products.
3. A compact Mermaid flow showing artwork, audio, and metadata evidence feeding
   into one Releaseforge handoff packet. Every node is also explained in
   accessible prose/table form so the meaning does not depend on the diagram.
4. A focused tool table with a purpose, a repository link, and a literal current
   state. Releaseforge is named as a draft; linked core repositories are not
   described as hosted services or external certification systems.
5. Artist/label identity and working principles from the existing README,
   tightened but retained.

### Start-here guide

`START_HERE.md` uses a deliberately narrow sequence:

1. Explain that Releaseforge is the flagship local proof workflow and remains a
   draft review branch.
2. Link directly to the draft PR and its current branch tree, then show the
   documented synthetic-demo commands. The commands use a new local destination
   and do not inspect real music or artwork.
3. Explain the four-tool evidence map: Coverforge for visual delivery captures,
   Mastergate for declared PCM WAV measurements, Releaseledger for declared
   metadata, and Releaseforge for one local review packet. The guide does not
   claim the tools are required, automatically interoperable beyond documented
   captures, or a replacement for human approval.
4. Link to the existing Releaseforge privacy-minimal pilot protocol and repeat
   the no-upload/no-sensitive-data boundary in profile-level language.

## Exact boundary language

The launchpad may say that a tool can be inspected, cloned, or run locally. It
must not say that it is released, production-ready, paid, compliant, approved,
or accepted by a distributor. It must not call local checks proof of rights,
ownership, approval, platform acceptance, or public-release readiness.

No raw paths, media, hashes, client data, release metadata, credentials, or
private account state belongs in either profile file.

## Link and content validation

Before publishing the draft PR:

1. Verify every local Markdown target exists.
2. Verify each external GitHub link resolves to the intended repository, draft
   PR, or development branch using GitHub CLI metadata rather than assuming a
   default-branch state.
3. Scan the rendered-source Markdown for credential-like tokens, file URIs,
   absolute local paths, and prohibited release/compliance claims.
4. Inspect the diff manually for concise, accurate language and preserve the
   profile's personal artist/label identity.

## Acceptance criteria

- A visitor can identify Releaseforge as the flagship and find one safe first
  local demo path in under a minute.
- The relationship of the four core tools is visually and textually clear.
- Draft/experimental state and local/privacy boundaries are explicit.
- The change stays static and contains no user-data, deployment, payment,
  account, tracking, or outreach action.
- The implementation ships as a draft child PR of the existing profile-portfolio
  draft and does not merge or retarget that parent.
