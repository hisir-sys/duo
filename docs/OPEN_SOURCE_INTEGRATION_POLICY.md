# Open-source integration and zero-cost policy

This document records the current integration policy for DuoAI Studio. It is not a legal opinion; review the exact release tag, package metadata, bundled assets, and dependency tree before redistribution.

## User constraints

- Do not newly adopt MIT-licensed coding-agent projects or model-serving components.
- Prefer genuine, maintained, open-source projects with licences that permit commercial use, modification, and redistribution.
- Exclude non-commercial, research-only, source-available, proprietary, or otherwise incompatible terms.
- Do not execute inference locally on the user's computer.
- Never route a request to a paid model or paid fallback in Zero-Cost mode.

## Important licensing distinction

Open-source licences always contain conditions. Apache-2.0 is permissive, but requires preservation of copyright, licence, and applicable NOTICE information, and includes patent provisions. "No conditions at all" is not a practical open-source licensing category.

The current desktop foundation already includes third-party packages with their own licences. The policy in this file applies to new agent/model integrations; a complete dependency audit is required before making any claim that the entire application contains no MIT-licensed transitive dependency.

## Candidate integrations — not yet vendored

| Project | Reported licence | Potential use | Current decision |
|---|---|---|---|
| cline/cline SDK | Apache-2.0 | Embedded agent runtime, tools, sessions, events, checkpoints, subagents | Preferred candidate; integrate only after package/dependency and tool-permission audit |
| Aider-AI/aider | Apache-2.0 | Specialist repository-aware editing/review engine | Secondary candidate; investigate programmatic interface and dependency tree |
| aaif-goose/goose | Apache-2.0 | Alternative general-purpose agent runtime and API | Reference candidate; do not bundle its separate desktop application |

These are candidate projects, not dependencies currently included in DuoAI. The licence must be checked at the exact version being integrated, including all transitive packages and assets.

## Model policy

Model code, model weights, datasets, and inference-host terms are separate legal and operational layers. A permissively licensed agent does not grant rights to model weights. Each model needs a recorded model-card/weight licence and use restrictions.

DuoAI must not describe a model as "free" merely because its weights are public or its repository is on GitHub.

## Zero-Cost mode requirements

1. A provider/model must be explicitly marked as verified zero-price before it can be selected in Zero-Cost mode.
2. Unknown, expired, promotional, or ambiguous pricing is treated as unavailable.
3. Paid fallback is disabled. On quota exhaustion, pause and explain the limit.
4. Never silently upgrade a model or provider.
5. Display provider limits and last verification date when available.
6. No claim of unlimited or permanent free hosted inference.

## Current execution architecture

- The Python Master Orchestrator remains the source of truth for planning.
- The worker team now executes independent tasks in a dependency stage concurrently, with a default cap of three active workers.
- Worker execution has bounded retries and persists a run checkpoint after each completed task.
- Workers still create isolated proposals only. They do not modify the selected source project or execute commands.
- Expanding to 12 concurrent workers requires explicit resource and provider-quota controls; 12 logical roles do not imply 12 simultaneous model calls.

## Next integration gate

Before adding an external coding-agent SDK:
- pin an exact release;
- inspect its top-level and transitive licences;
- review security advisories and tool execution defaults;
- implement a restricted tool policy and workspace sandbox;
- keep provider credentials in the OS vault;
- add integration tests for cancellation, timeout, restart, and recovery;
- document all required third-party notices.
