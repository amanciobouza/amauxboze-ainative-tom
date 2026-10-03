from __future__ import annotations

from amauxboze.contracts import (
    ContextBundle,
    ContextEngine,
    ContextItem,
    ContextRequest,
    KnowledgeProvider,
)


class DefaultContextEngine(ContextEngine):
    def __init__(self, knowledge: KnowledgeProvider):
        self.knowledge = knowledge

    def build(self, request: ContextRequest) -> ContextBundle:
        items: list[ContextItem] = []
        remaining = request.max_chars

        for scope in request.knowledge_scopes:
            for doc in self.knowledge.list(scope):
                if len(items) >= request.max_items or remaining <= 0:
                    break
                full = self.knowledge.read(doc.path)
                content = full.content[:remaining]
                items.append(
                    ContextItem(
                        source=full.path,
                        content=content,
                        provenance={"scope": scope},
                    )
                )
                remaining -= len(content)

        return ContextBundle(
            items=items,
            role_context={"agent_id": request.agent_id},
            workflow_context={"workflow_id": request.workflow_id, "task": request.task},
        )
