# Delta: Isometrisches Pixel-Office mit Agenten und Prozessstart

## ADDED Requirements

### Requirement: Office identity and layout

The office MUST show a distinct desk for each registered agent, a coffee area and a clearly identified human founder using original pixel-art assets.

#### Scenario: Initial office

- Given the eight V1 agents, when the office opens, then every actor maps to the same registry identity as the organization and detail views.

### Requirement: Activity-driven representation

Actor placement MUST reflect authoritative activity state; decorative animations MUST NOT modify runtime state.

#### Scenario: Idle and uncertain activity

- Given one working, one confirmed idle and one stale agent, when the projection updates, then they appear at desk, coffee area and neutral unknown state respectively, without generating runtime commands.

### Requirement: Safe founder launch

Selecting the founder MUST open the shared process launcher and MUST require validated input and an explicit start command.

#### Scenario: Founder selection

- Given the founder is selected, when a user browses a process then closes the form, then no workflow starts; submitting valid input starts one run through WorkflowService.

### Requirement: Accessible resilient scene

The same agent selection and process launching MUST be available through a keyboard-accessible DOM alternative and reduced-motion mode.

#### Scenario: Graphics or stream failure

- Given rendering is unavailable or the stream disconnects, when the office is visited, then the list alternative remains usable and stale activity is visibly labeled.

### Requirement: Modular governance

isometric-agent-office MUST preserve provider-neutral contracts, human approval, explicit permissions, bounded context, retry/idempotency semantics and traceable evaluation evidence as described in design.md.

#### Scenario: Governed integration

- Given the feature is accessed through any UI route, when a command or provider operation is requested, then the same typed service and policy boundaries apply and the UI does not invoke LangGraph, providers or local filesystem paths directly.
