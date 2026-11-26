from __future__ import annotations

# Standard library imports
import shutil
import subprocess
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, cast

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue

HELM_MISSING = shutil.which("helm") is None


class TestObjectStorageChart:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    CHART: ClassVar[Path] = ROOT / "deploy" / "charts" / "object-storage"
    NAMESPACE: ClassVar[str] = "cell-test"
    NAME: ClassVar[str] = "object-storage"
    PORT: ClassVar[int] = 9000
    REPOSITORY: ClassVar[str] = "quay.io/minio/minio"
    TAG_PREFIX: ClassVar[str] = "RELEASE."
    SECRET: ClassVar[str] = "object-storage-root"
    ARGS: ClassVar[List[str]] = ["server", "/data"]
    ENV_FROM: ClassVar[List[Dict[str, Dict[str, str]]]] = [{"secretRef": {"name": SECRET}}]
    PEERS: ClassVar[List[Dict[str, Dict[str, JsonValue]]]] = [{"podSelector": {}}]
    ROOT_ENV: ClassVar[List[str]] = ["MINIO_ROOT_USER", "MINIO_ROOT_PASSWORD"]

    def _load(self, name: str) -> Dict[str, JsonValue]:
        loaded = yaml.safe_load((self.CHART / name).read_text(encoding="utf-8"))
        assert isinstance(loaded, dict)
        return cast(Dict[str, JsonValue], loaded)

    def _section(self, document: JsonValue, key: str) -> Dict[str, JsonValue]:
        assert isinstance(document, dict)
        section = document[key]
        assert isinstance(section, dict)
        return section

    def _render(self) -> List[Dict[str, JsonValue]]:
        result = subprocess.run(
            ["helm", "template", self.NAME, str(self.CHART), "--namespace", self.NAMESPACE],
            capture_output=True,
            text=True,
            check=True,
        )
        return [cast(Dict[str, JsonValue], d) for d in yaml.safe_load_all(result.stdout) if d]

    def _find(self, kind: str) -> Dict[str, JsonValue]:
        found: Optional[Dict[str, JsonValue]] = None
        for document in self._render():
            metadata = self._section(document, "metadata")
            if document["kind"] == kind and metadata["name"] == self.NAME:
                found = document
        assert found is not None
        return found

    def _container(self) -> Dict[str, JsonValue]:
        spec = self._section(self._find("StatefulSet"), "spec")
        containers = self._section(self._section(spec, "template"), "spec")["containers"]
        assert isinstance(containers, list)
        container = containers[0]
        assert isinstance(container, dict)
        return container

    def test_chart_yaml_declares_the_name(self) -> None:
        assert self._load("Chart.yaml")["name"] == self.NAME

    def test_values_pin_the_image_and_name_the_root_secret(self) -> None:
        values = self._load("values.yaml")
        image = self._section(values, "image")
        assert image["repository"] == self.REPOSITORY
        assert str(image["tag"]).startswith(self.TAG_PREFIX)
        assert self._section(values, "persistence")["size"]
        assert values["rootCredentialsSecret"] == self.SECRET

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_statefulset_serves_data_with_the_root_secret(self) -> None:
        container = self._container()
        assert container["args"] == self.ARGS
        assert container["envFrom"] == self.ENV_FROM
        ports = container["ports"]
        assert isinstance(ports, list)
        assert any(isinstance(p, dict) and p["containerPort"] == self.PORT for p in ports)

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_service_exposes_the_object_storage_port(self) -> None:
        ports = self._section(self._find("Service"), "spec")["ports"]
        assert isinstance(ports, list)
        assert any(isinstance(p, dict) and p["port"] == self.PORT for p in ports)

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_network_policy_admits_only_pods_of_the_same_namespace(self) -> None:
        spec = self._section(self._find("NetworkPolicy"), "spec")
        assert spec["policyTypes"] == ["Ingress"]
        ingress = spec["ingress"]
        assert isinstance(ingress, list)
        sources: List[JsonValue] = []
        for rule in ingress:
            assert isinstance(rule, dict)
            peers = rule["from"]
            assert isinstance(peers, list)
            sources.extend(peers)
        assert sources == self.PEERS

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_no_root_credential_is_written_as_a_literal_value(self) -> None:
        env = self._container().get("env") or []
        assert isinstance(env, list)
        for entry in env:
            assert isinstance(entry, dict)
            assert not (entry["name"] in self.ROOT_ENV and "value" in entry)
