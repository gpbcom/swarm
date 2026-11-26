from __future__ import annotations

# First-party imports
from swarm_models.simulation.commands.exceptions.command_mapping_catalog.s_e_invalid_command_mapping_catalog_exception import (
    SEInvalidCommandMappingCatalogException,
)


class SECommandMappingCatalogInvalidCommands(SEInvalidCommandMappingCatalogException):
    """Exception raised when an invalid ``commands`` is provided."""
