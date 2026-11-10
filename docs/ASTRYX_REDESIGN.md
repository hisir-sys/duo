# DuoAI Studio — Astryx UI redesign

This pass integrates Meta's Astryx design system into the existing React 19 + Vite + Electron renderer. It deliberately preserves the current Python backend, navigation state, project APIs, Master Orchestrator calls, worker execution, and review/workspace behavior.

## Astryx packages

- `@astryxdesign/core@0.7.12`
- `@astryxdesign/theme-neutral@0.7.12`
- `@stylexjs/stylex@0.19.0`
- `@astryxdesign/cli@0.7.12` (development tool)

The renderer loads Astryx reset, component CSS, and Neutral theme CSS before DuoAI's own theme and screen styles. The root is wrapped in Astryx's documented `Theme` provider and the application chrome now uses Astryx's `Button` component.

## Template patterns selected for DuoAI

The official Astryx template catalogue is available with:

```bash
npm run astryx -- template --list
```

The redesign maps these official page patterns to the existing screens:

| DuoAI screen | Astryx template pattern | Adaptation |
| --- | --- | --- |
| Home dashboard | Analytics Dashboard + Project Status Dashboard | Headline metrics, current work, activity, progress and system topology |
| Projects | Card Grid + Work Item Detail | Searchable project cards with a persistent project inspector |
| Agents | Card Grid | Filterable specialist directory and profile detail |
| Master Control Room | AI Chat Conversation + Project Status Dashboard | Request/planning surface, staged task plan, run status and worker results |
| Workspace | IDE + File Explorer | File tree, editor, task context and project navigation |
| Review Center | Inbox Table + Work Item Detail | Review queue with a focused detail pane |
| Settings | Settings Panels | Persistent category navigation and editable preference panels |

These are content/layout adaptations to DuoAI's existing screens, not wholesale copies of Astryx demo applications. The app keeps its own product copy, backend data flow and interactions.

## Visual direction

- Astryx Neutral foundation with warm grey, off-white and slate-blue accents.
- Apple-inspired translucent surfaces: layered blur, subtle inner highlights, fine borders and soft ambient shadows.
- Hover motion is short and restrained; touch layouts do not depend on hover.
- Existing light/dark preference remains the source of truth for DuoAI's app-level color mode.
- Reduced-motion preferences are respected.

## Local template inspection

From `desktop-ui`, use the scoped CLI through the npm script:

```bash
npm run astryx -- template analytics-dashboard
npm run astryx -- template ide
npm run astryx -- template settings-panels
npm run astryx -- component Button
npm run astryx -- docs theme
```

The CLI emits template source for inspection; do not overwrite the existing app screens blindly. Integrate individual template structures only where their data and interaction model matches DuoAI.

## Verification still required

This repository update was authored through GitHub. The Electron app has not been installed, launched, visually inspected, or built in this environment. Run `npm install` and `npm run build` from `desktop-ui` before treating this redesign as verified.
