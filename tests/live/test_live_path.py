from __future__ import annotations

# First-party imports
from tests.live.helpers import (
    DRONE_IDS,
    MISSION_ID,
    OTHER_OPERATOR_ID,
    drone_ids_of,
    live_url,
    receive_full_squad,
    receives_anything,
)
from tests.live.simulated_drones import SimulatedDrones


class TestLivePath:
    """Acceptance test of the live path: 10 simulated Drones, the leaf node, the cell and a WebSocket client.

    Notes:
        - The slow client (criterion 2) is proved at mailbox level by the swarm_live and gateway tests, because
          TCP buffers hide a slow reader end to end.
        - Without ``nats-server`` or ``swarm_core``, the fixtures skip the tests.
    """

    async def test_a_client_of_the_gateway_receives_the_squad_through_the_cell(
        self, simulated_drones: SimulatedDrones, gateway_port: int
    ) -> None:
        squad = await receive_full_squad(live_url(gateway_port))
        assert squad is not None
        assert squad.mission_id == MISSION_ID
        assert drone_ids_of(squad) == sorted(DRONE_IDS)

    async def test_a_client_of_the_flight_engine_receives_the_squad_locally(
        self, simulated_drones: SimulatedDrones, flight_engine_port: int
    ) -> None:
        squad = await receive_full_squad(live_url(flight_engine_port))
        assert squad is not None
        assert squad.mission_id == MISSION_ID
        assert drone_ids_of(squad) == sorted(DRONE_IDS)

    async def test_a_client_of_another_operator_receives_nothing(
        self, simulated_drones: SimulatedDrones, gateway_port: int
    ) -> None:
        assert not await receives_anything(live_url(gateway_port, OTHER_OPERATOR_ID))
