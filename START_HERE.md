# Start here

## Try one safe workflow first

[Releaseforge](https://github.com/notgabriels-sys/releaseforge/pull/1) is the
flagship experiment: a local proof workflow for the moment before a delivery
handoff or distributor upload. It is currently a draft pull request, not a
hosted service or a release-compliance authority.

Read the [draft review](https://github.com/notgabriels-sys/releaseforge/pull/1)
or inspect the [current development branch](https://github.com/notgabriels-sys/releaseforge/tree/codex/initial-implementation).
To run the documented synthetic demo locally:

```bash
git clone --branch codex/initial-implementation --single-branch https://github.com/notgabriels-sys/releaseforge.git
cd releaseforge
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
releaseforge demo ./releaseforge-demo
```

The installation may retrieve the package's normal dependency. The demo then
creates a new local directory with illustrative media and proof packets. It
does not inspect, upload, rename, delete, or modify a real release folder.

## How the core tools connect

| Workflow lane | Tool | Local role |
| --- | --- | --- |
| Artwork delivery | [Coverforge](https://github.com/notgabriels-sys/albumdesign) | Preflights artwork and exports a per-platform delivery pack. |
| Metadata review | [Releaseledger](https://github.com/notgabriels-sys/releaseledger) | Checks declared release metadata and prepares a reviewable handoff dossier. |
| Evidence synthesis | [Releaseforge](https://github.com/notgabriels-sys/releaseforge/pull/1) | Creates a local proof packet and can reconcile documented compatible captures. |

The tools can be used independently. Where a documented compatible capture is
available, Releaseforge can read it locally into a companion handoff packet;
it does not install, call, upload to, or otherwise contact another tool. The
workflow still needs human review for rights, approvals, and the actual delivery
destination.

## Pilot safely

The [privacy-minimal pilot protocol](https://github.com/notgabriels-sys/releaseforge/blob/codex/initial-implementation/docs/PILOT.md)
explains how to test a genuine local handoff without giving away release
material. Do not upload or paste music, artwork, project files, hashes, source
packets, release or client metadata, credentials, or payment information into
public feedback, issues, chat, or email.

A local check can clarify a handoff. It does not establish rights, ownership,
approval, platform acceptance, or public-release readiness.
