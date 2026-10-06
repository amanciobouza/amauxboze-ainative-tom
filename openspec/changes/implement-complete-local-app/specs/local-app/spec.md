## ADDED Requirements

### Requirement: Complete local application
The application SHALL expose all features in the control-plane and seven related feature proposals with the scope decisions recorded in this change.

#### Scenario: Local startup
- WHEN the user starts the local launcher
- THEN a loopback API and browser application expose dashboard, office, organization, departments, agents, skills, processes, approvals, knowledge, models, settings and retrospective rooms
- AND empty/unconfigured resources display their real status

### Requirement: Durable governed execution
The five business processes SHALL use persistent checkpoints, ordered events, typed metadata and revision-aware explicit commands.

#### Scenario: Restart at gate
- WHEN a run awaits founder approval and the API restarts
- THEN its existing gate resumes from its checkpoint without repeating completed model stages
- AND an outdated or duplicate decision cannot resume it twice

#### Scenario: Simulation and live
- WHEN simulation is selected
- THEN all artifacts and runs are labeled simulation and external actions and vault writes are suppressed
- WHEN live mode lacks a publishing adapter
- THEN the limitation is explicit and publication is never claimed

### Requirement: Explicit model routing
Live model calls SHALL use the provider-neutral gateway with explicit selected provider and model and SHALL NOT fall back from local to cloud.

#### Scenario: Local outage
- WHEN LM Studio is unavailable for a local-only task
- THEN execution pauses with an actionable error without using a configured cloud key

### Requirement: Safe knowledge and prerequisites
Knowledge access SHALL enforce the configured root and bounded content. Product launches SHALL resolve approved specification provenance from server-side state.

#### Scenario: Forged client data
- WHEN a caller supplies a traversal path or a claimed approval boolean without trusted run evidence
- THEN the request fails without a read, write or run creation

### Requirement: Bounded learning loops
Retrospectives SHALL retain attributed evidence and reviewed measurable experiments with finite model/context budgets, explicit knowledge export and no automatic production edits.

#### Scenario: Inconclusive result
- WHEN experiment evidence cannot establish improvement
- THEN evaluation records inconclusive and its rationale without launching another cycle

### Requirement: Accessible honest projections
Office activity and KPIs SHALL derive from persisted runtime evidence, with unknown/stale and unavailable values represented explicitly and an accessible list alternative.

#### Scenario: No commerce source
- WHEN the dashboard opens without a commerce connector
- THEN revenue and orders display unavailable with their reason rather than zero
