"""Pub/sub facade used by API streaming and graph nodes."""

from communication.event_bus import get_event_bus

__all__ = ["get_event_bus"]

