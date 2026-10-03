from __future__ import annotations

from amauxboze.contracts import TraceRecorder, TraceSpan


class InMemoryTraceRecorder(TraceRecorder):
    def __init__(self):
        self.spans: list[TraceSpan] = []

    def record(self, span: TraceSpan) -> None:
        self.spans.append(span)
