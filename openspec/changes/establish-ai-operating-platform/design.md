# Design

## Context

See proposal.md — Why.

Amaux Bozé uses:
- Obsidian as business knowledge and organizational memory
- GitHub as technical source control
- LangGraph as workflow orchestration
- LM Studio at `http://127.0.0.1:1234` for local models
- OpenAI and Anthropic as optional external model providers

The design must preserve separation between business knowledge and runtime implementation.

## Goals

- Make agents and skills declarative and inspectable.
- Keep models interchangeable.
- Keep company knowledge persistent outside model context.
- Support human-in-the-loop approval.
- Allow workflows to resume after interruption.
- Keep external actions permission-controlled.
- Make runtime behavior observable and testable.

## Non-Goals

- Implement business-specific workflows in this change.
- Automatically publish social content.
- Automatically approve prices or production.
- Replace Obsidian with a database.
- Introduce a vector database in V1.
- Build a full web UI in V1.

## Decisions

### 1. Python as the primary runtime

LangGraph orchestration and adapters will be implemented in Python.

Rationale:
- strong LangGraph ecosystem support
- straightforward integration with local and cloud LLM APIs
- suitable for file-based Obsidian integration
- simple testability

### 2. Declarative agent profiles

Runtime agent definitions will live in GitHub as structured files derived from the organizational role definitions.

The registry will validate:
- identity
- role
- mission
- allowed skills
- tool permissions
- approval boundaries

Business descriptions remain in Obsidian; runtime manifests remain in GitHub.

### 3. Declarative skill manifests

Each skill will have:
- metadata
- input schema
- output schema
- required context
- allowed tools
- model requirements
- approval requirements
- evaluation fixtures

Skills will not hard-code a specific LLM unless technically required.

### 4. Adapter boundary for Obsidian

The vault path is configured centrally:

`C:\Users\amanc\OneDrive\ObsidianVaults\Amaux Bozé`

Agents will not manipulate arbitrary filesystem paths. They will use an Obsidian adapter enforcing an allowed vault root and read/write policy.

### 5. Provider-neutral model router

The router will expose a common interface and support:
- LM Studio
- OpenAI
- Anthropic

Routing inputs may include:
- privacy requirement
- reasoning complexity
- creativity requirement
- latency preference
- cost preference
- model availability

Local-only requirements must never fall back silently to a cloud provider.

### 6. Explicit approval interrupts

Consequential actions will trigger a workflow interrupt.

Examples:
- publish externally
- change price
- approve production
- send consequential customer communication

Approval state becomes part of workflow state so execution can resume deterministically.

### 7. Durable workflow state

LangGraph state must be checkpointed using a persistent store suitable for local development and later migration.

Initial implementation may use a local development store, but the abstraction must support PostgreSQL for durable production use.

### 8. No vector database in V1

Obsidian Markdown files remain directly addressable by path, metadata, tags, and controlled search.

A vector database may be added later only if retrieval quality or scale requires it.

## Risks / Trade-offs

- **Local path coupling** → keep the path in central configuration and behind an adapter.
- **Multiple model providers increase variability** → normalize prompts, schemas, and evaluations at skill level.
- **Human gates slow automation** → intentional during early governance; delegation can be expanded later.
- **File-based knowledge can create concurrency issues** → serialize writes and use atomic file operations.
- **Local LM Studio availability is not guaranteed** → expose health checks and explicit provider fallback policies.

## Migration Plan

1. Add foundation modules and tests.
2. Add manifests for existing agents.
3. Add first skills.
4. Connect Obsidian read-only.
5. Add controlled write support.
6. Add model providers.
7. Add approval interrupt support.
8. Add workflow persistence.
9. Validate foundation before business workflow implementation.

## Open Questions

- Which persistent checkpoint backend will be used after local development: PostgreSQL directly or a LangGraph-supported abstraction?
- Which initial local models in LM Studio should be mapped to low-cost, reasoning, coding, and creative task classes?
