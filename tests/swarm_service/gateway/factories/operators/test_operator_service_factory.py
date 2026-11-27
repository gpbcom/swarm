from __future__ import annotations

# Third-party imports
from pytest import MonkeyPatch

# First-party imports
from swarm_models.config.gateway.gateway_config import GatewayConfig
from swarm_service.gateway.factories.operators.operator_service_factory import OperatorServiceFactory
from swarm_service.gateway.operators.operator_service import OperatorService


class TestOperatorServiceFactory:
    def test_create_builds_an_operator_service(self) -> None:
        assert isinstance(OperatorServiceFactory(GatewayConfig()).create(), OperatorService)

    def test_each_create_builds_a_new_operator_service(self) -> None:
        factory = OperatorServiceFactory(GatewayConfig())
        assert factory.create() is not factory.create()

    def test_create_needs_neither_the_dsn_nor_the_secret(self, monkeypatch: MonkeyPatch) -> None:
        config = GatewayConfig()
        monkeypatch.delenv(config.postgres.dsn_key, raising=False)
        monkeypatch.delenv(config.operators.keycloak.client_secret_key, raising=False)
        assert isinstance(OperatorServiceFactory(config).create(), OperatorService)
