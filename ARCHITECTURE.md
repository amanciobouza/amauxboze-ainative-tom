# Architecture

## Amaux Bozé AI Native TOM/OS

Amaux Bozé is being designed as a modular, local-first AI-native company operating system that can later evolve into a SaaS product.

The architecture separates organizational responsibility, reusable capabilities, orchestration, model intelligence, tools, policy, context, knowledge, events, and observability.

## High-Level Architecture

```text
                    CONTROL PLANE
                         │
         ┌───────────────┼───────────────┐
         │               │               │
   Workflow Engine   Organization    Event Engine
         │               │               │
         └──────────┬────┴─────┬─────────┘
                    │          │
                  Agents    Policy Engine
                    │
                  Skills
                    │
              Context Engine
                    │
          ┌─────────┴─────────┐
          │                   │
     Tool Gateway        Model Gateway
          │                   │
        Plugins       LM Studio / Cloud LLMs
          │
     Integrations

             Memory / Knowledge
        Obsidian + Runtime State

          Observability / Evals
```

## Core Modules

1. **Control Plane** — future local web app and later SaaS UI/API
2. **Workflow Engine** — current implementation: LangGraph
3. **Agent Runtime** — role and responsibility definitions
4. **Skill Runtime** — reusable capabilities with typed contracts
5. **Context Engine** — bounded task-specific context construction
6. **Tool Gateway** — controlled access to external systems
7. **Model Gateway** — provider-neutral model invocation
8. **Memory / Knowledge** — organizational knowledge and runtime state
9. **Policy & Approval Engine** — permissions, guardrails, approvals
10. **Observability & Evaluation** — tracing, metrics, evals
11. **Event Engine** — direct and event-triggered workflow starts
12. **Plugin Registry** — replaceable providers and capability packs

## Stable Principles

- Contract-first architecture
- Provider neutrality
- Least privilege
- Human-in-the-loop for consequential actions
- Minimal context by default
- Typed module boundaries
- Explicit workflow state
- Durable history
- Idempotent external actions
- Retry and recovery
- First-class observability
- Spec-driven development via OpenSpec

## Source-of-Truth Boundaries

### OpenSpec
Defines software changes, architectural requirements, acceptance criteria, and implementation tasks.

### Obsidian
Holds business knowledge, organizational memory, decisions, learnings, and business-process documentation.

### GitHub
Holds code, contracts, runtime manifests, skills, tests, OpenSpec, and technical documentation.

## Current Implementations

- Workflow Engine → LangGraph
- Knowledge Provider → Obsidian
- Local Model Runtime → LM Studio
- External Model Providers → OpenAI / Anthropic
- Policy implementation → RegistryPolicyEngine
- Local Event Engine → in-process event bus
- Local tracing → in-memory recorder
- Local runtime DB → planned SQLite
- Future SaaS runtime DB → PostgreSQL

## Business Workflows V1

- New Watch Development
- Product Launch
- Content Campaign
- Customer Feedback → Learning
- Market Intelligence → Strategic Insight

## Local-First Application Direction

The final user experience will be a local web application that controls the entire TOM/OS.

Planned stack:

```text
Browser
  ↓
React + TypeScript + Vite
  ↓
FastAPI Control Plane
  ↓
TOM/OS Core
  ↓
LangGraph · Agents · Skills · Context · Policy · Tools · Models · Knowledge
```

The same boundaries should later support SaaS deployment without rewriting core business logic.

## Deeper References

- `openspec/config.yaml`
- `docs/ModularArchitecture.md`
- `docs/ApplicationArchitecture.md`
- `docs/OperatingModel.md`
- `docs/DecisionRights.md`
- `openspec/changes/`
