# Design

## Context

The business process is defined in:

`processes/Market-Intelligence-Strategic-Insight.md`

## Goals

- Separate evidence, observation, pattern, interpretation, insight, and decision.
- Preserve source/date/geography/confidence metadata.
- Support repeated research on the same topic over time.
- Detect meaningful change across observations.
- Collect functional interpretations without overwriting facts.
- Require founder direction for strategic action.
- Persist history in Obsidian.

## Non-Goals

- Fully autonomous strategic decisions.
- Predictive market forecasting in V1.
- Social listening at scale.
- A dedicated vector database in V1.

## Workflow State

The state will include:

- workflow_id
- research_question
- watch_topic
- geography
- evidence_pack
- observations
- pattern_analysis
- product_interpretation
- brand_interpretation
- commercial_interpretation
- customer_interpretation
- strategic_insight
- founder_decision
- knowledge_update
- current_state
- error/retry metadata

## Stage Ownership

1. Research Question → Nora
2. Evidence Collection → Nora
3. Observation Capture → Nora
4. Pattern / Change Detection → Nora
5. Product Interpretation → Lucien
6. Brand Interpretation → Élodie
7. Commercial Interpretation → Marc
8. Customer Interpretation → Sophie
9. Strategic Synthesis → Nora + Elena
10. Founder Decision → Amancio
11. Knowledge Update → Nora

## Evidence Model

Each observation must contain:
- statement
- source reference
- observed date
- geography / market
- confidence
- tags

Interpretation MUST NOT mutate the observation record.

## Founder Decision

Allowed outcomes:
- act
- investigate_further
- monitor
- archive

## Persistence

Suggested Obsidian workspace:

`Research/Intelligence/<workflow-id>/`

Persist:
- research question
- evidence pack
- observations
- pattern analysis
- each functional interpretation
- strategic insight
- founder decision
- follow-up condition
