from elevator_sim.core.controller import ElevatorController
from elevator_sim.core.model import DoorState


def test_door_blocks_movement_until_closed() -> None:
    controller = ElevatorController(floor_count=6, speed_fps=1.0)
    controller.add_request(3)
    controller.request_open_door()

    for _ in range(5):
        controller.update(0.2)
        assert controller.state.door_state in (DoorState.OPENING, DoorState.OPEN)
        assert controller.state.current_floor == 1.0
