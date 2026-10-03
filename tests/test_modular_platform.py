from datetime import datetime, timezone
from pathlib import Path

from amauxboze.adapters import ObsidianAdapter
from amauxboze.contracts import (
    ContextRequest,
    PluginManifest,
    RuntimeEvent,
    ToolRequest,
    TraceSpan,
)
from amauxboze.platform import (
    DefaultContextEngine,
    DefaultPluginRegistry,
    DefaultToolGateway,
    InMemoryTraceRecorder,
    InProcessEventEngine,
    ObsidianKnowledgeProvider,
    RegistryPolicyEngine,
)
from amauxboze.registries import AgentRegistry, AuthorizationService, SkillRegistry


def _policy():
    agents = AgentRegistry(Path("runtime/agents"))
    skills = SkillRegistry(Path("skills"))
    agents.load()
    skills.load()
    return RegistryPolicyEngine(AuthorizationService(agents, skills))


def test_tool_gateway_enforces_permissions_and_idempotency():
    gateway = DefaultToolGateway(_policy())
    calls = []
    gateway.register("social_publish", lambda payload: calls.append(payload) or {"ok": True})

    req = ToolRequest(
        agent_id="maya",
        skill_id="create-campaign-content",
        tool_name="social_publish",
        mode="action",
        payload={"post": "hello"},
        idempotency_key="post-1",
    )

    first = gateway.execute(req)
    second = gateway.execute(req)

    assert first.status == "ok"
    assert second.status == "ok"
    assert len(calls) == 1


def test_context_engine_respects_scope(tmp_path):
    adapter = ObsidianAdapter(tmp_path)
    provider = ObsidianKnowledgeProvider(adapter)
    adapter.write_text(
        "Brand/voice.md",
        "Purpose before status.",
        workflow_id="wf",
        agent_id="elodie",
        skill_id="brand",
    )

    engine = DefaultContextEngine(provider)
    bundle = engine.build(
        ContextRequest(
            task="write campaign",
            agent_id="maya",
            knowledge_scopes=["Brand"],
            max_items=5,
            max_chars=5000,
        )
    )
    assert len(bundle.items) == 1
    assert bundle.items[0].source == "Brand/voice.md"


def test_event_engine_dispatches():
    engine = InProcessEventEngine()
    seen = []
    engine.subscribe("workflow.requested", lambda event: seen.append(event.event_id))
    engine.publish(
        RuntimeEvent(
            event_id="evt-1",
            type="workflow.requested",
            timestamp=datetime.now(timezone.utc),
            source="test",
        )
    )
    assert seen == ["evt-1"]


def test_trace_recorder():
    recorder = InMemoryTraceRecorder()
    recorder.record(
        TraceSpan(
            trace_id="t1",
            span_id="s1",
            kind="skill",
            name="prepare-decision",
            started_at=datetime.now(timezone.utc),
        )
    )
    assert recorder.spans[0].name == "prepare-decision"


def test_plugin_registry():
    registry = DefaultPluginRegistry()
    manifest = PluginManifest(
        id="obsidian",
        version="0.1.0",
        plugin_type="knowledge_provider",
        capabilities=["read", "write", "search"],
    )
    provider = object()
    registry.register(manifest, provider)

    assert registry.get("obsidian") is provider
    assert [m.id for m in registry.manifests()] == ["obsidian"]
