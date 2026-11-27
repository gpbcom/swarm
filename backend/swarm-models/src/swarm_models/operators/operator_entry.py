from __future__ import annotations

# Standard library imports
from typing import ClassVar, List, Literal, Optional, Type

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.enums import Anchoring, Deployment, Jurisdiction, LlmProvider
from swarm_models.operators.exceptions import (
    SEOperatorEntryInvalidAnchoring,
    SEOperatorEntryInvalidDeployment,
    SEOperatorEntryInvalidFirstMissionPlannerEmail,
    SEOperatorEntryInvalidFirstMissionPlannerName,
    SEOperatorEntryInvalidJurisdictions,
    SEOperatorEntryInvalidLlmProvider,
    SEOperatorEntryInvalidName,
)


class OperatorEntry(SwarmModel):
    """The body of the request that creates an Operator.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys.
        BEFORE (ClassVar[Literal["before"]]): The validator mode that runs before Pydantic's own validation.
        NAME_FIELD (ClassVar[str]): The name of the ``name`` field.
        DEPLOYMENT_FIELD (ClassVar[str]): The name of the ``deployment`` field.
        JURISDICTIONS_FIELD (ClassVar[str]): The name of the ``jurisdictions`` field.
        LLM_PROVIDER_FIELD (ClassVar[str]): The name of the ``llm_provider`` field.
        ANCHORING_FIELD (ClassVar[str]): The name of the ``anchoring`` field.
        PLANNER_NAME_FIELD (ClassVar[str]): The name of the ``first_mission_planner_name`` field.
        PLANNER_EMAIL_FIELD (ClassVar[str]): The name of the ``first_mission_planner_email`` field.
        EMAIL_SEPARATOR (ClassVar[str]): The character between the local part and the domain of an address.
        DOMAIN_SEPARATOR (ClassVar[str]): The character that must appear in the domain of an address.
        name (Optional[str]): The name of the Operator, if given.
        deployment (Optional[Deployment]): Where its Swarm runs, if given.
        jurisdictions (List[Jurisdiction]): The jurisdictions it flies under, without duplicate.
        llm_provider (Optional[LlmProvider]): The kind of language model of its AI agents, if given.
        anchoring (Anchoring): How its Evidence records are anchored.
        first_mission_planner_name (Optional[str]): The name of its first Mission planner, if given.
        first_mission_planner_email (Optional[str]): The email address of its first Mission planner, if given.

    Notes:
        - It is lenient on presence, so that the service can name every field that is missing.
        - A blank text becomes ``None``, and ``None`` becomes the default.
    """

    model_config = ConfigDict(extra="forbid")

    BEFORE: ClassVar[Literal["before"]] = "before"
    NAME_FIELD: ClassVar[str] = "name"
    DEPLOYMENT_FIELD: ClassVar[str] = "deployment"
    JURISDICTIONS_FIELD: ClassVar[str] = "jurisdictions"
    LLM_PROVIDER_FIELD: ClassVar[str] = "llm_provider"
    ANCHORING_FIELD: ClassVar[str] = "anchoring"
    PLANNER_NAME_FIELD: ClassVar[str] = "first_mission_planner_name"
    PLANNER_EMAIL_FIELD: ClassVar[str] = "first_mission_planner_email"
    EMAIL_SEPARATOR: ClassVar[str] = "@"
    DOMAIN_SEPARATOR: ClassVar[str] = "."

    name: Optional[str] = Field(default=None, description="The name of the Operator.")
    deployment: Optional[Deployment] = Field(default=None, description="Where the Operator's Swarm runs.")
    jurisdictions: List[Jurisdiction] = Field(
        default_factory=list, description="The jurisdictions the Operator flies under."
    )
    llm_provider: Optional[LlmProvider] = Field(
        default=None, description="The kind of language model of the Operator's AI agents."
    )
    anchoring: Anchoring = Field(
        default=Anchoring.QUALIFIED_TIMESTAMPING, description="How the Operator's Evidence records are anchored."
    )
    first_mission_planner_name: Optional[str] = Field(
        default=None, description="The name of the first Mission planner."
    )
    first_mission_planner_email: Optional[str] = Field(
        default=None, description="The email address of the first Mission planner."
    )

    ############################
    # Internal Helpers Methods #
    ############################

    @classmethod
    def _optional_text(cls, field: str, value: JsonValue, error: Type[Exception]) -> Optional[str]:
        """Parse an optional text, where ``None`` and a blank text become ``None``.

        Args:
            field (str): The name of the field, for the message.
            value (JsonValue): The raw value.
            error (Type[Exception]): The exception raised when the value is not a string.

        Returns:
            Optional[str]: The stripped text, or ``None``.

        Raises:
            Exception: The given ``error`` when the value is neither ``None`` nor a string.
        """
        if value is None:
            return None
        if not isinstance(value, str):
            raise error(f"Invalid {field}: {value!r}. Must be a string.")
        return value.strip() or None

    @field_validator(NAME_FIELD, mode=BEFORE)
    def validate_name(cls, value: JsonValue) -> Optional[str]:
        """Validate ``name``, where a blank text becomes ``None``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            Optional[str]: The stripped name, or ``None``.

        Raises:
            SEOperatorEntryInvalidName: When the value is neither ``None`` nor a string.
        """
        return cls._optional_text(cls.NAME_FIELD, value, SEOperatorEntryInvalidName)

    @field_validator(DEPLOYMENT_FIELD, mode=BEFORE)
    def validate_deployment(cls, value: JsonValue) -> Optional[Deployment]:
        """Validate ``deployment``, where ``None`` stays ``None``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            Optional[Deployment]: The deployment, or ``None``.

        Raises:
            SEOperatorEntryInvalidDeployment: When the value is not exactly a deployment.
        """
        if value is None:
            return None
        if isinstance(value, Deployment):
            return value
        if isinstance(value, str) and value in {member.value for member in Deployment}:
            return Deployment(value)
        raise SEOperatorEntryInvalidDeployment(
            f"Invalid {cls.DEPLOYMENT_FIELD}: {value!r}. Must be one of {[member.value for member in Deployment]}."
        )

    @field_validator(JURISDICTIONS_FIELD, mode=BEFORE)
    def validate_jurisdictions(cls, value: JsonValue) -> List[Jurisdiction]:
        """Validate ``jurisdictions``, where ``None`` becomes an empty list.

        Args:
            value (JsonValue): The raw value.

        Returns:
            List[Jurisdiction]: The jurisdictions, in the given order.

        Raises:
            SEOperatorEntryInvalidJurisdictions: When the value is not a list of distinct jurisdictions.
        """
        if value is None:
            return []
        if not isinstance(value, (list, tuple)):
            raise SEOperatorEntryInvalidJurisdictions(
                f"Invalid {cls.JURISDICTIONS_FIELD}: {value!r}. Must be a list of jurisdictions."
            )
        allowed = {member.value for member in Jurisdiction}
        parsed: List[Jurisdiction] = []
        for item in value:
            if isinstance(item, Jurisdiction):
                parsed.append(item)
            elif isinstance(item, str) and item in allowed:
                parsed.append(Jurisdiction(item))
            else:
                raise SEOperatorEntryInvalidJurisdictions(
                    f"Invalid {cls.JURISDICTIONS_FIELD}: {item!r}. Must be one of {sorted(allowed)}."
                )
        if len(set(parsed)) != len(parsed):
            raise SEOperatorEntryInvalidJurisdictions(
                f"Invalid {cls.JURISDICTIONS_FIELD}: {value!r}. Must hold no duplicate."
            )
        return parsed

    @field_validator(LLM_PROVIDER_FIELD, mode=BEFORE)
    def validate_llm_provider(cls, value: JsonValue) -> Optional[LlmProvider]:
        """Validate ``llm_provider``, where ``None`` stays ``None``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            Optional[LlmProvider]: The provider, or ``None``.

        Raises:
            SEOperatorEntryInvalidLlmProvider: When the value is not exactly a provider.
        """
        if value is None:
            return None
        if isinstance(value, LlmProvider):
            return value
        if isinstance(value, str) and value in {member.value for member in LlmProvider}:
            return LlmProvider(value)
        raise SEOperatorEntryInvalidLlmProvider(
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
            SEOperatorEntryInvalidAnchoring: When the value is not exactly an anchoring.
        """
        if value is None:
            return Anchoring.QUALIFIED_TIMESTAMPING
        if isinstance(value, Anchoring):
            return value
        if isinstance(value, str) and value in {member.value for member in Anchoring}:
            return Anchoring(value)
        raise SEOperatorEntryInvalidAnchoring(
            f"Invalid {cls.ANCHORING_FIELD}: {value!r}. Must be one of {[member.value for member in Anchoring]}."
        )

    @field_validator(PLANNER_NAME_FIELD, mode=BEFORE)
    def validate_first_mission_planner_name(cls, value: JsonValue) -> Optional[str]:
        """Validate ``first_mission_planner_name``, where a blank text becomes ``None``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            Optional[str]: The stripped name, or ``None``.

        Raises:
            SEOperatorEntryInvalidFirstMissionPlannerName: When the value is neither ``None`` nor a string.
        """
        return cls._optional_text(cls.PLANNER_NAME_FIELD, value, SEOperatorEntryInvalidFirstMissionPlannerName)

    @field_validator(PLANNER_EMAIL_FIELD, mode=BEFORE)
    def validate_first_mission_planner_email(cls, value: JsonValue) -> Optional[str]:
        """Validate ``first_mission_planner_email``, where a blank text becomes ``None``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            Optional[str]: The stripped address, or ``None``.

        Raises:
            SEOperatorEntryInvalidFirstMissionPlannerEmail: When the value is not a string, or an address with
                not exactly one separator or a domain without a dot.
        """
        email = cls._optional_text(cls.PLANNER_EMAIL_FIELD, value, SEOperatorEntryInvalidFirstMissionPlannerEmail)
        if email is None:
            return None
        local, separator, domain = email.partition(cls.EMAIL_SEPARATOR)
        if (
            not separator
            or not local
            or cls.EMAIL_SEPARATOR in domain
            or cls.DOMAIN_SEPARATOR not in domain
            or domain.startswith(cls.DOMAIN_SEPARATOR)
            or domain.endswith(cls.DOMAIN_SEPARATOR)
            or any(character.isspace() for character in email)
        ):
            raise SEOperatorEntryInvalidFirstMissionPlannerEmail(
                f"Invalid {cls.PLANNER_EMAIL_FIELD}: {value!r}. "
                "Must be a local part and a domain with a dot, around one separator, with no whitespace."
            )
        return email
