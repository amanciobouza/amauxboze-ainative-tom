from types import SimpleNamespace

import pytest

from amauxboze.contracts import ModelRequest
from amauxboze.control_plane.contracts import AppSettings
from amauxboze.control_plane.model_transport import LiveModelGateway


def test_lm_studio_uses_native_json_schema_and_records_usage(monkeypatch):
    calls = []
    response = SimpleNamespace(choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(content='{"summary":"evidence missing"}'))], usage=SimpleNamespace(model_dump=lambda: {"completion_tokens": 4}))
    def create(**kwargs):
        calls.append(kwargs)
        return response
    monkeypatch.setattr("amauxboze.control_plane.model_transport.OpenAI", lambda **kwargs: SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))))
    gateway = LiveModelGateway(AppSettings(vault_path="vault", model="local-model"))
    schema = {"type": "object", "properties": {"summary": {"type": "string"}}, "required": ["summary"]}
    output = gateway.invoke(ModelRequest(task="prepare", prompt="Return JSON", output_schema=schema))
    assert calls[0]["response_format"] == {"type": "json_schema", "json_schema": {"name": "stage_result", "schema": schema, "strict": True}}
    assert output.provider == "lm_studio" and output.model == "local-model"
    assert gateway.last_response.usage["completion_tokens"] == 4


def test_local_only_task_rejects_cloud_even_when_configured(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    gateway = LiveModelGateway(AppSettings(vault_path="vault", model="explicit-model", provider="openai", privacy="standard"))
    with pytest.raises(RuntimeError, match="forbids cloud"):
        gateway.invoke(ModelRequest(task="private", prompt="Sensitive local evidence", privacy="local_only"))


def test_provider_failure_does_not_fallback(monkeypatch):
    calls = []
    def client(**kwargs):
        calls.append(kwargs)
        raise RuntimeError("Local model unavailable")
    monkeypatch.setattr("amauxboze.control_plane.model_transport.OpenAI", client)
    monkeypatch.setenv("OPENAI_API_KEY", "configured-but-not-selected")
    gateway = LiveModelGateway(AppSettings(vault_path="vault", model="local-model"))
    with pytest.raises(RuntimeError):
        gateway.invoke(ModelRequest(task="local", prompt="Return JSON"))
    assert len(calls) == 1
    assert calls[0]["base_url"] == "http://127.0.0.1:1234/v1"


def test_exhausted_reasoning_budget_has_actionable_error(monkeypatch):
    response = SimpleNamespace(choices=[SimpleNamespace(finish_reason="length", message=SimpleNamespace(content=""))], usage=None)
    monkeypatch.setattr("amauxboze.control_plane.model_transport.OpenAI", lambda **kwargs: SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: response))))
    gateway = LiveModelGateway(AppSettings(vault_path="vault", model="local-model"))
    with pytest.raises(RuntimeError, match="exhausted its output budget"):
        gateway.invoke(ModelRequest(task="test", prompt="Return JSON"))


@pytest.mark.parametrize("provider", ["lm_studio", "openai", "anthropic"])
@pytest.mark.parametrize("language,expected", [("de", "German (Deutsch)"), ("en", "English")])
def test_agent_language_reaches_every_provider(monkeypatch, provider, language, expected):
    calls = []
    def create(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(content="{}"))], output_text="{}", content=[SimpleNamespace(type="text", text="{}")], usage=SimpleNamespace(model_dump=lambda: {}))
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)), responses=SimpleNamespace(create=create), messages=SimpleNamespace(create=create))
    monkeypatch.setattr("amauxboze.control_plane.model_transport.OpenAI", lambda **kwargs: client)
    monkeypatch.setattr("amauxboze.control_plane.model_transport.Anthropic", lambda **kwargs: client)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    gateway = LiveModelGateway(AppSettings(vault_path="vault", provider=provider, model="test-model", privacy="standard", agent_language=language))
    gateway.invoke(ModelRequest(task="test", prompt="Task data in another language", privacy="standard"))
    call = calls[0]
    instruction = call["messages"][0]["content"] if provider == "lm_studio" else call["instructions" if provider == "openai" else "system"]
    assert expected in instruction
    assert "Preserve schema keys, enum values" in instruction
