from __future__ import annotations

# First-party imports
from tests.harness.checks.helpers import call

CHANGED = ["services/missions/tests/api/test_x.py", "services/missions/src/missions/api/app.py"]


class TestChecksFailingFiles:
    def test_a_path_printed_from_the_service_root_names_the_changed_file(self) -> None:
        out = "FAILED tests/api/test_x.py::test_a - assert 1 == 2"
        found = call(f"checks.failing_files({out!r}, {CHANGED!r})")
        assert [name for name, _ in found] == [CHANGED[0]]

    def test_a_full_path_still_names_the_changed_file(self) -> None:
        out = f"{CHANGED[1]}:3:1: E501 line too long"
        found = call(f"checks.failing_files({out!r}, {CHANGED!r})")
        assert [name for name, _ in found] == [CHANGED[1]]

    def test_a_bare_file_name_names_nothing(self) -> None:
        out = "FAILED test_x.py::test_a"
        assert call(f"checks.failing_files({out!r}, {CHANGED!r})") == []
