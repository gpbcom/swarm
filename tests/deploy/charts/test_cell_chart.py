from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import ClassVar, Dict, List, Set, Tuple

import pytest
import yaml
from pydantic import JsonValue


class TestCellChart:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    CHART_DIR: ClassVar[Path] = ROOT / "deploy" / "charts" / "cell"
    EXPECTED_DEPENDENCIES: ClassVar[List[Dict[str, str]]] = [
        {
            "name": "database",
            "repository": "file://../database",
            "condition": "database.enabled",
        },
        {
            "name": "valkey",
            "repository": "file://../valkey",
            "condition": "valkey.enabled",
        },
        {
            "name": "object-storage",
            "alias": "objectStorage",
            "repository": "file://../object-storage",
            "condition": "objectStorage.enabled",
        },
        {
            "name": "vault-config",
            "alias": "vaultConfig",
            "repository": "file://../vault-config",
            "condition": "vaultConfig.enabled",
        },
        {
            "name": "nats",
            "repository": "file://../nats",
            "condition": "nats.enabled",
        },
    ]
    TOGGLES: ClassVar[List[str]] = ["database", "valkey", "objectStorage", "vaultConfig", "nats"]
    EXPECTED_RESOURCES: ClassVar[List[Tuple[str, str, str]]] = [
        ("postgresql.cnpg.io/v1", "Cluster", "database"),
        ("postgresql.cnpg.io/v1", "Pooler", "database-pooler-rw"),
        ("apps/v1", "StatefulSet", "valkey"),
        ("apps/v1", "StatefulSet", "object-storage"),
        ("batch/v1", "Job", "vault-config"),
        ("networking.k8s.io/v1", "NetworkPolicy", "valkey"),
        ("networking.k8s.io/v1", "NetworkPolicy", "object-storage"),
        ("apps/v1", "StatefulSet", "nats"),
        ("v1", "ConfigMap", "nats-config"),
        ("v1", "Service", "nats"),
        ("v1", "Service", "nats-headless"),
        ("policy/v1", "PodDisruptionBudget", "nats"),
        ("networking.k8s.io/v1", "NetworkPolicy", "nats"),
    ]
    FAKE_JWT: ClassVar[str] = "aGVhZGVy.cGF5bG9hZA.c2lnbmF0dXJl"
    FAKE_ACCOUNT: ClassVar[str] = "A" + "B" * 55
    NATS_LEAF: ClassVar[str] = "nats-leaf"
    SEMVER: ClassVar[str] = r"^\d+\.\d+\.\d+([-+].+)?$"
    API_VERSION_KEY: ClassVar[str] = "apiVersion"
    KIND_KEY: ClassVar[str] = "kind"
    METADATA_KEY: ClassVar[str] = "metadata"
    NAME_KEY: ClassVar[str] = "name"
    ENABLED_KEY: ClassVar[str] = "enabled"
    GLOBAL_KEY: ClassVar[str] = "global"
    SERVICES_KEY: ClassVar[str] = "services"
    DEPENDENCIES_KEY: ClassVar[str] = "dependencies"
    ENCODING: ClassVar[str] = "utf-8"

    def load(self, path: Path) -> Dict[str, JsonValue]:
        loaded: JsonValue = yaml.safe_load(path.read_text(encoding=self.ENCODING))
        assert isinstance(loaded, dict)
        return loaded

    def test_chart_yaml_describes_an_application_chart_named_cell(self) -> None:
        chart = self.load(self.CHART_DIR / "Chart.yaml")
        assert chart[self.API_VERSION_KEY] == "v2"
        assert chart[self.NAME_KEY] == "cell"
        assert chart["type"] == "application"
        version = chart["version"]
        assert isinstance(version, str)
        assert re.match(self.SEMVER, version)

    def test_the_dependencies_are_exactly_the_five_sub_charts(self) -> None:
        chart = self.load(self.CHART_DIR / "Chart.yaml")
        assert chart[self.DEPENDENCIES_KEY] == self.EXPECTED_DEPENDENCIES

    def test_no_dependency_is_named_nats_leaf(self) -> None:
        chart = self.load(self.CHART_DIR / "Chart.yaml")
        dependencies = chart[self.DEPENDENCIES_KEY]
        assert isinstance(dependencies, list)
        names = [str(dependency[self.NAME_KEY]) for dependency in dependencies if isinstance(dependency, dict)]
        assert self.NATS_LEAF not in names

    @pytest.mark.parametrize("toggle", TOGGLES)
    def test_every_sub_chart_is_enabled_by_default(self, toggle: str) -> None:
        values = self.load(self.CHART_DIR / "values.yaml")
        section = values[toggle]
        assert isinstance(section, dict)
        assert section[self.ENABLED_KEY] is True

    def test_the_default_services_are_empty(self) -> None:
        values = self.load(self.CHART_DIR / "values.yaml")
        global_values = values[self.GLOBAL_KEY]
        assert isinstance(global_values, dict)
        assert global_values[self.SERVICES_KEY] == []

    def test_the_lock_file_names_the_five_dependencies(self) -> None:
        lock = self.load(self.CHART_DIR / "Chart.lock")
        dependencies = lock[self.DEPENDENCIES_KEY]
        assert isinstance(dependencies, list)
        names = [str(dependency[self.NAME_KEY]) for dependency in dependencies if isinstance(dependency, dict)]
        assert sorted(names) == sorted(entry[self.NAME_KEY] for entry in self.EXPECTED_DEPENDENCIES)

    @pytest.mark.skipif(shutil.which("helm") is None, reason="helm is not installed")
    def test_the_cell_renders_its_data_platform(self, tmp_path: Path) -> None:
        charts = tmp_path / "charts"
        shutil.copytree(self.ROOT / "deploy" / "charts", charts)
        shutil.copytree(self.ROOT / "deploy" / "environments", tmp_path / "environments")
        cell = charts / "cell"
        subprocess.run(["helm", "dependency", "build", str(cell)], check=True, capture_output=True)
        rendered = subprocess.run(
            [
                "helm",
                "template",
                "cell",
                str(cell),
                "--namespace",
                "cell-test",
                "-f",
                str(tmp_path / "environments" / "dev" / "values.yaml"),
                "--set",
                "database.imageName=registry.example.org/swarm-postgres:16",
                "--set",
                f"nats.auth.operatorJwt={self.FAKE_JWT}",
                "--set",
                f"nats.auth.systemAccount={self.FAKE_ACCOUNT}",
                "--set",
                f"nats.auth.systemAccountJwt={self.FAKE_JWT}",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        found: Set[Tuple[str, str, str]] = set()
        for document in yaml.safe_load_all(rendered):
            if not isinstance(document, dict):
                continue
            metadata = document.get(self.METADATA_KEY)
            if not isinstance(metadata, dict):
                continue
            found.add(
                (
                    str(document.get(self.API_VERSION_KEY)),
                    str(document.get(self.KIND_KEY)),
                    str(metadata.get(self.NAME_KEY)),
                )
            )
        for expected in self.EXPECTED_RESOURCES:
            assert expected in found
