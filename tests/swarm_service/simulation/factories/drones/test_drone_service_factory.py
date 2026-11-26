from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar

# Third-party imports
import pytest

# First-party imports
from swarm_lifecycle.factories.factory import Factory
from swarm_models.config.app_config import AppConfig
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_models.simulation.registry.exceptions import SEAdapterRegistryHostRefusedError
from swarm_service.simulation.drones.drone_service import DroneService
from swarm_service.simulation.factories.drones.drone_service_factory import DroneServiceFactory
from tests.fakes.mavlink.helpers import DRONE_IDS, OPERATOR_ID


class TestDroneServiceFactory:
    FLIGHT_LOG_PATH_FIELD: ClassVar[str] = "flight_log_path"
    RELATIVE_FLIGHT_LOG: ClassVar[str] = "data/flight_log.sqlite3"
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
        factory = DroneServiceFactory(self._config(tmp_path, "127.0.0.1"))

        service = factory.create()

        assert isinstance(factory, Factory)
        assert isinstance(service, DroneService)
        assert [str(drone.drone_id) for drone in service.registry.drones()] == [DRONE_IDS[0]]

    def test_a_relative_path_is_read_in_the_folder_of_the_app(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        config = self._config(tmp_path, "127.0.0.1")
        relative = config.model_copy(
            update={
                self.FLIGHT_LOG_PATH_FIELD: self.RELATIVE_FLIGHT_LOG,
            }
        )
        monkeypatch.setenv(AppConfig.APP_ROOT_KEY, str(tmp_path))

        service = DroneServiceFactory(relative).create()

        assert service.store.path == str(tmp_path / self.RELATIVE_FLIGHT_LOG)

    def test_a_host_outside_the_simulated_list_is_refused(self, tmp_path: Path) -> None:
        factory = DroneServiceFactory(self._config(tmp_path, "203.0.113.7"))

        with pytest.raises(SEAdapterRegistryHostRefusedError):
            factory.create()
