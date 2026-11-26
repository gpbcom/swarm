from __future__ import annotations

# Standard library imports
from typing import ClassVar, List, Literal
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.simulation.simulations.exceptions import (
    SESimulationAcceptedInvalidDroneIds,
    SESimulationAcceptedInvalidMissionId,
)


class SimulationAccepted(SwarmModel):
    """The answer of ``POST /v1/simulations``: the simulated flight that has started.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the answer.
        mission_id (UUID): The Mission the simulated Flight log belongs to.
        drone_ids (List[UUID]): The simulated Drones that fly, in the order of the adapter registry.
        MISSION_ID_FIELD (ClassVar[str]): The name of the ``mission_id`` field.
        DRONE_IDS_FIELD (ClassVar[str]): The name of the ``drone_ids`` field.
        BEFORE (ClassVar[Literal["before"]]): The validator mode that runs before Pydantic's own validation.

    Notes:
        - The flight goes on after the answer: its progress and its end are in the simulated Flight log of the
          Mission, as they were for ``fly``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    MISSION_ID_FIELD: ClassVar[str] = "mission_id"
    DRONE_IDS_FIELD: ClassVar[str] = "drone_ids"
    BEFORE: ClassVar[Literal["before"]] = "before"

    mission_id: UUID = Field(description="The Mission the simulated Flight log belongs to, a UUID version 7.")
    drone_ids: List[UUID] = Field(description="The simulated Drones that fly, in the order of the adapter registry.")

    @field_validator(MISSION_ID_FIELD, mode=BEFORE)
    def validate_mission_id(cls, value: JsonValue) -> UUID:
        """Validate ``mission_id``.

        Args:
            value (JsonValue): A version 7 UUID or its string form.

        Returns:
            UUID: The identifier.

        Raises:
            SESimulationAcceptedInvalidMissionId: When the value is not a version 7 UUID.
        """
        return cls.parse_uuid7(cls.MISSION_ID_FIELD, value, SESimulationAcceptedInvalidMissionId)

    @field_validator(DRONE_IDS_FIELD, mode=BEFORE)
    def validate_drone_ids(cls, value: JsonValue) -> List[UUID]:
        """Validate ``drone_ids``.

        Args:
            value (JsonValue): A list of version 7 UUIDs or of their string forms.

        Returns:
            List[UUID]: The identifiers.

        Raises:
            SESimulationAcceptedInvalidDroneIds: When the value is not a list of version 7 UUIDs.
        """
        if not isinstance(value, list):
            raise SESimulationAcceptedInvalidDroneIds(f"Invalid drone_ids: {value!r}. Must be a list of UUIDs.")
        return [cls.parse_uuid7(cls.DRONE_IDS_FIELD, item, SESimulationAcceptedInvalidDroneIds) for item in value]
