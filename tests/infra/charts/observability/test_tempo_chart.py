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


class TestTempoChart:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[4]
    CHART: ClassVar[Path] = ROOT / "infra" / "charts" / "tempo"
    NAMESPACE: ClassVar[str] = "cell-test"
    NAME: ClassVar[str] = "tempo"
    REPOSITORY: ClassVar[str] = "grafana/tempo"
    PORTS: ClassVar[List[int]] = [3200, 4317]
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
    def test_the_service_exposes_the_tempo_ports(self) -> None:
        ports = self._section(self._find("Service"), "spec")["ports"]
        assert set(self.PORTS) <= set(self._numbers(ports, "port"))

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_statefulset_runs_one_tempo_with_a_volume_claim(self) -> None:
        tag = self._section(self._load("values.yaml"), "image")["tag"]
        spec = self._section(self._find("StatefulSet"), "spec")
        assert spec["replicas"] == 1
        claims = spec["volumeClaimTemplates"]
        assert isinstance(claims, list)
        assert len(claims) >= 1
        container = self._container("StatefulSet")
        assert container["image"] == f"{self.REPOSITORY}:{tag}"
        assert set(self.PORTS) <= set(self._numbers(container["ports"], "containerPort"))

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_tempo_receives_otlp_grpc_and_keeps_blocks_for_fourteen_days(self) -> None:
        found = [d for d in self._config_documents() if "distributor" in d]
        assert len(found) == 1
        config = found[0]
        receivers = self._section(self._section(config, "distributor"), "receivers")
        protocols = self._section(self._section(receivers, "otlp"), "protocols")
        assert "grpc" in protocols
        compaction = self._section(self._section(config, "compactor"), "compaction")
        assert compaction["block_retention"] == "336h"
