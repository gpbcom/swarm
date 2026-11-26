from __future__ import annotations

# Standard library imports
from typing import Union

# Third-party imports
import pytest

# First-party imports
from swarm_models.enums import LiveOperation, LiveRate, LiveTopicKind


class TestSwarmModelsLiveEnums:
    def test_the_operations_and_their_values(self) -> None:
        assert [(member.name, member.value) for member in LiveOperation] == [("SUBSCRIBE", "subscribe")]

    def test_the_topic_kinds_and_their_values(self) -> None:
        assert [(member.name, member.value) for member in LiveTopicKind] == [("SQUAD", "squad")]

    def test_the_rates_and_their_values(self) -> None:
        assert [(member.name, member.value) for member in LiveRate] == [("FULL", "full")]

    @pytest.mark.parametrize(
        "member",
        [LiveOperation.SUBSCRIBE, LiveTopicKind.SQUAD, LiveRate.FULL],
    )
    def test_a_member_is_built_from_its_string(self, member: Union[LiveOperation, LiveTopicKind, LiveRate]) -> None:
        assert type(member)(member.value) is member

    @pytest.mark.parametrize("enum", [LiveOperation, LiveTopicKind, LiveRate])
    def test_an_unknown_string_is_refused(self, enum: type[Union[LiveOperation, LiveTopicKind, LiveRate]]) -> None:
        with pytest.raises(ValueError):
            enum("unknown")

    @pytest.mark.parametrize("enum", [LiveOperation, LiveTopicKind, LiveRate])
    def test_no_value_has_a_hyphen(self, enum: type[Union[LiveOperation, LiveTopicKind, LiveRate]]) -> None:
        assert all("-" not in member.value for member in enum)
