from pathlib import Path

from langgraph.types import Command

from amauxboze.adapters import ObsidianAdapter
from amauxboze.models import ModelRouter
from amauxboze.registries import AgentRegistry, AuthorizationService, SkillRegistry
from amauxboze.workflows.minimal_foundation import (
    MinimalWorkflowDependencies,
    build_minimal_foundation_workflow,
)


def test_minimal_workflow_interrupt_and_resume(tmp_path: Path, monkeypatch):
    context = tmp_path / "Organization" / "00_Operating-Model.md"
    context.parent.mkdir(parents=True)
    context.write_text("# Operating Model\nFounder retains final approval.", encoding="utf-8")

    agents = AgentRegistry(Path("runtime/agents"))
    skills = SkillRegistry(Path("skills"))
    agents.load()
    skills.load()

    router = ModelRouter()
    monkeypatch.setattr(router, "lm_studio_available", lambda: True)

    deps = MinimalWorkflowDependencies(
        agents=agents,
        skills=skills,
        authorization=AuthorizationService(agents, skills),
        obsidian=ObsidianAdapter(tmp_path),
        router=router,
        execute_model=lambda provider, prompt: "Decision brief generated locally.",
    )

    graph = build_minimal_foundation_workflow(deps)
    config = {"configurable": {"thread_id": "test-minimal"}}

    first = graph.invoke(
        {
            "workflow_id": "wf-test",
            "workflow_name": "minimal-foundation",
            "current_state": "STARTED",
            "payload": {
                "question": "Launch the watch?",
                "options": ["launch", "wait"],
                "evidence": ["prototype ready"],
            },
        },
        config=config,
    )

    assert "__interrupt__" in first

    resumed = graph.invoke(Command(resume="approve"), config=config)
    assert resumed["approval_status"] == "approved"
    assert resumed["model_provider"] == "lm_studio"
    assert resumed["result"]["summary"] == "Decision brief generated locally."
