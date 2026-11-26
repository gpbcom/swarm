from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from swarm_lifecycle.factories.factory import Factory
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_models.simulation.commands.command_mapping_catalog import CommandMappingCatalog
from swarm_models.simulation.registry.simulated_squad_catalog import SimulatedSquadCatalog
from swarm_service.simulation.drones.drone_service import DroneService
from swarm_service.simulation.registry.adapter_registry import AdapterRegistry
from swarm_service.simulation.routes.square_route_builder import SquareRouteBuilder
from swarm_storage.simulation.flight_logs.flight_log_store import FlightLogStore


class DroneServiceFactory(Factory[DroneService]):
    """Build the Drone service from the Simulator's configuration.

    Attributes:
        config (SimulatorConfig): The configuration of the Simulator.

    Notes:
        - The registry is loaded here, so a Drone on a host outside ``simulated_hosts`` stops the build (BR-014).
        - **The paths of the configuration are read in the app's folder** (``SimulatorConfig.in_app_folder``), so that
          a relative path means the same file whatever folder the app starts in.
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

    def _build(self) -> DroneService:
        """Build the service, with its registry loaded and its store not yet open.

        Returns:
            DroneService: The new service.
        """
        registry_config = self.config.registry
        squad = SimulatedSquadCatalog.load(SimulatorConfig.in_app_folder(registry_config.squad_catalog_path))
        mapping = CommandMappingCatalog.load(SimulatorConfig.in_app_folder(registry_config.command_mapping_path))
        registry = AdapterRegistry(registry_config.simulated_hosts)
        registry.load(squad)
        store = FlightLogStore(str(SimulatorConfig.in_app_folder(self.config.flight_log_path)))
        builder = SquareRouteBuilder(self.config.route)
        self.logger.debug("Built the registry of %d Drones.", len(squad.drones))
        return DroneService(registry, store, mapping, builder, self.config.flight)
