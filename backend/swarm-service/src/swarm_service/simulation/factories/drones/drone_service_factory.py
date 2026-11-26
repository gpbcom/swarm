from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from pathlib import Path
from typing import Optional

# First-party imports
from simulator.models.commands.command_mapping_catalog import CommandMappingCatalog
from simulator.models.config.simulator_config import SimulatorConfig
from simulator.models.registry.simulated_squad_catalog import SimulatedSquadCatalog
from simulator.service.commands.simulated_command_service import SimulatedCommandService
from simulator.service.registry.adapter_registry import AdapterRegistry
from simulator.storage.edge.flight_log_store import FlightLogStore
from swarm_lifecycle.factories.factory import Factory


class SimulatedCommandServiceFactory(Factory[SimulatedCommandService]):
    """Build the simulated command service from the Simulator's configuration.

    Attributes:
        config (SimulatorConfig): The configuration of the Simulator.

    Notes:
        - The registry is loaded here, so a Drone on a host outside ``simulated_hosts`` stops the build (BR-014).
    """

    def __init__(self, config: SimulatorConfig, logger: Optional[Logger] = None) -> None:
        """Create the factory.

        Args:
            config (SimulatorConfig): The configuration of the Simulator.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> SimulatedCommandService:
        """Build the service, with its registry loaded and its store not yet open.

        Returns:
            SimulatedCommandService: The new service.
        """
        registry_config = self.config.registry
        squad = SimulatedSquadCatalog.load(Path(registry_config.squad_catalog_path))
        mapping = CommandMappingCatalog.load(Path(registry_config.command_mapping_path))
        registry = AdapterRegistry(registry_config.simulated_hosts)
        registry.load(squad)
        store = FlightLogStore(self.config.flight_log_path)
        self.logger.debug("Built the registry of %d Drones.", len(squad.drones))
        return SimulatedCommandService(registry, store, mapping, self.config.flight)
