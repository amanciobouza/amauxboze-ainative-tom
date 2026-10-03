# Design: Agentendetails, aktuelle Arbeit und Historie

## Product outcome

Für jeden Agenten zeigen, wer er ist, was er kann, woran er arbeitet und welche Ergebnisse er geliefert hat.

## Proposed decisions

Profiltexte kommen aus versionierten Agentenbeschreibungen bzw. KnowledgeProvider mit Herkunft, Skills aus der Registry. Aktivität wird aus persistierten Stage-Events abgeleitet, niemals aus animierten Figuren. Zustände: working, waiting_approval, blocked, idle, unavailable, unknown. Mehrere parallele Aufgaben bleiben sichtbar; working hat visuell Vorrang, weitere wartende Aufgaben bleiben als Badge. Fehlende/stale Telemetrie bedeutet unknown, niemals automatisch idle. Historie ist paginiert, filterbar und restartfest. Keine privaten Prompts, Secrets oder unbeschränkten Kundendaten anzeigen.

## Contract sketch (to finalize before implementation)

AgentProfile(agent_id, name, role, mission, background_source, skills, tool_permissions, approval_boundaries); AgentActivity(agent_id, state, active_assignments, waiting_assignments, observed_at, freshness); ActivityRecord(run_id, stage_id, skill_id, attempt_id, status, timestamps, artifact_refs, trace_id).

## Dependency ownership

- add-organization-structure
- build-local-control-plane: persistent run/event repositories
- modularize-ai-native-os: agent/skill tracing

Shared API shell, repositories, approval service and UI shell belong to build-local-control-plane; provider/policy/tracing abstractions belong to modularize-ai-native-os. This change owns the feature-specific projections, contracts, screens and acceptance tests. Shared work must not be duplicated.

## Failure, security and verification

Use structured API errors, explicit loading/empty/stale states and trace correlation. Test happy paths plus the failure scenarios in the spec. Redact secrets and scope evidence to permitted knowledge. Commands revalidate server-side; display configuration never grants permissions. Restart/reconnect handling must not fabricate work or duplicate side effects.

## Open product decisions

- Welche Hintergrundinformationen aus agents/ sollen sichtbar sein?
- Soll die Historie in V1 nur Prozessarbeit oder auch unabhängige Agentenaufgaben erfassen?

## Governance and boundaries

Status: DRAFT FOR PRODUCT REVIEW. Specification work is authorized; application implementation is not yet authorized. No checked implementation task means a feature has been delivered.

All cross-module DTOs MUST be typed. Business services depend on contracts, with LangGraph behind WorkflowService/engine adapters, Obsidian behind KnowledgeProvider, model calls behind ModelGateway, and external access/actions behind ToolGateway plus PolicyEngine. Consequential actions retain explicit human approval. Runtime state belongs in repositories (SQLite locally, PostgreSQL replaceable later); organizational evidence/knowledge belongs behind KnowledgeProvider. Commands carry stable idempotency identities; retries and uncertain outcomes are explicit. Correlation/run/attempt IDs connect events, traces and evaluations. Task context is bounded and permissions are explicit. No browser filesystem access or provider credentials. Local V1 binds to loopback; SaaS authentication/tenancy is future scope without changing business contracts.
