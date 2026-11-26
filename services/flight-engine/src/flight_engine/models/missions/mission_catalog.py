from __future__ import annotations

# Standard library imports
from typing import ClassVar, List, Literal, Self, Set
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator, model_validator

# First-party imports
from flight_engine.models.missions.exceptions import (
    SEMissionCatalogDuplicateMission,
    SEMissionCatalogDuplicatePort,
    SEMissionCatalogInvalidMissions,
    SEMissionCatalogUnreadable,
)
from flight_engine.models.missions.mission_entry import MissionEntry
from swarm_catalog.models.yaml_catalog import YamlCatalog


class MissionCatalog(YamlCatalog):
    """The Missions the engine flies, loaded from ``conf/catalogs/missions.yaml``.

    Attributes:
        missions (List[MissionEntry]): The Missions, each with its own MAVLink port.
        UNREADABLE (type[Exception]): The exception raised when the file cannot be read.
        MISSIONS_FIELD (str): The name of the ``missions`` field, for its validator.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.
        AFTER (str): The validator mode that runs after Pydantic's own validation.

    Notes:
        - Until the Pre-flight check copy arrives, the Missions of the edge come from this catalogue.
        - A Mission id and a MAVLink port are each used once, so a frame maps to one Mission.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    UNREADABLE: ClassVar[type[Exception]] = SEMissionCatalogUnreadable
    MISSIONS_FIELD: ClassVar[str] = "missions"
    BEFORE: ClassVar[Literal["before"]] = "before"
    AFTER: ClassVar[Literal["after"]] = "after"

    missions: List[MissionEntry] = Field(default_factory=list, description="The Missions the engine flies.")

    @field_validator(MISSIONS_FIELD, mode=BEFORE)
    def validate_missions(cls, value: JsonValue) -> JsonValue:
        """Validate ``missions``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The list of Missions, left for Pydantic to build, or an empty one when ``None``.

        Raises:
            SEMissionCatalogInvalidMissions: If the value is not a list of mappings.
        """
        if value is None:
            return []
        if not isinstance(value, list) or not all(isinstance(item, (dict, MissionEntry)) for item in value):
            raise SEMissionCatalogInvalidMissions(f"Invalid missions: {value!r}. Must be a list of Missions.")
        return value

    @model_validator(mode=AFTER)
    def validate_unique_missions(self) -> Self:
        """Check that no Mission id and no MAVLink port is used twice.

        Returns:
            Self: The catalogue.

        Raises:
            SEMissionCatalogDuplicateMission: If two Missions have the same id.
            SEMissionCatalogDuplicatePort: If two Missions have the same MAVLink port.
        """
        mission_ids: Set[UUID] = set()
        ports: Set[int] = set()
        for mission in self.missions:
            if mission.mission_id in mission_ids:
                raise SEMissionCatalogDuplicateMission(
                    f"Duplicate mission_id: {str(mission.mission_id)!r}. Must be used once."
                )
            if mission.mavlink_port in ports:
                raise SEMissionCatalogDuplicatePort(
                    f"Duplicate mavlink_port: {mission.mavlink_port!r}. Must be used once."
                )
            mission_ids.add(mission.mission_id)
            ports.add(mission.mavlink_port)
        return self
