"""Command line that writes or checks the committed JSON Schema bundle."""

from __future__ import annotations

# Standard library imports
import argparse
import sys
from pathlib import Path
from typing import List, Optional

# First-party imports
from swarm_models.models.schemas.exceptions import SESchemaError
from swarm_models.service.schemas.schema_exporter import SchemaExporter


def main(argv: Optional[List[str]] = None) -> int:
    """Write the schema bundle, or check that the committed one is current.

    Args:
        argv (Optional[List[str]]): The arguments. Defaults to ``sys.argv``.

    Returns:
        int: 0 on success, 1 when ``--check`` finds a stale bundle, 2 on an error.
    """
    parser = argparse.ArgumentParser(prog="swarm-models-schemas", description="Export the JSON Schema bundle.")
    parser.add_argument("--check", action="store_true", help="Fail when the bundle on disk is out of date.")
    parser.add_argument("--output", default=None, help="The folder of the bundle.")
    arguments = parser.parse_args(argv)
    try:
        exporter = SchemaExporter(root=Path(arguments.output) if arguments.output else None)
        if arguments.check:
            if exporter.is_stale():
                print(
                    f"{exporter.path} is out of date. Run swarm-models-schemas to regenerate it.",
                    file=sys.stderr,
                )
                return 1
            print(f"{exporter.path} is up to date.")
            return 0
        print(f"Wrote {exporter.export()}.")
        return 0
    except SESchemaError as error:
        print(error, file=sys.stderr)
        return 2
