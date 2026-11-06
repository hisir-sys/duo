# DuoAI Studio — Electron UI preview

This is the first UI-only Electron + React delivery, separate from the existing PySide6 application.

## Run

Requires Node.js 22 or newer.

```bash
cd desktop-ui
npm install
npm run dev
```

Build the renderer with `npm run build`.

## Current scope

- Centralized light-theme tokens and Inter / JetBrains Mono fonts
- Home screen, reusable metric treatment, and original Orb artwork
- Local activity search and Low Effects toggle
- Electron window with context isolation, sandboxing, and Node integration disabled

## Integration boundary

The Python backend and PySide6 app are unchanged. The Home screen uses labelled sample data. Provider status and activity are not connected to live backend state. A dedicated Python service/IPC contract is required before the renderer can safely access provider, project, orchestrator, worker, or review operations. This preview exposes no backend actions.

## ReactDrops licensing

ReactDrops source was reviewed, including registry metadata and its component licence. The licence restricts publishing component source as reusable development assets/source bundles. Because this repository is public, this preview uses original Orb and logo artwork rather than copying ReactDrops source into the repository. Reconsider integration only with written permission or another distribution arrangement that complies with that licence.
