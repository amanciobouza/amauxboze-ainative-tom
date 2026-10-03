# Design

## Goals

- Stable contracts between modules
- Provider replaceability
- Strict least-privilege tool access
- Minimal context sharing
- Vendor-neutral observability
- Event-driven workflow starts
- Plugin-based extensibility
- Compatibility with local-first and future SaaS deployment

## Core Contracts

### ContextProvider

Input:
- task
- agent
- workflow
- knowledge scopes
- token/context budget

Output:
- ContextBundle

### ToolGateway

Input:
- acting agent
- skill
- requested tool/action
- payload

Responsibilities:
- authorize
- validate
- enforce approval policy
- execute provider
- emit trace/event

### ModelGateway

Input:
- task requirements
- prompt/messages
- privacy policy

Responsibilities:
- select provider/model
- invoke
- normalize output
- record telemetry

### KnowledgeProvider

Operations:
- read
- search
- write
- list
- link

Initial implementation:
- ObsidianKnowledgeProvider

Future:
- database, document store, enterprise connectors

### PolicyEngine

Responsibilities:
- agent-to-skill permission
- skill-to-tool permission
- action approval requirements
- guardrails
- local-only / cloud data policy

### EventEngine

Event envelope:
- event_id
- type
- timestamp
- source
- subject
- payload
- correlation_id

Examples:
- workflow.requested
- approval.requested
- approval.resolved
- customer.feedback.received
- product.approved
- campaign.published
- intelligence.review_due

### Observability

Trace hierarchy:

Workflow Run
→ Agent
→ Skill
→ Model / Tool
→ Result

Required metadata:
- duration
- status
- provider/model
- retries
- approval state
- error
- usage/cost when available

## Plugin Registry

Plugin manifests declare:
- plugin id
- version
- plugin type
- capabilities
- configuration schema
- health check
- factory/entrypoint

Plugin types:
- model_provider
- tool_provider
- knowledge_provider
- event_source
- workflow_pack
- skill_pack

## Context Engineering

Agents MUST NOT receive the whole knowledge base by default.

Context Engine builds a bounded ContextBundle from:
- role context
- workflow state
- selected knowledge
- relevant history
- policy metadata

## Migration Strategy

1. Add contracts without breaking current implementations.
2. Wrap current ModelRouter as ModelGateway implementation.
3. Wrap ObsidianAdapter as KnowledgeProvider.
4. Wrap AuthorizationService + approval logic as PolicyEngine.
5. Add ToolGateway façade.
6. Add ContextEngine.
7. Add EventEngine.
8. Add TraceRecorder interface.
9. Gradually refactor workflows to use interfaces.
