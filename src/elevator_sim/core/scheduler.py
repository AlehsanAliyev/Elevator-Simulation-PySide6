from __future__ import annotations

from dataclasses import dataclass
from typing import Deque, List, Optional, Set
from collections import deque

from .model import Direction


@dataclass(frozen=True)
class NextStop:
    floor: int
    direction: Direction


class BaseScheduler:
    name = "Base"

    def add_request(self, floor: int) -> None:
        raise NotImplementedError

    def remove_request(self, floor: int) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def pending_requests(self) -> List[int]:
        raise NotImplementedError

    def next_stop(self, current_floor: float, direction: Direction) -> Optional[NextStop]:
        raise NotImplementedError


class SimpleScheduler(BaseScheduler):
    name = "Simple"

    def __init__(self) -> None:
        self._target: Optional[int] = None

    def add_request(self, floor: int) -> None:
        self._target = floor

    def remove_request(self, floor: int) -> None:
        if self._target == floor:
            self._target = None

    def clear(self) -> None:
        self._target = None

    def pending_requests(self) -> List[int]:
        return [self._target] if self._target is not None else []

    def next_stop(self, current_floor: float, direction: Direction) -> Optional[NextStop]:
        if self._target is None:
            return None
        if current_floor == self._target:
            return NextStop(self._target, Direction.IDLE)
        next_dir = Direction.UP if self._target > current_floor else Direction.DOWN
        return NextStop(self._target, next_dir)


class FifoScheduler(BaseScheduler):
    name = "FIFO"

    def __init__(self) -> None:
        self._queue: Deque[int] = deque()

    def add_request(self, floor: int) -> None:
        if floor not in self._queue:
            self._queue.append(floor)

    def remove_request(self, floor: int) -> None:
        try:
            self._queue.remove(floor)
        except ValueError:
            return

    def clear(self) -> None:
        self._queue.clear()

    def pending_requests(self) -> List[int]:
        return list(self._queue)

    def next_stop(self, current_floor: float, direction: Direction) -> Optional[NextStop]:
        if not self._queue:
            return None
        target = self._queue[0]
        if current_floor == target:
            return NextStop(target, Direction.IDLE)
        next_dir = Direction.UP if target > current_floor else Direction.DOWN
        return NextStop(target, next_dir)


class ScanScheduler(BaseScheduler):
    name = "SCAN"

    def __init__(self) -> None:
        self._requests: Set[int] = set()

    def add_request(self, floor: int) -> None:
        self._requests.add(floor)

    def remove_request(self, floor: int) -> None:
        self._requests.discard(floor)

    def clear(self) -> None:
        self._requests.clear()

    def pending_requests(self) -> List[int]:
        return sorted(self._requests)

    def next_stop(self, current_floor: float, direction: Direction) -> Optional[NextStop]:
        if not self._requests:
            return None

        floors = sorted(self._requests)

        if direction == Direction.UP:
            ahead = [floor for floor in floors if floor > current_floor]
            if ahead:
                return NextStop(min(ahead), Direction.UP)
            behind = [floor for floor in floors if floor < current_floor]
            if behind:
                return NextStop(max(behind), Direction.DOWN)
        elif direction == Direction.DOWN:
            behind = [floor for floor in floors if floor < current_floor]
            if behind:
                return NextStop(max(behind), Direction.DOWN)
            ahead = [floor for floor in floors if floor > current_floor]
            if ahead:
                return NextStop(min(ahead), Direction.UP)
        else:
            nearest = min(floors, key=lambda f: (abs(f - current_floor), f))
            if nearest == current_floor:
                return NextStop(nearest, Direction.IDLE)
            next_dir = Direction.UP if nearest > current_floor else Direction.DOWN
            return NextStop(nearest, next_dir)

        return None
