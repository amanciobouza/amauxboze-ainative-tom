# Delta for Workflow Runtime

## ADDED Requirements

### Requirement: LangGraph orchestration

Business workflows MUST be implementable as LangGraph graphs with explicit state transitions.

### Requirement: Durable workflow state

Workflow state MUST be checkpointed so a workflow can resume after interruption or process restart.

### Requirement: Observable execution

Each workflow execution MUST expose:
- workflow identifier
- current state
- participating agents
- executed skills
- model/provider used
- approval status
- errors

### Requirement: Idempotent resume

A resumed workflow MUST avoid repeating completed external side effects.

#### Scenario: Resume after approval interrupt
- GIVEN a workflow paused after preparing an external action
- WHEN approval is received
- THEN only the pending action and subsequent steps execute
