## ADDED Requirements

### Requirement: Profile-aware business stage execution
The system SHALL provide a model stage executor compatible with all five existing business workflow callback interfaces. It SHALL load current registered guidance, enforce skill permission and schemas, and invoke the provider-neutral Model Gateway using skill routing requirements. It SHALL NOT execute tools or grant approvals.

#### Scenario: Elena executes a business skill
- WHEN the profile-aware executor is injected into a business workflow and Elena's stage runs
- THEN the model prompt includes her current communication instructions, the task input and skill output schema
- AND communication instructions do not change the validated task payload

#### Scenario: Unauthorized skill or invalid output
- WHEN skill access is denied or the model returns invalid JSON or a schema-invalid object
- THEN execution fails without accepting an artifact or bypassing workflow approval

### Requirement: Declarative communication guidance
Agent manifests SHALL support typed optional communication instructions with an empty default.

#### Scenario: Existing profile without instructions
- WHEN an existing agent manifest omits communication instructions
- THEN the manifest loads with an empty instruction list

### Requirement: Elena's direct operating style
Elena SHALL use original blunt, evidence-led, outcome-focused guidance, challenge unsupported claims including the founder's, and retain existing approval boundaries.

#### Scenario: Weak plan or missing evidence
- WHEN Elena reviews a plan lacking measurable outcomes or supporting evidence
- THEN her guidance requires an explicit verdict, the evidence gap and a concrete next step
- AND prohibits invented numbers, personal insults and unauthorized commitments

### Requirement: Foundation prompt uses registered guidance
The foundation workflow SHALL include the registered agent's communication instructions in its decision prompt while preserving skill schemas and human approval.

#### Scenario: Decision brief generation
- WHEN the foundation workflow invokes its model executor
- THEN the prompt includes Elena's registered instructions
- AND the resulting decision still awaits founder approval
