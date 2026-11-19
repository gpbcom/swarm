from __future__ import annotations

import pytest

from swarm_logging.models.enums import LogFormat


class TestLogFormat:
    def test_the_members_and_their_values(self) -> None:
        assert [(member.name, member.value) for member in LogFormat] == [("COLOURED", "coloured"), ("JSON", "json")]

    @pytest.mark.parametrize(("text", "expected"), [("coloured", LogFormat.COLOURED), ("json", LogFormat.JSON)])
    def test_a_member_is_built_from_its_string(self, text: str, expected: LogFormat) -> None:
        assert LogFormat(text) is expected

    def test_an_unknown_string_is_refused(self) -> None:
        with pytest.raises(ValueError):
            LogFormat("xml")
