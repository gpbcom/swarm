from __future__ import annotations

# Standard library imports
from typing import ClassVar, List, Literal
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.enums import Anchoring, Deployment, Jurisdiction, LlmProvider
from swarm_models.operators.exceptions import (
    SEOperatorInvalidAnchoring,
    SEOperatorInvalidDeployment,
    SEOperatorInvalidId,
    SEOperatorInvalidJurisdictions,
    SEOperatorInvalidLlmProvider,
    SEOperatorInvalidName,
)


class Operator(SwarmModel):
    """The organisation that flies Missions for its Clients, global to every cell.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys.
        BEFORE (ClassVar[Literal["before"]]): The validator mode that runs before Pydantic's own validation.
        ID_FIELD (ClassVar[str]): The name of the ``id`` field.
        NAME_FIELD (ClassVar[str]): The name of the ``name`` field.
        DEPLOYMENT_FIELD (ClassVar[str]): The name of the ``deployment`` field.
        JURISDICTIONS_FIELD (ClassVar[str]): The name of the ``jurisdictions`` field.
        LLM_PROVIDER_FIELD (ClassVar[str]): The name of the ``llm_provider`` field.
        ANCHORING_FIELD (ClassVar[str]): The name of the ``anchoring`` field.
        id (UUID): The version 7 identifier of the Operator.
        name (str): The name of the Operator.
        deployment (Deployment): Where the Operator's Swarm runs.
        jurisdictions (List[Jurisdiction]): The jurisdictions the Operator flies under, at least one, no duplicate.
        llm_provider (LlmProvider): The kind of language model of its AI agents, Claude by default.
        anchoring (Anchoring): How its Evidence records are anchored, qualified timestamping by default.

    Notes:
        - An Operator lives in exactly one cell, given by its ``CellAssignment``.
        - ``id``, ``name``, ``deployment`` and ``jurisdictions`` have no default, so ``None`` is refused for them.
        - ``None`` becomes the default for ``llm_provider`` and ``anchoring``.
    """

    model_config = ConfigDict(extra="forbid")

    BEFORE: ClassVar[Literal["before"]] = "before"
    ID_FIELD: ClassVar[str] = "id"
    NAME_FIELD: ClassVar[str] = "name"
    DEPLOYMENT_FIELD: ClassVar[str] = "deployment"
    JURISDICTIONS_FIELD: ClassVar[str] = "jurisdictions"
    LLM_PROVIDER_FIELD: ClassVar[str] = "llm_provider"
    ANCHORING_FIELD: ClassVar[str] = "anchoring"

    id: UUID = Field(description="The version 7 identifier of the operator.")
    name: str = Field(description="The name of the operator.")
    deployment: Deployment = Field(description="Where the Operator's Swarm runs.")
    jurisdictions: List[Jurisdiction] = Field(
        description="The jurisdictions the Operator flies under, at least one and no duplicate."
    )
    llm_provider: LlmProvider = Field(
        default=LlmProvider.CLAUDE, description="The kind of language model of the Operator's AI agents."
    )
    anchoring: Anchoring = Field(
        default=Anchoring.QUALIFIED_TIMESTAMPING, description="How the Operator's Evidence records are anchored."
    )

    @field_validator(ID_FIELD, mode=BEFORE)
    def validate_id(cls, value: JsonValue) -> UUID:
        """Validate ``id``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            UUID: The version 7 UUID.

        Raises:
            SEOperatorInvalidId: When the value is not a version 7 UUID.
        """
        return cls.parse_uuid7(cls.ID_FIELD, value, SEOperatorInvalidId)

    @field_validator(NAME_FIELD, mode=BEFORE)
    def validate_name(cls, value: JsonValue) -> str:
        """Validate ``name``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            str: The stripped name.

        Raises:
            SEOperatorInvalidName: When the value is not a non-empty string.
        """
        return cls.parse_text(cls.NAME_FIELD, value, SEOperatorInvalidName)

    @field_validator(DEPLOYMENT_FIELD, mode=BEFORE)
    def validate_deployment(cls, value: JsonValue) -> Deployment:
        """Validate ``deployment``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            Deployment: The deployment.

        Raises:
            SEOperatorInvalidDeployment: When the value is not exactly a deployment.
        """
        if isinstance(value, Deployment):
            return value
        if isinstance(value, str) and value in {member.value for member in Deployment}:
            return Deployment(value)
        raise SEOperatorInvalidDeployment(
            f"Invalid {cls.DEPLOYMENT_FIELD}: {value!r}. Must be one of {[member.value for member in Deployment]}."
        )

    @field_validator(JURISDICTIONS_FIELD, mode=BEFORE)
    def validate_jurisdictions(cls, value: JsonValue) -> List[Jurisdiction]:
        """Validate ``jurisdictions``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            List[Jurisdiction]: The jurisdictions, in the given order.

        Raises:
            SEOperatorInvalidJurisdictions: When the value is not a non-empty list of distinct jurisdictions.
        """
        if not isinstance(value, (list, tuple)) or not value:
            raise SEOperatorInvalidJurisdictions(
                f"Invalid {cls.JURISDICTIONS_FIELD}: {value!r}. Must be a non-empty list of jurisdictions."
            )
        allowed = {member.value for member in Jurisdiction}
        parsed: List[Jurisdiction] = []
        for item in value:
            if isinstance(item, Jurisdiction):
                parsed.append(item)
            elif isinstance(item, str) and item in allowed:
                parsed.append(Jurisdiction(item))
            else:
                raise SEOperatorInvalidJurisdictions(
                    f"Invalid {cls.JURISDICTIONS_FIELD}: {item!r}. Must be one of {sorted(allowed)}."
                )
        if len(set(parsed)) != len(parsed):
            raise SEOperatorInvalidJurisdictions(
                f"Invalid {cls.JURISDICTIONS_FIELD}: {value!r}. Must hold no duplicate."
            )
        return parsed

    @field_validator(LLM_PROVIDER_FIELD, mode=BEFORE)
    def validate_llm_provider(cls, value: JsonValue) -> LlmProvider:
        """Validate ``llm_provider``, where ``None`` becomes the default.

        Args:
            value (JsonValue): The raw value.

        Returns:
            LlmProvider: The provider, Claude for ``None``.

        Raises:
            SEOperatorInvalidLlmProvider: When the value is not exactly a provider.
        """
        if value is None:
            return LlmProvider.CLAUDE
        if isinstance(value, LlmProvider):
            return value
        if isinstance(value, str) and value in {member.value for member in LlmProvider}:
            return LlmProvider(value)
        raise SEOperatorInvalidLlmProvider(
            f"Invalid {cls.LLM_PROVIDER_FIELD}: {value!r}. Must be one of {[member.value for member in LlmProvider]}."
        )

    @field_validator(ANCHORING_FIELD, mode=BEFORE)
    def validate_anchoring(cls, value: JsonValue) -> Anchoring:
        """Validate ``anchoring``, where ``None`` becomes the default.

        Args:
            value (JsonValue): The raw value.

        Returns:
            Anchoring: The anchoring, qualified timestamping for ``None``.

        Raises:
            SEOperatorInvalidAnchoring: When the value is not exactly an anchoring.
        """
        if value is None:
            return Anchoring.QUALIFIED_TIMESTAMPING
        if isinstance(value, Anchoring):
            return value
        if isinstance(value, str) and value in {member.value for member in Anchoring}:
            return Anchoring(value)
        raise SEOperatorInvalidAnchoring(
            f"Invalid {cls.ANCHORING_FIELD}: {value!r}. Must be one of {[member.value for member in Anchoring]}."
        )
