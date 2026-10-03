# Design: Feedback-Zyklen und Retrospektiven-Räume

## Product outcome

Agenten reflektieren belegte Ergebnisse, schlagen Verbesserungen vor und entwickeln prüfbare Experimente mit menschlicher Entscheidung.

## Proposed decisions

Retrospektivenraum ist ein fachlicher Workspace und optional ein Office-Raum mit derselben ID, kein zweiter Runtime. Start manuell für abgeschlossene Runs/Abteilung; automatische Run-Completed-Trigger sind ein separat freizugebender Modus mit dedupliziertem Event und ohne selbstverstärkende Feedbackschleifen. Elena moderiert standardmäßig; die zuständigen Agenten liefern begrenzte, evidenzbasierte Beiträge über ModelGateway/ContextEngine. Rohbeobachtung, Interpretation und Vorschlag bleiben getrennt. Lifecycle: draft→collecting→synthesizing→awaiting_review→approved|rejected|held→experimenting→evaluating→closed; Modell-/Toolfehler mit Retryzustand. Agenten dürfen Vorschläge, Spezifikationsentwürfe und Sandbox-Experimente entwickeln. Keine selbständige Änderung von Code, produktiven Skills, Rechten, Preisen oder öffentlichen Inhalten. Umsetzung von Software erfordert ein freigegebenes OpenSpec-Change; externe Writes gehen durch ToolGateway/Policy und Human Approval. Reviews im bestehenden Prozess dienen als fachlicher Input; sie ersetzen keine Software-Governance.

## Contract sketch (to finalize before implementation)

Retrospective(id, scope, run_refs, participant_ids, facilitator_id, status, context_budget, trigger_event_id); Contribution(id, author_id, evidence_refs, observation, interpretation, proposal); Improvement(id, owner_id, hypothesis, baseline, metric, target, risk, approval_id, experiment_refs, status); EvaluationResult(experiment_id, baseline_ref, result_ref, outcome, rationale).

## Dependency ownership

- add-business-process-instances
- add-agent-detail-activity
- modularize-ai-native-os: models, context, policy, tool gateway and evaluations
- build-local-control-plane: durable events, approvals and knowledge

Shared API shell, repositories, approval service and UI shell belong to build-local-control-plane; provider/policy/tracing abstractions belong to modularize-ai-native-os. This change owns the feature-specific projections, contracts, screens and acceptance tests. Shared work must not be duplicated.

## Failure, security and verification

Use structured API errors, explicit loading/empty/stale states and trace correlation. Test happy paths plus the failure scenarios in the spec. Redact secrets and scope evidence to permitted knowledge. Commands revalidate server-side; display configuration never grants permissions. Restart/reconnect handling must not fabricate work or duplicate side effects.

## Open product decisions

- Nur Vorschläge/Entwürfe in V1 oder ausdrücklich delegierte risikoarme Experimente?
- Welche Baseline und Erfolgsmetriken sollen Prozessverbesserungen zuerst verwenden?
- Welche Feedback-Zyklen sollen automatisch nach Prozessabschluss starten?

## Governance and boundaries

Status: DRAFT FOR PRODUCT REVIEW. Specification work is authorized; application implementation is not yet authorized. No checked implementation task means a feature has been delivered.

All cross-module DTOs MUST be typed. Business services depend on contracts, with LangGraph behind WorkflowService/engine adapters, Obsidian behind KnowledgeProvider, model calls behind ModelGateway, and external access/actions behind ToolGateway plus PolicyEngine. Consequential actions retain explicit human approval. Runtime state belongs in repositories (SQLite locally, PostgreSQL replaceable later); organizational evidence/knowledge belongs behind KnowledgeProvider. Commands carry stable idempotency identities; retries and uncertain outcomes are explicit. Correlation/run/attempt IDs connect events, traces and evaluations. Task context is bounded and permissions are explicit. No browser filesystem access or provider credentials. Local V1 binds to loopback; SaaS authentication/tenancy is future scope without changing business contracts.
