# Design: Company-Dashboard mit nachvollziehbaren KPIs

## Product outcome

Die Startseite zeigt den Zustand der Firma und lenkt auf Prozesse, Freigaben, Blockaden und Learnings.

## Proposed decisions

V1-Vorschlag: aktive Runs = queued+running+waiting_approval+held; wartende Freigaben = offene Approval-Envelopes; fehlgeschlagene Runs = aktueller Status failed; abgeschlossene Runs im gewählten Fenster; Erfolgsquote = completed/(completed+failed+rejected+cancelled) mit Nenner und expliziter Definition; mediane Durchlaufzeit = completed_at-created_at abgeschlossener Runs einschließlich Wartezeit; neue Learnings = eindeutige persistierte Learning-Referenzen im Fenster. Für operative Statuszahlen gilt Snapshot-Zeit, für Zeitfenster UTC gespeichert und lokale Zeitzone dargestellt; Standard letzte 7 Tage. Kommerzielle KPIs wie Umsatz, Bestellungen, Conversion sind konfigurierbare spätere MetricsProvider und bleiben ohne Quelle unavailable, nie Null oder ausgedacht. Costs nur soweit tatsächliche Telemetrie verfügbar ist. Kein direkter Shopify-/Datenbankzugriff in der UI.

## Contract sketch (to finalize before implementation)

KpiDefinition(id, name, unit, formula, source, window, owner, thresholds); KpiValue(definition_id, value|null, period_start, period_end, observed_at, freshness, coverage, unavailable_reason); CompanyDashboard(kpis, approval_refs, blocked_run_refs, learning_refs, health).

## Dependency ownership

- add-business-process-instances
- build-local-control-plane: runtime events, health and knowledge services

Shared API shell, repositories, approval service and UI shell belong to build-local-control-plane; provider/policy/tracing abstractions belong to modularize-ai-native-os. This change owns the feature-specific projections, contracts, screens and acceptance tests. Shared work must not be duplicated.

## Failure, security and verification

Use structured API errors, explicit loading/empty/stale states and trace correlation. Test happy paths plus the failure scenarios in the spec. Redact secrets and scope evidence to permitted knowledge. Commands revalidate server-side; display configuration never grants permissions. Restart/reconnect handling must not fabricate work or duplicate side effects.

## Open product decisions

- Welche kommerziellen KPIs sind bereits zuverlässig messbar?
- Soll die Erfolgsquote abgelehnte/cancelled Entscheidungen als unerfolgreich zählen oder separat ausweisen?

## Governance and boundaries

Status: IMPLEMENTATION AUTHORIZED by the founder request to implement the whole app. Scope decisions and shared delivery are recorded in implement-complete-local-app/design.md. Task completion remains evidence-based.

All cross-module DTOs MUST be typed. Business services depend on contracts, with LangGraph behind WorkflowService/engine adapters, Obsidian behind KnowledgeProvider, model calls behind ModelGateway, and external access/actions behind ToolGateway plus PolicyEngine. Consequential actions retain explicit human approval. Runtime state belongs in repositories (SQLite locally, PostgreSQL replaceable later); organizational evidence/knowledge belongs behind KnowledgeProvider. Commands carry stable idempotency identities; retries and uncertain outcomes are explicit. Correlation/run/attempt IDs connect events, traces and evaluations. Task context is bounded and permissions are explicit. No browser filesystem access or provider credentials. Local V1 binds to loopback; SaaS authentication/tenancy is future scope without changing business contracts.
