from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal, Tuple

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.keycloak.exceptions import (
    SEKeycloakAdminConfigInvalidClientId,
    SEKeycloakAdminConfigInvalidClientSecretKey,
    SEKeycloakAdminConfigInvalidRealm,
    SEKeycloakAdminConfigInvalidRequestTimeoutS,
    SEKeycloakAdminConfigInvalidServerUrl,
    SEKeycloakAdminConfigInvalidSignInClientId,
)


class KeycloakAdminConfig(BaseModel):
    """The configuration of the calls the gateway makes to the Keycloak admin API.

    Attributes:
        server_url (str): The base URL of Keycloak, without a trailing slash.
        realm (str): The realm that holds the Operators' accounts.
        client_id (str): The confidential client the gateway signs in with.
        client_secret_key (str): The environment entry that holds the secret of ``client_id``.
        sign_in_client_id (str): The client of the application a new person signs in to.
        request_timeout_s (float): The timeout of a call to Keycloak, in seconds.
        SERVER_URL_FIELD (str): The name of the ``server_url`` field.
        REALM_FIELD (str): The name of the ``realm`` field.
        CLIENT_ID_FIELD (str): The name of the ``client_id`` field.
        CLIENT_SECRET_KEY_FIELD (str): The name of the ``client_secret_key`` field.
        SIGN_IN_CLIENT_ID_FIELD (str): The name of the ``sign_in_client_id`` field.
        REQUEST_TIMEOUT_S_FIELD (str): The name of the ``request_timeout_s`` field.
        DEFAULT_SERVER_URL (str): The default Keycloak service of the global layer.
        DEFAULT_REALM (str): The default realm.
        DEFAULT_CLIENT_ID (str): The default admin client.
        DEFAULT_CLIENT_SECRET_KEY (str): The default environment entry of the secret.
        DEFAULT_SIGN_IN_CLIENT_ID (str): The default sign-in client.
        DEFAULT_REQUEST_TIMEOUT_S (float): The default timeout.
        URL_SCHEMES (Tuple[str, ...]): The schemes a server URL may start with.
        TRAILING_SLASH (str): The character removed from the end of the server URL.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - **The secret is never here**: ``client_secret_key`` only names the environment entry that holds it.
    """

    SERVER_URL_FIELD: ClassVar[str] = "server_url"
    REALM_FIELD: ClassVar[str] = "realm"
    CLIENT_ID_FIELD: ClassVar[str] = "client_id"
    CLIENT_SECRET_KEY_FIELD: ClassVar[str] = "client_secret_key"
    SIGN_IN_CLIENT_ID_FIELD: ClassVar[str] = "sign_in_client_id"
    REQUEST_TIMEOUT_S_FIELD: ClassVar[str] = "request_timeout_s"
    DEFAULT_SERVER_URL: ClassVar[str] = "http://keycloak.global.svc.cluster.local:8080"
    DEFAULT_REALM: ClassVar[str] = "swarm"
    DEFAULT_CLIENT_ID: ClassVar[str] = "swarm-gateway-admin"
    DEFAULT_CLIENT_SECRET_KEY: ClassVar[str] = "SWARM_GATEWAY_KEYCLOAK_CLIENT_SECRET"
    DEFAULT_SIGN_IN_CLIENT_ID: ClassVar[str] = "back-office"
    DEFAULT_REQUEST_TIMEOUT_S: ClassVar[float] = 5.0
    URL_SCHEMES: ClassVar[Tuple[str, ...]] = ("http://", "https://")
    TRAILING_SLASH: ClassVar[str] = "/"
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    server_url: str = Field(default=DEFAULT_SERVER_URL, description="The base URL of Keycloak.")
    realm: str = Field(default=DEFAULT_REALM, description="The realm that holds the Operators' accounts.")
    client_id: str = Field(default=DEFAULT_CLIENT_ID, description="The confidential client the gateway signs in with.")
    client_secret_key: str = Field(
        default=DEFAULT_CLIENT_SECRET_KEY,
        description="The environment entry that holds the secret of the client. Never the secret itself.",
    )
    sign_in_client_id: str = Field(
        default=DEFAULT_SIGN_IN_CLIENT_ID, description="The client of the application a new person signs in to."
    )
    request_timeout_s: float = Field(
        default=DEFAULT_REQUEST_TIMEOUT_S, description="The timeout of a call to Keycloak, in seconds."
    )

    @field_validator(SERVER_URL_FIELD, mode=BEFORE)
    def validate_server_url(cls, value: JsonValue) -> JsonValue:
        """Validate ``server_url``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped URL without its trailing slash, or the default when ``None``.

        Raises:
            SEKeycloakAdminConfigInvalidServerUrl: If the value is not an http or https URL.
        """
        if value is None:
            return cls.DEFAULT_SERVER_URL
        if not isinstance(value, str) or not value.strip().startswith(cls.URL_SCHEMES):
            raise SEKeycloakAdminConfigInvalidServerUrl(f"Invalid server_url: {value!r}. Must be an http or https URL.")
        return value.strip().rstrip(cls.TRAILING_SLASH)

    @field_validator(REALM_FIELD, mode=BEFORE)
    def validate_realm(cls, value: JsonValue) -> JsonValue:
        """Validate ``realm``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped realm, or the default when ``None``.

        Raises:
            SEKeycloakAdminConfigInvalidRealm: If the value is not a non-empty string.
        """
        if value is None:
            return cls.DEFAULT_REALM
        if not isinstance(value, str) or not value.strip():
            raise SEKeycloakAdminConfigInvalidRealm(f"Invalid realm: {value!r}. Must be a non-empty string.")
        return value.strip()

    @field_validator(CLIENT_ID_FIELD, mode=BEFORE)
    def validate_client_id(cls, value: JsonValue) -> JsonValue:
        """Validate ``client_id``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped client, or the default when ``None``.

        Raises:
            SEKeycloakAdminConfigInvalidClientId: If the value is not a non-empty string.
        """
        if value is None:
            return cls.DEFAULT_CLIENT_ID
        if not isinstance(value, str) or not value.strip():
            raise SEKeycloakAdminConfigInvalidClientId(f"Invalid client_id: {value!r}. Must be a non-empty string.")
        return value.strip()

    @field_validator(CLIENT_SECRET_KEY_FIELD, mode=BEFORE)
    def validate_client_secret_key(cls, value: JsonValue) -> JsonValue:
        """Validate ``client_secret_key``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped entry name, or the default when ``None``.

        Raises:
            SEKeycloakAdminConfigInvalidClientSecretKey: If the value is not a non-empty string.
        """
        if value is None:
            return cls.DEFAULT_CLIENT_SECRET_KEY
        if not isinstance(value, str) or not value.strip():
            raise SEKeycloakAdminConfigInvalidClientSecretKey(
                f"Invalid client_secret_key: {value!r}. Must be a non-empty string."
            )
        return value.strip()

    @field_validator(SIGN_IN_CLIENT_ID_FIELD, mode=BEFORE)
    def validate_sign_in_client_id(cls, value: JsonValue) -> JsonValue:
        """Validate ``sign_in_client_id``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped client, or the default when ``None``.

        Raises:
            SEKeycloakAdminConfigInvalidSignInClientId: If the value is not a non-empty string.
        """
        if value is None:
            return cls.DEFAULT_SIGN_IN_CLIENT_ID
        if not isinstance(value, str) or not value.strip():
            raise SEKeycloakAdminConfigInvalidSignInClientId(
                f"Invalid sign_in_client_id: {value!r}. Must be a non-empty string."
            )
        return value.strip()

    @field_validator(REQUEST_TIMEOUT_S_FIELD, mode=BEFORE)
    def validate_request_timeout_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``request_timeout_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SEKeycloakAdminConfigInvalidRequestTimeoutS: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_REQUEST_TIMEOUT_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SEKeycloakAdminConfigInvalidRequestTimeoutS(
                f"Invalid request_timeout_s: {value!r}. Must be a positive number."
            )
        return value
