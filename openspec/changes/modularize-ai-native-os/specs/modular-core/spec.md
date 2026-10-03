# Delta for Modular Core

## ADDED Requirements

### Requirement: Contract-based modules

Core business workflows MUST depend on stable interfaces rather than provider-specific implementations.

### Requirement: Minimal context

The Context Engine MUST provide only task-relevant context by default.

### Requirement: Tool mediation

External tool calls MUST pass through a Tool Gateway.

### Requirement: Policy enforcement

The Tool Gateway MUST consult the Policy Engine before consequential or restricted actions.

### Requirement: Provider-neutral models

Business workflows MUST invoke models through the Model Gateway.

### Requirement: Provider-neutral knowledge

Business workflows MUST access organizational knowledge through a Knowledge Provider interface.

### Requirement: Event-driven triggers

The system MUST support workflow initiation from typed events in addition to direct user commands.

### Requirement: Traceability

Every workflow run MUST be traceable across agent, skill, model, tool, approval, and error boundaries.

### Requirement: Plugin discovery

Replaceable providers MUST be registerable through a Plugin Registry.

### Requirement: Backward-compatible migration

Existing V1 workflows MUST continue to function during incremental migration to the modular interfaces.
