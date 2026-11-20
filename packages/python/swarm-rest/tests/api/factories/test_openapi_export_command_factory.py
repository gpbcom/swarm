from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from swarm_lifecycle.factories.runnable_factory import RunnableFactory
from swarm_rest.api.cli.openapi_export_command import OpenApiExportCommand
from swarm_rest.api.factories.openapi_export_command_factory import OpenApiExportCommandFactory


class TestOpenApiExportCommandFactory:
    def test_create_returns_a_new_command_built_from_the_arguments(self, tmp_path: Path) -> None:
        app = FastAPI()
        path = tmp_path / "openapi.json"
        factory = OpenApiExportCommandFactory(app, path, True)
        assert isinstance(factory, RunnableFactory)
        first = factory.create()
        second = factory.create()
        assert isinstance(first, OpenApiExportCommand)
        assert first is not second
        assert first.app is app
        assert first.path == path
        assert first.check is True
