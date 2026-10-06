# Profile-aware business workflow execution

The five business workflow dependency constructors accept an `execute_stage` callback. Use `ModelStageExecutor` to apply each registered agent's profile, including Elena's direct operating style, on every model invocation:

```python
from amauxboze.workflows.model_stage_executor import ModelStageExecutor

# Loaded registries and a working provider-neutral ModelGateway implementation.
execute_stage = ModelStageExecutor(agents, skills, model_gateway)
# Pass execute_stage=execute_stage to the existing workflow dependencies.
```

This works with WatchDevelopmentDependencies, ProductLaunchDependencies,
ContentCampaignDependencies, CustomerFeedbackDependencies and
MarketIntelligenceDependencies. Existing test or custom callbacks remain valid.
The executor includes role instructions separately from the validated task input,
uses skill model requirements and requires a schema-valid JSON object response.
Workflow policy checks, approval interrupts, persistence and recovery stay in
the workflow. The executor does not execute tools or approve actions.

The existing RouterModelGateway only selects a provider and returns empty content;
it is not a live model transport. Supply a working ModelGateway implementation
to generate artifacts. Empty or malformed responses fail rather than produce
mock artifacts. Prompt propagation is tested with a recording gateway; actual
tone quality still requires evaluation against the chosen model.

The local application supplies `control_plane.model_transport.LiveModelGateway` for LM Studio, OpenAI and Anthropic, with explicit provider selection and local-only enforcement. See [LocalApplication.md](LocalApplication.md). The separate simulation executor is always labelled as simulation.
