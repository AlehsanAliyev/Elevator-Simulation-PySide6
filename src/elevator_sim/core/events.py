from dataclasses import dataclass

from .model import Direction


class Event:
    """Base type for events emitted by the controller."""


@dataclass(frozen=True)
class RequestAdded(Event):
    floor: int


@dataclass(frozen=True)
class ArrivedAtFloor(Event):
    floor: int


@dataclass(frozen=True)
class DoorOpened(Event):
    floor: int


@dataclass(frozen=True)
class DoorClosed(Event):
    floor: int


@dataclass(frozen=True)
class DirectionChanged(Event):
    direction: Direction


@dataclass(frozen=True)
class EmergencyStop(Event):
    active: bool


def format_event(event: Event) -> str:
    if isinstance(event, RequestAdded):
        return f"Request added: floor {event.floor}"
    if isinstance(event, ArrivedAtFloor):
        return f"Arrived at floor {event.floor}"
    if isinstance(event, DoorOpened):
        return f"Door opened at floor {event.floor}"
    if isinstance(event, DoorClosed):
        return f"Door closed at floor {event.floor}"
    if isinstance(event, DirectionChanged):
        return f"Direction changed: {event.direction.value}"
    if isinstance(event, EmergencyStop):
        state = "engaged" if event.active else "cleared"
        return f"Emergency stop {state}"
    return "Unknown event"
