from __future__ import annotations

# Standard library imports
import json
from logging import Logger, getLogger
from pathlib import Path
from typing import ClassVar, Optional, Tuple, Type

# Third-party imports
from pydantic import BaseModel
from pydantic.json_schema import models_json_schema

# First-party imports
from swarm_models.models.commands.command import Command
from swarm_models.models.events.actor import Actor
from swarm_models.models.events.event import Event
from swarm_models.models.operators.cell_assignment import CellAssignment
from swarm_models.models.operators.operator import Operator
from swarm_models.models.people.person import Person
from swarm_models.models.people.role import Role
from swarm_models.models.telemetry.squad_frame import SquadFrame
from swarm_models.models.telemetry.telemetry_frame import TelemetryFrame
from swarm_models.storage.schemas.schema_folder import SchemaFolder


class SchemaExporter:
    """Render the JSON Schema bundle of the models, write it and detect a stale one.

    Attributes:
        MODELS (ClassVar[Tuple[Type[BaseModel], ...]]): The models exported, in order.
        FILE_NAME (ClassVar[str]): The name of the bundle file.
        TITLE (ClassVar[str]): The title of the bundle.
        folder (SchemaFolder): The folder the bundle lives in.
        logger (Logger): Logger instance.

    Notes:
        - One bundle is exported, rather than one file per model, so that Rust and TypeScript share one set of type
          names.
        - The text is canonical (sorted keys, two spaces, one final newline), so that a stale file is detected by a
          plain comparison.
        - Storage errors propagate unchanged.
    """

    MODELS: ClassVar[Tuple[Type[BaseModel], ...]] = (
        Operator,
        CellAssignment,
        Person,
        Role,
        Actor,
        Event,
        TelemetryFrame,
        SquadFrame,
        Command,
    )
    FILE_NAME: ClassVar[str] = "swarm_models.schema.json"
    TITLE: ClassVar[str] = "Swarm models"

    def __init__(self, root: Optional[Path] = None, logger: Optional[Logger] = None) -> None:
        """Create an exporter.

        Args:
            root (Optional[Path]): The folder of the bundle. Defaults to ``SchemaFolder.DEFAULT_ROOT``.
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.folder = SchemaFolder(root or SchemaFolder.DEFAULT_ROOT)

    ############################
    # Publicly Exposed Methods #
    ############################

    @property
    def path(self) -> Path:
        """The path of the bundle file."""
        return self.folder.path(self.FILE_NAME)

    def render(self) -> str:
        """Render the bundle as canonical JSON text.

        Returns:
            str: The text, ending with one newline.
        """
        _, bundle = models_json_schema([(model, "validation") for model in self.MODELS], title=self.TITLE)
        text = json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        self.logger.debug("Rendered the schema bundle of %d models.", len(self.MODELS))
        return text

    def export(self) -> Path:
        """Write the bundle.

        Returns:
            Path: The path written.
        """
        target = self.folder.write(self.FILE_NAME, self.render())
        self.logger.info("Exported the schema bundle to %s.", target)
        return target

    def is_stale(self) -> bool:
        """Tell whether the file on disk differs from the rendered bundle.

        Returns:
            bool: ``True`` when the file is missing or different.
        """
        if self.folder.read(self.FILE_NAME) == self.render():
            self.logger.debug("The schema bundle %s is current.", self.FILE_NAME)
            return False
        self.logger.warning("The schema bundle %s is stale.", self.FILE_NAME)
        return True
