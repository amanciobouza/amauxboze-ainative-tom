# Design: Abteilungen und startbare Geschäftsprozesse

## Product outcome

Prozesse über fachliche Abteilungen entdecken und mit verständlichen Eingaben sicher starten.

## Proposed decisions

Eine zentrale Prozessregistrierung wird von Abteilungen, Office und Workflows verwendet. V1 enthält die fünf bestehenden Businessprozesse, keine erfundenen ausführbaren Prozesse. Entwurf: Watch Development→Product; Product Launch→Commerce; Content Campaign→Marketing; Feedback Learning→Customer; Market Intelligence→Intelligence; Operations/Elena koordiniert alle. Formulare unterstützen explizit die tatsächlich benötigten Schemafelder und verständliche Validierung. Freitext kann keine Rechte ausweiten. Product Launch erfordert referenzierte, nachweisbar freigegebene Produktspezifikation; ein Browser-Boolean reicht nicht. Nicht ausführbare/mocked Prozesse werden klar markiert und dürfen nicht als Live-Aktion erscheinen.

## Contract sketch (to finalize before implementation)

Department(id, name, mission, member_ids); ProcessDefinition(id, version, name, description, owner_department_id, participant_department_ids, input_schema, prerequisites, approval_summary, enabled, disabled_reason); StartProcessCommand(process_id, version, input, idempotency_key).

## Dependency ownership

- add-organization-structure
- build-local-control-plane: workflow service, catalog/start API and UI foundation
- modularize-ai-native-os: policy enforcement

Shared API shell, repositories, approval service and UI shell belong to build-local-control-plane; provider/policy/tracing abstractions belong to modularize-ai-native-os. This change owns the feature-specific projections, contracts, screens and acceptance tests. Shared work must not be duplicated.

## Failure, security and verification

Use structured API errors, explicit loading/empty/stale states and trace correlation. Test happy paths plus the failure scenarios in the spec. Redact secrets and scope evidence to permitted knowledge. Commands revalidate server-side; display configuration never grants permissions. Restart/reconnect handling must not fabricate work or duplicate side effects.

## Open product decisions

- Welche Abteilungen und Prozessverantwortlichen willst du bestätigen?
- Welche Prozesse sollen zuerst mit echten Modellen laufen und welche explizit im Simulationsmodus?

## Governance and boundaries

Status: IMPLEMENTATION AUTHORIZED by the founder request to implement the whole app. Scope decisions and shared delivery are recorded in implement-complete-local-app/design.md. Task completion remains evidence-based.

All cross-module DTOs MUST be typed. Business services depend on contracts, with LangGraph behind WorkflowService/engine adapters, Obsidian behind KnowledgeProvider, model calls behind ModelGateway, and external access/actions behind ToolGateway plus PolicyEngine. Consequential actions retain explicit human approval. Runtime state belongs in repositories (SQLite locally, PostgreSQL replaceable later); organizational evidence/knowledge belongs behind KnowledgeProvider. Commands carry stable idempotency identities; retries and uncertain outcomes are explicit. Correlation/run/attempt IDs connect events, traces and evaluations. Task context is bounded and permissions are explicit. No browser filesystem access or provider credentials. Local V1 binds to loopback; SaaS authentication/tenancy is future scope without changing business contracts.
