from __future__ import annotations

from typing import ClassVar

from swarm_lifecycle.factories.factory import Factory
from swarm_rest.models.config.rest_config import RestConfig
from swarm_rest.service.factories.idempotency_service_factory import IdempotencyServiceFactory
from swarm_rest.service.idempotency.idempotency_service import IdempotencyService


class TestIdempotencyServiceFactory:
    TTL_S: ClassVar[float] = 120.5
    MAX_ENTRIES: ClassVar[int] = 7

    def a_config(self) -> RestConfig:
        return RestConfig(idempotency_ttl_s=self.TTL_S, idempotency_max_entries=self.MAX_ENTRIES)

    def test_the_factory_is_a_factory_of_idempotency_services(self) -> None:
        assert isinstance(IdempotencyServiceFactory(self.a_config()), Factory)

    def test_create_returns_a_service_whose_store_uses_the_configuration(self) -> None:
        service = IdempotencyServiceFactory(self.a_config()).create()
        assert isinstance(service, IdempotencyService)
        assert service.store.ttl_s == self.TTL_S
        assert service.store.max_entries == self.MAX_ENTRIES

    def test_two_created_services_have_distinct_stores(self) -> None:
        factory = IdempotencyServiceFactory(self.a_config())
        assert factory.create().store is not factory.create().store
