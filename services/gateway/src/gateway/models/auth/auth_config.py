from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal, Tuple

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from gateway.models.auth.exceptions import (
    SEAuthConfigInvalidAudience,
    SEAuthConfigInvalidIssuerUrl,
    SEAuthConfigInvalidJwksCacheTtlS,
    SEAuthConfigInvalidLeewayS,
    SEAuthConfigInvalidRequestTimeoutS,
)


class AuthConfig(BaseModel):
    """The configuration of the check of the tokens the gateway receives.

    Attributes:
        issuer_url (str): The URL of the identity provider that issues the tokens, without a trailing slash.
        audience (str): The audience a token must name.
        jwks_cache_ttl_s (float): How long the signing keys are kept, in seconds.
        leeway_s (float): The clock skew accepted on the times of a token, in seconds.
        request_timeout_s (float): The timeout of a call to the identity provider, in seconds.
        ISSUER_URL_FIELD (str): The name of the ``issuer_url`` field.
        AUDIENCE_FIELD (str): The name of the ``audience`` field.
        JWKS_CACHE_TTL_S_FIELD (str): The name of the ``jwks_cache_ttl_s`` field.
        LEEWAY_S_FIELD (str): The name of the ``leeway_s`` field.
        REQUEST_TIMEOUT_S_FIELD (str): The name of the ``request_timeout_s`` field.
        DEFAULT_AUDIENCE (str): The default audience.
        DEFAULT_JWKS_CACHE_TTL_S (float): The default lifetime of the signing keys.
        DEFAULT_LEEWAY_S (float): The default clock skew.
        DEFAULT_REQUEST_TIMEOUT_S (float): The default timeout.
        URL_SCHEMES (Tuple[str, ...]): The schemes an issuer URL may start with.
        TRAILING_SLASH (str): The character removed from the end of the issuer URL.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - **No secret is held here**: the gateway only checks signatures with the public keys of the issuer.
        - ``leeway_s`` may be zero, the other durations must be positive.
    """

    ISSUER_URL_FIELD: ClassVar[str] = "issuer_url"
    AUDIENCE_FIELD: ClassVar[str] = "audience"
    JWKS_CACHE_TTL_S_FIELD: ClassVar[str] = "jwks_cache_ttl_s"
    LEEWAY_S_FIELD: ClassVar[str] = "leeway_s"
    REQUEST_TIMEOUT_S_FIELD: ClassVar[str] = "request_timeout_s"
    DEFAULT_AUDIENCE: ClassVar[str] = "swarm-gateway"
    DEFAULT_JWKS_CACHE_TTL_S: ClassVar[float] = 300.0
    DEFAULT_LEEWAY_S: ClassVar[float] = 0.0
    DEFAULT_REQUEST_TIMEOUT_S: ClassVar[float] = 5.0
    URL_SCHEMES: ClassVar[Tuple[str, ...]] = ("http://", "https://")
    TRAILING_SLASH: ClassVar[str] = "/"
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    issuer_url: str = Field(description="The URL of the identity provider that issues the tokens.")
    audience: str = Field(default=DEFAULT_AUDIENCE, description="The audience a token must name.")
    jwks_cache_ttl_s: float = Field(
        default=DEFAULT_JWKS_CACHE_TTL_S, description="How long the signing keys are kept, in seconds."
    )
    leeway_s: float = Field(
        default=DEFAULT_LEEWAY_S, description="The clock skew accepted on the times of a token, in seconds."
    )
    request_timeout_s: float = Field(
        default=DEFAULT_REQUEST_TIMEOUT_S, description="The timeout of a call to the identity provider, in seconds."
    )

    @field_validator(ISSUER_URL_FIELD, mode=BEFORE)
    def validate_issuer_url(cls, value: JsonValue) -> JsonValue:
        """Validate ``issuer_url``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped URL, without its trailing slash.

        Raises:
            SEAuthConfigInvalidIssuerUrl: If the value is not an http or https URL.
        """
        if not isinstance(value, str) or not value.strip().startswith(cls.URL_SCHEMES):
            raise SEAuthConfigInvalidIssuerUrl(f"Invalid issuer_url: {value!r}. Must be an http or https URL.")
        return value.strip().rstrip(cls.TRAILING_SLASH)

    @field_validator(AUDIENCE_FIELD, mode=BEFORE)
    def validate_audience(cls, value: JsonValue) -> JsonValue:
        """Validate ``audience``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped audience, or the default when ``None``.

        Raises:
            SEAuthConfigInvalidAudience: If the value is not a non-empty string.
        """
        if value is None:
            return cls.DEFAULT_AUDIENCE
        if not isinstance(value, str) or not value.strip():
            raise SEAuthConfigInvalidAudience(f"Invalid audience: {value!r}. Must be a non-empty string.")
        return value.strip()

    @field_validator(JWKS_CACHE_TTL_S_FIELD, mode=BEFORE)
    def validate_jwks_cache_ttl_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``jwks_cache_ttl_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SEAuthConfigInvalidJwksCacheTtlS: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_JWKS_CACHE_TTL_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SEAuthConfigInvalidJwksCacheTtlS(f"Invalid jwks_cache_ttl_s: {value!r}. Must be a positive number.")
        return value

    @field_validator(LEEWAY_S_FIELD, mode=BEFORE)
    def validate_leeway_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``leeway_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SEAuthConfigInvalidLeewayS: If the value is not a number of at least zero.
        """
        if value is None:
            return cls.DEFAULT_LEEWAY_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise SEAuthConfigInvalidLeewayS(f"Invalid leeway_s: {value!r}. Must be a number of at least zero.")
        return value

    @field_validator(REQUEST_TIMEOUT_S_FIELD, mode=BEFORE)
    def validate_request_timeout_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``request_timeout_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SEAuthConfigInvalidRequestTimeoutS: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_REQUEST_TIMEOUT_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SEAuthConfigInvalidRequestTimeoutS(
                f"Invalid request_timeout_s: {value!r}. Must be a positive number."
            )
        return value
