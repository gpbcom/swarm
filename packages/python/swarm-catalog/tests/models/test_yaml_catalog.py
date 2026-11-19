from __future__ import annotations

from pathlib import Path
from typing import Optional

import pytest
from pydantic import ValidationError, create_model

from swarm_catalog.models.exceptions import SEYamlCatalogUnreadable
from swarm_catalog.models.yaml_catalog import YamlCatalog


class TestYamlCatalog:
    def test_an_empty_mapping_loads(self, tmp_path: Path) -> None:
        path = tmp_path / "catalog.yaml"
        path.write_text("{}", encoding="utf-8")
        assert isinstance(YamlCatalog.load(path), YamlCatalog)

    @pytest.mark.parametrize(
        ("content", "has_cause"),
        [
            (None, True),
            ("key: [unclosed", True),
            ("- a\n- b\n", False),
            ("", False),
        ],
    )
    def test_an_unreadable_file_is_refused(self, tmp_path: Path, content: Optional[str], has_cause: bool) -> None:
        path = tmp_path / "catalog.yaml"
        if content is not None:
            path.write_text(content, encoding="utf-8")
        with pytest.raises(SEYamlCatalogUnreadable) as info:
            YamlCatalog.load(path)
        assert (info.value.__cause__ is not None) is has_cause

    def test_an_unknown_key_is_refused(self, tmp_path: Path) -> None:
        path = tmp_path / "catalog.yaml"
        path.write_text("extra: 1\n", encoding="utf-8")
        with pytest.raises(ValidationError):
            YamlCatalog.load(path)

    def test_a_subclass_loads_its_field_in_utf8(self, tmp_path: Path) -> None:
        sample = create_model("SampleCatalog", __base__=YamlCatalog, name=(str, ...))
        path = tmp_path / "catalog.yaml"
        path.write_text("name: Drône éclair 無人機\n", encoding="utf-8")
        assert sample.load(path).name == "Drône éclair 無人機"  # type: ignore[attr-defined]

    def test_a_subclass_can_change_the_exception(self, tmp_path: Path) -> None:
        sample = create_model("LookupCatalog", __base__=YamlCatalog, name=(str, ...))
        sample.UNREADABLE = LookupError
        with pytest.raises(LookupError):
            sample.load(tmp_path / "missing.yaml")

    def test_a_loaded_catalogue_is_frozen(self, tmp_path: Path) -> None:
        sample = create_model("FrozenCatalog", __base__=YamlCatalog, name=(str, ...))
        path = tmp_path / "catalog.yaml"
        path.write_text("name: a\n", encoding="utf-8")
        catalog = sample.load(path)
        with pytest.raises(ValidationError):
            catalog.name = "b"  # type: ignore[attr-defined]

    def test_the_exception_is_not_a_value_error(self) -> None:
        assert issubclass(SEYamlCatalogUnreadable, Exception)
        assert not issubclass(SEYamlCatalogUnreadable, ValueError)
