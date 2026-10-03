# Delta for Approval Gates

## ADDED Requirements

### Requirement: Consequential-action approval

The runtime MUST require explicit human approval before configured consequential actions.

Consequential actions include at minimum:
- publishing external content
- changing a product price
- approving production
- sending consequential customer communication

#### Scenario: Action reaches approval gate
- GIVEN a workflow reaches a consequential action
- WHEN no approval exists
- THEN execution MUST pause before the action

#### Scenario: Approved action resumes
- GIVEN a paused workflow with a valid approval
- WHEN execution resumes
- THEN the workflow proceeds from the approval point without repeating completed side effects

#### Scenario: Rejected action
- GIVEN a paused workflow
- WHEN the founder rejects the action
- THEN the workflow MUST follow its rejection or revision path
