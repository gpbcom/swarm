from __future__ import annotations

# First-party imports
from flight_engine.models.missions.exceptions.mission_catalog.se_invalid_mission_catalog_exception import (
    SEInvalidMissionCatalogException,
)


class SEMissionCatalogDuplicateMission(SEInvalidMissionCatalogException):
    """Raised when two Missions have the same ``mission_id``."""
