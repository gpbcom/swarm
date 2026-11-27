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


class TestOtelCollectorChart:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[4]
    CHART: ClassVar[Path] = ROOT / "infra" / "charts" / "otel-collector"
    NAMESPACE: ClassVar[str] = "cell-test"
    NAME: ClassVar[str] = "otel-collector"
    REPOSITORY: ClassVar[str] = "otel/opentelemetry-collector-contrib"
    PORTS: ClassVar[List[int]] = [4317, 4318]
    SLOW_THRESHOLD_MS: ClassVar[int] = 250
    SAMPLING_PERCENTAGE: ClassVar[int] = 5
    DEFAULT_CELL: ClassVar[str] = "local"
    REDACTED: ClassVar[List[str]] = ["authorization", "cookie", "password", "token", "secret", "email"]
    ENDPOINTS: ClassVar[List[str]] = ["tempo:4317", "http://prometheus:9090/api/v1/write", "http://loki:3100/otlp"]
    PIPELINES: ClassVar[List[str]] = ["traces", "metrics", "logs"]
    EXPORTERS: ClassVar[List[str]] = ["otlp", "prometheusremotewrite", "otlphttp"]
    PEERS: ClassVar[List[Dict[str, Dict[str, JsonValue]]]] = [{"podSelector": {}}]
    DRONE_ID: ClassVar[str] = "drone_id"
    DELETE: ClassVar[str] = "delete"

    def _load(self, name: str) -> Dict[str, JsonValue]:
        loaded = yaml.safe_load((self.CHART / name).read_text(encoding="utf-8"))
        assert isinstance(loaded, dict)
        return cast(Dict[str, JsonValue], loaded)

    def _section(self, document: JsonValue, key: str) -> Dict[str, JsonValue]:
        assert isinstance(document, dict)
        section = document[key]
        assert isinstance(section, dict)
        return section

    def _items(self, document: JsonValue, key: str) -> List[JsonValue]:
        assert isinstance(document, dict)
        items = document[key]
        assert isinstance(items, list)
        return items

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
            if document["kind"] == kind:
                found = document
        assert found is not None
        return found

    def _config(self) -> Dict[str, JsonValue]:
        data = self._section(self._find("ConfigMap"), "data")
        for text in data.values():
            assert isinstance(text, str)
            parsed = yaml.safe_load(text)
            if isinstance(parsed, dict) and "receivers" in parsed:
                return cast(Dict[str, JsonValue], parsed)
        raise AssertionError("no collector configuration in the ConfigMap")

    def _pipeline(self, name: str) -> Dict[str, JsonValue]:
        return self._section(self._section(self._section(self._config(), "service"), "pipelines"), name)

    def _processors(self, name: str) -> List[str]:
        return [str(p) for p in self._items(self._pipeline(name), "processors")]

    def _processor_text(self, name: str) -> str:
        processors = self._section(self._config(), "processors")
        return json.dumps(processors[name])

    def _of_kind(self, pipeline: str, kind: str) -> List[str]:
        return [p for p in self._processors(pipeline) if p.split("/")[0] == kind]

    def _policy_types(self) -> Dict[str, Dict[str, JsonValue]]:
        processors = self._section(self._config(), "processors")
        name = next(p for p in processors if p.split("/")[0] == "tail_sampling")
        policies = self._items(processors[name], "policies")
        found: Dict[str, Dict[str, JsonValue]] = {}
        for policy in policies:
            assert isinstance(policy, dict)
            kind = str(policy["type"])
            found[kind] = cast(Dict[str, JsonValue], policy[kind])
        return found

    def test_chart_yaml_declares_api_v2_and_the_name(self) -> None:
        chart = self._load("Chart.yaml")
        assert chart["apiVersion"] == "v2"
        assert chart["name"] == self.NAME

    def test_values_pin_the_image_and_default_the_cell(self) -> None:
        values = self._load("values.yaml")
        image = self._section(values, "image")
        assert image["repository"] == self.REPOSITORY
        assert image["tag"]
        assert image["tag"] != "latest"
        assert values["cell"] == self.DEFAULT_CELL

    def test_values_default_the_sampling_to_the_budget(self) -> None:
        sampling = self._section(self._load("values.yaml"), "sampling")
        assert sampling["slowThresholdMs"] == self.SLOW_THRESHOLD_MS
        assert sampling["percentage"] == self.SAMPLING_PERCENTAGE

    def test_values_list_the_redacted_keys(self) -> None:
        redacted = self._items(self._load("values.yaml"), "redactedKeys")
        for key in self.REDACTED:
            assert key in redacted

    def test_values_allow_no_cors_origin_by_default(self) -> None:
        assert self._section(self._load("values.yaml"), "cors")["allowedOrigins"] == []

    def test_values_name_the_backend_endpoints(self) -> None:
        text = json.dumps(self._load("values.yaml"))
        for endpoint in self.ENDPOINTS:
            assert endpoint in text

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_deployment_exposes_the_otlp_ports(self) -> None:
        spec = self._section(self._find("Deployment"), "spec")
        containers = self._items(self._section(self._section(spec, "template"), "spec"), "containers")
        ports = self._items(containers[0], "ports")
        exposed = [p["containerPort"] for p in ports if isinstance(p, dict)]
        for port in self.PORTS:
            assert port in exposed

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_service_exposes_the_otlp_ports(self) -> None:
        ports = self._items(self._section(self._find("Service"), "spec"), "ports")
        exposed = [p["port"] for p in ports if isinstance(p, dict)]
        for port in self.PORTS:
            assert port in exposed

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_otlp_receiver_has_grpc_and_http(self) -> None:
        protocols = self._section(self._section(self._section(self._config(), "receivers"), "otlp"), "protocols")
        assert "grpc" in protocols
        assert "http" in protocols

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_resource_processor_upserts_the_cell(self) -> None:
        text = self._processor_text("resource")
        assert "cell" in text
        assert "upsert" in text
        assert self.DEFAULT_CELL in text

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    @pytest.mark.parametrize("pipeline", PIPELINES)
    def test_every_pipeline_deletes_the_redacted_keys(self, pipeline: str) -> None:
        names = self._of_kind(pipeline, "attributes") + self._of_kind(pipeline, "transform")
        assert names
        text = " ".join(self._processor_text(name) for name in names)
        assert self.DELETE in text
        for key in self.REDACTED:
            assert key in text

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_metrics_pipeline_deletes_the_drone_id_label(self) -> None:
        names = self._of_kind("metrics", "attributes") + self._of_kind("metrics", "transform")
        texts = [self._processor_text(name) for name in names]
        assert any(self.DRONE_ID in text and self.DELETE in text for text in texts)

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_traces_pipeline_samples_errors_slow_requests_and_the_rest(self) -> None:
        assert self._of_kind("traces", "tail_sampling")
        policies = self._policy_types()
        assert "ERROR" in json.dumps(policies["status_code"])
        assert policies["latency"]["threshold_ms"] == self.SLOW_THRESHOLD_MS
        assert policies["probabilistic"]["sampling_percentage"] == self.SAMPLING_PERCENTAGE

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_exporters_reach_tempo_prometheus_and_loki(self) -> None:
        exporters = self._section(self._config(), "exporters")
        kinds = [name.split("/")[0] for name in exporters]
        for kind in self.EXPORTERS:
            assert kind in kinds
        text = json.dumps(exporters)
        for endpoint in self.ENDPOINTS:
            assert endpoint in text

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    @pytest.mark.parametrize("pipeline", PIPELINES)
    def test_every_pipeline_is_limited_then_batched_before_its_exporters(self, pipeline: str) -> None:
        processors = self._processors(pipeline)
        assert processors[0].split("/")[0] == "memory_limiter"
        assert processors[-1].split("/")[0] == "batch"
        assert self._items(self._pipeline(pipeline), "exporters")
        assert "otlp" in self._items(self._pipeline(pipeline), "receivers")

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_network_policy_admits_only_pods_of_the_same_namespace(self) -> None:
        spec = self._section(self._find("NetworkPolicy"), "spec")
        assert spec["policyTypes"] == ["Ingress"]
        sources: List[JsonValue] = []
        for rule in self._items(spec, "ingress"):
            sources.extend(self._items(rule, "from"))
        assert sources == self.PEERS
