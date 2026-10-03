# Design

## Context

The business process is defined in:

`processes/Product-Launch.md`

The Product Launch workflow begins only after a product has an approved specification.

## Goals

- Preserve product truth from approved specs.
- Create coherent launch messaging and channel content.
- Separate content preparation from external publication.
- Require founder approval before activation.
- Capture launch outcomes and learnings in Obsidian.
- Keep publishing tools replaceable and permission-controlled.

## Non-Goals

- Autonomous price changes.
- Autonomous publication without approval.
- Supplier ordering.
- Inventory planning beyond launch-readiness inputs.
- Full marketing attribution platform.

## Workflow State

The state will include:

- workflow_id
- product_id
- product_specification
- launch_brief
- product_truth_pack
- messaging_framework
- commercial_setup
- content_plan
- support_pack
- market_context
- launch_readiness
- founder_decision
- activation_result
- performance_snapshot
- launch_learning
- current_state
- artifacts
- errors

## Stage Ownership

1. Launch Brief → Elena
2. Product Truth Pack → Lucien
3. Narrative & Messaging → Élodie
4. Commercial Setup → Marc
5. Content Production → Maya
6. Customer & Community Readiness → Sophie
7. Market Context Check → Nora
8. Integrated Launch Review → Elena
9. Founder Gate → Amancio
10. Publish & Activate → Marc / Maya / Sophie through approved tools
11. Post-Launch Learning → Elena with inputs from Marc, Maya, Sophie, Nora

## Approval Gate

The founder gate supports:
- approve
- revise
- hold
- cancel

Only `approve` may advance to activation.

## Activation Boundary

V1 MUST distinguish between:
- prepared launch action
- approved launch action
- executed external action

No external publication may occur without both:
1. founder approval
2. tool permission for the acting agent

## Product Truth

Claims in messaging and content MUST be traceable to the Product Truth Pack.

The workflow MUST not invent:
- specifications
- manufacturing claims
- certification claims
- availability claims
- pricing facts

## Post-Launch Learning

The workflow should capture:
- commerce performance
- content performance
- qualitative customer response
- relevant external market context
- recommended next experiment

## Persistence

Suggested Obsidian workspace:

`Products/Launches/<workflow-id>/`

Approved artifacts and final launch learning must be persisted with trace metadata.
