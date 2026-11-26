from __future__ import annotations

# First-party imports
from flight_engine.models.missions.exceptions.mission_catalog.se_invalid_mission_catalog_exception import (
    SEInvalidMissionCatalogException,
)


class SEMissionCatalogDuplicatePort(SEInvalidMissionCatalogException):
    """Raised when two Missions listen on the same ``mavlink_port``."""
