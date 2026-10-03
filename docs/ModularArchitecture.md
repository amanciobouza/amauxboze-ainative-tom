# Modular Architecture

## Principle

> Everything is replaceable except the contracts and the knowledge.

The Amaux Bozé AI Native TOM/OS is organized into replaceable modules behind stable contracts.

## Modules

1. Control Plane
2. Workflow Engine
3. Agent Runtime
4. Skill Runtime
5. Context Engine
6. Tool Gateway
7. Model Gateway
8. Memory / Knowledge
9. Policy & Approval Engine
10. Observability & Evaluation
11. Event Engine
12. Plugin Registry

## Dependency Rule

Higher-level modules depend on contracts, not concrete implementations.

Examples:
- Workflow Engine depends on ModelGateway, not LM Studio directly.
- Skill Runtime depends on ToolGateway, not Shopify directly.
- Context Engine depends on KnowledgeProvider, not Obsidian directly.
- Control Plane depends on WorkflowService, not LangGraph internals.

## Contract-First Boundaries

All cross-module interactions SHOULD use typed Pydantic models.

Core contracts include:
- AgentDefinition
- SkillDefinition
- WorkflowDefinition
- WorkflowRun
- ApprovalRequest
- ContextRequest
- ContextBundle
- ToolRequest
- ToolResult
- ModelRequest
- ModelResponse
- Observation
- Insight
- Decision
- RuntimeEvent
- TraceSpan

## Plugin Families

Plugins may provide:
- model providers
- tool providers
- knowledge providers
- workflow packs
- agents
- skills
- event sources
- exporters

## Architecture Rule

Business workflows MUST NOT import provider-specific implementations directly.

Provider-specific code belongs behind interfaces in plugin or adapter modules.
