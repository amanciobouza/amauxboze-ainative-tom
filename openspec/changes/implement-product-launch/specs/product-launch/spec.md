# Delta for Product Launch

## ADDED Requirements

### Requirement: Launch requires approved product specification

The system MUST require an approved product specification before Product Launch can begin.

#### Scenario: Missing approved specification
- GIVEN no approved product specification exists
- WHEN Product Launch is requested
- THEN the workflow MUST reject startup

### Requirement: Product Truth Pack

The workflow MUST create a Product Truth Pack before messaging and content are produced.

#### Scenario: Messaging claims product fact
- GIVEN messaging contains a product claim
- WHEN the claim is reviewed
- THEN the claim MUST be supported by the Product Truth Pack

### Requirement: Specialist launch artifacts remain distinct

Messaging, commercial setup, content, support readiness, and market context MUST remain independently retrievable artifacts.

### Requirement: Founder approval before activation

The workflow MUST pause before external activation.

#### Scenario: Founder approves launch
- GIVEN a launch-readiness package exists
- WHEN the founder approves
- THEN activation MAY proceed through authorized tools

#### Scenario: Founder requests revision
- GIVEN a launch-readiness package exists
- WHEN the founder selects revise
- THEN the workflow MUST return to launch preparation

#### Scenario: Founder holds launch
- GIVEN a launch-readiness package exists
- WHEN the founder selects hold
- THEN the workflow enters ON_HOLD

#### Scenario: Founder cancels launch
- GIVEN a launch-readiness package exists
- WHEN the founder selects cancel
- THEN the workflow enters CANCELLED

### Requirement: External actions require authorization

The workflow MUST verify tool permissions before any external publishing or commerce action.

### Requirement: No invented claims

Product, manufacturing, price, certification, and availability claims MUST originate from approved source artifacts.

### Requirement: Post-launch learning

After activation, the workflow MUST support a learning phase that combines commerce, content, customer, and market signals into a persisted launch-learning artifact.

### Requirement: Resume without duplicated activation

If the workflow resumes after interruption, already executed external actions MUST NOT be repeated.
