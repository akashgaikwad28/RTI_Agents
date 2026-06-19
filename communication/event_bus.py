"""Async in-process event bus for agent/tool/workflow events."""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from typing import Awaitable, Callable

from communication.message_schema import WorkflowEvent

Subscriber = Callable[[WorkflowEvent], Awaitable[None]]


class EventBus:
    def __init__(self, max_history: int = 1000):
        self._subscribers: dict[str, list[Subscriber]] = defaultdict(list)
        self._history: deque[WorkflowEvent] = deque(maxlen=max_history)
        self._queue: asyncio.Queue[WorkflowEvent] = asyncio.Queue()

    async def publish(self, event_type: str, payload: dict, *, request_id: str | None = None, node: str | None = None) -> WorkflowEvent:
        event = WorkflowEvent(event_type=event_type, payload=payload, request_id=request_id, node=node)
        self._history.append(event)
        await self._queue.put(event)
        subscribers = [*self._subscribers.get(event_type, []), *self._subscribers.get("*", [])]
        await asyncio.gather(*(subscriber(event) for subscriber in subscribers), return_exceptions=True)
        return event

    def subscribe(self, event_type: str, subscriber: Subscriber) -> None:
        self._subscribers[event_type].append(subscriber)

    def history(self, *, request_id: str | None = None, limit: int = 100) -> list[WorkflowEvent]:
        events = [event for event in self._history if request_id is None or event.request_id == request_id]
        return events[-limit:]

    async def stream(self, *, request_id: str | None = None):
        while True:
            event = await self._queue.get()
            if request_id is None or event.request_id == request_id:
                yield event


_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    global _bus
    if _bus is None:
        _bus = EventBus()
    return _bus

