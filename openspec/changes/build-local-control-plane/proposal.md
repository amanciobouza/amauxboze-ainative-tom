# Proposal

## Why

The AI-native operating system currently exists as code, specifications, agent manifests, skills, and LangGraph workflows.

Amaux Bozé needs a single local application that makes this system operable without directly invoking Python, editing runtime configuration, or manually interacting with LangGraph.

The same application architecture must later support deployment as a SaaS web application.

## What Changes

Build a local-first web application that acts as the control plane for the entire Amaux Bozé AI-native operating system.

The application will provide:

1. Dashboard
2. Workflow launcher and run history
3. Approval inbox
4. Agent organization browser
5. Skill registry browser
6. Obsidian knowledge access
7. Model / LM Studio status and routing view
8. Settings and integration health

## Capabilities

### New Capabilities

- **control-plane-api** — backend API exposing workflows, agents, skills, approvals, knowledge and models.
- **control-plane-ui** — local browser application for operating the company.
- **workflow-run-management** — start, inspect, resume and recover workflows.
- **approval-inbox** — central UI for LangGraph human approval interrupts.
- **runtime-state-store** — persistent application/workflow metadata.
- **model-management-ui** — inspect local model availability and routing.
- **knowledge-browser** — controlled application access to Obsidian knowledge.

## Impact

Normal operation of the AI-native company should happen through this application.

CLI and direct code invocation may remain available for development and debugging, but are no longer the primary user interface.
