# Tasks

## 1. Project Foundation

- [x] 1.1 Create Python package structure for runtime, registries, adapters, and workflows
- [x] 1.2 Add configuration loader for `config/project.yaml`
- [x] 1.3 Add environment/secrets handling and `.env.example`
- [x] 1.4 Add test framework and base CI workflow

## 2. Agent Registry

- [x] 2.1 Define agent manifest schema
- [x] 2.2 Convert the eight V1 agent profiles into runtime manifests
- [x] 2.3 Implement manifest loader and validation
- [x] 2.4 Implement agent permission checks
- [x] 2.5 Add registry tests

## 3. Skill Registry

- [x] 3.1 Define skill manifest schema
- [x] 3.2 Define canonical skill folder layout
- [x] 3.3 Implement skill discovery and version validation
- [x] 3.4 Implement input/output schema validation
- [x] 3.5 Add authorization checks between agents and skills
- [x] 3.6 Add registry tests

## 4. Obsidian Adapter

- [x] 4.1 Implement vault-root path validation
- [x] 4.2 Implement controlled Markdown read
- [x] 4.3 Implement controlled Markdown write
- [x] 4.4 Add write audit metadata
- [x] 4.5 Add atomic-write and concurrency protection
- [x] 4.6 Add adapter tests

## 5. Model Router

- [x] 5.1 Define provider-neutral model interface
- [x] 5.2 Implement LM Studio provider
- [x] 5.3 Implement LM Studio health/model availability check
- [x] 5.4 Implement OpenAI provider
- [x] 5.5 Implement Anthropic provider
- [x] 5.6 Implement policy-aware routing
- [x] 5.7 Implement strict local-only behavior
- [x] 5.8 Add router tests

## 6. Approval Gates

- [x] 6.1 Define approval request state
- [x] 6.2 Implement LangGraph interrupt for approval
- [x] 6.3 Implement approve/reject/revise outcomes
- [x] 6.4 Add protection against duplicate side effects
- [x] 6.5 Add approval tests

## 7. Workflow Runtime

- [x] 7.1 Define shared workflow state model
- [x] 7.2 Configure LangGraph checkpointing
- [x] 7.3 Add workflow run identifiers and metadata
- [x] 7.4 Add structured execution logging
- [x] 7.5 Add resume/recovery tests

## 8. Validation

- [ ] 8.1 Validate all OpenSpec artifacts
- [ ] 8.2 Run automated test suite
- [x] 8.3 Demonstrate a minimal workflow using one agent, one skill, Obsidian read, model routing, and one approval gate
- [ ] 8.4 Review foundation before starting business workflow implementations
