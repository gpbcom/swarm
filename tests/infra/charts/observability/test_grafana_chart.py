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


class TestGrafanaChart:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[4]
    CHART: ClassVar[Path] = ROOT / "infra" / "charts" / "grafana"
    NAMESPACE: ClassVar[str] = "cell-test"
    NAME: ClassVar[str] = "grafana"
    REPOSITORY: ClassVar[str] = "grafana/grafana"
    PORTS: ClassVar[List[int]] = [3000]
    PEERS: ClassVar[List[Dict[str, Dict[str, JsonValue]]]] = [{"podSelector": {}}]

    def _load(self, name: str) -> Dict[str, JsonValue]:
        loaded = yaml.safe_load((self.CHART / name).read_text(encoding="utf-8"))
        assert isinstance(loaded, dict)
        return cast(Dict[str, JsonValue], loaded)

    def _section(self, document: JsonValue, key: str) -> Dict[str, JsonValue]:
        assert isinstance(document, dict)
        section = document[key]
        assert isinstance(section, dict)
        return section

    def _render_text(self) -> str:
        result = subprocess.run(
            ["helm", "template", self.NAME, str(self.CHART), "--namespace", self.NAMESPACE],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def _render(self) -> List[Dict[str, JsonValue]]:
        return [cast(Dict[str, JsonValue], d) for d in yaml.safe_load_all(self._render_text()) if d]

    def _find(self, kind: str) -> Dict[str, JsonValue]:
        found: Optional[Dict[str, JsonValue]] = None
        for document in self._render():
            metadata = self._section(document, "metadata")
            if document["kind"] == kind and metadata["name"] == self.NAME:
                found = document
        assert found is not None
        return found

    def _container(self, kind: str) -> Dict[str, JsonValue]:
        spec = self._section(self._find(kind), "spec")
        containers = self._section(self._section(spec, "template"), "spec")["containers"]
        assert isinstance(containers, list)
        container = containers[0]
        assert isinstance(container, dict)
        return container

    def _numbers(self, ports: JsonValue, key: str) -> List[JsonValue]:
        assert isinstance(ports, list)
        return [p[key] for p in ports if isinstance(p, dict)]

    def _config_documents(self) -> List[Dict[str, JsonValue]]:
        documents: List[Dict[str, JsonValue]] = []
        for document in self._render():
            if document["kind"] != "ConfigMap":
                continue
            data = document.get("data")
            assert isinstance(data, dict)
            for text in data.values():
                assert isinstance(text, str)
                loaded = yaml.safe_load(text)
                if isinstance(loaded, dict):
                    documents.append(cast(Dict[str, JsonValue], loaded))
        return documents

    def test_chart_yaml_declares_api_v2_and_the_name(self) -> None:
        chart = self._load("Chart.yaml")
        assert chart["apiVersion"] == "v2"
        assert chart["name"] == self.NAME

    def test_values_pin_the_image(self) -> None:
        image = self._section(self._load("values.yaml"), "image")
        assert image["repository"] == self.REPOSITORY
        assert image["tag"]
        assert image["tag"] != "latest"

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
    def test_the_service_exposes_the_grafana_ports(self) -> None:
        ports = self._section(self._find("Service"), "spec")["ports"]
        assert set(self.PORTS) <= set(self._numbers(ports, "port"))

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_deployment_runs_one_grafana_on_its_port(self) -> None:
        tag = self._section(self._load("values.yaml"), "image")["tag"]
        spec = self._section(self._find("Deployment"), "spec")
        assert spec["replicas"] == 1
        container = self._container("Deployment")
        assert container["image"] == f"{self.REPOSITORY}:{tag}"
        assert set(self.PORTS) <= set(self._numbers(container["ports"], "containerPort"))

    SECRET: ClassVar[str] = "grafana-admin"

    def _sources(self) -> Dict[str, Dict[str, JsonValue]]:
        found = [d for d in self._config_documents() if "datasources" in d]
        assert len(found) == 1
        listed = found[0]["datasources"]
        assert isinstance(listed, list)
        return {str(s["name"]).lower(): s for s in listed if isinstance(s, dict)}

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_data_sources_are_prometheus_loki_and_tempo(self) -> None:
        sources = self._sources()
        assert sources["prometheus"]["url"] == "http://prometheus:9090"
        assert sources["loki"]["url"] == "http://loki:3100"
        assert sources["tempo"]["url"] == "http://tempo:3200"

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_tempo_is_linked_to_loki_by_trace_id(self) -> None:
        sources = self._sources()
        links = self._section(sources["tempo"]["jsonData"], "tracesToLogsV2")
        assert links["datasourceUid"] == sources["loki"]["uid"]

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_admin_credentials_come_from_the_secret_and_no_password_is_literal(self) -> None:
        assert self._load("values.yaml")["adminSecretName"] == self.SECRET
        env = self._container("Deployment")["env"]
        assert isinstance(env, list)
        refs: List[Dict[str, JsonValue]] = []
        for entry in env:
            assert isinstance(entry, dict)
            if "valueFrom" in entry:
                refs.append(self._section(self._section(entry, "valueFrom"), "secretKeyRef"))
            else:
                assert "PASSWORD" not in str(entry["name"]).upper()
        assert len(refs) >= 2
        assert all(ref["name"] == self.SECRET for ref in refs)
