from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from amauxboze.contracts import EventEngine, RuntimeEvent

EventHandler = Callable[[RuntimeEvent], None]


class InProcessEventEngine(EventEngine):
    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self.events: list[RuntimeEvent] = []

    def publish(self, event: RuntimeEvent) -> None:
        self.events.append(event)
        for handler in list(self._handlers.get(event.type, [])):
            handler(event)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)
