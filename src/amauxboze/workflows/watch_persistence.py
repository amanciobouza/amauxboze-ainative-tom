from __future__ import annotations

import json
from pathlib import PurePosixPath
from typing import Any

from amauxboze.adapters import ObsidianAdapter


class WatchDevelopmentPersistence:
    def __init__(self, obsidian: ObsidianAdapter):
        self.obsidian = obsidian

    @staticmethod
    def workspace(workflow_id: str) -> str:
        return str(PurePosixPath("Products") / "Development" / workflow_id)

    def persist_artifact(
        self,
        *,
        workflow_id: str,
        artifact_type: str,
        agent_id: str,
        skill_id: str,
        content: dict[str, Any],
    ) -> None:
        path = f"{self.workspace(workflow_id)}/{artifact_type}.md"
        payload = json.dumps(content, ensure_ascii=False, indent=2)
        body = f"# {artifact_type.replace('_', ' ').title()}\n\n{payload}\n"
        self.obsidian.write_text(
            path,
            body,
            workflow_id=workflow_id,
            agent_id=agent_id,
            skill_id=skill_id,
        )

    def persist_decision(
        self,
        *,
        workflow_id: str,
        gate: str,
        decision: str,
        rationale: str,
        approver: str = "Amancio",
    ) -> None:
        path = f"{self.workspace(workflow_id)}/decision-{gate}.md"
        body = (
            f"# Decision — {gate}\n\n"
            f"- Approver: {approver}\n"
            f"- Decision: {decision}\n"
            f"- Rationale: {rationale}\n"
        )
        self.obsidian.write_text(
            path,
            body,
            workflow_id=workflow_id,
            agent_id="amancio",
            skill_id="founder-approval",
        )
