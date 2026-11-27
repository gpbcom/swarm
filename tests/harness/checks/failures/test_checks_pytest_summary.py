from __future__ import annotations

# Standard library imports
from pathlib import Path

# First-party imports
from tests.harness.checks.helpers import call

FAILED_TEST = "tests/scripts/test_swarm_apps.py"
OUTPUT = (
    "/venv/lib/pytest_asyncio/plugin.py:217: PytestDeprecationWarning: The configuration option "
    '"asyncio_default_fixture_loop_scope" is unset.\n'
    "  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))\n"
    + "."
    * 70
    + "\n=================================== FAILURES ===================================\n"
    "____________ TestSwarmApps.test_the_gateway_configuration_is_its_default ____________\n"
    "E   AssertionError: assert {...} == {...}\n"
    "=========================== short test summary info ============================\n"
    f"FAILED {FAILED_TEST}::TestSwarmApps::test_the_gateway_configuration_is_its_default - AssertionError\n"
    "1 failed, 5397 passed, 3 warnings in 412.07s\n"
)


class TestChecksPytestSummary:
    def test_the_failing_test_is_named_from_pytest_s_short_summary(self) -> None:
        found = call(f"checks.pytest_failures({OUTPUT!r})")
        assert found == [
            [
                FAILED_TEST,
                f"FAILED {FAILED_TEST}::TestSwarmApps::test_the_gateway_configuration_is_its_default - AssertionError",
            ]
        ]

    def test_a_collection_error_names_its_file(self) -> None:
        out = "ERROR tests/swarm_models/test_x.py - ModuleNotFoundError: No module named 'tests.nope'\n"
        assert [name for name, _ in call(f"checks.pytest_failures({out!r})")] == ["tests/swarm_models/test_x.py"]

    def test_a_failed_pytest_check_names_the_test_file_not_the_tests_folder(self, tmp_path: Path) -> None:
        setup = (
            f"checks.ROOT = Path({str(tmp_path)!r})\n"
            f"checks.run = lambda command, cwd=None, env=None: (1, {OUTPUT!r})\n"
            f"c = checks.Checks('T9.04', Path({str(tmp_path)!r}), ['backend/apps/gateway/conf/app.yaml'])\n"
            "c.check(checks.PYTEST_CHECK, ['uv', 'run', 'pytest'], 'tests')"
        )
        [failure] = call("c.failures", setup)
        assert failure["file"] == FAILED_TEST
        assert "Warning" not in failure["detail"]
        assert "AssertionError" in failure["detail"]

    def test_warnings_never_make_the_detail_of_a_failure(self, tmp_path: Path) -> None:
        setup = (
            f"checks.ROOT = Path({str(tmp_path)!r})\n"
            "checks.run = lambda command, cwd=None, env=None: "
            "(1, 'error: broken\\nDeprecationWarning: old\\n  warnings.warn(x)')\n"
            f"c = checks.Checks('T9.04', Path({str(tmp_path)!r}), [])\n"
            "c.check('lint', ['pnpm', 'lint'], 'frontend')"
        )
        [failure] = call("c.failures", setup)
        assert failure["detail"] == "error: broken"
