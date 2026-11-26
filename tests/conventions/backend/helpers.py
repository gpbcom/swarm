from __future__ import annotations

# Standard library imports
import os
from pathlib import Path

# First-party imports
from tests.conventions.helpers import repo_root


def backend_root() -> Path:
    """Return the repository root whose ``backend/`` and ``scripts/`` are checked.

    The variable ``SWARM_CONVENTIONS_BACKEND_ROOT`` overrides the repository root.
    """
    override = os.environ.get("SWARM_CONVENTIONS_BACKEND_ROOT")
    if override:
        return Path(override)
    return repo_root()
