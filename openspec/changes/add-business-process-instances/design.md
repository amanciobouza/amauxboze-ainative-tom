# Design: Laufende Prozessinstanzen, Freigaben und Wiederaufnahme

## Product outcome

Aktive und vergangene Geschäftsprozesse einschließlich Stufen, Verantwortung, Ergebnissen und Freigaben zentral steuerbar machen.

## Proposed decisions

Status normalisiert: queued, running, waiting_approval, held, failed, completed, rejected, cancelled; das Workflow-Original bleibt als Detail erhalten. held ist nicht completed und bedeutet keinen laufenden Worker. Erlaubte Commands stammen aus WorkflowService; kein generischer Retry für jeden Zustand. Persistente LangGraph-Checkpoints hinter Engine-Adapter zusätzlich zu Metadaten sind zwingend: SQLite-Metadaten allein reichen nicht für Resume. SSE nutzt persistierte Event-IDs/Sequenzen, Replay nach reconnect und Snapshot bei Lücken. Freigaben sind an Run und Revision gebunden; doppelte/stale Entscheidungen erzeugen keine zweite Wirkung. Retry nutzt stabile Action-IDs und durable Idempotenz; unbekannter externer Erfolg wird als reconciliation_required blockiert statt blind wiederholt.

## Contract sketch (to finalize before implementation)

ProcessRun(id, definition_id, definition_version, status, current_stage, active_agent_ids, created_at, updated_at, revision); StageAttempt(id, run_id, stage_id, agent_id, skill_id, status, attempt_number, trace_id); ApprovalEnvelope(id, run_id, revision, action, allowed_decisions, artifact_refs); RunEvent(id, run_id, sequence, timestamp, type, payload).

## Dependency ownership

- modularize-ai-native-os: workflow/policy/trace abstractions
- build-local-control-plane: repositories, durable checkpointing, workflow/approval API and SSE

Shared API shell, repositories, approval service and UI shell belong to build-local-control-plane; provider/policy/tracing abstractions belong to modularize-ai-native-os. This change owns the feature-specific projections, contracts, screens and acceptance tests. Shared work must not be duplicated.

## Failure, security and verification

Use structured API errors, explicit loading/empty/stale states and trace correlation. Test happy paths plus the failure scenarios in the spec. Redact secrets and scope evidence to permitted knowledge. Commands revalidate server-side; display configuration never grants permissions. Restart/reconnect handling must not fabricate work or duplicate side effects.

## Open product decisions

- Soll ein bewusster Hold manuell wieder aufgenommen werden und mit welcher Entscheidung? Bestehende Workflow-Semantik bleibt bis zur Freigabe erhalten.
- Ist V1 auf manuelle Prozessstarts beschränkt, oder sollen ausgewählte Event-Starts schon bedienbar sein?

## Governance and boundaries

Status: IMPLEMENTATION AUTHORIZED by the founder request to implement the whole app. Scope decisions and shared delivery are recorded in implement-complete-local-app/design.md. Task completion remains evidence-based.

All cross-module DTOs MUST be typed. Business services depend on contracts, with LangGraph behind WorkflowService/engine adapters, Obsidian behind KnowledgeProvider, model calls behind ModelGateway, and external access/actions behind ToolGateway plus PolicyEngine. Consequential actions retain explicit human approval. Runtime state belongs in repositories (SQLite locally, PostgreSQL replaceable later); organizational evidence/knowledge belongs behind KnowledgeProvider. Commands carry stable idempotency identities; retries and uncertain outcomes are explicit. Correlation/run/attempt IDs connect events, traces and evaluations. Task context is bounded and permissions are explicit. No browser filesystem access or provider credentials. Local V1 binds to loopback; SaaS authentication/tenancy is future scope without changing business contracts.
