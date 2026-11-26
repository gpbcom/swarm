from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar


class RepositoryPaths:
    """The folders of the repository that the scripts read and write.

    Attributes:
        ROOT (ClassVar[Path]): The repository root.
        SCHEMAS (ClassVar[Path]): The folder of the JSON Schema bundle of ``swarm-models``.

    Notes:
        The scripts run from the repository, as an editable member of the uv workspace, so the root is found from this
        file. Code under ``backend/`` never does this: an app receives its folder (``NoFileDepthPath``).
    """

    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    SCHEMAS: ClassVar[Path] = ROOT / "backend" / "swarm-models" / "schemas"
