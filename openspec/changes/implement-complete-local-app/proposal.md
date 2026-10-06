# Complete local TOM/OS application

## Why
The founder explicitly authorized implementing the entire app and working through the needed tasks. Existing control-plane and seven feature proposals define the intended product but contain no application implementation.

## What Changes
Deliver the FastAPI/SQLite control plane and React/TypeScript/Vite application: dashboard, original isometric office, organization/departments, agent profiles/activity, skills, all five process launchers, persistent LangGraph runs/approvals/recovery, knowledge, live model transports/settings, retrospective rooms and measurable experiment review. Preserve existing agent rights and business workflow decisions.

## Scope decisions
Use proposed defaults: Amancio is the human founder; flat reporting; seven departments; original warm office; manual starts and manual retrospective triggers; proposal-only software improvements. Simulation is explicitly labeled and isolated from live metrics/knowledge/actions. Live external publishing remains unavailable without configured adapters; never pretend publication succeeded. Commercial metrics remain unavailable without a source. Optional cloud model calls require explicit provider selection, configured model and server-side credentials. Local model calls never fall back to cloud.

## Related changes
Implements build-local-control-plane and the seven add-* feature changes. This proposal records authorization and resolves their draft review gates, with shared implementation owned here. Verification evidence and remaining limitations stay truthful; no remote CI result is asserted without running CI.
