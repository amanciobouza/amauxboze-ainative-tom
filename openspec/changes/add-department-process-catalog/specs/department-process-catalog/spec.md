# Delta: Abteilungen und startbare Geschäftsprozesse

## ADDED Requirements

### Requirement: Department process discovery

Departments MUST show missions, members and a shared versioned catalog of owned and participating processes.

#### Scenario: Cross-functional process

- Given Product Launch belongs to Commerce and involves Marketing and Customer, when departments are browsed, then each references the same process definition rather than a duplicate implementation.

### Requirement: Validated explicit start

Starting a process MUST validate its registered input schema, prerequisites and permissions server-side and require an explicit command.

#### Scenario: Invalid and repeated submission

- Given invalid input or missing prerequisites, when start is submitted, then no run is created; repeating the same valid idempotency key returns the same run.

### Requirement: Approved product provenance

Product Launch MUST resolve approval evidence from trusted persisted state rather than accepting client-provided approval assertions.

#### Scenario: Forged approval

- Given a client marks an unapproved specification as approved, when Product Launch is requested, then the backend rejects it with a structured prerequisite error.

### Requirement: Honest executable catalog

Disabled, unavailable or simulation-only processes MUST expose a reason and execution mode.

#### Scenario: Unavailable model/provider

- Given a process cannot execute in its configured mode, when the catalog is displayed, then its limitation is visible and a live execution is not silently replaced by a mock.

### Requirement: Modular governance

department-process-catalog MUST preserve provider-neutral contracts, human approval, explicit permissions, bounded context, retry/idempotency semantics and traceable evaluation evidence as described in design.md.

#### Scenario: Governed integration

- Given the feature is accessed through any UI route, when a command or provider operation is requested, then the same typed service and policy boundaries apply and the UI does not invoke LangGraph, providers or local filesystem paths directly.
