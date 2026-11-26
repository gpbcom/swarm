from __future__ import annotations

# Standard library imports
import os
import sys
from pathlib import Path

# First-party imports
from swarm_models.enums import Language
from swarm_models.i18n.catalogs.exceptions import SECatalogError
from swarm_service.shared.i18n.catalog_checker import CatalogChecker


def main() -> int:
    """Check that every Python message of Swarm is translated into every language.

    Returns:
        int: 0 when the catalogues are complete, 1 when a translation is missing, 2 on a catalogue error.

    Notes:
        - The script takes no argument: it checks the catalogues shipped with ``swarm_storage``, or the folder the
          environment entry ``SWARM_I18N_LOCALES`` names.
        - Only ``scripts/`` prints, because this output is for the person at the terminal.
    """
    folder = os.environ.get(CatalogChecker.LOCALES_KEY, "").strip()
    try:
        checker = CatalogChecker.at(Path(folder) if folder else None)
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
