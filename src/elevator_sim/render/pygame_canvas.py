from __future__ import annotations

from typing import Optional

import pygame
from PySide6.QtGui import QImage

from ..core.model import DoorState, ElevatorState


class PygameCanvas:
    _pygame_ready = False

    def __init__(self, width: int, height: int, floor_count: int = 6) -> None:
        if not PygameCanvas._pygame_ready:
            pygame.init()
            pygame.font.init()
            PygameCanvas._pygame_ready = True

        self.width = width
        self.height = height
        self.floor_count = max(2, floor_count)
        self.surface = pygame.Surface((self.width, self.height))
        self.font = pygame.font.Font(None, 20)
        self._buffer: Optional[bytes] = None

        self._colors = {
            "sky": (16, 196, 222),
            "building": (32, 42, 54),
            "line": (220, 220, 220),
            "car": (245, 182, 89),
            "car_border": (30, 30, 30),
            "door_open": (98, 187, 108),
            "door_closed": (200, 86, 86),
        }

    def set_floor_count(self, floor_count: int) -> None:
        self.floor_count = max(2, floor_count)

    def draw(self, state: ElevatorState) -> QImage:
        self.surface.fill(self._colors["sky"])

        building_x = int(self.width * 0.15)
        building_w = int(self.width * 0.7)
        pygame.draw.rect(self.surface, self._colors["building"], (building_x, 0, building_w, self.height))

        floor_h = self.height / self.floor_count
        for i in range(self.floor_count):
            y = int(self.height - (i + 1) * floor_h)
            pygame.draw.line(self.surface, self._colors["line"], (building_x, y), (building_x + building_w, y), 2)
            label = self.font.render(str(i + 1), True, self._colors["line"])
            self.surface.blit(label, (building_x + building_w + 6, y + int(floor_h * 0.35)))

        car_w = int(building_w * 0.35)
        car_h = int(floor_h * 0.75)
        car_x = building_x + int(building_w * 0.5 - car_w * 0.5)
        car_y = int(self.height - state.current_floor * floor_h + (floor_h - car_h) * 0.5)
        pygame.draw.rect(self.surface, self._colors["car"], (car_x, car_y, car_w, car_h))
        pygame.draw.rect(self.surface, self._colors["car_border"], (car_x, car_y, car_w, car_h), 2)

        door_color = self._colors["door_open"] if state.door_state == DoorState.OPEN else self._colors["door_closed"]
        door_gap = int(car_w * 0.08) if state.door_state == DoorState.OPEN else 0
        door_w = int((car_w - door_gap) / 2)
        pygame.draw.rect(self.surface, door_color, (car_x + 4, car_y + 4, door_w - 4, car_h - 8))
        pygame.draw.rect(
            self.surface,
            door_color,
            (car_x + door_w + door_gap + 2, car_y + 4, door_w - 4, car_h - 8),
        )

        self._buffer = pygame.image.tostring(self.surface, "RGB")
        return QImage(self._buffer, self.width, self.height, QImage.Format_RGB888)
