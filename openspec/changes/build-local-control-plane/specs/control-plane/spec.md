# Delta for Local Control Plane

## ADDED Requirements

### Requirement: Single application control plane

The system MUST expose normal AI-native company operations through one local web application.

### Requirement: Local browser operation

The application MUST be usable through a browser on the local machine without requiring a cloud deployment.

### Requirement: Workflow management

The application MUST allow the user to start supported workflows and inspect their current state.

### Requirement: Human approval inbox

Pending LangGraph approval interrupts MUST be visible and actionable from a central approval inbox.

### Requirement: Workflow resume

Submitting an approval or recovery action through the application MUST resume the corresponding persisted workflow.

### Requirement: Agent organization view

The application MUST expose the defined agent hierarchy, roles, permissions and assigned skills.

### Requirement: Skill registry view

The application MUST expose skill contracts and versions.

### Requirement: Knowledge access

The application MUST provide controlled read access to the configured Obsidian vault through the backend.

### Requirement: Local model visibility

The application MUST display LM Studio connectivity and available local models.

### Requirement: Persistent runtime state

Workflow run metadata and approval state MUST survive application restarts.

### Requirement: SaaS-compatible boundaries

The UI MUST communicate with the runtime through an API boundary rather than directly importing backend implementation code.
