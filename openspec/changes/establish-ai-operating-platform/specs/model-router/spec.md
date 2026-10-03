# Delta for Model Router

## ADDED Requirements

### Requirement: Provider-neutral invocation

The runtime MUST expose a common model invocation interface supporting LM Studio, OpenAI, and Anthropic.

### Requirement: Local LM Studio provider

The LM Studio adapter MUST support the configured base URL:

`http://127.0.0.1:1234`

#### Scenario: Local provider available
- GIVEN LM Studio is reachable and an eligible model is loaded
- WHEN a local-routed request is made
- THEN the request is executed locally

### Requirement: Policy-aware routing

Model selection MUST consider task and policy metadata.

Relevant metadata MAY include:
- privacy
- reasoning complexity
- creativity
- coding capability
- latency
- cost

#### Scenario: Local-only task
- GIVEN a task marked local-only
- WHEN LM Studio is unavailable
- THEN execution MUST fail or pause explicitly
- AND MUST NOT silently send data to a cloud provider
