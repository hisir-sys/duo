# DuoAI Studio — Electron desktop interface

The Electron + React interface now connects to the existing Python core through a restricted JSON-lines process bridge. The Python core remains the source of truth for provider credentials, configuration, projects, Master planning and worker execution.

## Run on Fedora / Linux

Requires Node.js 22+ and the Python dependencies from the repository root.

```bash
# From the repository root
python3 -m pip install -r requirements.txt

cd desktop-ui
npm install
npm run build
npm run dev:linux
```

If Node is installed through the VS Code Flatpak NVM directory, add that Node binary directory to PATH before running npm.

## Backend bridge

Electron starts `electron/backend_bridge.py` as a child Python process. Renderer calls go through a narrow preload API and Electron IPC; the renderer cannot import Node or Python modules directly.

The bridge exposes an allow-list of operations:
- Health and provider status
- Save, remove and test provider credentials
- List and create local projects
- Read and save shared memory
- Create validated Master Orchestrator plans
- Run the existing proposal-only worker team
- List saved worker runs

Provider secrets are never returned to the renderer. The Python core continues to store credentials through the operating system credential manager. Do not add API keys to local storage, renderer state persistence, logs, or project records.

## Worker safety boundary

The Master Orchestrator creates dependency-aware plans using configured providers. Specialist workers run in isolated folders below `~/.duoai/workspaces`. Coding workers save proposed files; testing, review and research workers return reports. Worker agents do not execute shell commands or modify the selected source project. Human inspection and manual application remain required.

## Current functional scope

- Live Python backend connection status in the app shell
- Provider settings connected to the existing secure credential vault
- Live provider connection tests and model discovery
- Project list and project creation backed by `~/.duoai/projects`
- Master Orchestrator planning through the existing Python implementation
- Worker execution through the existing isolated proposal system
- Worker result and proposed-artifact inspection in the Master Control Room
- Light/dark themes, reduced-motion support and fixed frosted-glass navigation

Some areas remain preview-only: activity feed and throughput chart, detailed agent telemetry, full workspace file editing, and final review/approval actions. The Electron renderer is not yet bundled into the existing PyInstaller Windows installer; packaged desktop distribution needs a separate packaging step that includes the Python runtime/bridge and Electron assets.

## Build and verification

`npm run build` checks TypeScript and builds the renderer. From the repository root, run `pytest -q` for the Python test suite, including bridge contract tests.

Never treat a successful UI build as proof that an external provider is connected. Provider connection tests make a real request to the selected official provider API.
