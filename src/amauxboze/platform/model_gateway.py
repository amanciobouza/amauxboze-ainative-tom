from __future__ import annotations

from amauxboze.contracts import ModelGateway, ModelRequest, ModelResponse
from amauxboze.models import ModelRouter, RoutingRequest


class RouterModelGateway(ModelGateway):
    def __init__(self, router: ModelRouter):
        self.router = router

    def invoke(self, request: ModelRequest) -> ModelResponse:
        provider = self.router.choose_provider(
            RoutingRequest(
                privacy=request.privacy,
                reasoning=request.reasoning,
                creativity=request.creativity,
                coding=request.coding,
                preferred_providers=tuple(request.preferred_providers),
            )
        )
        return ModelResponse(
            provider=provider,
            model=None,
            content="",
            usage={},
        )
