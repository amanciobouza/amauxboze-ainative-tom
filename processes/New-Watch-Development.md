# New Watch Development

## Purpose

Turn founder intent or an identified opportunity into a technically feasible, commercially coherent, brand-aligned Amaux Bozé watch concept ready for production approval.

## Trigger

The process starts when one of the following occurs:
- Founder requests a new watch or collection
- Market Intelligence identifies a relevant opportunity
- An existing collection requires an extension
- Customer or commercial signals justify a new concept

## Process Owner

**Lucien — Head of Product & Watch Design**

## Final Approver

**Amancio — Founder**

## Participating Agents

- Elena — coordination and decision preparation
- Nora — market and competitor evidence
- Lucien — product concept and technical specification
- Élodie — brand and narrative fit
- Marc — commercial and pricing perspective
- Sophie — customer insight
- Kai — only when tooling, automation, or technical workflow support is required

## Workflow

### 1. Intent Definition
Owner: Elena

Inputs:
- Founder brief
- Existing strategic priorities
- Relevant prior decisions

Outputs:
- Product development brief
- Goals
- Constraints
- Open questions

Gate:
- Founder confirms intent when the brief materially changes strategic scope

### 2. Evidence Gathering
Owner: Nora

Inputs:
- Product development brief
- Competitor landscape
- Watch category trends
- Customer and pricing signals

Outputs:
- Evidence pack
- Relevant observations
- Market constraints
- Opportunity hypotheses

Rule:
Research provides evidence, not final product decisions.

### 3. Product Concept
Owner: Lucien

Inputs:
- Product development brief
- Evidence pack
- Existing collection architecture
- Technical constraints

Outputs:
- Concept options
- Movement recommendation
- Case/dial/hands direction
- Initial specification
- Feasibility notes

### 4. Brand & Narrative Review
Owner: Élodie

Inputs:
- Product concepts
- Brand principles
- Existing collection narrative

Outputs:
- Brand-fit assessment
- Naming directions
- Narrative opportunities
- Conflicts or dilution risks

### 5. Commercial Review
Owner: Marc

Inputs:
- Product concept
- Indicative BOM / manufacturing assumptions
- Market evidence
- Target price

Outputs:
- Pricing recommendation
- Commercial risks
- Positioning implications
- Launch feasibility

### 6. Customer Perspective
Owner: Sophie

Inputs:
- Concept
- Customer feedback
- Review patterns
- Community signals

Outputs:
- Customer relevance assessment
- Potential objections
- Language customers are likely to understand or misunderstand

### 7. Integrated Recommendation
Owner: Elena

Inputs:
- Product concept
- Brand review
- Commercial review
- Customer perspective
- Market evidence

Outputs:
- Decision brief
- Open trade-offs
- Recommendation options
- Risks

### 8. Founder Gate
Owner: Amancio

Possible outcomes:
- Approve for detailed specification
- Revise
- Hold
- Reject

### 9. Final Product Specification
Owner: Lucien

Outputs:
- Final watch specification
- Supplier brief
- Design constraints
- Open production assumptions

### 10. Production Approval
Owner: Amancio

Outcome:
- Approved for sourcing / production
- Returned for revision
- Cancelled

## State Model

```text
IDEA
→ BRIEFED
→ RESEARCHED
→ CONCEPTED
→ BRAND_REVIEWED
→ COMMERCIAL_REVIEWED
→ CUSTOMER_REVIEWED
→ DECISION_READY
→ APPROVED_FOR_SPEC
→ SPEC_COMPLETE
→ APPROVED_FOR_PRODUCTION
```

Alternative terminal states:
- ON_HOLD
- REJECTED
- CANCELLED

## Required Artifacts

- Product Development Brief
- Market Evidence Pack
- Product Concept
- Brand Fit Review
- Commercial Review
- Customer Perspective
- Decision Brief
- Final Product Specification
- Production Approval Record

## Knowledge Capture

All meaningful product decisions must record:
- What was decided
- Why
- What alternatives were considered
- What evidence informed the decision
- Who approved it
- Date of decision

These records belong in Obsidian.

## Automation Boundary

LangGraph may coordinate the workflow, invoke approved skills, collect outputs, persist state, and pause at human gates.

LangGraph must not:
- approve production
- change final pricing
- publish a product
- alter brand principles
without explicit founder approval.
