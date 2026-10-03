# Amaux Bozé AI Native — Application Architecture

## Product Goal

Build a local-first application that operates the Amaux Bozé AI-native company and can later evolve into a multi-user SaaS web application without replacing the core architecture.

The application is the control plane for:

- Agents
- Skills
- LangGraph workflows
- Human approvals
- Obsidian knowledge
- Local and cloud LLMs
- Shopify and future external integrations
- Workflow history and observability
- Company operating status

## Architectural Principle

> Build a web application that runs locally first, not a local-only desktop application.

This avoids creating a dead-end architecture that later has to be rewritten for SaaS.

## V1 Runtime

```text
Browser
  │
  │ http://localhost:3000
  ▼
React Web App
  │
  │ REST / SSE
  ▼
FastAPI Control Plane
  │
  ├── LangGraph Runtime
  ├── Agent Registry
  ├── Skill Registry
  ├── Approval Service
  ├── Model Router
  ├── Obsidian Adapter
  └── Integration Tools
        │
        ├── Obsidian Vault
        │   C:\Users\amanc\OneDrive\ObsidianVaults\Amaux Bozé
        │
        ├── LM Studio
        │   http://127.0.0.1:1234
        │
        ├── OpenAI
        ├── Anthropic
        ├── Shopify
        └── Future integrations
```

## Application Responsibilities

### Dashboard
- company status
- running workflows
- approvals waiting
- recent learnings
- recent intelligence
- active product / campaign work

### Workflows
- start workflows
- inspect current stage
- view generated artifacts
- approve / revise / hold / reject
- resume failed workflows
- review completed runs

### Agents
- view organizational hierarchy
- inspect role, mission, background and permissions
- inspect assigned skills
- inspect recent work

### Skills
- browse skill registry
- inspect version, input/output contract and model requirements
- inspect evaluations
- enable future controlled editing

### Knowledge
- browse Obsidian through the application
- search company knowledge
- inspect decisions, observations and learnings
- open linked source notes

### Models
- inspect LM Studio health
- list available local models
- configure task-class routing
- show whether a workflow uses local / OpenAI / Anthropic

### Approvals
- central approval inbox
- see requested action and supporting artifacts
- approve
- revise
- hold
- reject / cancel as supported by workflow

### Settings
- Obsidian path
- LM Studio endpoint
- provider configuration
- integration status
- runtime health

## Local-First Deployment

V1 should run as two local services:

- frontend: React + TypeScript + Vite
- backend: Python + FastAPI

The user opens the application in a normal browser.

This is intentionally preferred over a native desktop framework in V1 because the same frontend/backend separation can later be deployed directly as SaaS.

## State

### Obsidian
Business knowledge and durable organizational memory.

### Runtime Database
Application and workflow state that does not belong in Obsidian.

Local V1:
- SQLite behind a repository abstraction

Future SaaS:
- PostgreSQL

The application layer MUST NOT expose database-specific behavior to workflows.

## SaaS Evolution

The future transition should replace deployment concerns, not business logic.

### Local
```text
localhost frontend
localhost FastAPI
SQLite
local Obsidian Vault
local LM Studio
```

### SaaS
```text
Web frontend
Hosted FastAPI
PostgreSQL
tenant-scoped knowledge storage / connectors
cloud or customer-specific model providers
authentication + authorization
```

LangGraph workflows, agent definitions, skill contracts and business logic remain reusable.

## Key Rule

The application is the user interface.

Users should not need to:
- start Python scripts manually
- edit YAML to operate normal workflows
- call LangGraph directly
- use LM Studio APIs directly
- navigate runtime files to approve actions

Those remain implementation details behind the application.
