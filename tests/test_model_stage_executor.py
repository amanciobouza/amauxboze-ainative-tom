import importlib
import json
from pathlib import Path

import pytest

from amauxboze.contracts import ModelGateway, ModelResponse
from amauxboze.registries import AgentRegistry, SkillRegistry
from amauxboze.workflows.model_stage_executor import ModelStageExecutor


class RecordingGateway(ModelGateway):
    def __init__(self, content):
        self.content = content
        self.requests = []

    def invoke(self, request):
        self.requests.append(request)
        return ModelResponse(provider="test", content=self.content)


def registries():
    agents = AgentRegistry(Path("runtime/agents"))
    skills = SkillRegistry(Path("skills"))
    agents.load()
    skills.load()
    return agents, skills


@pytest.mark.parametrize("content", ["", "not JSON", "[]", "{}", '{"objective": 12}'])
def test_rejects_invalid_model_output(content):
    agents, skills = registries()
    gateway = RecordingGateway(content)
    executor = ModelStageExecutor(agents, skills, gateway)
    with pytest.raises(ValueError):
        executor("elena", "define-product-brief", {"founder_brief": "Build a watch"})


def test_denied_skill_and_invalid_input_never_invoke_model():
    agents, skills = registries()
    gateway = RecordingGateway("{}")
    executor = ModelStageExecutor(agents, skills, gateway)
    with pytest.raises(PermissionError):
        executor("maya", "define-product-brief", {"founder_brief": "Build a watch"})
    with pytest.raises(ValueError):
        executor("elena", "define-product-brief", {})
    assert gateway.requests == []


def test_bounded_task_context_and_review_feedback_reach_model_without_payload_changes():
    from amauxboze.contracts import ContextBundle, ContextEngine, ContextItem
    requests = []
    class RecordingContext(ContextEngine):
        def build(self, request):
            requests.append(request)
            return ContextBundle(items=[ContextItem(source="Organization/priorities.md", content="Founder values evidence.")])
    agents, skills = registries()
    output = {"objective": "Evidence first", "constraints": [], "open_questions": []}
    gateway = RecordingGateway(json.dumps(output))
    executor = ModelStageExecutor(agents, skills, gateway, context_engine=RecordingContext(), max_context_chars=2000, workflow_id="run-context")
    executor.workflow_feedback = "Define a measurable outcome."
    payload = {"founder_brief": "Build a watch"}
    assert executor("elena", "define-product-brief", payload) == output
    assert payload == {"founder_brief": "Build a watch"}
    assert requests[0].max_chars == 2000 and requests[0].max_items == 5
    assert requests[0].knowledge_scopes == skills.get("define-product-brief").context
    assert "Organization/priorities.md" in gateway.requests[0].prompt
    assert "Define a measurable outcome." in gateway.requests[0].prompt


@pytest.mark.parametrize(
    "module_name,builder,test_name",
    [
        ("watch_development", "build_new_watch_development_workflow", "test_happy_path_through_both_founder_gates"),
        ("product_launch", "build_product_launch_workflow", "test_happy_path_activates_once_and_completes"),
        ("content_campaign", "build_content_campaign_workflow", "test_happy_path_publishes_once_and_completes"),
        ("customer_feedback", "build_customer_feedback_workflow", "test_product_implication_routing"),
        ("market_intelligence", "build_market_intelligence_workflow", "test_evidence_backed_observation_path"),
    ],
)
def test_business_workflows_use_profile_aware_executor(monkeypatch, module_name, builder, test_name):
    # Reuse real workflow scenarios and their valid domain artifacts. Only the
    # model transport is replaced; approval and workflow assertions still run.
    scenario = importlib.import_module(f"test_{module_name}_workflow")
    original_builder = getattr(scenario, builder)
    agents, skills = registries()
    requests = []

    def build_with_model(deps):
        original_stage = deps.execute_stage

        class Gateway(ModelGateway):
            def invoke(self, request):
                profile = json.loads(request.prompt.split("Agent profile:\n", 1)[1].split("\nSkill:", 1)[0])
                payload = json.loads(request.prompt.split("Task input:\n", 1)[1].split("\nReturn only", 1)[0])
                agent = next(a for a in agents.load().values() if a.name == profile["name"])
                requests.append((agent.id, request, profile))
                output = original_stage(agent.id, request.task, payload)
                return ModelResponse(provider="test", content=json.dumps(output))

        deps.execute_stage = ModelStageExecutor(agents, skills, Gateway())
        return original_builder(deps)

    monkeypatch.setattr(scenario, builder, build_with_model)
    getattr(scenario, test_name)()
    elena_requests = [entry for entry in requests if entry[0] == "elena"]
    assert elena_requests
    for _, request, profile in elena_requests:
        assert profile["communication_instructions"] == agents.get("elena").communication_instructions
        assert profile["approval_boundaries"] == agents.get("elena").approval_boundaries
        model = skills.get(request.task).model
        assert request.preferred_providers == model.preferred_providers
        assert request.reasoning == model.reasoning
