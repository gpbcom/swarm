from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_catalog.models.yaml_catalog import YamlCatalog
from swarm_web.models.signals.exceptions import (
    SEInvalidSignalRedactionCatalogException,
    SESignalRedactionCatalogInvalidFragments,
    SESignalRedactionCatalogInvalidUrlKeys,
    SESignalRedactionCatalogUnreadable,
)
from swarm_web.models.signals.signal_redaction_catalog import SignalRedactionCatalog


class TestSignalRedactionCatalog:
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "fragments": ["password", "token"],
        "url_keys": ["url.full", "http.target"],
    }
    REQUIRED_FRAGMENTS: ClassVar[List[str]] = [
        "authorization",
        "cookie",
        "password",
        "secret",
        "token",
        "credential",
        "email",
    ]
    REQUIRED_URL_KEYS: ClassVar[List[str]] = ["url.full", "http.target"]

    def build(self, **changes: JsonValue) -> SignalRedactionCatalog:
        values: Dict[str, JsonValue] = dict(self.VALID)
        values.update(changes)
        return SignalRedactionCatalog.model_validate(values)

    def test_it_is_a_yaml_catalog(self) -> None:
        assert issubclass(SignalRedactionCatalog, YamlCatalog)

    def test_the_unreadable_exception_is_its_own(self) -> None:
        assert SignalRedactionCatalog.UNREADABLE is SESignalRedactionCatalogUnreadable

    def test_full_valid_construction(self) -> None:
        assert self.build().model_dump() == self.VALID

    def test_a_valid_file_loads(self, tmp_path: Path) -> None:
        path = tmp_path / "redactions.yaml"
        path.write_text(yaml.safe_dump(self.VALID), encoding=SignalRedactionCatalog.ENCODING)
        assert SignalRedactionCatalog.load(path).model_dump() == self.VALID

    def test_an_unreadable_file_is_refused(self, tmp_path: Path) -> None:
        with pytest.raises(SESignalRedactionCatalogUnreadable):
            SignalRedactionCatalog.load(tmp_path / "missing.yaml")

    def test_a_file_that_is_not_a_mapping_is_refused(self, tmp_path: Path) -> None:
        path = tmp_path / "redactions.yaml"
        path.write_text("- a\n", encoding=SignalRedactionCatalog.ENCODING)
        with pytest.raises(SESignalRedactionCatalogUnreadable):
            SignalRedactionCatalog.load(path)

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("fragments", [], SESignalRedactionCatalogInvalidFragments),
            ("fragments", None, SESignalRedactionCatalogInvalidFragments),
            ("fragments", "token", SESignalRedactionCatalogInvalidFragments),
            ("fragments", [""], SESignalRedactionCatalogInvalidFragments),
            ("fragments", ["  "], SESignalRedactionCatalogInvalidFragments),
            ("fragments", [" token"], SESignalRedactionCatalogInvalidFragments),
            ("fragments", ["Token"], SESignalRedactionCatalogInvalidFragments),
            ("fragments", [3], SESignalRedactionCatalogInvalidFragments),
            ("url_keys", [], SESignalRedactionCatalogInvalidUrlKeys),
            ("url_keys", None, SESignalRedactionCatalogInvalidUrlKeys),
            ("url_keys", "url.full", SESignalRedactionCatalogInvalidUrlKeys),
            ("url_keys", [""], SESignalRedactionCatalogInvalidUrlKeys),
            ("url_keys", ["  "], SESignalRedactionCatalogInvalidUrlKeys),
            ("url_keys", [" url.full"], SESignalRedactionCatalogInvalidUrlKeys),
            ("url_keys", ["URL.full"], SESignalRedactionCatalogInvalidUrlKeys),
            ("url_keys", [3], SESignalRedactionCatalogInvalidUrlKeys),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: value})

    @pytest.mark.parametrize(
        "error",
        [SESignalRedactionCatalogInvalidFragments, SESignalRedactionCatalogInvalidUrlKeys],
    )
    def test_every_field_error_is_a_catalog_exception(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidSignalRedactionCatalogException)

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(extra=1)

    def test_round_trip(self) -> None:
        catalog = self.build()
        assert SignalRedactionCatalog.model_validate(catalog.model_dump()) == catalog

    def test_the_reference_catalogue_is_shipped(self) -> None:
        assert Path(SignalRedactionCatalog.REFERENCE_PATH).is_file()

    def test_the_reference_catalogue_holds_the_required_fragments(self) -> None:
        catalog = SignalRedactionCatalog.load(Path(SignalRedactionCatalog.REFERENCE_PATH))
        assert set(self.REQUIRED_FRAGMENTS) <= set(catalog.fragments)

    def test_the_reference_catalogue_holds_the_required_url_keys(self) -> None:
        catalog = SignalRedactionCatalog.load(Path(SignalRedactionCatalog.REFERENCE_PATH))
        assert set(self.REQUIRED_URL_KEYS) <= set(catalog.url_keys)
