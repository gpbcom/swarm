from __future__ import annotations

# Standard library imports
import sys

# First-party imports
from swarm_models.schemas.exceptions import SESchemaError
from swarm_scripts.repository_paths import RepositoryPaths
from swarm_scripts.swarm_apps import SwarmApps
from swarm_service.shared.openapi.openapi_exporter import OpenApiExporter


def main() -> int:
    """Check that the published OpenAPI document of every app, or of the one ``SWARM_APP`` names, is up to date.

    Returns:
        int: 0 when every document is up to date, 1 when one is out of date, 2 when ``SWARM_APP`` names no app or a
            document cannot be read.
    """
    apps = SwarmApps()
    selected = apps.selected()
    if not selected:
        print(f"{SwarmApps.APP_KEY} names no app: {apps.requested()!r}.", file=sys.stderr)
        return 2
    code = 0
    for app in selected:
        try:
            exporter = OpenApiExporter(SwarmApps.APPLICATIONS[app](), RepositoryPaths.OPENAPI, app.value)
            stale = exporter.is_stale()
        except SESchemaError as error:
            print(error, file=sys.stderr)
            return 2
        if stale:
            print(f"{exporter.path} is out of date. Run uv run swarm-openapi-export to regenerate it.", file=sys.stderr)
            code = 1
        else:
            print(f"{exporter.path} is up to date.")
    return code
