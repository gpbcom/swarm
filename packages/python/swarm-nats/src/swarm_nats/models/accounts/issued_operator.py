from __future__ import annotations

# Standard library imports
from re import fullmatch
from typing import ClassVar, Dict, Literal, Union

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, SecretStr, field_validator

# First-party imports
from swarm_models.models.base.swarm_model import SwarmModel
from swarm_nats.models.accounts.exceptions import (
    SEIssuedOperatorInvalidJwt,
    SEIssuedOperatorInvalidName,
    SEIssuedOperatorInvalidPublicKey,
    SEIssuedOperatorInvalidSeed,
    SEIssuedOperatorInvalidSystemAccount,
)
from swarm_nats.models.accounts.issued_account import IssuedAccount


class IssuedOperator(SwarmModel):
    """The NATS operator that was issued, with its signed JWT and its system account.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the model.
        BEFORE (ClassVar[Literal["before"]]): The validation mode of every validator.
        NAME_FIELD (ClassVar[str]): The name of ``name``.
        PUBLIC_KEY_FIELD (ClassVar[str]): The name of ``public_key``.
        JWT_FIELD (ClassVar[str]): The name of ``jwt``.
        SEED_FIELD (ClassVar[str]): The name of ``seed``.
        SYSTEM_ACCOUNT_FIELD (ClassVar[str]): The name of ``system_account``.
        PUBLIC_KEY_PATTERN (ClassVar[str]): The form of the public key of an operator.
        SEED_PATTERN (ClassVar[str]): The form of the seed of an operator.
        JWT_PATTERN (ClassVar[str]): The form of a JWT, three base64url parts joined by dots.
        name (str): The name of the operator.
        public_key (str): The public NKey of the operator.
        jwt (str): The signed JWT of the operator.
        seed (SecretStr): The seed of the operator.
        system_account (IssuedAccount): The system account the operator names.

    Notes:
        - **The seed is a secret**: it is a ``SecretStr``, so it never appears in ``repr``, ``str`` or logs.
        - No field has a default, so ``None`` is refused.
        - The errors of the system account are raised as they are.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    BEFORE: ClassVar[Literal["before"]] = "before"
    NAME_FIELD: ClassVar[str] = "name"
    PUBLIC_KEY_FIELD: ClassVar[str] = "public_key"
    JWT_FIELD: ClassVar[str] = "jwt"
    SEED_FIELD: ClassVar[str] = "seed"
    SYSTEM_ACCOUNT_FIELD: ClassVar[str] = "system_account"
    PUBLIC_KEY_PATTERN: ClassVar[str] = r"O[A-Z2-7]{55}"
    SEED_PATTERN: ClassVar[str] = r"SO[A-Z2-7]{56}"
    JWT_PATTERN: ClassVar[str] = r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"

    name: str = Field(description="The name of the operator.")
    public_key: str = Field(description="The public NKey of the operator.")
    jwt: str = Field(description="The signed JWT of the operator.")
    seed: SecretStr = Field(description="The seed of the operator.")
    system_account: IssuedAccount = Field(description="The system account the operator names.")

    @field_validator(NAME_FIELD, mode=BEFORE)
    def validate_name(cls, value: JsonValue) -> str:
        """Validate ``name``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            str: The stripped name.

        Raises:
            SEIssuedOperatorInvalidName: When the value is not a non-empty string.
        """
        return cls.parse_text(cls.NAME_FIELD, value, SEIssuedOperatorInvalidName)

    @field_validator(PUBLIC_KEY_FIELD, mode=BEFORE)
    def validate_public_key(cls, value: JsonValue) -> str:
        """Validate ``public_key``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            str: The public key.

        Raises:
            SEIssuedOperatorInvalidPublicKey: When the value is not the public key of an operator.
        """
        if not isinstance(value, str) or fullmatch(cls.PUBLIC_KEY_PATTERN, value) is None:
            raise SEIssuedOperatorInvalidPublicKey(
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
            SEIssuedOperatorInvalidJwt: When the value is not three base64url parts joined by dots.
        """
        if not isinstance(value, str) or fullmatch(cls.JWT_PATTERN, value) is None:
            raise SEIssuedOperatorInvalidJwt(f"Invalid {cls.JWT_FIELD}: {value!r}. Must match {cls.JWT_PATTERN}.")
        return value

    @field_validator(SEED_FIELD, mode=BEFORE)
    def validate_seed(cls, value: Union[JsonValue, SecretStr]) -> SecretStr:
        """Validate ``seed``.

        Args:
            value (Union[JsonValue, SecretStr]): The raw value, a string or a secret string.

        Returns:
            SecretStr: The seed, kept secret.

        Raises:
            SEIssuedOperatorInvalidSeed: When the value is not the seed of an operator.

        Notes:
            - **The message never quotes the value**, because it is a secret.
        """
        secret = value.get_secret_value() if isinstance(value, SecretStr) else value
        if not isinstance(secret, str) or fullmatch(cls.SEED_PATTERN, secret) is None:
            raise SEIssuedOperatorInvalidSeed(f"Invalid {cls.SEED_FIELD}. Must match {cls.SEED_PATTERN}.")
        return SecretStr(secret)

    @field_validator(SYSTEM_ACCOUNT_FIELD, mode=BEFORE)
    def validate_system_account(cls, value: Union[JsonValue, IssuedAccount]) -> IssuedAccount:
        """Validate ``system_account``.

        Args:
            value (Union[JsonValue, IssuedAccount]): An account, or its fields.

        Returns:
            IssuedAccount: The system account.

        Raises:
            SEIssuedOperatorInvalidSystemAccount: When the value is neither an account nor its fields.
        """
        if isinstance(value, IssuedAccount):
            return value
        if isinstance(value, dict):
            fields: Dict[str, JsonValue] = value
            return IssuedAccount.model_validate(fields)
        raise SEIssuedOperatorInvalidSystemAccount(
            f"Invalid {cls.SYSTEM_ACCOUNT_FIELD}: {type(value).__name__}. Must be an IssuedAccount or its fields."
        )
