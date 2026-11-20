from __future__ import annotations

# Standard library imports
import shutil
import subprocess
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue


class TestDatabaseChart:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    CHART: ClassVar[Path] = ROOT / "deploy" / "charts" / "database"
    NAMESPACE: ClassVar[str] = "cell-test"
    IMAGE: ClassVar[str] = "registry.example.org/swarm-postgres:16"
    SERVICES: ClassVar[List[str]] = ["missions", "fleet"]
    HELM_MISSING: ClassVar[bool] = shutil.which("helm") is None

    API_VERSION: ClassVar[str] = "apiVersion"
    KIND: ClassVar[str] = "kind"
    METADATA: ClassVar[str] = "metadata"
    NAME: ClassVar[str] = "name"
    SPEC: ClassVar[str] = "spec"
    CLUSTER_KIND: ClassVar[str] = "Cluster"
    POOLER_KIND: ClassVar[str] = "Pooler"
    CNPG_API: ClassVar[str] = "postgresql.cnpg.io/v1"
    IMAGE_NAME: ClassVar[str] = "imageName"
    INSTANCES: ClassVar[str] = "instances"
    STORAGE: ClassVar[str] = "storage"
    SIZE: ClassVar[str] = "size"
    POOLER: ClassVar[str] = "pooler"
    POOL_MODE: ClassVar[str] = "poolMode"
    GLOBAL: ClassVar[str] = "global"
    SERVICES_KEY: ClassVar[str] = "services"
    POSTGRESQL: ClassVar[str] = "postgresql"
    PRELOAD: ClassVar[str] = "shared_preload_libraries"
    BOOTSTRAP: ClassVar[str] = "bootstrap"
    INITDB: ClassVar[str] = "initdb"
    DATABASE: ClassVar[str] = "database"
    POST_INIT: ClassVar[str] = "postInitApplicationSQL"
    SUPERUSER: ClassVar[str] = "enableSuperuserAccess"
    CLUSTER: ClassVar[str] = "cluster"
    TYPE: ClassVar[str] = "type"
    PGBOUNCER: ClassVar[str] = "pgbouncer"
    CHART_NAME: ClassVar[str] = "database"
    POOLER_NAME: ClassVar[str] = "database-pooler-rw"

    def _load(self, path: Path) -> Dict[str, JsonValue]:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(loaded, dict)
        return loaded

    def _dict(self, value: JsonValue, key: str) -> Dict[str, JsonValue]:
        assert isinstance(value, dict)
        child = value[key]
        assert isinstance(child, dict)
        return child

    def _render(self, *extra: str) -> subprocess.CompletedProcess[str]:
        command = [
            "helm",
            "template",
            self.CHART_NAME,
            str(self.CHART),
            "--namespace",
            self.NAMESPACE,
            *extra,
        ]
        return subprocess.run(command, capture_output=True, text=True, check=False)

    def _documents(self) -> List[Dict[str, JsonValue]]:
        result = self._render(
            "--set",
            f"imageName={self.IMAGE}",
            "--set",
            "global.services={" + ",".join(self.SERVICES) + "}",
        )
        assert result.returncode == 0, result.stderr
        return [d for d in yaml.safe_load_all(result.stdout) if isinstance(d, dict)]

    def _of_kind(self, kind: str) -> Dict[str, JsonValue]:
        found = [d for d in self._documents() if d[self.KIND] == kind]
        assert len(found) == 1
        return found[0]

    def _post_init(self) -> List[str]:
        cluster = self._of_kind(self.CLUSTER_KIND)
        initdb = self._dict(self._dict(cluster[self.SPEC], self.BOOTSTRAP), self.INITDB)
        statements = initdb[self.POST_INIT]
        assert isinstance(statements, list)
        return [str(s) for s in statements]

    def test_chart_yaml_declares_the_database_chart(self) -> None:
        chart = self._load(self.CHART / "Chart.yaml")
        assert chart[self.API_VERSION] == "v2"
        assert chart[self.NAME] == self.CHART_NAME

    def test_values_have_the_documented_defaults(self) -> None:
        values = self._load(self.CHART / "values.yaml")
        assert values[self.INSTANCES] == 1
        assert values[self.IMAGE_NAME] == ""
        assert self.SIZE in self._dict(values, self.STORAGE)
        pooler = self._dict(values, self.POOLER)
        assert pooler[self.INSTANCES] == 1
        assert pooler[self.POOL_MODE] == "transaction"
        assert self._dict(values, self.GLOBAL)[self.SERVICES_KEY] == []

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_cluster_uses_the_given_image_and_one_instance(self) -> None:
        cluster = self._of_kind(self.CLUSTER_KIND)
        assert cluster[self.API_VERSION] == self.CNPG_API
        assert self._dict(cluster, self.METADATA)[self.NAME] == self.CHART_NAME
        spec = self._dict(cluster, self.SPEC)
        assert spec[self.IMAGE_NAME] == self.IMAGE
        assert spec[self.INSTANCES] == 1
        assert spec[self.SUPERUSER] is True

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_cluster_preloads_timescaledb(self) -> None:
        spec = self._dict(self._of_kind(self.CLUSTER_KIND), self.SPEC)
        libraries = self._dict(spec, self.POSTGRESQL)[self.PRELOAD]
        assert isinstance(libraries, list)
        assert "timescaledb" in libraries

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_cluster_bootstraps_the_swarm_database(self) -> None:
        spec = self._dict(self._of_kind(self.CLUSTER_KIND), self.SPEC)
        assert self._dict(self._dict(spec, self.BOOTSTRAP), self.INITDB)[self.DATABASE] == "swarm"

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    @pytest.mark.parametrize("extension", ["postgis", "timescaledb"])
    def test_the_cluster_creates_the_extensions(self, extension: str) -> None:
        assert f"CREATE EXTENSION IF NOT EXISTS {extension}" in "\n".join(self._post_init())

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    @pytest.mark.parametrize("service", SERVICES)
    def test_each_service_gets_a_nologin_role_and_its_schema(self, service: str) -> None:
        statements = self._post_init()
        assert any(f"CREATE ROLE {service}" in s and "NOLOGIN" in s for s in statements)
        assert any(f"CREATE SCHEMA IF NOT EXISTS {service} AUTHORIZATION {service}" in s for s in statements)

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_pooler_fronts_the_primary_in_transaction_mode(self) -> None:
        pooler = self._of_kind(self.POOLER_KIND)
        assert pooler[self.API_VERSION] == self.CNPG_API
        assert self._dict(pooler, self.METADATA)[self.NAME] == self.POOLER_NAME
        spec = self._dict(pooler, self.SPEC)
        assert self._dict(spec, self.CLUSTER)[self.NAME] == self.CHART_NAME
        assert spec[self.TYPE] == "rw"
        assert self._dict(spec, self.PGBOUNCER)[self.POOL_MODE] == "transaction"

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_rendering_without_an_image_name_fails(self) -> None:
        result = self._render()
        assert result.returncode != 0
        assert self.IMAGE_NAME in result.stderr
