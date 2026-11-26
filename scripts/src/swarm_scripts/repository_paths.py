from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar


class RepositoryPaths:
    """The folders of the repository that the scripts read and write.

    Attributes:
        ROOT (ClassVar[Path]): The repository root.
        SCHEMAS (ClassVar[Path]): The folder of the JSON Schema bundle of ``swarm-models``.
        APPS (ClassVar[Path]): The folder of the apps, each in ``<app>/`` with its ``conf/`` and ``migrations/``.
        OPENAPI (ClassVar[Path]): The folder of the published OpenAPI documents, one ``<app>.json`` per app.

    Notes:
        The scripts run from the repository, as an editable member of the uv workspace, so the root is found from this
        file. Code under ``backend/`` never does this: an app receives its folder (``NoFileDepthPath``).
    """

    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    SCHEMAS: ClassVar[Path] = ROOT / "backend" / "swarm-models" / "schemas"
    APPS: ClassVar[Path] = ROOT / "backend" / "apps"
    OPENAPI: ClassVar[Path] = ROOT / "frontend" / "packages" / "api-client" / "openapi"
