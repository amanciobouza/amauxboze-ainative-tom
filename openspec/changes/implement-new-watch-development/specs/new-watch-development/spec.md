# Delta for New Watch Development

## ADDED Requirements

### Requirement: End-to-end watch development workflow

The system MUST implement New Watch Development as a LangGraph workflow with explicit stages matching the approved business process.

#### Scenario: Workflow starts from founder brief
- GIVEN a valid founder brief
- WHEN a new workflow is started
- THEN the workflow enters Intent Definition
- AND assigns Elena as the responsible agent

### Requirement: Evidence before concept

The workflow MUST complete Evidence Gathering before Product Concept begins.

#### Scenario: Research not complete
- GIVEN no evidence pack exists
- WHEN Product Concept execution is requested
- THEN the workflow MUST not advance

### Requirement: Specialist reviews remain distinct

Brand, commercial, and customer reviews MUST be stored as separate artifacts.

#### Scenario: Integrated recommendation is prepared
- GIVEN product concept, brand review, commercial review, and customer review exist
- WHEN Elena prepares the integrated recommendation
- THEN each source artifact remains independently retrievable

### Requirement: Founder gate before final specification

The workflow MUST pause for founder approval before detailed specification.

#### Scenario: Founder approves
- GIVEN an integrated recommendation
- WHEN the founder selects approve
- THEN the workflow advances to Final Product Specification

#### Scenario: Founder requests revision
- GIVEN an integrated recommendation
- WHEN the founder selects revise
- THEN the workflow returns to the appropriate revision stage

#### Scenario: Founder rejects
- GIVEN an integrated recommendation
- WHEN the founder selects reject
- THEN the workflow enters REJECTED

### Requirement: Founder-only production approval

Production approval MUST require a separate founder gate.

#### Scenario: Production approved
- GIVEN a completed final product specification
- WHEN the founder explicitly approves production
- THEN the workflow enters APPROVED_FOR_PRODUCTION

### Requirement: Durable knowledge capture

Approved decisions MUST be written to Obsidian with traceable metadata.

#### Scenario: Product approved
- GIVEN founder approval
- WHEN the decision is persisted
- THEN the record includes workflow id, decision, rationale, evidence references, approver, and timestamp

### Requirement: Model portability

The workflow MUST invoke skills through the model router rather than directly binding stages to a single model provider.

### Requirement: Resume after interruption

The workflow MUST resume from founder gates without re-running already completed specialist stages.
