# Design

## Context

The business process is defined in:

`processes/Content-Campaign.md`

## Goals

- Turn campaign intent into a reusable structured brief.
- Keep message architecture separate from channel execution.
- Validate audience relevance and factual support before publication.
- Align content with commercial intent without reducing all content to conversion copy.
- Require founder approval before external publication.
- Persist campaign artifacts and learning in Obsidian.

## Non-Goals

- Autonomous public publishing without approval.
- Paid media buying.
- Full attribution modeling.
- Asset rendering or video generation in V1.

## Workflow State

The state will include:

- workflow_id
- campaign_objective
- audience
- campaign_brief
- message_architecture
- audience_evidence
- channel_strategy
- commercial_alignment
- content_package
- brand_review
- founder_decision
- publish_result
- performance_snapshot
- campaign_learning
- current_state
- error/retry metadata

## Stage Ownership

1. Campaign Objective → Elena
2. Message Architecture → Élodie
3. Audience & Evidence Check → Sophie + Nora
4. Channel Strategy → Maya
5. Commercial Alignment → Marc
6. Content Production → Maya
7. Brand Review → Élodie
8. Founder Gate → Amancio
9. Publish → Maya through authorized channel tools
10. Performance Review → Maya / Marc / Sophie / Nora
11. Learning Capture → Elena

## Founder Gate

Allowed decisions:
- approve
- revise
- hold
- cancel

Only `approve` may advance to publication.

## Publishing Boundary

Publication MUST require:
1. founder approval
2. agent action permission
3. an idempotency key to prevent duplicate publication on resume

## Evidence Boundary

Factual claims that depend on external or product facts MUST be traceable to source artifacts.

## Persistence

Suggested Obsidian workspace:

`Brand/Campaigns/<workflow-id>/`

Persist:
- campaign brief
- message architecture
- evidence
- channel strategy
- commercial alignment
- content package
- brand review
- founder decision
- publish result
- campaign learning
