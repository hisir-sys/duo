# DuoAI Repository Status Audit

**Audit date:** 2026-11-11  
**Repository:** `hisir-sys/duo`  
**Branch reviewed:** `main`  
**Main HEAD at audit time:** `196ef6ce3f71247b8070b2467d3107cd1141432b`

## Executive summary

The repository contains two desktop application surfaces:

- The established Python/PySide6 application, whose business logic and persistence live primarily in `core.py` and the provider/orchestrator modules.
- The newer Electron/React renderer in `desktop-ui`, which has a restricted Electron IPC bridge and a JSON-lines Python adapter.

The latest main-branch commit is a dependency compatibility adjustment: it pins `@astryxdesign/core`, `@astryxdesign/theme-neutral`, and `@astryxdesign/cli` to version `0.7.11` instead of `0.7.12`.

## Verified repository state

### Latest main commit

- Commit: `196ef6ce3f71247b8070b2467d3107cd1141432b`
- Message: `fix: pin Astryx packages to published stable version`
- Changed file: `desktop-ui/package.json`
- Change: Astryx packages pinned from `0.7.12` to `0.7.11`.

### Electron-to-Python integration present on main

The following files were read from `main`:

- `desktop-ui/electron/main.cjs`
- `desktop-ui/electron/preload.cjs`
- `desktop-ui/electron/backend_bridge.py`

The Electron main process starts the Python bridge and communicates over newline-delimited JSON. The preload exposes a narrow `duoDesktop.backend.invoke` API. Renderer access to Node integration is disabled, context isolation and sandboxing are enabled, and the main process allow-lists backend methods.

The bridge currently exposes these operation groups:

- Provider listing, saving/removing credentials, and connection tests.
- Project listing, creation, retrieval, and updates.
- Shared-memory retrieval and saving.
- Master plan creation and worker execution.
- Agent-run listing.

The adapter imports the existing `core`, `provider_registry`, and Master plan validation code. Provider keys are retrieved and stored through the existing Python credential-vault path; the renderer is not given raw credentials by the bridge.

### Existing Python core

The inspected `core.py` uses local `~/.duoai` storage, atomic writes for JSON/text persistence, OS keyring-backed provider credentials, project records, Master planning, and provider clients. The root README documents Python 3.11 and the existing PySide6 application as the established source-run path.

### Existing reliability work

A separate branch named `feat/duoai-reliability-release` exists. Its notable reliability/security work is represented by commit `53b71db61be7d66caf568e844918a4a887aeaf96` (2026-11-06), which includes credential-vault hardening, atomic persistence, bounded audio capture, safer exports, tests, pinned Python dependencies, and a Windows installer workflow. This audit does not assume that branch is merged into `main`.

## Verification limits and risks

- The latest main commit's combined GitHub status response contained no status entries. This is **not** evidence of a passing build.
- No local Electron build, Python test suite, or end-to-end UI/backend session was run as part of this repository inspection.
- The bridge source exists, but packaged-app resource inclusion and the production Windows installer path were not validated here.
- The root README still describes the PySide6 application as the normal run path; the Electron UI's production packaging and support status should be documented explicitly once verified.
- The bridge currently offers project CRUD and Master planning/run operations, but this audit does not claim every visible renderer control is wired to a real backend operation.

## Recommended next development sequence

1. Run `python -m pytest -q` in the supported Python environment and `npm run build` in `desktop-ui`.
2. Launch the Electron app and verify backend health, provider setup, project creation/reload, Master planning, worker execution, and run-history refresh.
3. Test failure paths: missing Python runtime, missing credential vault, provider errors, backend process exit, and malformed IPC arguments.
4. Verify that the Windows package includes the Python bridge and all required Python modules/resources, then run a clean-install smoke test.
5. Update the README and release workflow only after the above checks pass.

## Audit conclusion

The repository has a meaningful Electron-to-Python integration foundation on `main`, but it is not yet justified to label the Electron experience fully production-verified. The next milestone should be a reproducible build plus an end-to-end integration test, followed by installer validation.
