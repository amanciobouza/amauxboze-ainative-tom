# Delta: Organisation und Agentenstruktur

## ADDED Requirements

### Requirement: Canonical organization

The system MUST project organization data from validated configuration and agent/skill registries without maintaining a separate frontend authority.

#### Scenario: Valid organization

- Given Amancio and the eight registered agents, when the organization is opened, then every identity appears once with its type, mission, department membership and explicit reporting/coordination relationships.

### Requirement: Safe hierarchy

The organization model MUST reject duplicate identities, cycles and unresolved references.

#### Scenario: Invalid hierarchy

- Given a cyclic or unresolved organization configuration, when it is loaded, then a structured diagnostic is returned and the UI does not invent a valid hierarchy.

### Requirement: Navigable accessible view

The UI MUST offer a keyboard-accessible hierarchy/list and link each agent to its detail page.

#### Scenario: Agent navigation

- Given an agent selected by keyboard or pointer, when details are requested, then the same stable agent ID is opened without changing any permissions.

### Requirement: Modular governance

organization-structure MUST preserve provider-neutral contracts, human approval, explicit permissions, bounded context, retry/idempotency semantics and traceable evaluation evidence as described in design.md.

#### Scenario: Governed integration

- Given the feature is accessed through any UI route, when a command or provider operation is requested, then the same typed service and policy boundaries apply and the UI does not invoke LangGraph, providers or local filesystem paths directly.
