from __future__ import annotations

# Standard library imports
import sys

# First-party imports
from swarm_models.schemas.exceptions import SESchemaError
from swarm_scripts.repository_paths import RepositoryPaths
from swarm_scripts.swarm_apps import SwarmApps
from swarm_service.shared.openapi.openapi_exporter import OpenApiExporter


def main() -> int:
    """Write the OpenAPI document of every app, or of the one ``SWARM_APP`` names.

    Returns:
        int: 0 when every document is written, 2 when ``SWARM_APP`` names no app or a document cannot be written.
    """
    apps = SwarmApps()
    selected = apps.selected()
    if not selected:
        print(f"{SwarmApps.APP_KEY} names no app: {apps.requested()!r}.", file=sys.stderr)
        return 2
    for app in selected:
        try:
            path = OpenApiExporter(SwarmApps.APPLICATIONS[app](), RepositoryPaths.OPENAPI, app.value).export()
        except SESchemaError as error:
            print(error, file=sys.stderr)
            return 2
        print(f"Wrote {path}.")
    return 0
