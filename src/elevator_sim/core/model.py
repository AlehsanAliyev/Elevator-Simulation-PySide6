from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Direction(Enum):
    UP = "Up"
    DOWN = "Down"
    IDLE = "Idle"


class DoorState(Enum):
    CLOSED = "Closed"
    OPENING = "Opening"
    OPEN = "Open"
    CLOSING = "Closing"


@dataclass
class ElevatorState:
    current_floor: float = 1.0
    direction: Direction = Direction.IDLE
    door_state: DoorState = DoorState.CLOSED
    speed_fps: float = 1.0
    target_floor: Optional[int] = None
