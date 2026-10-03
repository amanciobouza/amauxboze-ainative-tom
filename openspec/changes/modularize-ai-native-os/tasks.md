# Tasks

## 1. Contracts

- [x] 1.1 Add core contract package
- [x] 1.2 Add ContextRequest / ContextBundle
- [x] 1.3 Add ToolRequest / ToolResult
- [x] 1.4 Add ModelRequest / ModelResponse
- [x] 1.5 Add Knowledge query/write contracts
- [x] 1.6 Add RuntimeEvent contract
- [x] 1.7 Add TraceSpan contract

## 2. Model Gateway

- [x] 2.1 Define ModelGateway interface
- [x] 2.2 Wrap current ModelRouter implementation
- [x] 2.3 Preserve local-only policy
- [ ] 2.4 Add normalized telemetry

## 3. Knowledge Provider

- [x] 3.1 Define KnowledgeProvider interface
- [x] 3.2 Implement ObsidianKnowledgeProvider
- [x] 3.3 Add search/list/read/write contract tests

## 4. Policy Engine

- [x] 4.1 Define PolicyEngine interface
- [x] 4.2 Wrap agent/skill authorization
- [ ] 4.3 Add approval-policy checks
- [ ] 4.4 Add tool guardrail hooks

## 5. Tool Gateway

- [x] 5.1 Define ToolGateway
- [x] 5.2 Register tool providers
- [x] 5.3 Enforce least privilege
- [ ] 5.4 Emit trace/event records
- [x] 5.5 Add idempotency support

## 6. Context Engine

- [x] 6.1 Define context-selection policies
- [x] 6.2 Build role context
- [x] 6.3 Build workflow context
- [x] 6.4 Retrieve scoped knowledge
- [x] 6.5 Enforce context budgets
- [x] 6.6 Add context provenance metadata

## 7. Event Engine

- [x] 7.1 Define event envelope
- [x] 7.2 Add in-process local event bus
- [x] 7.3 Add workflow trigger subscriptions
- [ ] 7.4 Add event persistence abstraction
- [x] 7.5 Preserve future external-broker boundary

## 8. Observability

- [x] 8.1 Define trace recorder interface
- [ ] 8.2 Trace workflow runs
- [ ] 8.3 Trace agent/skill execution
- [ ] 8.4 Trace model calls
- [ ] 8.5 Trace tool calls
- [ ] 8.6 Trace approvals/retries/errors
- [ ] 8.7 Add exporter abstraction

## 9. Plugin Registry

- [x] 9.1 Define plugin manifest
- [x] 9.2 Implement plugin discovery
- [ ] 9.3 Register current LM Studio/OpenAI/Anthropic providers
- [ ] 9.4 Register Obsidian provider
- [x] 9.5 Add health-check contract
- [x] 9.6 Add plugin tests

## 10. Workflow Migration

- [ ] 10.1 Migrate New Watch Development
- [ ] 10.2 Migrate Product Launch
- [ ] 10.3 Migrate Content Campaign
- [ ] 10.4 Migrate Customer Feedback Learning
- [ ] 10.5 Migrate Market Intelligence
- [ ] 10.6 Verify behavior parity

## 11. Validation

- [ ] 11.1 Validate OpenSpec
- [ ] 11.2 Run full test suite
- [ ] 11.3 Demonstrate provider replacement
- [ ] 11.4 Demonstrate tool permission enforcement
- [ ] 11.5 Demonstrate event-triggered workflow
- [ ] 11.6 Demonstrate end-to-end trace
