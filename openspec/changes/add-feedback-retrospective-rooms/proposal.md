# Feedback-Zyklen und Retrospektiven-Räume

## Why

Agenten reflektieren belegte Ergebnisse, schlagen Verbesserungen vor und entwickeln prüfbare Experimente mit menschlicher Entscheidung.

## What Changes

Introduce feedback-retrospective-rooms as a separately reviewable feature of the local control plane. Existing workflow business decisions and approval semantics remain intact unless an approved scenario explicitly changes them.

## Capabilities

### New Capabilities

- feedback-retrospective-rooms

## Impact

UI, typed application contracts, read models and service orchestration as specified in design.md. No application code is implemented by this proposal.

## Dependencies

- add-business-process-instances
- add-agent-detail-activity
- modularize-ai-native-os: models, context, policy, tool gateway and evaluations
- build-local-control-plane: durable events, approvals and knowledge

## Governance and boundaries

Status: DRAFT FOR PRODUCT REVIEW. Specification work is authorized; application implementation is not yet authorized. No checked implementation task means a feature has been delivered.

All cross-module DTOs MUST be typed. Business services depend on contracts, with LangGraph behind WorkflowService/engine adapters, Obsidian behind KnowledgeProvider, model calls behind ModelGateway, and external access/actions behind ToolGateway plus PolicyEngine. Consequential actions retain explicit human approval. Runtime state belongs in repositories (SQLite locally, PostgreSQL replaceable later); organizational evidence/knowledge belongs behind KnowledgeProvider. Commands carry stable idempotency identities; retries and uncertain outcomes are explicit. Correlation/run/attempt IDs connect events, traces and evaluations. Task context is bounded and permissions are explicit. No browser filesystem access or provider credentials. Local V1 binds to loopback; SaaS authentication/tenancy is future scope without changing business contracts.
