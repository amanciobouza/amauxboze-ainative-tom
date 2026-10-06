# Delta: Laufende Prozessinstanzen, Freigaben und Wiederaufnahme

## ADDED Requirements

### Requirement: Run overview and detail

The UI MUST expose filterable paginated run instances with stage, responsible agents, timestamps, artifacts, approval, retries, errors and permitted commands.

#### Scenario: Run inspection

- Given running, held and failed instances, when filtered or opened, then their actual states and permitted actions appear without changing runtime state.

### Requirement: Durable resume

Workflow checkpoints, pending approvals and execution metadata MUST survive restart behind repository/engine abstractions.

#### Scenario: Restart at approval

- Given a persisted approval interrupt, when the application restarts and a valid decision is submitted, then the matching checkpoint resumes without repeating completed stages.

### Requirement: Approval concurrency

Approval decisions MUST validate allowed decisions and current run revision atomically.

#### Scenario: Stale decision

- Given an approval has already been resolved, when a second or outdated decision is submitted, then it is rejected or returns its recorded outcome without resuming twice.

### Requirement: Reliable recovery and streaming

The system MUST replay ordered persisted events on reconnect and prevent duplicate consequential actions during recovery.

#### Scenario: Uncertain side effect

- Given an action may have succeeded before checkpoint persistence failed, when recovery is requested, then reconciliation is required unless provider idempotency or recorded outcome proves a safe retry.

### Requirement: Modular governance

business-process-instances MUST preserve provider-neutral contracts, human approval, explicit permissions, bounded context, retry/idempotency semantics and traceable evaluation evidence as described in design.md.

#### Scenario: Governed integration

- Given the feature is accessed through any UI route, when a command or provider operation is requested, then the same typed service and policy boundaries apply and the UI does not invoke LangGraph, providers or local filesystem paths directly.
