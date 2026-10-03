# Design

## Context

The business process is defined in:

`processes/Customer-Feedback-Learning.md`

## Goals

- Normalize raw feedback into a structured observation.
- Separate individual feedback from validated patterns.
- Route implications to the correct functional owner.
- Prioritize issues consistently.
- Require founder approval when changes affect product, pricing, brand principles, public commitments, or material operating policy.
- Persist both raw signals and synthesized learning.

## Non-Goals

- Autonomous refunds or compensation.
- Autonomous changes to product specs or pricing.
- Automatic public commitments.
- Full CRM implementation.

## Workflow State

The state will include:

- workflow_id
- source
- raw_feedback
- customer_context
- classified_feedback
- response_requirement
- response_draft
- pattern_analysis
- functional_implications
- prioritization
- founder_decision
- learning_record
- current_state
- error/retry metadata

## Stage Ownership

1. Intake → Sophie
2. Classification → Sophie
3. Immediate Response Need → Sophie
4. Pattern Detection → Nora
5. Functional Routing → Lucien / Élodie / Marc / Maya
6. Prioritization → Elena
7. Founder Gate → Amancio when consequential
8. Learning Capture → Sophie

## Consequential Change Detection

Founder approval is required if proposed action changes:
- product specification
- pricing
- brand principles
- public commitments
- material operating policy

## Persistence

Suggested Obsidian workspace:

`Customers/Feedback/<workflow-id>/`

Persist:
- raw observation
- classification
- response draft when applicable
- pattern analysis
- functional implications
- prioritization
- founder decision when required
- learning record
