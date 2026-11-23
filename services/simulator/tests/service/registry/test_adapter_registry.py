from __future__ import annotations

# Standard library imports
from logging import ERROR
from typing import ClassVar, List
from uuid import UUID

# Third-party imports
import pytest

# First-party imports
from simulator.models.enums import SimulatedDroneKind
from simulator.models.registry.exceptions import (
    SEAdapterRegistryDuplicateDroneError,
    SEAdapterRegistryHostRefusedError,
    SEAdapterRegistryUnknownDroneError,
)
from simulator.models.registry.registered_drone import RegisteredDrone
from simulator.models.registry.simulated_squad_catalog import SimulatedSquadCatalog
from simulator.service.registry.adapter_registry import AdapterRegistry


class TestAdapterRegistry:
    SIMULATED_HOSTS: ClassVar[List[str]] = ["synthetic-drones", "px4-sitl"]
    SYNTHETIC_HOST: ClassVar[str] = "synthetic-drones"
    SITL_HOST: ClassVar[str] = "px4-sitl"
    REAL_HOST: ClassVar[str] = "10.0.0.7"
    FIRST_ID: ClassVar[UUID] = UUID("01927f3e-8a1b-7c4d-9e2f-3a4b5c6d7e01")
    SECOND_ID: ClassVar[UUID] = UUID("01927f3e-8a1b-7c4d-9e2f-3a4b5c6d7e02")
    THIRD_ID: ClassVar[UUID] = UUID("01927f3e-8a1b-7c4d-9e2f-3a4b5c6d7e03")
    UNKNOWN_ID: ClassVar[UUID] = UUID("01927f3e-8a1b-7c4d-9e2f-3a4b5c6d7eff")

    def a_drone(self, drone_id: UUID, host: str = SYNTHETIC_HOST, port: int = 14600) -> RegisteredDrone:
        return RegisteredDrone(
            drone_id=drone_id,
            kind=SimulatedDroneKind.SYNTHETIC,
            host=host,
            port=port,
            system_id=1,
        )

    def test_registering_and_resolving_works(self) -> None:
        registry = AdapterRegistry(self.SIMULATED_HOSTS)
        drone = self.a_drone(self.FIRST_ID)
        registry.register(drone)
        assert registry.resolve(self.FIRST_ID) == drone
        assert registry.contains(self.FIRST_ID)

    def test_a_host_not_in_the_list_is_refused_and_nothing_is_registered(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        registry = AdapterRegistry(self.SIMULATED_HOSTS)
        with caplog.at_level(ERROR), pytest.raises(SEAdapterRegistryHostRefusedError):
            registry.register(self.a_drone(self.FIRST_ID, host=self.REAL_HOST))
        assert any(record.levelno == ERROR for record in caplog.records)
        assert not registry.contains(self.FIRST_ID)
        assert registry.drones() == []

    def test_a_duplicate_is_refused(self, caplog: pytest.LogCaptureFixture) -> None:
        registry = AdapterRegistry(self.SIMULATED_HOSTS)
        registry.register(self.a_drone(self.FIRST_ID))
        with caplog.at_level(ERROR), pytest.raises(SEAdapterRegistryDuplicateDroneError):
            registry.register(self.a_drone(self.FIRST_ID, port=14601))
        assert any(record.levelno == ERROR for record in caplog.records)
        assert len(registry.drones()) == 1

    def test_an_unknown_drone_id_is_refused_and_logged(self, caplog: pytest.LogCaptureFixture) -> None:
        registry = AdapterRegistry(self.SIMULATED_HOSTS)
        with caplog.at_level(ERROR), pytest.raises(SEAdapterRegistryUnknownDroneError):
            registry.resolve(self.UNKNOWN_ID)
        errors = [record for record in caplog.records if record.levelno == ERROR]
        assert errors
        assert any(str(self.UNKNOWN_ID) in record.getMessage() for record in errors)
        assert not registry.contains(self.UNKNOWN_ID)

    def test_load_registers_a_whole_catalog(self) -> None:
        registry = AdapterRegistry(self.SIMULATED_HOSTS)
        catalog = SimulatedSquadCatalog(
            drones=[
                self.a_drone(self.FIRST_ID, port=14600),
                self.a_drone(self.SECOND_ID, port=14601),
                self.a_drone(self.THIRD_ID, host=self.SITL_HOST, port=18570),
            ]
        )
        registry.load(catalog)
        assert registry.drones() == catalog.drones
        assert registry.contains(self.THIRD_ID)

    def test_drones_keeps_the_registration_order(self) -> None:
        registry = AdapterRegistry(self.SIMULATED_HOSTS)
        third = self.a_drone(self.THIRD_ID, port=14602)
        first = self.a_drone(self.FIRST_ID, port=14600)
        second = self.a_drone(self.SECOND_ID, port=14601)
        for drone in (third, first, second):
            registry.register(drone)
        assert registry.drones() == [third, first, second]
