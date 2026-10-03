# Delta for Obsidian Adapter

## ADDED Requirements

### Requirement: Vault-rooted access

The system MUST restrict Obsidian access to the configured vault root.

Configured root:

`C:\Users\amanc\OneDrive\ObsidianVaults\Amaux Bozé`

#### Scenario: Valid vault read
- GIVEN a relative path inside the configured vault
- WHEN an authorized skill requests the document
- THEN the adapter returns its contents

#### Scenario: Path escape attempt
- GIVEN a path that resolves outside the configured vault
- WHEN access is requested
- THEN the adapter MUST reject the request

### Requirement: Controlled writes

Write access MUST be explicitly authorized by agent and skill permissions.

#### Scenario: Read-only skill attempts write
- GIVEN a skill without Obsidian write permission
- WHEN it attempts to modify a note
- THEN the adapter MUST reject the operation

### Requirement: Traceable knowledge updates

Every write MUST record enough metadata to identify the initiating workflow, agent, skill, and timestamp.
