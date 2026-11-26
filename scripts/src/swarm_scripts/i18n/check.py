from __future__ import annotations

# Standard library imports
import argparse
import sys
from pathlib import Path
from typing import List, Optional

# First-party imports
from swarm_i18n.models.catalogs.exceptions import SECatalogError  # isort: skip
from swarm_i18n.service.catalogs.catalog_checker import CatalogChecker  # isort: skip
from swarm_models.enums import Language


def main(argv: Optional[List[str]] = None) -> int:
    """Check that every message is translated into every language.

    Args:
        argv (Optional[List[str]]): The arguments. Defaults to ``sys.argv``.

    Returns:
        int: 0 when the catalogues are complete, 1 when a translation is missing, 2 on a catalogue error.
    """
    parser = argparse.ArgumentParser(prog="swarm-i18n-check", description="Check the message catalogues.")
    parser.add_argument("--locales", default=None, help="The folder of the catalogues.")
    arguments = parser.parse_args(argv)
    try:
        checker = CatalogChecker.at(Path(arguments.locales) if arguments.locales else None)
        missing = checker.find_missing()
    except SECatalogError as error:
        print(error, file=sys.stderr)
        return 2
    if missing:
        for item in missing:
            print(f"{item.message_id}: {item.problem.value} in {item.language.value}.", file=sys.stderr)
        return 1
    names = ", ".join(language.name.capitalize() for language in Language)
    print(f"Every message is in {names}.")
    return 0
