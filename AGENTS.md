# AGENTS.md

## Purpose

This repository implements the **Amaux Bozé AI Native TOM/OS**.

This file is the short operational map for coding agents such as Codex. It is not the complete specification.

## Read First

Before significant changes, read:

1. `openspec/config.yaml`
2. `ARCHITECTURE.md`
3. `docs/ModularArchitecture.md`
4. `docs/ApplicationArchitecture.md`
5. the relevant active change under `openspec/changes/`

## Mandatory Development Rule

**All software changes are spec-driven using OpenSpec.**

Do not implement a substantial feature, architectural change, workflow, integration, or refactor outside an OpenSpec change.

For each change:

1. confirm business intent
2. create/update OpenSpec proposal, design, specs, and tasks
3. implement in dependency order
4. update task status only when actually complete
5. run OpenSpec validation and tests
6. preserve behavior unless the spec explicitly changes it

## Architecture Rules

- The system is an AI-native TOM/OS, not a collection of ad-hoc agents.
- Architecture is modular and contract-first.
- Everything is replaceable except the contracts and the knowledge.
- Business workflows depend on interfaces, not provider-specific implementations.
- LangGraph is the current workflow engine, not permanent business logic.
- Obsidian is the current knowledge provider, not permanent storage coupling.
- LM Studio, OpenAI, and Anthropic sit behind a provider-neutral Model Gateway.
- External actions must pass through Tool Gateway + Policy Engine.
- Context must be task-scoped and minimal by default.
- Consequential actions require explicit human approval until delegated.
- Observability, evaluations, retries, and traceability are first-class concerns.
- Event-driven workflow initiation must be supported.
- Providers and integrations should use plugin contracts.
- Local-first architecture must preserve a clean migration path to SaaS.

## Conceptual Model

- **Agent** = responsibility
- **Skill** = capability
- **Workflow** = collaboration/process
- **Tool** = controlled access
- **Model** = intelligence
- **Context Engine** = task-specific context selection
- **Policy Engine** = permissions, approvals, guardrails
- **Knowledge Provider** = organizational memory
- **Runtime State** = operational execution state

## Current Technology Choices

- Python
- LangGraph
- Obsidian
- LM Studio
- OpenAI / Anthropic as optional external providers
- OpenSpec
- FastAPI planned for the control plane
- React + TypeScript + Vite planned for the local-first web UI
- SQLite locally, PostgreSQL later for SaaS

## Project Constants

- Repository: `https://github.com/amanciobouza/amauxboze-ainative-tom`
- Obsidian Vault: `C:\Users\amanc\OneDrive\ObsidianVaults\Amaux Bozé`
- LM Studio: `http://127.0.0.1:1234`

## Quality Bar

Before considering work complete:

- contracts remain typed
- permissions are explicit
- approval boundaries are preserved
- provider-specific coupling is avoided
- tests cover happy paths and meaningful failure paths
- CI is green
- OpenSpec tasks reflect the real implementation state
