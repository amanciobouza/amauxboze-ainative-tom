# Design: Organisation und Agentenstruktur

## Product outcome

Die reale Verantwortungsstruktur der Firma sichtbar machen und Menschen, Agenten, Abteilungen und Koordination eindeutig unterscheiden.

## Proposed decisions

Registry-IDs bleiben stabil. Amancio ist ein Mensch und kein ausführender Agent. Entwurf: flache Berichtslinie aller acht Agenten zu Amancio; Elena koordiniert, ohne dadurch zusätzliche Freigaberechte zu erhalten. Das heutige ASCII-Organigramm ist mehrdeutig und darf nicht als neue Berechtigungsquelle dienen. Abteilungen gruppieren Verantwortung, ändern aber keine Toolrechte. Read-only V1; Rollen-/Rechte-Editing ist ausgeschlossen.

## Contract sketch (to finalize before implementation)

OrganizationNode(id, kind=human|agent|department, display_name, role, mission, parent_id, department_ids, registry_ref); OrganizationRelation(source_id, target_id, kind=reports_to|coordinates|member_of).

## Dependency ownership

- modularize-ai-native-os
- build-local-control-plane: registries, API and UI foundation

Shared API shell, repositories, approval service and UI shell belong to build-local-control-plane; provider/policy/tracing abstractions belong to modularize-ai-native-os. This change owns the feature-specific projections, contracts, screens and acceptance tests. Shared work must not be duplicated.

## Failure, security and verification

Use structured API errors, explicit loading/empty/stale states and trace correlation. Test happy paths plus the failure scenarios in the spec. Redact secrets and scope evidence to permitted knowledge. Commands revalidate server-side; display configuration never grants permissions. Restart/reconnect handling must not fabricate work or duplicate side effects.

## Open product decisions

- Ist die flache Berichtslinie zu Amancio korrekt?
- Sind Marketing, Operations, Product, Intelligence, Commerce, Customer und Technology die gewünschten Abteilungen?

## Governance and boundaries

Status: DRAFT FOR PRODUCT REVIEW. Specification work is authorized; application implementation is not yet authorized. No checked implementation task means a feature has been delivered.

All cross-module DTOs MUST be typed. Business services depend on contracts, with LangGraph behind WorkflowService/engine adapters, Obsidian behind KnowledgeProvider, model calls behind ModelGateway, and external access/actions behind ToolGateway plus PolicyEngine. Consequential actions retain explicit human approval. Runtime state belongs in repositories (SQLite locally, PostgreSQL replaceable later); organizational evidence/knowledge belongs behind KnowledgeProvider. Commands carry stable idempotency identities; retries and uncertain outcomes are explicit. Correlation/run/attempt IDs connect events, traces and evaluations. Task context is bounded and permissions are explicit. No browser filesystem access or provider credentials. Local V1 binds to loopback; SaaS authentication/tenancy is future scope without changing business contracts.
