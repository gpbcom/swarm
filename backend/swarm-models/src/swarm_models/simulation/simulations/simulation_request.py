from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.simulation.simulations.exceptions import SESimulationRequestInvalidMissionId


class SimulationRequest(SwarmModel):
    """The body of ``POST /v1/simulations``: what a simulated flight of the Squad is started for.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the request.
        mission_id (UUID): The Mission the simulated Flight log belongs to, a UUID version 7.
        MISSION_ID_FIELD (ClassVar[str]): The name of the ``mission_id`` field.
        BEFORE (ClassVar[Literal["before"]]): The validator mode that runs before Pydantic's own validation.

    Notes:
        - It holds what the command line of ``fly`` took, the configuration aside: the app reads that from its own
          ``conf/app.yaml``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    MISSION_ID_FIELD: ClassVar[str] = "mission_id"
    BEFORE: ClassVar[Literal["before"]] = "before"

    mission_id: UUID = Field(description="The Mission the simulated Flight log belongs to, a UUID version 7.")

    @field_validator(MISSION_ID_FIELD, mode=BEFORE)
    def validate_mission_id(cls, value: JsonValue) -> UUID:
        """Validate ``mission_id``.

        Args:
            value (JsonValue): A version 7 UUID or its string form.

        Returns:
            UUID: The identifier.

        Raises:
            SESimulationRequestInvalidMissionId: When the value is not a version 7 UUID.
        """
        return cls.parse_uuid7(cls.MISSION_ID_FIELD, value, SESimulationRequestInvalidMissionId)
