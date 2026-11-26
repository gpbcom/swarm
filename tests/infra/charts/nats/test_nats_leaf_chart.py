from __future__ import annotations

# Standard library imports
import re
import shutil
import subprocess
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Tuple, cast

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue

HELM_MISSING = shutil.which("helm") is None


class TestNatsLeafChart:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[4]
    CHART: ClassVar[Path] = ROOT / "deploy" / "charts" / "nats-leaf"
    CELL_CHART: ClassVar[Path] = ROOT / "deploy" / "charts" / "cell" / "Chart.yaml"
    RELEASE: ClassVar[str] = "edge"
    NAME: ClassVar[str] = "nats-leaf"
    NAMESPACE: ClassVar[str] = "edge-test"
    DOMAIN: ClassVar[str] = "edge-test"
    URL: ClassVar[str] = "tls://cell.example.org:7422"
    PORT: ClassVar[int] = 4222
    CONFIG_NAME: ClassVar[str] = "nats-leaf-config"
    CONFIG_KEY: ClassVar[str] = "nats.conf"
    CREDENTIALS_SECRET: ClassVar[str] = "nats-leaf-credentials"
    TLS_SECRET: ClassVar[str] = "nats-leaf-tls"
    CREDENTIALS_PATH: ClassVar[str] = "/etc/nats-leaf-credentials/edge.creds"
    SEMVER: ClassVar[str] = r"^\d+\.\d+\.\d+([-+].+)?$"
    NKEY_SEED: ClassVar[str] = r"S[OAU][A-Z2-7]{56}"
    TLS_FILES: ClassVar[Tuple[str, ...]] = ("tls.crt", "tls.key", "ca.crt")
    URL_ARGS: ClassVar[List[str]] = ["--set", f"remote.url={URL}"]
    DOMAIN_ARGS: ClassVar[List[str]] = ["--set", f"jetstream.domain={DOMAIN}"]
    BASE_ARGS: ClassVar[List[str]] = [*URL_ARGS, *DOMAIN_ARGS]
    BAD_CASES: ClassVar[List[Tuple[List[str], str]]] = [
        (DOMAIN_ARGS, "remote.url"),
        (["--set", "remote.url=nats://cell.example.org:7422", *DOMAIN_ARGS], "remote.url"),
        (URL_ARGS, "jetstream.domain"),
        (["--set", "jetstream.domain=cell", *URL_ARGS], "jetstream.domain"),
    ]

    def _load(self, name: str) -> Dict[str, JsonValue]:
        loaded = yaml.safe_load((self.CHART / name).read_text(encoding="utf-8"))
        assert isinstance(loaded, dict)
        return cast(Dict[str, JsonValue], loaded)

    def _section(self, document: JsonValue, key: str) -> Dict[str, JsonValue]:
        assert isinstance(document, dict)
        section = document[key]
        assert isinstance(section, dict)
        return section

    def _helm(self, tmp_path: Path, extra: List[str]) -> subprocess.CompletedProcess[str]:
        copy = tmp_path / self.NAME
        shutil.copytree(self.CHART, copy)
        return subprocess.run(
            ["helm", "template", self.RELEASE, str(copy), "--namespace", self.NAMESPACE, *extra],
            capture_output=True,
            text=True,
            check=False,
        )

    def _render_text(self, tmp_path: Path) -> str:
        result = self._helm(tmp_path, self.BASE_ARGS)
        assert result.returncode == 0, result.stderr
        return result.stdout

    def _render(self, tmp_path: Path) -> List[Dict[str, JsonValue]]:
        text = self._render_text(tmp_path)
        return [cast(Dict[str, JsonValue], d) for d in yaml.safe_load_all(text) if d]

    def _find(self, tmp_path: Path, kind: str) -> Dict[str, JsonValue]:
        found: Optional[Dict[str, JsonValue]] = None
        for document in self._render(tmp_path):
            metadata = self._section(document, "metadata")
            if document["kind"] == kind and metadata["name"] == self.NAME:
                found = document
        assert found is not None
        return found

    def _config(self, tmp_path: Path) -> str:
        found: Optional[str] = None
        for document in self._render(tmp_path):
            metadata = self._section(document, "metadata")
            if document["kind"] == "ConfigMap" and metadata["name"] == self.CONFIG_NAME:
                text = self._section(document, "data")[self.CONFIG_KEY]
                assert isinstance(text, str)
                found = text
        assert found is not None
        return found

    def test_chart_yaml_declares_api_v2_the_name_and_a_semver_version(self) -> None:
        chart = self._load("Chart.yaml")
        assert chart["apiVersion"] == "v2"
        assert chart["name"] == self.NAME
        assert chart["type"] == "application"
        version = chart["version"]
        assert isinstance(version, str)
        assert re.match(self.SEMVER, version)

    def test_values_pin_the_image_and_leave_the_remote_to_the_edge(self) -> None:
        values = self._load("values.yaml")
        image = self._section(values, "image")
        assert image["repository"] == "nats"
        assert image["tag"]
        assert image["tag"] != "latest"
        jetstream = self._section(values, "jetstream")
        assert jetstream["domain"] == ""
        assert self._section(jetstream, "fileStorage")["size"]
        remote = self._section(values, "remote")
        assert remote["url"] == ""
        assert remote["credentialsSecret"] == self.CREDENTIALS_SECRET
        assert remote["tlsSecret"] == self.TLS_SECRET
        assert self._section(values, "ports")["client"] == self.PORT

    def test_the_cell_chart_does_not_list_the_leaf_node(self) -> None:
        text = self.CELL_CHART.read_text(encoding="utf-8")
        assert self.NAME not in text

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_statefulset_runs_one_leaf_node_with_a_volume_claim(self, tmp_path: Path) -> None:
        spec = self._section(self._find(tmp_path, "StatefulSet"), "spec")
        assert spec["replicas"] == 1
        claims = spec["volumeClaimTemplates"]
        assert isinstance(claims, list)
        assert len(claims) >= 1

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_pod_mounts_the_credentials_and_tls_secrets(self, tmp_path: Path) -> None:
        spec = self._section(self._find(tmp_path, "StatefulSet"), "spec")
        pod = self._section(self._section(spec, "template"), "spec")
        volumes = pod["volumes"]
        assert isinstance(volumes, list)
        names: List[JsonValue] = []
        for volume in volumes:
            assert isinstance(volume, dict)
            secret = volume.get("secret")
            if isinstance(secret, dict):
                names.append(secret["secretName"])
        assert self.CREDENTIALS_SECRET in names
        assert self.TLS_SECRET in names

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_config_enables_jetstream_with_the_edge_domain(self, tmp_path: Path) -> None:
        config = self._config(tmp_path)
        assert "jetstream" in config
        assert self.DOMAIN in config

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_config_connects_the_leaf_node_to_the_cell_over_mtls(self, tmp_path: Path) -> None:
        config = self._config(tmp_path)
        assert "leafnodes" in config
        assert "remotes" in config
        assert self.URL in config
        assert "credentials" in config
        assert self.CREDENTIALS_PATH in config
        for name in self.TLS_FILES:
            assert name in config

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_config_has_no_cluster_block(self, tmp_path: Path) -> None:
        assert "cluster" not in self._config(tmp_path)

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_service_exposes_the_client_port(self, tmp_path: Path) -> None:
        ports = self._section(self._find(tmp_path, "Service"), "spec")["ports"]
        assert isinstance(ports, list)
        assert any(isinstance(p, dict) and p["port"] == self.PORT for p in ports)

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_chart_renders_a_network_policy(self, tmp_path: Path) -> None:
        assert self._find(tmp_path, "NetworkPolicy")

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    @pytest.mark.parametrize(("extra", "value"), BAD_CASES)
    def test_a_missing_or_unsafe_value_fails_the_rendering(self, tmp_path: Path, extra: List[str], value: str) -> None:
        result = self._helm(tmp_path, extra)
        assert result.returncode != 0
        assert value in result.stderr

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_no_rendered_document_holds_a_password_or_a_seed(self, tmp_path: Path) -> None:
        text = self._render_text(tmp_path)
        assert "password" not in text.lower()
        assert re.search(self.NKEY_SEED, text) is None
