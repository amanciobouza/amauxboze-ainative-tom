from datetime import datetime, timezone

from amauxboze.contracts import (
    ContextRequest,
    ModelRequest,
    PluginManifest,
    RuntimeEvent,
    ToolRequest,
)


def test_context_request_defaults():
    req = ContextRequest(task="prepare launch", agent_id="elena")
    assert req.max_items == 20
    assert req.knowledge_scopes == []


def test_tool_request_requires_explicit_mode():
    req = ToolRequest(
        agent_id="maya",
        skill_id="create-campaign-content",
        tool_name="social_publish",
        mode="action",
    )
    assert req.mode == "action"


def test_model_request_is_provider_neutral():
    req = ModelRequest(task="summarize", prompt="hello")
    assert req.preferred_providers == []


def test_runtime_event_shape():
    event = RuntimeEvent(
        event_id="evt-1",
        type="workflow.requested",
        timestamp=datetime.now(timezone.utc),
        source="control-plane",
    )
    assert event.type == "workflow.requested"


def test_plugin_manifest():
    manifest = PluginManifest(
        id="lm-studio",
        version="0.1.0",
        plugin_type="model_provider",
        capabilities=["chat"],
    )
    assert manifest.health_check is True
