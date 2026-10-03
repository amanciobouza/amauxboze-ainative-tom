# Proposal

## Why

Amaux Bozé needs a stable technical foundation for operating a small AI-native company with multiple specialized agents, reusable skills, persistent company knowledge, multiple interchangeable LLM providers, and human approval for consequential actions.

The current business organization and workflows are documented, but there is no runtime contract defining how agents are registered, how skills are discovered and executed, how Obsidian is accessed, how models are selected, how approvals interrupt workflows, or how LangGraph persists execution state.

## What Changes

Introduce a shared AI operating platform with six foundational capabilities:

1. Agent Registry
2. Skill Registry
3. Obsidian Knowledge Adapter
4. Model Router
5. Human Approval Gates
6. LangGraph Workflow Runtime

The platform will provide common infrastructure for later business workflows such as New Watch Development, Product Launch, Content Campaign, Customer Feedback → Learning, and Market Intelligence → Strategic Insight.

## Capabilities

### New Capabilities

- **agent-registry** — load and validate agent roles, responsibilities, permissions, and allowed skills.
- **skill-registry** — discover, validate, version, and execute reusable skills.
- **obsidian-adapter** — controlled read/write access to the Amaux Bozé Obsidian vault.
- **model-router** — select LM Studio, OpenAI, or Anthropic based on task requirements and policy.
- **approval-gates** — pause consequential actions until explicit human approval.
- **workflow-runtime** — execute LangGraph workflows with durable state and observable transitions.

## Impact

This change establishes shared architecture and contracts but does not yet implement the five business workflows. Those will be separate OpenSpec changes built on top of this foundation.
