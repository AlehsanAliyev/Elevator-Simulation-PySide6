from elevator_sim.core.model import Direction
from elevator_sim.core.scheduler import ScanScheduler


def test_scan_ordering_example() -> None:
    scheduler = ScanScheduler()
    for floor in (5, 1, 3):
        scheduler.add_request(floor)

    current = 2
    direction = Direction.UP
    order = []

    while scheduler.pending_requests():
        decision = scheduler.next_stop(current, direction)
        assert decision is not None
        order.append(decision.floor)
        scheduler.remove_request(decision.floor)
        current = decision.floor
        direction = decision.direction

    assert order == [3, 5, 1]
