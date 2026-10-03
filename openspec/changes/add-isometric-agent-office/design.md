# Design: Isometrisches Pixel-Office mit Agenten und Prozessstart

## Product outcome

Die Firma als lebendiges Büro im Stil eines 90er-Jahre-Pixel-Adventures erlebbar machen: Arbeitsplätze, Kaffeepause und Chef als Einstieg in Geschäftsprozesse.

## Proposed decisions

Eigenständige isometrische 2D-Pixelgrafik mit warmem 90er-Adventure-Charakter, eigenen Figuren/Tiles und lesbaren Namenslabels. Alle acht Agenten erhalten stabile Arbeitsplätze; bestätigte idle-Agenten sitzen/stehen in der Kaffeezone, working-Agenten am Tisch. waiting_approval/blocked werden mit eindeutigen Badges gezeigt, unknown/unavailable neutral markiert. Bewegung ist dekorativ und führt niemals Tools oder Arbeit aus. Amancio ist standardmäßig der anklickbare Founder; Klick öffnet denselben Katalog/Formularfluss wie die Abteilungsansicht. Kein Start allein durch Klick auf Figur. Responsive Szene mit Zoom/Pan, Tastaturauswahl, DOM-Liste und reduced-motion. Vorschlag für Performance-Abnahme: 30 FPS bei acht Figuren auf dokumentiertem Referenzgerät; Lasttest mit 50 dargestellten Figuren, ohne den V1-Organisationsumfang zu erweitern.

## Contract sketch (to finalize before implementation)

OfficeLayout(version, tile_size, rooms, desk_assignments, coffee_slots, founder_anchor); OfficeActor(agent_id, activity_state, location, activity_refs); LaunchContext(source=office, initiator_id, process_id).

## Dependency ownership

- add-agent-detail-activity
- add-department-process-catalog
- add-business-process-instances

Shared API shell, repositories, approval service and UI shell belong to build-local-control-plane; provider/policy/tracing abstractions belong to modularize-ai-native-os. This change owns the feature-specific projections, contracts, screens and acceptance tests. Shared work must not be duplicated.

## Failure, security and verification

Use structured API errors, explicit loading/empty/stale states and trace correlation. Test happy paths plus the failure scenarios in the spec. Redact secrets and scope evidence to permitted knowledge. Commands revalidate server-side; display configuration never grants permissions. Restart/reconnect handling must not fabricate work or duplicate side effects.

## Open product decisions

- Ist Amancio die Chef-Figur oder Elena als operative Chefin?
- Gewünschtes visuelles Vorbild: eher gemütliches Büro oder Fantasy-Werkstatt? Originalgrafik bleibt der vorgeschlagene Ansatz.

## Governance and boundaries

Status: DRAFT FOR PRODUCT REVIEW. Specification work is authorized; application implementation is not yet authorized. No checked implementation task means a feature has been delivered.

All cross-module DTOs MUST be typed. Business services depend on contracts, with LangGraph behind WorkflowService/engine adapters, Obsidian behind KnowledgeProvider, model calls behind ModelGateway, and external access/actions behind ToolGateway plus PolicyEngine. Consequential actions retain explicit human approval. Runtime state belongs in repositories (SQLite locally, PostgreSQL replaceable later); organizational evidence/knowledge belongs behind KnowledgeProvider. Commands carry stable idempotency identities; retries and uncertain outcomes are explicit. Correlation/run/attempt IDs connect events, traces and evaluations. Task context is bounded and permissions are explicit. No browser filesystem access or provider credentials. Local V1 binds to loopback; SaaS authentication/tenancy is future scope without changing business contracts.
