from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Self

# Third-party imports
import yaml
from pydantic import BaseModel, ConfigDict, JsonValue

# First-party imports
from swarm_catalog.models.exceptions import SEYamlCatalogUnreadable


class YamlCatalog(BaseModel):
    """A frozen Pydantic model loaded from a YAML file.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the loaded catalog.
        UNREADABLE (type[Exception]): The exception raised when the file cannot be read.

    Notes:
        - Subclasses set ``UNREADABLE`` to their own exception, so that callers catch an error named after the
          catalog and not the generic one.
        - **The exception must not subclass ``ValueError``**, because pydantic would wrap it in a validation error.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    UNREADABLE: ClassVar[type[Exception]] = SEYamlCatalogUnreadable

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def load(cls, path: Path) -> Self:
        """Load one catalog from a YAML file.

        Args:
            path (Path): The YAML file to read, in UTF-8.

        Returns:
            Self: The validated catalog.

        Raises:
            Exception: ``UNREADABLE`` when the file cannot be read, is not valid YAML or is not a mapping.
        """
        try:
            with path.open(encoding="utf-8") as stream:
                data: JsonValue = yaml.safe_load(stream)
        except (OSError, yaml.YAMLError) as error:
            raise cls.UNREADABLE(f"Unreadable catalog: {path}. Must be a YAML mapping in UTF-8.") from error
        if not isinstance(data, dict):
            raise cls.UNREADABLE(f"Unreadable catalog: {path}. Must be a YAML mapping in UTF-8.")
        return cls.model_validate(data)
