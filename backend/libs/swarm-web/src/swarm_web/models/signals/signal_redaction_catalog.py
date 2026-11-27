from __future__ import annotations

# Standard library imports
from importlib.resources import files
from pathlib import Path
from typing import ClassVar, List, Literal

# Third-party imports
from pydantic import Field, JsonValue, field_validator

# First-party imports
from swarm_catalog.models.yaml_catalog import YamlCatalog
from swarm_web.models.signals.exceptions import (
    SESignalRedactionCatalogInvalidFragments,
    SESignalRedactionCatalogInvalidUrlKeys,
    SESignalRedactionCatalogUnreadable,
)


class SignalRedactionCatalog(YamlCatalog):
    """What a signal must never carry: the attribute names to redact and the URL keys to scrub.

    Attributes:
        REFERENCE_PATH (Path): The reference catalogue shipped with the package.
        UNREADABLE (type[Exception]): The exception raised when the file cannot be read.
        FRAGMENTS_FIELD (ClassVar[str]): The name of the ``fragments`` field.
        URL_KEYS_FIELD (ClassVar[str]): The name of the ``url_keys`` field.
        BEFORE (ClassVar[Literal["before"]]): The mode of the validators.
        fragments (List[str]): The lower case fragments of an attribute name whose value is redacted.
        url_keys (List[str]): The lower case attribute names that hold a URL, whose secrets are scrubbed.
    """

    REFERENCE_PATH: ClassVar[Path] = Path(str(files("swarm_web").joinpath("conf", "signal_redactions.yaml")))
    UNREADABLE: ClassVar[type[Exception]] = SESignalRedactionCatalogUnreadable
    FRAGMENTS_FIELD: ClassVar[str] = "fragments"
    URL_KEYS_FIELD: ClassVar[str] = "url_keys"
    BEFORE: ClassVar[Literal["before"]] = "before"

    fragments: List[str] = Field(description="The lower case fragments of an attribute name whose value is redacted.")
    url_keys: List[str] = Field(description="The lower case attribute names that hold a URL, scrubbed of secrets.")

    @field_validator(FRAGMENTS_FIELD, mode=BEFORE)
    def validate_fragments(cls, value: JsonValue) -> JsonValue:
        """Validate ``fragments``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The fragments.

        Raises:
            SESignalRedactionCatalogInvalidFragments: If the value is not a non-empty list of lower case strings.
        """
        if not cls._is_valid(value):
            raise SESignalRedactionCatalogInvalidFragments(
                f"Invalid fragments: {value!r}. Must be a non-empty list of stripped lower case strings."
            )
        return value

    @field_validator(URL_KEYS_FIELD, mode=BEFORE)
    def validate_url_keys(cls, value: JsonValue) -> JsonValue:
        """Validate ``url_keys``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The URL keys.

        Raises:
            SESignalRedactionCatalogInvalidUrlKeys: If the value is not a non-empty list of lower case strings.
        """
        if not cls._is_valid(value):
            raise SESignalRedactionCatalogInvalidUrlKeys(
                f"Invalid url_keys: {value!r}. Must be a non-empty list of stripped lower case strings."
            )
        return value

    ############################
    # Internal Helpers Methods #
    ############################

    @classmethod
    def _is_valid(cls, value: JsonValue) -> bool:
        """Tell whether a value is a non-empty list of stripped, lower case, non-empty strings.

        Args:
            value (JsonValue): The raw input.

        Returns:
            bool: True when the list is valid.
        """
        if not isinstance(value, list) or not value:
            return False
        return all(isinstance(item, str) and item and item == item.strip().lower() for item in value)
