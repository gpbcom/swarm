from __future__ import annotations

# Standard library imports
import zipfile
from pathlib import Path
from typing import ClassVar, Tuple

# Third-party imports
import pytest

# First-party imports
from tests.rust.swarm_core.helpers import build_wheel, install, make_venv, run_python


class TestSwarmCoreWheel:
    FUNCTIONS: ClassVar[Tuple[str, ...]] = ("safety_tick", "planner_plan", "mavlink_encode")

    @pytest.fixture(scope="class")
    def built(self, tmp_path_factory: pytest.TempPathFactory) -> Tuple[Path, Path]:
        wheel = build_wheel(tmp_path_factory.mktemp("wheel"))
        python = make_venv(tmp_path_factory.mktemp("env") / "venv")
        install(python, wheel)
        return wheel, python

    def test_maturin_builds_exactly_one_wheel_named_after_the_module(self, built: Tuple[Path, Path]) -> None:
        wheel, _ = built
        assert wheel.name.startswith("swarm_core-")
        assert wheel.name.endswith(".whl")

    def test_the_wheel_holds_a_type_stub_for_the_module(self, built: Tuple[Path, Path]) -> None:
        wheel, _ = built
        with zipfile.ZipFile(wheel) as archive:
            names = archive.namelist()
        assert any(name.startswith("swarm_core") and name.endswith(".pyi") for name in names)

    def test_the_module_comes_from_the_installed_wheel(self, built: Tuple[Path, Path]) -> None:
        _, python = built
        result = run_python(python, "import swarm_core; print(swarm_core.__file__)")
        assert result.returncode == 0, result.stderr
        assert Path(result.stdout.strip()).resolve().is_relative_to(python.parent.parent.resolve())

    @pytest.mark.parametrize("function", FUNCTIONS)
    @pytest.mark.parametrize(("values", "expected"), [("[1, 2, 3]", "6"), ("[]", "0")])
    def test_a_function_returns_the_wrapping_sum(
        self, built: Tuple[Path, Path], function: str, values: str, expected: str
    ) -> None:
        _, python = built
        result = run_python(python, f"import swarm_core; print(swarm_core.{function}({values}))")
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == expected

    @pytest.mark.parametrize("function", FUNCTIONS)
    def test_a_non_integer_value_raises_a_type_error(self, built: Tuple[Path, Path], function: str) -> None:
        _, python = built
        code = (
            "import swarm_core\n"
            "try:\n"
            f"    swarm_core.{function}(['a'])\n"
            "except Exception as error:\n"
            "    print(type(error).__name__)\n"
        )
        result = run_python(python, code)
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "TypeError"
