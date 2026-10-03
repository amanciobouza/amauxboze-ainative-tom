from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Any, Callable

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from .state import WorkflowState

logger = logging.getLogger("amauxboze.workflows")


class SideEffectGuard:
    def __init__(self) -> None:
        self._completed: set[str] = set()

    def run_once(self, key: str, fn: Callable[[], Any]) -> Any:
        if key in self._completed:
            return None
        result = fn()
        self._completed.add(key)
        return result


class WorkflowRuntime:
    def __init__(self) -> None:
        self.checkpointer = MemorySaver()
        self.side_effect_guard = SideEffectGuard()

    @staticmethod
    def new_workflow_id(prefix: str = "wf") -> str:
        return f"{prefix}-{uuid.uuid4()}"

    def build_linear_graph(
        self,
        name: str,
        nodes: list[tuple[str, Callable[[WorkflowState], WorkflowState]]],
    ):
        graph = StateGraph(WorkflowState)

        for node_name, fn in nodes:
            graph.add_node(node_name, fn)

        if not nodes:
            raise ValueError("A workflow must contain at least one node")

        graph.add_edge(START, nodes[0][0])
        for index in range(len(nodes) - 1):
            graph.add_edge(nodes[index][0], nodes[index + 1][0])
        graph.add_edge(nodes[-1][0], END)

        return graph.compile(checkpointer=self.checkpointer)

    def log_state(self, state: WorkflowState) -> None:
        logger.info(
            json.dumps(
                {
                    "workflow_id": state.get("workflow_id"),
                    "workflow_name": state.get("workflow_name"),
                    "current_state": state.get("current_state"),
                    "agent_id": state.get("agent_id"),
                    "skill_id": state.get("skill_id"),
                    "model_provider": state.get("model_provider"),
                    "approval_status": state.get("approval_status"),
                    "error": state.get("error"),
                },
                ensure_ascii=False,
            )
        )
