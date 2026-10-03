from __future__ import annotations

from pathlib import Path

from amauxboze.adapters import ObsidianAdapter
from amauxboze.contracts import (
    KnowledgeDocument,
    KnowledgeProvider,
    KnowledgeQuery,
    KnowledgeWrite,
)


class ObsidianKnowledgeProvider(KnowledgeProvider):
    def __init__(self, adapter: ObsidianAdapter):
        self.adapter = adapter

    def read(self, path: str) -> KnowledgeDocument:
        return KnowledgeDocument(path=path, content=self.adapter.read_text(path))

    def search(self, query: KnowledgeQuery) -> list[KnowledgeDocument]:
        root = self.adapter.vault_root
        results: list[KnowledgeDocument] = []
        needle = query.query.lower()

        scopes = [root / scope for scope in query.scopes] if query.scopes else [root]

        for scope in scopes:
            if not scope.exists():
                continue
            for path in scope.rglob("*.md"):
                try:
                    content = path.read_text(encoding="utf-8")
                except OSError:
                    continue
                if needle in content.lower() or needle in path.name.lower():
                    rel = str(path.relative_to(root)).replace("\\", "/")
                    results.append(KnowledgeDocument(path=rel, content=content))
                    if len(results) >= query.limit:
                        return results
        return results

    def write(self, request: KnowledgeWrite) -> KnowledgeDocument:
        path = self.adapter.write_text(
            request.path,
            request.content,
            workflow_id=request.workflow_id,
            agent_id=request.agent_id,
            skill_id=request.skill_id,
        )
        rel = str(path.relative_to(self.adapter.vault_root)).replace("\\", "/")
        return KnowledgeDocument(path=rel, content=path.read_text(encoding="utf-8"))

    def list(self, scope: str = "") -> list[KnowledgeDocument]:
        root = self.adapter._resolve_inside_vault(scope) if scope else self.adapter.vault_root
        docs: list[KnowledgeDocument] = []
        if not root.exists():
            return docs
        for path in root.rglob("*.md"):
            rel = str(path.relative_to(self.adapter.vault_root)).replace("\\", "/")
            docs.append(KnowledgeDocument(path=rel, content=""))
        return docs
