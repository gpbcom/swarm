from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from swarm_lifecycle.factories.factory import Factory
from swarm_rest.models.config.rest_config import RestConfig
from swarm_rest.service.idempotency.idempotency_service import IdempotencyService
from swarm_rest.storage.idempotency.memory_idempotency_store import MemoryIdempotencyStore


class IdempotencyServiceFactory(Factory[IdempotencyService]):
    """Builds idempotency services, each with its own in-memory store.

    Attributes:
        config (RestConfig): The settings the store is built from.
    """

    def __init__(self, config: RestConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the factory.

        Args:
            config (RestConfig): The settings the store is built from.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> IdempotencyService:
        """Build one service with a new store.

        Returns:
            IdempotencyService: A service whose store uses ``idempotency_ttl_s`` and ``idempotency_max_entries``.
        """
        store = MemoryIdempotencyStore(self.config.idempotency_ttl_s, self.config.idempotency_max_entries)
        self.logger.debug("Built a store of %d entries.", self.config.idempotency_max_entries)
        return IdempotencyService(store)
