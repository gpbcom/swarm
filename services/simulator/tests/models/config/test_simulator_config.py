from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Dict

import pytest
import yaml
from pydantic import JsonValue, ValidationError

from simulator.models.config.exceptions import (
    SEFlightConfigInvalidArmTimeout,
    SESimulatorConfigInvalidFlightLogPath,
    SESimulatorConfigInvalidOperatorId,
    SESimulatorConfigNoCredentials,
    SESimulatorConfigSubjectOutsideOperator,
    SESimulatorConfigUnreadable,
)
from simulator.models.config.flight_config import FlightConfig
from simulator.models.config.registry_config import RegistryConfig
from simulator.models.config.route_config import RouteConfig
from simulator.models.config.simulator_config import SimulatorConfig
from swarm_catalog.models.yaml_catalog import YamlCatalog
from swarm_nats.models.config.nats_client_config import NatsClientConfig
from swarm_nats.models.config.nats_responder_config import NatsResponderConfig


class TestSimulatorConfig:
    OPERATOR_ID: ClassVar[str] = "018f4c1e-5b7a-7c3e-9a1b-2d4e6f8a0b1c"
    VERSION_4_ID: ClassVar[str] = "6f1c2a4e-8b3d-4c5e-9a7f-1d2e3f4a5b6c"
    CREDENTIALS_PATH: ClassVar[str] = "creds/simulated.creds"
    SUBJECT: ClassVar[str] = "op.018f4c1e-5b7a-7c3e-9a1b-2d4e6f8a0b1c.mission.*.command"
    APP_YAML: ClassVar[Path] = Path(__file__).resolve().parents[3] / "conf" / "app.yaml"
    OPERATOR_ID_KEY: ClassVar[str] = "operator_id"
    NATS_KEY: ClassVar[str] = "nats"
    RESPONDER_KEY: ClassVar[str] = "responder"
    CREDENTIALS_PATH_KEY: ClassVar[str] = "credentials_path"
    SUBJECT_KEY: ClassVar[str] = "subject"
    QUEUE_GROUP_KEY: ClassVar[str] = "queue_group"
    FLIGHT_LOG_PATH_KEY: ClassVar[str] = "flight_log_path"
    QUEUE_GROUP: ClassVar[str] = "simulator"
    ENCODING: ClassVar[str] = "utf-8"

    def required(self) -> Dict[str, JsonValue]:
        return {
            self.OPERATOR_ID_KEY: self.OPERATOR_ID,
            self.NATS_KEY: {self.CREDENTIALS_PATH_KEY: self.CREDENTIALS_PATH},
            self.RESPONDER_KEY: {self.SUBJECT_KEY: self.SUBJECT, self.QUEUE_GROUP_KEY: self.QUEUE_GROUP},
        }

    def test_it_is_a_yaml_catalog_that_names_its_own_error(self) -> None:
        assert issubclass(SimulatorConfig, YamlCatalog)
        assert SimulatorConfig.UNREADABLE is SESimulatorConfigUnreadable

    def test_defaults(self) -> None:
        config = SimulatorConfig.model_validate(self.required())
        assert str(config.operator_id) == self.OPERATOR_ID
        assert config.registry == RegistryConfig()
        assert config.route == RouteConfig()
        assert config.flight == FlightConfig()
        assert config.flight_log_path == "data/flight_log.sqlite3"
        assert config.nats.credentials_path == self.CREDENTIALS_PATH
        assert config.responder.subject == self.SUBJECT

    def test_full_valid_construction(self) -> None:
        config = SimulatorConfig(
            operator_id=self.OPERATOR_ID,
            nats=NatsClientConfig(credentials_path=self.CREDENTIALS_PATH),
            responder=NatsResponderConfig(subject=self.SUBJECT, queue_group=self.QUEUE_GROUP),
            registry=RegistryConfig(simulated_hosts=["sim"]),
            route=RouteConfig(side_m=10.0),
            flight=FlightConfig(arm_timeout_s=9.0),
            flight_log_path="other/log.sqlite3",
        )
        assert config.registry.simulated_hosts == ["sim"]
        assert config.route.side_m == 10.0
        assert config.flight.arm_timeout_s == 9.0
        assert config.flight_log_path == "other/log.sqlite3"

    def test_none_becomes_the_default(self) -> None:
        config = SimulatorConfig.model_validate({**self.required(), self.FLIGHT_LOG_PATH_KEY: None})
        default = SimulatorConfig.model_fields[self.FLIGHT_LOG_PATH_KEY].get_default(call_default_factory=True)
        assert config.flight_log_path == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("operator_id", "", SESimulatorConfigInvalidOperatorId),
            ("operator_id", "not_a_uuid", SESimulatorConfigInvalidOperatorId),
            ("operator_id", VERSION_4_ID, SESimulatorConfigInvalidOperatorId),
            ("operator_id", 3, SESimulatorConfigInvalidOperatorId),
            ("operator_id", None, SESimulatorConfigInvalidOperatorId),
            ("flight_log_path", "", SESimulatorConfigInvalidFlightLogPath),
            ("flight_log_path", "   ", SESimulatorConfigInvalidFlightLogPath),
            ("flight_log_path", 3, SESimulatorConfigInvalidFlightLogPath),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            SimulatorConfig.model_validate({**self.required(), name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            SimulatorConfig.model_validate({**self.required(), "colour": "red"})

    def test_round_trip(self) -> None:
        config = SimulatorConfig.model_validate(self.required())
        data: Dict[str, JsonValue] = config.model_dump()
        assert SimulatorConfig.model_validate(data) == config

    def test_a_nested_section_is_validated_by_its_own_model(self) -> None:
        with pytest.raises(SEFlightConfigInvalidArmTimeout):
            SimulatorConfig.model_validate({**self.required(), "flight": {"arm_timeout_s": 0}})

    @pytest.mark.parametrize("name", ["nats", "responder"])
    def test_a_missing_required_section_is_refused(self, name: str) -> None:
        data = {key: value for key, value in self.required().items() if key != name}
        with pytest.raises(ValidationError):
            SimulatorConfig.model_validate(data)

    def test_a_missing_operator_id_is_refused(self) -> None:
        data = {key: value for key, value in self.required().items() if key != self.OPERATOR_ID_KEY}
        with pytest.raises((ValidationError, SESimulatorConfigInvalidOperatorId)):
            SimulatorConfig.model_validate(data)

    @pytest.mark.parametrize(
        "subject",
        [
            "op.018f4c1e-5b7a-7c3e-9a1b-2d4e6f8a0b1d.mission.*.command",
            "mission.*.command",
            "op.018f4c1e-5b7a-7c3e-9a1b-2d4e6f8a0b1c",
            "op.018f4c1e-5b7a-7c3e-9a1b-2d4e6f8a0b1cx.mission.*.command",
        ],
    )
    def test_a_subject_outside_the_operator_is_refused(self, subject: str) -> None:
        data = self.required()
        data[self.RESPONDER_KEY] = {self.SUBJECT_KEY: subject, self.QUEUE_GROUP_KEY: self.QUEUE_GROUP}
        with pytest.raises(SESimulatorConfigSubjectOutsideOperator):
            SimulatorConfig.model_validate(data)

    def test_a_simulated_squad_without_credentials_is_refused(self) -> None:
        data = self.required()
        data[self.NATS_KEY] = {}
        with pytest.raises(SESimulatorConfigNoCredentials):
            SimulatorConfig.model_validate(data)

    def test_load_reads_a_yaml_file(self, tmp_path: Path) -> None:
        path = tmp_path / "config.yaml"
        path.write_text(yaml.safe_dump(self.required()), encoding=self.ENCODING)
        assert SimulatorConfig.load(path) == SimulatorConfig.model_validate(self.required())

    def test_a_missing_file_is_unreadable(self, tmp_path: Path) -> None:
        with pytest.raises(SESimulatorConfigUnreadable):
            SimulatorConfig.load(tmp_path / "missing.yaml")

    def test_a_file_that_is_not_a_mapping_is_unreadable(self, tmp_path: Path) -> None:
        path = tmp_path / "list.yaml"
        path.write_text("- a\n- b\n", encoding=self.ENCODING)
        with pytest.raises(SESimulatorConfigUnreadable):
            SimulatorConfig.load(path)

    def test_the_application_file_loads_with_the_deployment_values_and_keeps_every_default(
        self, tmp_path: Path
    ) -> None:
        data = yaml.safe_load(self.APP_YAML.read_text(encoding=self.ENCODING))
        assert isinstance(data, dict)
        data[self.OPERATOR_ID_KEY] = self.OPERATOR_ID
        data.setdefault(self.NATS_KEY, {})[self.CREDENTIALS_PATH_KEY] = self.CREDENTIALS_PATH
        data.setdefault(self.RESPONDER_KEY, {})[self.SUBJECT_KEY] = self.SUBJECT
        copy = tmp_path / "app.yaml"
        copy.write_text(yaml.safe_dump(data), encoding=self.ENCODING)
        config = SimulatorConfig.load(copy)
        assert str(config.operator_id) == self.OPERATOR_ID
        assert config.registry == RegistryConfig()
        assert config.route == RouteConfig()
        assert config.flight == FlightConfig()
        assert config.flight_log_path == SimulatorConfig.model_fields[self.FLIGHT_LOG_PATH_KEY].get_default()
        assert config.nats == NatsClientConfig(credentials_path=self.CREDENTIALS_PATH)
        ignored = {self.SUBJECT_KEY, self.QUEUE_GROUP_KEY}
        responder_defaults = NatsResponderConfig(subject=self.SUBJECT, queue_group=config.responder.queue_group)
        assert config.responder.model_dump(exclude=ignored) == responder_defaults.model_dump(exclude=ignored)
