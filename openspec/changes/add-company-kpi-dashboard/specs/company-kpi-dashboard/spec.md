# Delta: Company-Dashboard mit nachvollziehbaren KPIs

## ADDED Requirements

### Requirement: Company landing page

The application MUST open on a dashboard showing operational KPIs, pending approvals, blocked/failed runs, recent learnings and runtime health.

#### Scenario: Default start

- Given persisted runtime data, when the application opens, then the dashboard is the landing route and cards link to the underlying filtered resources.

### Requirement: Auditable metrics

Every KPI MUST expose formula, source, time window, coverage and freshness; aggregation MUST deduplicate run/event identities.

#### Scenario: Duplicate or late event

- Given duplicate events and a late completion, when metrics recalculate, then each run is counted once in the documented timestamp window.

### Requirement: Honest missing data

Unavailable or stale metrics MUST be explicitly marked and MUST NOT be substituted with fabricated values or zero.

#### Scenario: Missing commerce source

- Given no connected commerce metrics provider, when revenue is requested, then unavailable and its reason are shown rather than zero revenue.

### Requirement: Stable time semantics

KPI calculations MUST use defined UTC boundaries with local display and explicit terminal-outcome denominators.

#### Scenario: Empty and boundary window

- Given no terminal runs and events at the exact window boundary, when KPIs are calculated, then the documented half-open interval is applied and an undefined success rate is marked unavailable.

### Requirement: Modular governance

company-kpi-dashboard MUST preserve provider-neutral contracts, human approval, explicit permissions, bounded context, retry/idempotency semantics and traceable evaluation evidence as described in design.md.

#### Scenario: Governed integration

- Given the feature is accessed through any UI route, when a command or provider operation is requested, then the same typed service and policy boundaries apply and the UI does not invoke LangGraph, providers or local filesystem paths directly.
