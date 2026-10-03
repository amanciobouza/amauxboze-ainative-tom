# Proposal

## Why

The current system has working agents, skills, LangGraph workflows, model routing, approvals, and Obsidian persistence.

To become a state-of-the-art AI-native TOM/OS and later SaaS platform, the architecture must prevent tight coupling between business logic and concrete technologies such as LangGraph, LM Studio, Obsidian, Shopify, or any single model provider.

## What Changes

Introduce explicit modular platform boundaries and contracts for:

1. Context Engine
2. Tool Gateway
3. Model Gateway
4. Knowledge Provider
5. Policy Engine
6. Event Engine
7. Observability & Evaluation
8. Plugin Registry

Existing workflows will gradually depend on these contracts instead of concrete adapters.

## Capabilities

### New Capabilities

- **context-engine** — build minimal task-specific context bundles.
- **tool-gateway** — mediate all external actions and data access.
- **model-gateway** — provider-neutral model invocation.
- **knowledge-provider** — provider-neutral organizational knowledge access.
- **policy-engine** — permissions, approval requirements, and guardrails.
- **event-engine** — start workflows from internal/external events.
- **observability** — trace workflows, agents, skills, models, tools, approvals, errors.
- **plugin-registry** — discover and register replaceable providers and capability packs.

## Impact

This change is architectural. It should preserve existing business behavior while improving replaceability, testability, security, and SaaS readiness.
