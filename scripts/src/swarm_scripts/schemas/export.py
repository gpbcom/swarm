from __future__ import annotations

# Standard library imports
import sys

# First-party imports
from swarm_models.schemas.exceptions import SESchemaError
from swarm_scripts.repository_paths import RepositoryPaths
from swarm_service.shared.schema.schema_exporter import SchemaExporter


def main() -> int:
    """Write the JSON Schema bundle of ``swarm-models``.

    Returns:
        int: 0 when the bundle is written, 2 on an error.
    """
    try:
        path = SchemaExporter(RepositoryPaths.SCHEMAS).export()
    except SESchemaError as error:
        print(error, file=sys.stderr)
        return 2
    print(f"Wrote {path}.")
    return 0
