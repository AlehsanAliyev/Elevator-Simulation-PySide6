from __future__ import annotations

from typing import List, Optional

from .events import (
    ArrivedAtFloor,
    DirectionChanged,
    DoorClosed,
    DoorOpened,
    EmergencyStop,
    Event,
    RequestAdded,
)
from .model import Direction, DoorState, ElevatorState
from .scheduler import BaseScheduler, FifoScheduler


class ElevatorController:
    def __init__(
        self,
        floor_count: int = 6,
        scheduler: Optional[BaseScheduler] = None,
        speed_fps: float = 1.0,
        door_open_time: float = 0.6,
        door_close_time: float = 0.6,
        dwell_time: float = 1.5,
    ) -> None:
        self.floor_count = max(2, floor_count)
        self.scheduler = scheduler or FifoScheduler()
        self.state = ElevatorState(speed_fps=speed_fps)
        self.door_open_time = door_open_time
        self.door_close_time = door_close_time
        self.dwell_time = dwell_time
        self.door_timer = 0.0
        self.emergency_stop = False
        self._events: List[Event] = []

    def set_floor_count(self, floor_count: int) -> None:
        self.floor_count = max(2, floor_count)
        valid_requests = [f for f in self.scheduler.pending_requests() if 1 <= f <= self.floor_count]
        self.scheduler.clear()
        for floor in valid_requests:
            self.scheduler.add_request(floor)

    def set_scheduler(self, scheduler: BaseScheduler) -> None:
        pending = self.scheduler.pending_requests()
        self.scheduler = scheduler
        for floor in pending:
            self.scheduler.add_request(floor)

    def reset(self) -> None:
        self.scheduler.clear()
        self.state = ElevatorState(speed_fps=self.state.speed_fps)
        self.door_timer = 0.0
        self.emergency_stop = False

    def add_request(self, floor: int) -> bool:
        if floor < 1 or floor > self.floor_count:
            return False
        self.scheduler.add_request(floor)
        self._emit(RequestAdded(floor))
        return True

    def request_open_door(self) -> bool:
        if self.emergency_stop:
            return False
        if self.state.door_state == DoorState.OPEN:
            self.door_timer = self.dwell_time
            return True
        if self.state.door_state in (DoorState.CLOSED, DoorState.CLOSING):
            if self.state.direction != Direction.IDLE:
                return False
            self.state.door_state = DoorState.OPENING
            self.door_timer = self.door_open_time
            return True
        return False

    def request_close_door(self) -> bool:
        if self.emergency_stop:
            return False
        if self.state.door_state in (DoorState.OPEN, DoorState.OPENING):
            self.state.door_state = DoorState.CLOSING
            self.door_timer = self.door_close_time
            return True
        return False

    def set_emergency_stop(self, active: bool) -> None:
        if self.emergency_stop == active:
            return
        self.emergency_stop = active
        if active:
            self._set_direction(Direction.IDLE)
        self._emit(EmergencyStop(active))

    def update(self, dt: float) -> None:
        if dt <= 0.0:
            return
        if self.emergency_stop:
            return

        self._advance_doors(dt)
        if self.state.door_state != DoorState.CLOSED:
            return

        decision = self.scheduler.next_stop(self.state.current_floor, self.state.direction)
        if decision is None:
            self._set_direction(Direction.IDLE)
            self.state.target_floor = None
            return

        self.state.target_floor = decision.floor
        if decision.direction != Direction.IDLE:
            self._set_direction(decision.direction)

        if abs(self.state.current_floor - decision.floor) < 1e-3:
            self._arrive_at_floor(decision.floor)
            return

        step = self.state.speed_fps * dt
        if self.state.current_floor < decision.floor:
            self.state.current_floor = min(self.state.current_floor + step, decision.floor)
            self._set_direction(Direction.UP)
        elif self.state.current_floor > decision.floor:
            self.state.current_floor = max(self.state.current_floor - step, decision.floor)
            self._set_direction(Direction.DOWN)

        if abs(self.state.current_floor - decision.floor) < 1e-3:
            self._arrive_at_floor(decision.floor)

    def consume_events(self) -> List[Event]:
        events = list(self._events)
        self._events.clear()
        return events

    def pending_requests(self) -> List[int]:
        return self.scheduler.pending_requests()

    def _advance_doors(self, dt: float) -> None:
        if self.state.door_state == DoorState.OPENING:
            self.door_timer -= dt
            if self.door_timer <= 0.0:
                self.state.door_state = DoorState.OPEN
                self.door_timer = self.dwell_time
                self._emit(DoorOpened(int(round(self.state.current_floor))))
        elif self.state.door_state == DoorState.OPEN:
            self.door_timer -= dt
            if self.door_timer <= 0.0:
                self.state.door_state = DoorState.CLOSING
                self.door_timer = self.door_close_time
        elif self.state.door_state == DoorState.CLOSING:
            self.door_timer -= dt
            if self.door_timer <= 0.0:
                self.state.door_state = DoorState.CLOSED
                self._emit(DoorClosed(int(round(self.state.current_floor))))

    def _arrive_at_floor(self, floor: int) -> None:
        self.state.current_floor = float(floor)
        self.state.target_floor = None
        self.scheduler.remove_request(floor)
        self._emit(ArrivedAtFloor(floor))
        self.state.door_state = DoorState.OPENING
        self.door_timer = self.door_open_time
        self._set_direction(Direction.IDLE)

    def _set_direction(self, direction: Direction) -> None:
        if self.state.direction != direction:
            self.state.direction = direction
            self._emit(DirectionChanged(direction))

    def _emit(self, event: Event) -> None:
        self._events.append(event)
