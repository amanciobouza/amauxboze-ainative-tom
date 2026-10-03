# Delta: Agentendetails, aktuelle Arbeit und Historie

## ADDED Requirements

### Requirement: Profile and capabilities

The detail view MUST display registry-backed role, mission, skills with versions/contracts, explicit permissions and approval boundaries; missing biography MUST be marked unavailable.

#### Scenario: Known and missing profile data

- Given a registered agent with no background text, when details load, then validated identity and skills appear and biography is marked unavailable rather than fabricated.

### Requirement: Truthful current work

Current work MUST derive from authoritative stage lifecycle events and expose concurrent assignments and telemetry freshness.

#### Scenario: Concurrent and stale work

- Given two active assignments and a disconnected event stream, when the view refreshes, then both assignments remain visible and freshness becomes stale/unknown without claiming completion.

### Requirement: Durable history

The system MUST provide paginated execution history with run, skill, outcome, retry and artifact references after restart.

#### Scenario: History after restart

- Given a finished stage and a failed retry recorded before restart, when history is reopened, then both attempts and their linked results remain distinguishable.

### Requirement: Modular governance

agent-detail-activity MUST preserve provider-neutral contracts, human approval, explicit permissions, bounded context, retry/idempotency semantics and traceable evaluation evidence as described in design.md.

#### Scenario: Governed integration

- Given the feature is accessed through any UI route, when a command or provider operation is requested, then the same typed service and policy boundaries apply and the UI does not invoke LangGraph, providers or local filesystem paths directly.
