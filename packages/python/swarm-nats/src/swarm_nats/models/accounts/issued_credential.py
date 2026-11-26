from __future__ import annotations

# Standard library imports
from re import fullmatch
from typing import ClassVar, Literal, Optional, Union
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, SecretStr, field_validator, model_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_nats.models.accounts.exceptions import (
    SEIssuedCredentialInconsistentKind,
    SEIssuedCredentialInvalidJwt,
    SEIssuedCredentialInvalidKind,
    SEIssuedCredentialInvalidName,
    SEIssuedCredentialInvalidOperatorId,
    SEIssuedCredentialInvalidPublicKey,
    SEIssuedCredentialInvalidSeed,
)
from swarm_nats.models.enums import CredentialKind


class IssuedCredential(SwarmModel):
    """A NATS user credential that was issued, with its signed JWT.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the model.
        BEFORE (ClassVar[Literal["before"]]): The validation mode of the field validators.
        AFTER (ClassVar[Literal["after"]]): The validation mode of the model validator.
        OPERATOR_ID_FIELD (ClassVar[str]): The name of ``operator_id``.
        KIND_FIELD (ClassVar[str]): The name of ``kind``.
        NAME_FIELD (ClassVar[str]): The name of ``name``.
        PUBLIC_KEY_FIELD (ClassVar[str]): The name of ``public_key``.
        JWT_FIELD (ClassVar[str]): The name of ``jwt``.
        SEED_FIELD (ClassVar[str]): The name of ``seed``.
        NAME_PATTERN (ClassVar[str]): The form of a name, with no white space.
        PUBLIC_KEY_PATTERN (ClassVar[str]): The form of the public key of a user.
        SEED_PATTERN (ClassVar[str]): The form of the seed of a user.
        JWT_PATTERN (ClassVar[str]): The form of a JWT, three base64url parts joined by dots.
        operator_id (Optional[UUID]): The Operator the credential belongs to, ``None`` for the system account.
        kind (CredentialKind): The kind of identity the credential is issued to.
        name (str): The name of the identity, such as an edge node.
        public_key (str): The public NKey of the user.
        jwt (str): The signed JWT of the user.
        seed (SecretStr): The seed of the user.

    Notes:
        - **The seed is a secret**: it is a ``SecretStr``, so it never appears in ``repr``, ``str`` or logs.
        - The kind is ``SYSTEM`` if and only if there is no Operator, so one Operator never reaches another's
          account.
        - Only ``operator_id`` may be ``None``, but it has no default either.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    BEFORE: ClassVar[Literal["before"]] = "before"
    AFTER: ClassVar[Literal["after"]] = "after"
    OPERATOR_ID_FIELD: ClassVar[str] = "operator_id"
    KIND_FIELD: ClassVar[str] = "kind"
    NAME_FIELD: ClassVar[str] = "name"
    PUBLIC_KEY_FIELD: ClassVar[str] = "public_key"
    JWT_FIELD: ClassVar[str] = "jwt"
    SEED_FIELD: ClassVar[str] = "seed"
    NAME_PATTERN: ClassVar[str] = r"\S+"
    PUBLIC_KEY_PATTERN: ClassVar[str] = r"U[A-Z2-7]{55}"
    SEED_PATTERN: ClassVar[str] = r"SU[A-Z2-7]{56}"
    JWT_PATTERN: ClassVar[str] = r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"

    operator_id: Optional[UUID] = Field(
        description="The Operator the credential belongs to, None for the system account."
    )
    kind: CredentialKind = Field(description="The kind of identity the credential is issued to.")
    name: str = Field(description="The name of the identity, such as an edge node.")
    public_key: str = Field(description="The public NKey of the user.")
    jwt: str = Field(description="The signed JWT of the user.")
    seed: SecretStr = Field(description="The seed of the user.")

    @field_validator(OPERATOR_ID_FIELD, mode=BEFORE)
    def validate_operator_id(cls, value: JsonValue) -> Optional[UUID]:
        """Validate ``operator_id``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            Optional[UUID]: The version 7 UUID, or ``None`` for the system account.

        Raises:
            SEIssuedCredentialInvalidOperatorId: When the value is not a version 7 UUID.
        """
        if value is None:
            return None
        return cls.parse_uuid7(cls.OPERATOR_ID_FIELD, value, SEIssuedCredentialInvalidOperatorId)

    @field_validator(KIND_FIELD, mode=BEFORE)
    def validate_kind(cls, value: JsonValue) -> CredentialKind:
        """Validate ``kind``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            CredentialKind: The kind.

        Raises:
            SEIssuedCredentialInvalidKind: When the value is not a credential kind.
        """
        if isinstance(value, str) and value in {kind.value for kind in CredentialKind}:
            return CredentialKind(value)
        raise SEIssuedCredentialInvalidKind(
            f"Invalid {cls.KIND_FIELD}: {value!r}. Must be one of {[kind.value for kind in CredentialKind]}."
        )

    @field_validator(NAME_FIELD, mode=BEFORE)
    def validate_name(cls, value: JsonValue) -> str:
        """Validate ``name``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            str: The stripped name.

        Raises:
            SEIssuedCredentialInvalidName: When the value is empty or holds white space.
        """
        text = cls.parse_text(cls.NAME_FIELD, value, SEIssuedCredentialInvalidName)
        if fullmatch(cls.NAME_PATTERN, text) is None:
            raise SEIssuedCredentialInvalidName(f"Invalid {cls.NAME_FIELD}: {value!r}. Must hold no white space.")
        return text

    @field_validator(PUBLIC_KEY_FIELD, mode=BEFORE)
    def validate_public_key(cls, value: JsonValue) -> str:
        """Validate ``public_key``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            str: The public key.

        Raises:
            SEIssuedCredentialInvalidPublicKey: When the value is not the public key of a user.
        """
        if not isinstance(value, str) or fullmatch(cls.PUBLIC_KEY_PATTERN, value) is None:
            raise SEIssuedCredentialInvalidPublicKey(
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
            SEIssuedCredentialInvalidJwt: When the value is not three base64url parts joined by dots.
        """
        if not isinstance(value, str) or fullmatch(cls.JWT_PATTERN, value) is None:
            raise SEIssuedCredentialInvalidJwt(f"Invalid {cls.JWT_FIELD}: {value!r}. Must match {cls.JWT_PATTERN}.")
        return value

    @field_validator(SEED_FIELD, mode=BEFORE)
    def validate_seed(cls, value: Union[JsonValue, SecretStr]) -> SecretStr:
        """Validate ``seed``.

        Args:
            value (Union[JsonValue, SecretStr]): The raw value, a string or a secret string.

        Returns:
            SecretStr: The seed, kept secret.

        Raises:
            SEIssuedCredentialInvalidSeed: When the value is not the seed of a user.

        Notes:
            - **The message never quotes the value**, because it is a secret.
        """
        secret = value.get_secret_value() if isinstance(value, SecretStr) else value
        if not isinstance(secret, str) or fullmatch(cls.SEED_PATTERN, secret) is None:
            raise SEIssuedCredentialInvalidSeed(f"Invalid {cls.SEED_FIELD}. Must match {cls.SEED_PATTERN}.")
        return SecretStr(secret)

    @model_validator(mode=AFTER)
    def validate_kind_and_operator(self) -> IssuedCredential:
        """Check that the kind is ``SYSTEM`` if and only if there is no Operator.

        Returns:
            IssuedCredential: The credential.

        Raises:
            SEIssuedCredentialInconsistentKind: When only one of the two says it is a system credential.
        """
        if (self.kind == CredentialKind.SYSTEM) != (self.operator_id is None):
            raise SEIssuedCredentialInconsistentKind(
                f"Invalid {self.KIND_FIELD}: {self.kind.value!r}. "
                f"Must be {CredentialKind.SYSTEM.value!r} if and only if {self.OPERATOR_ID_FIELD} is None."
            )
        return self
