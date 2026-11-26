from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, Literal, Type

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_catalog.models.yaml_catalog import YamlCatalog
from swarm_models.flight.telemetry.exceptions import (
    SEDroneStateCatalogInvalidDefaultState,
    SEDroneStateCatalogInvalidSystemStatusStates,
    SEDroneStateCatalogUnreadable,
)
from swarm_models.telemetry.enums import DroneState


class DroneStateCatalog(YamlCatalog):
    """The state of a Drone for each MAVLink ``system_status``, loaded from ``conf/catalogs/drone_states.yaml``.

    Attributes:
        system_status_states (Dict[int, DroneState]): The state of each listed ``system_status``.
        default_state (DroneState): The state of a ``system_status`` that is not listed.
        UNREADABLE (type[Exception]): The exception raised when the file cannot be read.
        SYSTEM_STATUS_STATES_FIELD (str): The name of the ``system_status_states`` field, for its validator.
        DEFAULT_STATE_FIELD (str): The name of the ``default_state`` field, for its validator.
        SYSTEM_STATUS_MIN (int): The smallest ``system_status``.
        SYSTEM_STATUS_MAX (int): The largest ``system_status``, an unsigned 8-bit integer.
        DEFAULT_STATE (DroneState): The default of ``default_state``, grounded.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        A Drone whose status the catalogue does not list is grounded by default, the safe reading.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    UNREADABLE: ClassVar[type[Exception]] = SEDroneStateCatalogUnreadable
    SYSTEM_STATUS_STATES_FIELD: ClassVar[str] = "system_status_states"
    DEFAULT_STATE_FIELD: ClassVar[str] = "default_state"
    SYSTEM_STATUS_MIN: ClassVar[int] = 0
    SYSTEM_STATUS_MAX: ClassVar[int] = 255
    DEFAULT_STATE: ClassVar[DroneState] = DroneState.GROUNDED
    BEFORE: ClassVar[Literal["before"]] = "before"

    system_status_states: Dict[int, DroneState] = Field(
        default_factory=dict,
        description="The state of a Drone for each MAVLink system_status that is listed.",
    )
    default_state: DroneState = Field(
        default=DEFAULT_STATE,
        description="The state of a Drone whose system_status is not listed. Defaults to grounded.",
    )

    @field_validator(SYSTEM_STATUS_STATES_FIELD, mode=BEFORE)
    def validate_system_status_states(cls, value: JsonValue) -> JsonValue:
        """Validate ``system_status_states``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The mapping from each ``system_status`` to its state, or an empty one when ``None``.

        Raises:
            SEDroneStateCatalogInvalidSystemStatusStates: If a key is not a ``system_status`` or a value is not a
                state of a Drone.
        """
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise SEDroneStateCatalogInvalidSystemStatusStates(
                f"Invalid {cls.SYSTEM_STATUS_STATES_FIELD}: {value!r}. Must be a mapping from a status to a state."
            )
        states: Dict[str, JsonValue] = {}
        for status, state in value.items():
            if isinstance(status, bool) or not isinstance(status, int):
                raise SEDroneStateCatalogInvalidSystemStatusStates(
                    f"Invalid {cls.SYSTEM_STATUS_STATES_FIELD}: {value!r}. Each key must be an integer."
                )
            if status < cls.SYSTEM_STATUS_MIN or status > cls.SYSTEM_STATUS_MAX:
                raise SEDroneStateCatalogInvalidSystemStatusStates(
                    f"Invalid {cls.SYSTEM_STATUS_STATES_FIELD}: {value!r}. "
                    f"Each key must be in [{cls.SYSTEM_STATUS_MIN}, {cls.SYSTEM_STATUS_MAX}]."
                )
            states[str(status)] = cls.parse_state(
                cls.SYSTEM_STATUS_STATES_FIELD, state, SEDroneStateCatalogInvalidSystemStatusStates
            )
        return states

    @field_validator(DEFAULT_STATE_FIELD, mode=BEFORE)
    def validate_default_state(cls, value: JsonValue) -> JsonValue:
        """Validate ``default_state``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The state, or the default when ``None``.

        Raises:
            SEDroneStateCatalogInvalidDefaultState: If the value is not a state of a Drone.
        """
        if value is None:
            return cls.DEFAULT_STATE.value
        return cls.parse_state(cls.DEFAULT_STATE_FIELD, value, SEDroneStateCatalogInvalidDefaultState)

    ############################
    # Internal Helpers Methods #
    ############################

    @classmethod
    def parse_state(cls, field: str, value: JsonValue, error: Type[Exception]) -> str:
        """Parse the state of a Drone.

        Args:
            field (str): The name of the field, for the message.
            value (JsonValue): The raw value, a state name.
            error (Type[Exception]): The exception raised when the value is refused.

        Returns:
            str: The name of the state.

        Raises:
            Exception: The given ``error`` when the value is not a state of a Drone.
        """
        if not isinstance(value, str) or value not in {state.value for state in DroneState}:
            raise error(f"Invalid {field}: {value!r}. Must be a state of a Drone.")
        return str(value)

    ############################
    # Publicly Exposed Methods #
    ############################

    def state_of(self, system_status: int) -> DroneState:
        """Give the state of a Drone for a MAVLink ``system_status``.

        Args:
            system_status (int): The ``system_status`` of the Drone's last heartbeat.

        Returns:
            DroneState: The listed state, or ``default_state`` when the status is not listed.
        """
        return self.system_status_states.get(system_status, self.default_state)
