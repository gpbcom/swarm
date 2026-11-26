from __future__ import annotations

# Standard library imports
from typing import ClassVar, List, Literal, Mapping

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from simulator.models.routes.exceptions import SERouteInvalidWaypoints
from simulator.models.routes.waypoint import Waypoint
from swarm_models.base.swarm_model import SwarmModel


class Route(SwarmModel):
    """The ordered waypoints a drone flies.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the route.
        waypoints (List[Waypoint]): The waypoints, in the order they are flown.
        WAYPOINTS_FIELD (str): The name of the ``waypoints`` field, for its validator.
        WAYPOINTS_MIN (int): The fewest waypoints a route holds.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - A waypoint may be given as a ``Waypoint`` or as a mapping.
        - ``waypoints`` has no default, so ``None`` is refused.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    WAYPOINTS_FIELD: ClassVar[str] = "waypoints"
    WAYPOINTS_MIN: ClassVar[int] = 2
    BEFORE: ClassVar[Literal["before"]] = "before"

    waypoints: List[Waypoint] = Field(description="The waypoints, in the order they are flown.")

    ############################
    # Publicly Exposed Methods #
    ############################

    @field_validator(WAYPOINTS_FIELD, mode=BEFORE)
    def validate_waypoints(cls, value: JsonValue) -> JsonValue:
        """Validate ``waypoints``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The list of waypoints.

        Raises:
            SERouteInvalidWaypoints: When the value is not a list of at least two waypoints.
        """
        if not isinstance(value, list) or len(value) < cls.WAYPOINTS_MIN:
            raise SERouteInvalidWaypoints(
                f"Invalid {cls.WAYPOINTS_FIELD}: {value!r}. Must be a list of at least {cls.WAYPOINTS_MIN} waypoints."
            )
        for item in value:
            if not isinstance(item, (Waypoint, Mapping)):
                raise SERouteInvalidWaypoints(
                    f"Invalid {cls.WAYPOINTS_FIELD}: {item!r}. Every waypoint must be a Waypoint or a mapping."
                )
        return value
