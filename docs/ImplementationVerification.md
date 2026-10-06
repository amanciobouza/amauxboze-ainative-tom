# Local application delivery verification

Verified on 2026-10-03. Scope and completed tasks: `openspec/changes/implement-complete-local-app/` and `build-local-control-plane/tasks.md`.

## Delivered application

The Windows launcher serves the React UI at http://127.0.0.1:3000 and the local FastAPI control plane at http://127.0.0.1:8000. Production mode builds and serves the UI from the API. SQLite retains settings, events, runs, checkpoints, decisions and retrospective records across restarts.

All 13 navigation screens are implemented: dashboard, original isometric office, organization, departments, process catalog, run history/detail, approval inbox, retrospective rooms, agents, skills, knowledge, models and settings. Five existing business workflows execute through their actual LangGraph graphs. Forms, approval provenance, retries, hold/resume, artifacts, stage usage and activity share backend records. Elena receives her direct profile instructions in live execution.

Retrospectives support bounded participant contributions, synthesis, founder decisions, proposed experiments, manual results and inconclusive outcomes. Closed live learnings can be exported only through the audited Tool Gateway and Policy Engine. Simulation is explicit throughout and cannot become live evidence.

## Verification results

- Backend: 106 tests passed (21.63 seconds in the final full run). Windows denied writes to the pre-existing pytest cache; this produced one cache warning without affecting tests.
- Frontend: 3 component tests passed; TypeScript checks and Vite production build passed.
- OpenSpec structural validation and `git diff --check` passed.
- Browser: all 13 screens, process creation, both simulated founder approvals, retrospective review/experiment/result, Elena profile and mobile navigation passed with zero page errors. At 390-pixel mobile width there was no horizontal overflow.
- Original office and mobile screenshots were visually inspected. Screenshot artifacts: `.runtime/screenshots/` (local generated files, ignored by Git).
- Browser office stress measurement: 50 decorative actors, approximately 60 FPS over 90 animation frames; reduced-motion mode. Reference: Windows 11 build 26200, Intel64 Family 6 Model 183, Edge 154.0.4258.53. This is a local reference measurement, not a universal performance guarantee.
- npm audit reported zero known vulnerabilities in the installed dependency tree.
- Real LM Studio verification completed the live concept stages using `google/gemma-4-e4b`. Run `43bce8a2-c348-492a-ba73-949ab835ec9e` is waiting for the founder concept decision; no live business approval was granted during implementation. This persisted through launcher restart.
- CI jobs are configured for Python, frontend build/tests and browser smoke. Remote CI was not run because these workspace changes have not been pushed.

## Explicit limits

This delivery is the authorized local v1. Public publishing and commerce integrations have no configured execution adapters. The app reports their absence and does not invent published content, revenue, orders or conversion metrics. Cloud providers require explicit configuration and a privacy-mode change; there is no cloud fallback. Agent capabilities historically declared without a registered skill are shown as unavailable.

Process and retrospective initiation is manual. Experiment results are entered with evidence; the app does not manufacture improvements. Software improvement proposals remain proposals and require a separate OpenSpec implementation and review. No automatic production code changes, external publishing or external vault writes were performed during verification.

Historical feature checklists include broader acceptance and CI conditions. Their outstanding combined items remain visible; the consolidated local-v1 checklist records the work actually completed. See `docs/LocalApplication.md` for operation, settings and integration boundaries.
