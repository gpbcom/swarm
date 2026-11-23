from __future__ import annotations

# Standard library imports
from typing import AsyncIterator, List

# Third-party imports
import pytest

# First-party imports
from services.simulator.tests.helpers import (
    START_LAT_E7,
    START_LON_E7,
    a_flight_config,
    a_registered_drone,
    a_square_route,
)
from services.simulator.tests.stand_in_drone import StandInDrone
from services.simulator.tests.stand_in_drones import StandInDrones
from simulator.clients.mavlink.mavlink_drone_client import MavlinkDroneClient
from simulator.models.commands.mavlink_command_spec import MavlinkCommandSpec
from simulator.models.mavlink.exceptions import SEMavlinkClientRefusedError, SEMavlinkClientTimeoutError

NAV_TAKEOFF = 22
NAV_WAYPOINT = 16
NAV_LAND = 21
RETURN_TO_LAUNCH = 20
UNSUPPORTED_COMMAND = 777
ITEM_COUNT = 7


class TestMavlinkDroneClient:
    @pytest.fixture(autouse=True)
    async def close_clients(self) -> AsyncIterator[None]:
        self.clients: List[MavlinkDroneClient] = []
        yield
        for client in self.clients:
            await client.close()

    def a_client(self, stand_in: StandInDrone) -> MavlinkDroneClient:
        client = MavlinkDroneClient(a_registered_drone(stand_in), a_flight_config())
        self.clients.append(client)
        return client

    async def test_connect_gets_the_heartbeat(self, stand_in_drone: StandInDrone) -> None:
        client = self.a_client(stand_in_drone)
        await client.connect()

    async def test_a_silent_drone_times_out_on_connect(self, stand_in_drones: StandInDrones) -> None:
        client = self.a_client(stand_in_drones.make(silent=True))
        with pytest.raises(SEMavlinkClientTimeoutError):
            await client.connect()

    async def test_position_is_the_start_of_the_stand_in(self, stand_in_drone: StandInDrone) -> None:
        client = self.a_client(stand_in_drone)
        await client.connect()
        assert await client.position() == (START_LAT_E7, START_LON_E7)

    async def test_upload_sends_seven_items_with_the_right_commands(self, stand_in_drone: StandInDrone) -> None:
        client = self.a_client(stand_in_drone)
        route = a_square_route()
        await client.connect()
        await client.upload_route(route)
        items = stand_in_drone.uploaded_items
        assert [item[0] for item in items] == list(range(ITEM_COUNT))
        assert [item[1] for item in items] == [NAV_TAKEOFF] + [NAV_WAYPOINT] * 5 + [NAV_LAND]
        first, last = route.waypoints[0], route.waypoints[-1]
        assert items[0][2:4] == (first.lat_e7, first.lon_e7)
        assert items[-1][2:4] == (last.lat_e7, last.lon_e7)
        for item, waypoint in zip(items[1:6], route.waypoints):
            assert item[2:5] == (waypoint.lat_e7, waypoint.lon_e7, pytest.approx(waypoint.altitude_m))

    async def test_a_refused_mission_raises_the_refused_error(self, stand_in_drones: StandInDrones) -> None:
        client = self.a_client(stand_in_drones.make(refuse_mission=True))
        await client.connect()
        with pytest.raises(SEMavlinkClientRefusedError):
            await client.upload_route(a_square_route())

    async def test_a_drone_that_refuses_to_arm_times_out(self, stand_in_drones: StandInDrones) -> None:
        client = self.a_client(stand_in_drones.make(refuse_arm=True))
        await client.connect()
        with pytest.raises(SEMavlinkClientTimeoutError):
            await client.arm()

    async def test_start_then_next_reached_gives_every_seq_in_order(self, stand_in_drone: StandInDrone) -> None:
        client = self.a_client(stand_in_drone)
        await client.connect()
        await client.upload_route(a_square_route())
        await client.arm()
        await client.start_route()
        reached = [await client.next_reached() for _ in range(ITEM_COUNT)]
        assert reached == list(range(ITEM_COUNT))

    async def test_a_stalled_route_times_out(self, stand_in_drones: StandInDrones) -> None:
        client = self.a_client(stand_in_drones.make(stall_after_seq=2))
        await client.connect()
        await client.upload_route(a_square_route())
        await client.arm()
        await client.start_route()
        assert [await client.next_reached() for _ in range(3)] == [0, 1, 2]
        with pytest.raises(SEMavlinkClientTimeoutError):
            await client.next_reached()

    async def test_start_before_arming_is_refused(self, stand_in_drone: StandInDrone) -> None:
        client = self.a_client(stand_in_drone)
        await client.connect()
        await client.upload_route(a_square_route())
        with pytest.raises(SEMavlinkClientRefusedError):
            await client.start_route()

    async def test_an_accepted_command_is_true_and_recorded(self, stand_in_drone: StandInDrone) -> None:
        client = self.a_client(stand_in_drone)
        await client.connect()
        assert await client.send_command(MavlinkCommandSpec(command_id=RETURN_TO_LAUNCH)) is True
        assert RETURN_TO_LAUNCH in stand_in_drone.received_commands

    async def test_an_unsupported_command_is_false(self, stand_in_drone: StandInDrone) -> None:
        client = self.a_client(stand_in_drone)
        await client.connect()
        assert await client.send_command(MavlinkCommandSpec(command_id=UNSUPPORTED_COMMAND)) is False
        assert UNSUPPORTED_COMMAND in stand_in_drone.received_commands

    async def test_close_is_safe_twice(self, stand_in_drone: StandInDrone) -> None:
        client = self.a_client(stand_in_drone)
        await client.connect()
        await client.close()
        await client.close()
