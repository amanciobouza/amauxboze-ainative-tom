# Delta: Feedback-Zyklen und Retrospektiven-Räume

## ADDED Requirements

### Requirement: Evidence-based retrospective

Retrospectives MUST capture scoped evidence and separate attributed observations, interpretations and improvement proposals.

#### Scenario: Unsupported proposal

- Given an agent proposes a change without supporting evidence, when the review is prepared, then the evidence gap is explicit and the proposal is not presented as an established fact.

### Requirement: Bounded collaborative development

Agent contributions MUST execute through model/context/skill contracts with finite round, context and retry budgets.

#### Scenario: Provider failure or endless discussion

- Given a model fails or the round budget is exhausted, when the cycle advances, then it pauses in a visible recoverable/review state without unbounded calls or cloud fallback for local-only context.

### Requirement: Governed improvements

Improvements MUST have an owner, hypothesis, measurable baseline/target, risk and review decision; consequential implementation MUST require explicit approval and software changes MUST reference OpenSpec.

#### Scenario: Proposed policy/code change

- Given agents draft a change to permissions or code, when a proposal is approved for exploration, then no production change occurs until the separately authorized OpenSpec implementation and policy approvals are satisfied.

### Requirement: Closed measurable loop

Approved experiments MUST record results against baseline, retain evidence through KnowledgeProvider and link follow-up work without recursively spawning cycles.

#### Scenario: Inconclusive experiment and duplicate trigger

- Given an inconclusive experiment and duplicate completion event, when the cycle closes or opens, then the result remains inconclusive and only one retrospective is created for the same trigger identity.

### Requirement: Dedicated room view

A retrospective room MUST expose participants, contributions, review status, improvements and experiments and link to the originating processes.

#### Scenario: Room inspection

- Given an awaiting-review retrospective, when its room opens, then the user can inspect evidence and allowed review decisions; entering the room itself executes no change.

### Requirement: Modular governance

feedback-retrospective-rooms MUST preserve provider-neutral contracts, human approval, explicit permissions, bounded context, retry/idempotency semantics and traceable evaluation evidence as described in design.md.

#### Scenario: Governed integration

- Given the feature is accessed through any UI route, when a command or provider operation is requested, then the same typed service and policy boundaries apply and the UI does not invoke LangGraph, providers or local filesystem paths directly.
