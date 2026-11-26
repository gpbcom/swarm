from __future__ import annotations

# Standard library imports
import sys

# First-party imports
from swarm_models.schemas.exceptions import SESchemaError
from swarm_scripts.repository_paths import RepositoryPaths
from swarm_service.shared.schema.schema_exporter import SchemaExporter


def main() -> int:
    """Check that the committed JSON Schema bundle of ``swarm-models`` is up to date.

    Returns:
        int: 0 when it is up to date, 1 when it is out of date, 2 on an error.
    """
    try:
        exporter = SchemaExporter(RepositoryPaths.SCHEMAS)
        stale = exporter.is_stale()
    except SESchemaError as error:
        print(error, file=sys.stderr)
        return 2
    if stale:
        print(f"{exporter.path} is out of date. Run uv run swarm-schemas-export to regenerate it.", file=sys.stderr)
        return 1
    print(f"{exporter.path} is up to date.")
    return 0
