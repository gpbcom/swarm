from __future__ import annotations

# Standard library imports
from pathlib import Path

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_rest.api.cli.openapi_cli import OpenApiCli


class TestOpenApiCli:
    TITLE = "Cli test"
    VERSION = "1.0.0"
    CHECK_FLAG = "--check"
    OUTPUT_FLAG = "--output"
    UNKNOWN_FLAG = "--unknown"
    EXIT_OK = 0
    EXIT_DIFFERENT = 1
    EXIT_USAGE = 2

    def build_app(self) -> FastAPI:
        return FastAPI(title=self.TITLE, version=self.VERSION)

    def test_no_argument_writes_the_default_output(self, tmp_path: Path) -> None:
        default = tmp_path / "default" / "openapi.json"
        assert OpenApiCli(self.build_app, default).main([]) == self.EXIT_OK
        assert default.is_file()

    def test_output_writes_the_given_path(self, tmp_path: Path) -> None:
        default = tmp_path / "default.json"
        other = tmp_path / "other.json"
        assert OpenApiCli(self.build_app, default).main([self.OUTPUT_FLAG, str(other)]) == self.EXIT_OK
        assert other.is_file()
        assert not default.exists()

    def test_check_of_a_missing_file_returns_one(self, tmp_path: Path) -> None:
        missing = tmp_path / "missing.json"
        cli = OpenApiCli(self.build_app, tmp_path / "default.json")
        assert cli.main([self.CHECK_FLAG, self.OUTPUT_FLAG, str(missing)]) == self.EXIT_DIFFERENT
        assert not missing.exists()

    def test_check_of_a_written_file_returns_zero(self, tmp_path: Path) -> None:
        path = tmp_path / "openapi.json"
        cli = OpenApiCli(self.build_app, tmp_path / "default.json")
        cli.main([self.OUTPUT_FLAG, str(path)])
        assert cli.main([self.CHECK_FLAG, self.OUTPUT_FLAG, str(path)]) == self.EXIT_OK

    def test_an_unknown_argument_returns_two(self, tmp_path: Path) -> None:
        cli = OpenApiCli(self.build_app, tmp_path / "default.json")
        assert cli.main([self.UNKNOWN_FLAG]) == self.EXIT_USAGE
