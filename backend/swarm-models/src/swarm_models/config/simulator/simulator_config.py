from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal, Self, Type, Union
from uuid import UUID

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, ValidationInfo, field_validator, model_validator

# First-party imports
from swarm_models.config.app_config import AppConfig
from swarm_models.config.nats.nats_responder_config import NatsResponderConfig
from swarm_models.config.simulator.exceptions import (
    SESimulatorConfigInvalidFlightLogPath,
    SESimulatorConfigInvalidOperatorId,
    SESimulatorConfigInvalidRest,
    SESimulatorConfigNoCredentials,
    SESimulatorConfigSubjectOutsideOperator,
    SESimulatorConfigUnreadable,
)
from swarm_models.config.simulator.flight_config import FlightConfig
from swarm_models.config.simulator.registry_config import RegistryConfig
from swarm_models.config.simulator.route_config import RouteConfig
from swarm_nats.models.config.nats_client_config import NatsClientConfig
from swarm_web.models.config.rest_config import RestConfig


class SimulatorConfig(AppConfig):
    """The configuration of the simulator app.

    Attributes:
        operator_id (UUID): The Operator the simulated squad belongs to, a UUID version 7.
        nats (NatsClientConfig): The connection to NATS, with the credentials of kind simulated.
        responder (NatsResponderConfig): The responder that serves the commands of the Operator.
        registry (RegistryConfig): Where the catalogues are read and which hosts are simulated.
        route (RouteConfig): The route the simulator flies.
        flight (FlightConfig): The timings of a flight.
        flight_log_path (str): The path of the flight log.
        rest (RestConfig): The settings of the REST server of ``POST /v1/simulations``.
        UNREADABLE (type[Exception]): The exception raised when the file cannot be read.
        OPERATOR_ID_FIELD (str): The name of the ``operator_id`` field.
        FLIGHT_LOG_PATH_FIELD (str): The name of the ``flight_log_path`` field.
        REGISTRY_FIELD (str): The name of the ``registry`` field.
        ROUTE_FIELD (str): The name of the ``route`` field.
        FLIGHT_FIELD (str): The name of the ``flight`` field.
        REST_FIELD (str): The name of the ``rest`` field.
        DEFAULT_FLIGHT_LOG_PATH (str): The default path of the flight log.
        OPERATOR_ID_VERSION (int): The UUID version an Operator identifier must have.
        SUBJECT_PREFIX (str): The start of every subject of an Operator, before its identifier.
        SUBJECT_SEPARATOR (str): The separator between the identifier and the rest of a subject.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.
        AFTER (str): The validator mode that runs after Pydantic's own validation.

    Notes:
        - **The credentials and the subject come from the deployment, never from a default.** A simulated squad
          must not be able to reach another Operator's subjects (BR-014).
        - The nested sections are validated by their own models.
        - The folders of the app come from ``AppConfig``, whose ``APP_ROOT_KEY`` the image sets, and every relative
          path of this configuration is read in the folder of the app.
    """

    UNREADABLE: ClassVar[Type[Exception]] = SESimulatorConfigUnreadable
    OPERATOR_ID_FIELD: ClassVar[str] = "operator_id"
    FLIGHT_LOG_PATH_FIELD: ClassVar[str] = "flight_log_path"
    REGISTRY_FIELD: ClassVar[str] = "registry"
    ROUTE_FIELD: ClassVar[str] = "route"
    FLIGHT_FIELD: ClassVar[str] = "flight"
    REST_FIELD: ClassVar[str] = "rest"
    DEFAULT_FLIGHT_LOG_PATH: ClassVar[str] = "data/flight_log.sqlite3"
    OPERATOR_ID_VERSION: ClassVar[int] = 7
    SUBJECT_PREFIX: ClassVar[str] = "op."
    SUBJECT_SEPARATOR: ClassVar[str] = "."
    BEFORE: ClassVar[Literal["before"]] = "before"
    AFTER: ClassVar[Literal["after"]] = "after"

    model_config = ConfigDict(validate_default=True)

    operator_id: UUID = Field(description="The Operator the simulated squad belongs to, a UUID version 7. Required.")
    nats: NatsClientConfig = Field(description="The connection to NATS, with credentials of kind simulated. Required.")
    responder: NatsResponderConfig = Field(description="The responder that serves the Operator's commands. Required.")
    registry: RegistryConfig = Field(
        default_factory=RegistryConfig,
        description="Where the catalogues are read and which hosts are simulated.",
    )
    route: RouteConfig = Field(default_factory=RouteConfig, description="The route the simulator flies.")
    flight: FlightConfig = Field(default_factory=FlightConfig, description="The timings of a flight.")
    flight_log_path: str = Field(
        default=DEFAULT_FLIGHT_LOG_PATH,
        description="The path of the flight log. Defaults to data/flight_log.sqlite3.",
    )
    rest: RestConfig = Field(default_factory=RestConfig, description="The settings of the REST server.")

    @field_validator(OPERATOR_ID_FIELD, mode=BEFORE)
    def validate_operator_id(cls, value: Union[JsonValue, UUID]) -> Union[JsonValue, UUID]:
        """Validate ``operator_id``.

        Args:
            value (Union[JsonValue, UUID]): The raw input.

        Returns:
            Union[JsonValue, UUID]: The identifier as a UUID.

        Raises:
            SESimulatorConfigInvalidOperatorId: If the value is not a UUID version 7.
        """
        if isinstance(value, UUID):
            identifier = value
        elif isinstance(value, str) and value.strip():
            try:
                identifier = UUID(value.strip())
            except ValueError as error:
                raise SESimulatorConfigInvalidOperatorId(
                    f"Invalid operator_id: {value!r}. Must be a UUID version {cls.OPERATOR_ID_VERSION}."
                ) from error
        else:
            raise SESimulatorConfigInvalidOperatorId(
                f"Invalid operator_id: {value!r}. Must be a UUID version {cls.OPERATOR_ID_VERSION}."
            )
        if identifier.version != cls.OPERATOR_ID_VERSION:
            raise SESimulatorConfigInvalidOperatorId(
                f"Invalid operator_id: {value!r}. Must be a UUID version {cls.OPERATOR_ID_VERSION}."
            )
        return identifier

    @field_validator(REGISTRY_FIELD, ROUTE_FIELD, FLIGHT_FIELD, mode=BEFORE)
    def validate_section(cls, value: Union[JsonValue, BaseModel], info: ValidationInfo) -> Union[JsonValue, BaseModel]:
        """Validate one of the sections that have a default.

        Args:
            value (Union[JsonValue, BaseModel]): The raw input.
            info (ValidationInfo): The field being validated.

        Returns:
            Union[JsonValue, BaseModel]: The section, or the default section when ``None``.
        """
        if value is None:
            return cls.model_fields[str(info.field_name)].get_default(call_default_factory=True)
        return value

    @field_validator(REST_FIELD, mode=BEFORE)
    def validate_rest(cls, value: Union[JsonValue, RestConfig]) -> Union[JsonValue, RestConfig]:
        """Validate ``rest``.

        Args:
            value (Union[JsonValue, RestConfig]): The raw input.

        Returns:
            Union[JsonValue, RestConfig]: The section, or the default section when ``None``.

        Raises:
            SESimulatorConfigInvalidRest: If the value is neither a mapping nor a RestConfig.
        """
        if value is None:
            return cls.model_fields[cls.REST_FIELD].get_default(call_default_factory=True)
        if not isinstance(value, (dict, RestConfig)):
            raise SESimulatorConfigInvalidRest(f"Invalid rest: {type(value).__name__}. Must be a mapping.")
        return value

    @field_validator(FLIGHT_LOG_PATH_FIELD, mode=BEFORE)
    def validate_flight_log_path(cls, value: JsonValue) -> JsonValue:
        """Validate ``flight_log_path``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped path, or the default when ``None``.

        Raises:
            SESimulatorConfigInvalidFlightLogPath: If the value is not a non-empty string.
        """
        if value is None:
            return cls.DEFAULT_FLIGHT_LOG_PATH
        if not isinstance(value, str) or not value.strip():
            raise SESimulatorConfigInvalidFlightLogPath(
                f"Invalid flight_log_path: {value!r}. Must be a non-empty string."
            )
        return value.strip()

    @model_validator(mode=AFTER)
    def validate_deployment(self) -> Self:
        """Check the values the deployment gives.

        Returns:
            Self: This configuration.

        Raises:
            SESimulatorConfigNoCredentials: If no NATS credentials file is given.
            SESimulatorConfigSubjectOutsideOperator: If the responder subject is not under the Operator.
        """
        if self.nats.credentials_path is None:
            raise SESimulatorConfigNoCredentials(
                "Invalid nats: no credentials_path. Must name a credentials file of kind simulated."
            )
        prefix = f"{self.SUBJECT_PREFIX}{self.operator_id}{self.SUBJECT_SEPARATOR}"
        if not self.responder.subject.startswith(prefix):
            raise SESimulatorConfigSubjectOutsideOperator(
                f"Invalid subject: {self.responder.subject!r}. Must start with {prefix!r}."
            )
        return self
