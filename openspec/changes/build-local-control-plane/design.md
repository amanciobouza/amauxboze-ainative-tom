# Design

## Context

The existing runtime already provides:
- Agent Registry
- Skill Registry
- Obsidian Adapter
- Model Router
- Approval Gates
- LangGraph workflows
- OpenSpec governance

What is missing is an application shell and persistent control-plane API around those capabilities.

## Goals

- Run completely on the local machine.
- Use a browser-based web UI.
- Require no SaaS infrastructure for V1.
- Keep frontend/backend boundaries suitable for later SaaS deployment.
- Surface all approval requests centrally.
- Make workflow execution observable.
- Make local LM Studio status visible.
- Keep Obsidian as company knowledge memory.
- Avoid coupling workflows to SQLite.

## Non-Goals

- Multi-tenancy in V1.
- User authentication in local V1.
- Public internet deployment in V1.
- Native desktop packaging in V1.
- Replacing Obsidian.
- Connecting every social publishing API in V1.

## Technology Decisions

### Frontend
React + TypeScript + Vite.

Rationale:
- simple local development
- production-capable SPA
- easy later SaaS deployment
- avoids server-side rendering complexity that is not needed for this application

### Backend
FastAPI.

Rationale:
- same Python runtime as LangGraph and adapters
- typed API models
- streaming-friendly
- clean separation from UI

### Communication
- REST for commands and resources
- Server-Sent Events (SSE) for workflow/run updates in V1
- WebSocket only if later required

### Runtime State Store

V1:
- SQLite
- repository abstraction

Future:
- PostgreSQL

Stored here:
- workflow run metadata
- UI state
- approval requests
- activation idempotency records
- runtime events
- model routing telemetry

Not stored here:
- primary business knowledge that belongs in Obsidian

### Backend Module Boundary

```text
api/
  workflows
  approvals
  agents
  skills
  knowledge
  models
  settings
  health

services/
  workflow_service
  approval_service
  knowledge_service
  model_service

repositories/
  workflow_run_repository
  approval_repository
  event_repository
```

## UI Navigation

```text
Dashboard
Workflows
Approvals
Agents
Skills
Knowledge
Models
Settings
```

## Workflow UX

A workflow detail page must show:

- workflow name
- current state
- current responsible agent
- timeline
- generated artifacts
- model/provider used
- pending approval
- errors
- retry control
- final outcome

## Approval UX

Approval cards must show:

- requesting workflow
- requested action
- decision context
- supporting artifacts
- available decision buttons

The UI must use the allowed decisions declared by the active LangGraph interrupt.

## Local Model UX

The application queries LM Studio at:

`http://127.0.0.1:1234`

The Models screen shows:

- server reachable/unreachable
- available local models
- currently preferred task mappings
- cloud provider availability
- local-only policy status

## Knowledge UX

The UI accesses Obsidian only through the backend adapter.

The browser must never receive arbitrary local filesystem access.

Configured vault:

`C:\Users\amanc\OneDrive\ObsidianVaults\Amaux Bozé`

## Local Startup Target

A single developer command should eventually launch:

- backend
- frontend

Example target:

`./run-local`

Windows-compatible equivalent must also be provided.

## SaaS Migration Boundary

Future SaaS work should primarily add:
- authentication
- tenancy
- PostgreSQL
- hosted knowledge layer / connectors
- secret management
- deployment infrastructure

It should not require rewriting:
- workflows
- skill registry
- agent registry
- model-routing contract
- approval semantics
