from __future__ import annotations

# Standard library imports
from re import fullmatch
from typing import ClassVar, Literal, Union

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, SecretStr, field_validator

# First-party imports
from swarm_models.accounts.exceptions import (
    SEIssuedAccountInvalidJwt,
    SEIssuedAccountInvalidName,
    SEIssuedAccountInvalidPublicKey,
    SEIssuedAccountInvalidSeed,
)
from swarm_models.base.swarm_model import SwarmModel


class IssuedAccount(SwarmModel):
    """A NATS account that was issued, with its signed JWT.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the model.
        BEFORE (ClassVar[Literal["before"]]): The validation mode of every validator.
        NAME_FIELD (ClassVar[str]): The name of ``name``.
        PUBLIC_KEY_FIELD (ClassVar[str]): The name of ``public_key``.
        JWT_FIELD (ClassVar[str]): The name of ``jwt``.
        SEED_FIELD (ClassVar[str]): The name of ``seed``.
        PUBLIC_KEY_PATTERN (ClassVar[str]): The form of the public key of an account.
        SEED_PATTERN (ClassVar[str]): The form of the seed of an account.
        JWT_PATTERN (ClassVar[str]): The form of a JWT, three base64url parts joined by dots.
        name (str): The name of the account, the identifier of its Operator or ``SYS``.
        public_key (str): The public NKey of the account.
        jwt (str): The signed JWT of the account.
        seed (SecretStr): The seed of the account.

    Notes:
        - **The seed is a secret**: it is a ``SecretStr``, so it never appears in ``repr``, ``str`` or logs.
        - No field has a default, so ``None`` is refused.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    BEFORE: ClassVar[Literal["before"]] = "before"
    NAME_FIELD: ClassVar[str] = "name"
    PUBLIC_KEY_FIELD: ClassVar[str] = "public_key"
    JWT_FIELD: ClassVar[str] = "jwt"
    SEED_FIELD: ClassVar[str] = "seed"
    PUBLIC_KEY_PATTERN: ClassVar[str] = r"A[A-Z2-7]{55}"
    SEED_PATTERN: ClassVar[str] = r"SA[A-Z2-7]{56}"
    JWT_PATTERN: ClassVar[str] = r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"

    name: str = Field(description="The name of the account, the identifier of its Operator or SYS.")
    public_key: str = Field(description="The public NKey of the account.")
    jwt: str = Field(description="The signed JWT of the account.")
    seed: SecretStr = Field(description="The seed of the account.")

    @field_validator(NAME_FIELD, mode=BEFORE)
    def validate_name(cls, value: JsonValue) -> str:
        """Validate ``name``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            str: The stripped name.

        Raises:
            SEIssuedAccountInvalidName: When the value is not a non-empty string.
        """
        return cls.parse_text(cls.NAME_FIELD, value, SEIssuedAccountInvalidName)

    @field_validator(PUBLIC_KEY_FIELD, mode=BEFORE)
    def validate_public_key(cls, value: JsonValue) -> str:
        """Validate ``public_key``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            str: The public key.

        Raises:
            SEIssuedAccountInvalidPublicKey: When the value is not the public key of an account.
        """
        if not isinstance(value, str) or fullmatch(cls.PUBLIC_KEY_PATTERN, value) is None:
            raise SEIssuedAccountInvalidPublicKey(
                f"Invalid {cls.PUBLIC_KEY_FIELD}: {value!r}. Must match {cls.PUBLIC_KEY_PATTERN}."
            )
        return value

    @field_validator(JWT_FIELD, mode=BEFORE)
    def validate_jwt(cls, value: JsonValue) -> str:
        """Validate ``jwt``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            str: The JWT.

        Raises:
            SEIssuedAccountInvalidJwt: When the value is not three base64url parts joined by dots.
        """
        if not isinstance(value, str) or fullmatch(cls.JWT_PATTERN, value) is None:
            raise SEIssuedAccountInvalidJwt(f"Invalid {cls.JWT_FIELD}: {value!r}. Must match {cls.JWT_PATTERN}.")
        return value

    @field_validator(SEED_FIELD, mode=BEFORE)
    def validate_seed(cls, value: Union[JsonValue, SecretStr]) -> SecretStr:
        """Validate ``seed``.

        Args:
            value (Union[JsonValue, SecretStr]): The raw value, a string or a secret string.

        Returns:
            SecretStr: The seed, kept secret.

        Raises:
            SEIssuedAccountInvalidSeed: When the value is not the seed of an account.

        Notes:
            - **The message never quotes the value**, because it is a secret.
        """
        secret = value.get_secret_value() if isinstance(value, SecretStr) else value
        if not isinstance(secret, str) or fullmatch(cls.SEED_PATTERN, secret) is None:
            raise SEIssuedAccountInvalidSeed(f"Invalid {cls.SEED_FIELD}. Must match {cls.SEED_PATTERN}.")
        return SecretStr(secret)
