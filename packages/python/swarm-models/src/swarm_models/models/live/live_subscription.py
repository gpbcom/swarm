from __future__ import annotations

# Standard library imports
import re
from typing import ClassVar, Pattern
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.models.base.swarm_model import SwarmModel
from swarm_models.models.enums import LiveOperation, LiveRate, LiveTopicKind
from swarm_models.models.live.exceptions import (
    SELiveSubscriptionInvalidOp,
    SELiveSubscriptionInvalidRate,
    SELiveSubscriptionInvalidTopic,
)


class LiveSubscription(SwarmModel):
    """The message a client sends on the live WebSocket to follow a topic.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the subscription.
        TOPIC_PREFIX (ClassVar[str]): The first part of every topic.
        TOPIC_SEPARATOR (ClassVar[str]): The separator between the parts of a topic.
        TOPIC_PATTERN (ClassVar[Pattern[str]]): The shape of a topic, ``mission/<id>/<kind>``.
        op (LiveOperation): What the client asks.
        topic (str): The topic followed, ``mission/<version 7 UUID>/<kind>``.
        rate (LiveRate): How often frames are sent. Defaults to full.

    Notes:
        - The topic stays a string on the wire,
          and ``mission()`` and ``kind()`` read its parts.
        - **A mission identifier that is not a version 7 UUID is refused.**
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    TOPIC_PREFIX: ClassVar[str] = "mission"
    TOPIC_SEPARATOR: ClassVar[str] = "/"
    TOPIC_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^mission/([^/]+)/([^/]+)$")

    op: LiveOperation = Field(description="What the client asks.")
    topic: str = Field(description="The topic followed, mission/<version 7 UUID>/<kind>.")
    rate: LiveRate = Field(default=LiveRate.FULL, description="How often frames are sent.")

    @field_validator("op", mode="before")
    def validate_op(cls, value: JsonValue) -> LiveOperation:
        """Validate ``op``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            LiveOperation: The operation.

        Raises:
            SELiveSubscriptionInvalidOp: When the value is not a known operation.
        """
        if isinstance(value, str) and value in {member.value for member in LiveOperation}:
            return LiveOperation(value)
        raise SELiveSubscriptionInvalidOp(
            f"Invalid op: {value!r}. Must be one of {[member.value for member in LiveOperation]}."
        )

    @field_validator("topic", mode="before")
    def validate_topic(cls, value: JsonValue) -> str:
        """Validate ``topic``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            str: The topic.

        Raises:
            SELiveSubscriptionInvalidTopic: When the topic is not ``mission/<version 7 UUID>/<kind>``.
        """
        match = cls.TOPIC_PATTERN.match(value) if isinstance(value, str) else None
        if match is None or match.group(2) not in {member.value for member in LiveTopicKind}:
            raise SELiveSubscriptionInvalidTopic(
                f"Invalid topic: {value!r}. "
                f"Must be mission/<version 7 UUID>/<kind> with a kind in {[m.value for m in LiveTopicKind]}."
            )
        cls.parse_uuid7("topic", match.group(1), SELiveSubscriptionInvalidTopic)
        return str(value)

    @field_validator("rate", mode="before")
    def validate_rate(cls, value: JsonValue) -> LiveRate:
        """Validate ``rate``, where ``None`` becomes the default.

        Args:
            value (JsonValue): The raw value.

        Returns:
            LiveRate: The rate.

        Raises:
            SELiveSubscriptionInvalidRate: When the value is not a known rate.
        """
        if value is None:
            return LiveRate.FULL
        if isinstance(value, str) and value in {member.value for member in LiveRate}:
            return LiveRate(value)
        raise SELiveSubscriptionInvalidRate(
            f"Invalid rate: {value!r}. Must be one of {[member.value for member in LiveRate]}."
        )

    ############################
    # Publicly Exposed Methods #
    ############################

    def mission(self) -> UUID:
        """Read the Mission from the topic.

        Returns:
            UUID: The Mission identifier.
        """
        return UUID(self.topic.split(self.TOPIC_SEPARATOR)[1])

    def kind(self) -> LiveTopicKind:
        """Read the kind from the topic.

        Returns:
            LiveTopicKind: The kind.
        """
        return LiveTopicKind(self.topic.split(self.TOPIC_SEPARATOR)[2])

    @classmethod
    def topic_of(cls, mission_id: UUID, kind: LiveTopicKind) -> str:
        """Build the topic of a Mission and a kind.

        Args:
            mission_id (UUID): The Mission identifier.
            kind (LiveTopicKind): The kind.

        Returns:
            str: The topic.
        """
        return cls.TOPIC_SEPARATOR.join([cls.TOPIC_PREFIX, str(mission_id), kind.value])
