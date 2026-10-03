# Delta for Skill Registry

## ADDED Requirements

### Requirement: Discoverable versioned skills

The system MUST load reusable skills from a central registry with explicit version and schema metadata.

#### Scenario: Skill discovery
- GIVEN a registered skill
- WHEN an authorized agent requests the capability
- THEN the runtime can locate the skill and its metadata

### Requirement: Structured skill contract

Each skill MUST define inputs, outputs, context requirements, permitted tools, model requirements, and approval behavior.

#### Scenario: Invalid input
- GIVEN an input that does not satisfy the skill schema
- WHEN execution is requested
- THEN the skill MUST not execute and MUST return a validation error

### Requirement: Skills remain model-portable

A skill SHOULD declare capability requirements rather than hard-code a model provider unless provider-specific behavior is required.
