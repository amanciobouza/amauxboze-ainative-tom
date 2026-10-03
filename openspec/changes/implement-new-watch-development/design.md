# Design

## Context

The business process is defined in:

`processes/New-Watch-Development.md`

The workflow must convert that business definition into a deterministic LangGraph implementation without moving business authority into the software layer.

## Goals

- Coordinate all required specialist agents in a fixed business sequence.
- Preserve intermediate artifacts.
- Distinguish evidence, interpretation, recommendation, and decision.
- Pause at founder approval gates.
- Write approved artifacts and decisions to Obsidian.
- Support resume after interruption.
- Make every stage observable.

## Non-Goals

- Autonomous final product approval.
- Autonomous production approval.
- Supplier ordering.
- CAD or 3D asset generation.
- Shopify publishing.

## Workflow State

The workflow state will include:

- workflow_id
- product_working_title
- founder_brief
- constraints
- evidence_pack
- product_concepts
- brand_review
- commercial_review
- customer_review
- integrated_recommendation
- founder_decision
- final_specification
- production_decision
- current_state
- participating_agents
- artifacts
- errors

## Stage Ownership

1. Intent Definition → Elena
2. Evidence Gathering → Nora
3. Product Concept → Lucien
4. Brand Review → Élodie
5. Commercial Review → Marc
6. Customer Perspective → Sophie
7. Integrated Recommendation → Elena
8. Founder Gate → Amancio
9. Final Specification → Lucien
10. Production Approval → Amancio

## Founder Gates

### Gate 1 — Approve for Detailed Specification

Possible outcomes:
- approve
- revise
- hold
- reject

Only `approve` advances to final specification.

### Gate 2 — Production Approval

Possible outcomes:
- approve
- revise
- cancel

Only the founder may approve production.

## Artifact Model

Each stage produces a typed artifact.

Artifacts must include:
- workflow_id
- artifact_type
- created_by
- created_at
- source_inputs
- content
- status

## Obsidian Write Strategy

Draft intermediate artifacts may be written under a workflow-specific workspace.

Suggested target:

`Products/Development/<workflow-id>/`

Final approved records must include:
- decision
- rationale
- alternatives considered
- evidence used
- approver
- date

## Agent Execution

Each stage invokes an explicit skill assigned to the responsible agent.

The workflow runtime MUST authorize:
- agent → skill
- agent → tool
before execution.

## Model Routing

Each skill declares its own model requirements.

The workflow must not hard-code a single model provider.

## Error Handling

A failed stage moves the workflow to an error state with:
- failed stage
- agent
- skill
- error
- recoverability indicator

Recoverable failures may be retried.

## Observability

Every transition must expose:
- workflow id
- previous state
- next state
- agent
- skill
- model provider
- artifact produced
- approval status
