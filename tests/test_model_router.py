import pytest

from amauxboze.models import ModelRouter, RoutingRequest


def test_local_only_never_falls_back(monkeypatch):
    router = ModelRouter()
    monkeypatch.setattr(router, "lm_studio_available", lambda: False)

    with pytest.raises(RuntimeError, match="local-only"):
        router.choose_provider(RoutingRequest(privacy="local_only"))


def test_prefers_available_local(monkeypatch):
    router = ModelRouter()
    monkeypatch.setattr(router, "lm_studio_available", lambda: True)

    assert router.choose_provider(RoutingRequest()) == "lm_studio"
