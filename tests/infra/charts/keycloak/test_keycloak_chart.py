from __future__ import annotations

# Standard library imports
import json
import shutil
import subprocess
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, cast

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue

HELM_MISSING = shutil.which("helm") is None


class TestKeycloakChart:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[4]
    CHART: ClassVar[Path] = ROOT / "infra" / "charts" / "keycloak"
    REALM_FILE: ClassVar[Path] = CHART / "files" / "swarm-realm.json"
    NAMESPACE: ClassVar[str] = "global"
    NAME: ClassVar[str] = "keycloak"
    REPOSITORY: ClassVar[str] = "quay.io/keycloak/keycloak"
    ADMIN_SECRET: ClassVar[str] = "keycloak-admin"
    DATABASE_SECRET: ClassVar[str] = "keycloak-database-app"
    REALM_CONFIGMAP: ClassVar[str] = "keycloak-realm"
    REALM_KEY: ClassVar[str] = "swarm-realm.json"
    IMPORT_PATH: ClassVar[str] = "/opt/keycloak/data/import"
    DATABASE_CLUSTER: ClassVar[str] = "keycloak-database"
    CLUSTER_API_VERSION: ClassVar[str] = "postgresql.cnpg.io/v1"
    PORT: ClassVar[int] = 8080
    HOST: ClassVar[str] = "id.example.org"
    INGRESS_ARGS: ClassVar[List[str]] = ["--set", "ingress.enabled=true", "--set", f"ingress.host={HOST}"]
    SECRET_WORDS: ClassVar[List[str]] = ["password", "token", "secretkey", "secret_key", "apikey", "api_key"]
    ADMIN_REFS: ClassVar[Dict[str, str]] = {
        "KC_BOOTSTRAP_ADMIN_USERNAME": "username",
        "KC_BOOTSTRAP_ADMIN_PASSWORD": "password",
    }
    DATABASE_REFS: ClassVar[Dict[str, str]] = {"KC_DB_USERNAME": "username", "KC_DB_PASSWORD": "password"}

    def _load(self, name: str) -> Dict[str, JsonValue]:
        loaded = yaml.safe_load((self.CHART / name).read_text(encoding="utf-8"))
        assert isinstance(loaded, dict)
        return cast(Dict[str, JsonValue], loaded)

    def _section(self, document: JsonValue, key: str) -> Dict[str, JsonValue]:
        assert isinstance(document, dict)
        section = document[key]
        assert isinstance(section, dict)
        return section

    def _list(self, document: JsonValue, key: str) -> List[JsonValue]:
        assert isinstance(document, dict)
        items = document[key]
        assert isinstance(items, list)
        return items

    def _render(self, extra: Optional[List[str]] = None) -> List[Dict[str, JsonValue]]:
        result = subprocess.run(
            ["helm", "template", self.NAME, str(self.CHART), "--namespace", self.NAMESPACE, *(extra or [])],
            capture_output=True,
            text=True,
            check=True,
        )
        return [cast(Dict[str, JsonValue], d) for d in yaml.safe_load_all(result.stdout) if d]

    def _find(self, kind: str, name: str, extra: Optional[List[str]] = None) -> Dict[str, JsonValue]:
        found: Optional[Dict[str, JsonValue]] = None
        for document in self._render(extra):
            if document["kind"] == kind and self._section(document, "metadata")["name"] == name:
                found = document
        assert found is not None
        return found

    def _pod_spec(self) -> Dict[str, JsonValue]:
        spec = self._section(self._find("Deployment", self.NAME), "spec")
        return self._section(self._section(spec, "template"), "spec")

    def _container(self) -> Dict[str, JsonValue]:
        container = self._list(self._pod_spec(), "containers")[0]
        assert isinstance(container, dict)
        return container

    def _env(self) -> Dict[str, Dict[str, JsonValue]]:
        env: Dict[str, Dict[str, JsonValue]] = {}
        for entry in self._list(self._container(), "env"):
            assert isinstance(entry, dict)
            env[cast(str, entry["name"])] = entry
        return env

    def _secret_ref(self, entry: Dict[str, JsonValue]) -> Dict[str, JsonValue]:
        return self._section(self._section(entry, "valueFrom"), "secretKeyRef")

    def _keys(self, node: JsonValue) -> List[str]:
        keys: List[str] = []
        if isinstance(node, dict):
            for key, value in node.items():
                keys.append(key)
                keys.extend(self._keys(value))
        elif isinstance(node, list):
            for value in node:
                keys.extend(self._keys(value))
        return keys

    def test_chart_yaml_declares_api_v2_and_the_name(self) -> None:
        chart = self._load("Chart.yaml")
        assert chart["apiVersion"] == "v2"
        assert chart["name"] == self.NAME

    def test_values_pin_the_image_and_name_the_secret_and_the_database(self) -> None:
        values = self._load("values.yaml")
        image = self._section(values, "image")
        assert image["repository"] == self.REPOSITORY
        assert image["tag"]
        assert image["tag"] != "latest"
        assert self._section(values, "admin")["credentialsSecret"] == self.ADMIN_SECRET
        database = self._section(values, "database")
        assert database["instances"]
        assert self._section(database, "storage")["size"]
        assert self._section(values, "ingress")["enabled"] is False

    def test_values_hold_no_key_that_names_a_secret(self) -> None:
        keys = [key.lower() for key in self._keys(self._load("values.yaml"))]
        assert [key for key in keys if any(word in key for word in self.SECRET_WORDS)] == []

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_deployment_starts_keycloak_in_production_mode_and_imports_the_realm(self) -> None:
        tag = self._section(self._load("values.yaml"), "image")["tag"]
        container = self._container()
        assert container["image"] == f"{self.REPOSITORY}:{tag}"
        args = self._list(container, "args")
        assert "start" in args
        assert "--import-realm" in args
        assert "start-dev" not in args
        assert self._env()["KC_DB"]["value"] == "postgres"

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_admin_and_database_credentials_come_from_secrets(self) -> None:
        env = self._env()
        for name, key in self.ADMIN_REFS.items():
            reference = self._secret_ref(env[name])
            assert reference["name"] == self.ADMIN_SECRET
            assert reference["key"] == key
        for name, key in self.DATABASE_REFS.items():
            reference = self._secret_ref(env[name])
            assert reference["name"] == self.DATABASE_SECRET
            assert reference["key"] == key

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_no_password_is_a_literal_value(self) -> None:
        for name, entry in self._env().items():
            if "PASSWORD" in name:
                assert "value" not in entry

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_realm_configmap_is_mounted_where_keycloak_imports_it(self) -> None:
        volumes = [v for v in self._list(self._pod_spec(), "volumes") if isinstance(v, dict)]
        matching = [v for v in volumes if self._section(v, "configMap")["name"] == self.REALM_CONFIGMAP]
        assert len(matching) == 1
        mounts = [m for m in self._list(self._container(), "volumeMounts") if isinstance(m, dict)]
        assert any(m["name"] == matching[0]["name"] and m["mountPath"] == self.IMPORT_PATH for m in mounts)

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_realm_configmap_holds_the_swarm_realm_file(self) -> None:
        data = self._section(self._find("ConfigMap", self.REALM_CONFIGMAP), "data")
        expected = json.loads(self.REALM_FILE.read_text(encoding="utf-8"))
        assert json.loads(cast(str, data[self.REALM_KEY])) == expected

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_service_exposes_port_8080(self) -> None:
        ports = self._list(self._section(self._find("Service", self.NAME), "spec"), "ports")
        assert any(isinstance(p, dict) and p["port"] == self.PORT for p in ports)

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_a_cloudnativepg_cluster_holds_the_keycloak_database(self) -> None:
        cluster = self._find("Cluster", self.DATABASE_CLUSTER)
        assert cluster["apiVersion"] == self.CLUSTER_API_VERSION
        initdb = self._section(self._section(self._section(cluster, "spec"), "bootstrap"), "initdb")
        assert initdb["database"] == self.NAME
        assert initdb["owner"] == self.NAME

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_there_is_no_ingress_by_default(self) -> None:
        assert [d for d in self._render() if d["kind"] == "Ingress"] == []

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_an_enabled_ingress_routes_its_host_to_the_service(self) -> None:
        spec = self._section(self._find("Ingress", self.NAME, self.INGRESS_ARGS), "spec")
        rule = self._list(spec, "rules")[0]
        assert isinstance(rule, dict)
        assert rule["host"] == self.HOST
        path = self._list(self._section(rule, "http"), "paths")[0]
        service = self._section(self._section(path, "backend"), "service")
        assert service["name"] == self.NAME
        assert self._section(service, "port")["number"] == self.PORT
