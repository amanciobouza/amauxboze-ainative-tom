# Delta for Agent Registry

## ADDED Requirements

### Requirement: Agent manifests

The system MUST load agent definitions from version-controlled manifests.

#### Scenario: Valid agent manifest
- GIVEN a manifest with required identity, role, permissions, and skill references
- WHEN the registry loads the manifest
- THEN the agent becomes available to workflows

#### Scenario: Invalid agent manifest
- GIVEN a manifest missing a required field or referencing an unknown skill
- WHEN the registry loads the manifest
- THEN loading MUST fail with an actionable validation error

### Requirement: Permission boundaries

Each agent MUST have explicit permissions defining allowed skills and tool access.

#### Scenario: Agent attempts unauthorized skill
- GIVEN an agent that is not permitted to use a skill
- WHEN execution requests that skill
- THEN execution MUST be rejected before the skill runs
