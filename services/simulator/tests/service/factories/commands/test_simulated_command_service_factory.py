from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import pytest

from services.simulator.tests.helpers import DRONE_IDS, OPERATOR_ID
from simulator.models.config.simulator_config import SimulatorConfig
from simulator.models.registry.exceptions import SEAdapterRegistryHostRefusedError
from simulator.service.commands.simulated_command_service import SimulatedCommandService
from simulator.service.factories.commands.simulated_command_service_factory import SimulatedCommandServiceFactory
from swarm_lifecycle.factories.factory import Factory


class TestSimulatedCommandServiceFactory:
    SQUAD_YAML: ClassVar[str] = (
        "drones:\n  - drone_id: {drone_id}\n    kind: synthetic\n    host: {host}\n    port: 14600\n    system_id: 1\n"
    )
    MAPPING_YAML: ClassVar[str] = (
        "commands:\n  hold:\n    command_id: 193\n    param1: 0.0\n  return_home:\n    command_id: 20\n"
    )
    CONFIG_YAML: ClassVar[str] = (
        "operator_id: {operator_id}\n"
        "nats:\n"
        "  credentials_path: {folder}/simulated.creds\n"
        "responder:\n"
        "  subject: op.{operator_id}.mission.*.command\n"
        "  queue_group: simulator\n"
        "registry:\n"
        "  squad_catalog_path: {folder}/squad.yaml\n"
        "  command_mapping_path: {folder}/mapping.yaml\n"
        "flight_log_path: {folder}/flight_log.sqlite3\n"
    )

    def _config(self, tmp_path: Path, host: str) -> SimulatorConfig:
        squad = self.SQUAD_YAML.format(drone_id=DRONE_IDS[0], host=host)
        (tmp_path / "squad.yaml").write_text(squad, encoding="utf-8")
        (tmp_path / "mapping.yaml").write_text(self.MAPPING_YAML, encoding="utf-8")
        path = tmp_path / "app.yaml"
        path.write_text(self.CONFIG_YAML.format(operator_id=OPERATOR_ID, folder=tmp_path), encoding="utf-8")
        return SimulatorConfig.load(path)

    def test_the_factory_builds_a_service_from_the_catalogs(self, tmp_path: Path) -> None:
        factory = SimulatedCommandServiceFactory(self._config(tmp_path, "127.0.0.1"))

        service = factory.create()

        assert isinstance(factory, Factory)
        assert isinstance(service, SimulatedCommandService)
        assert [str(drone.drone_id) for drone in service.registry.drones()] == [DRONE_IDS[0]]

    def test_a_host_outside_the_simulated_list_is_refused(self, tmp_path: Path) -> None:
        factory = SimulatedCommandServiceFactory(self._config(tmp_path, "203.0.113.7"))

        with pytest.raises(SEAdapterRegistryHostRefusedError):
            factory.create()
