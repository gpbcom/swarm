from __future__ import annotations

# Standard library imports
import posixpath
import re
import shutil
import subprocess
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Pattern, Tuple, cast

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue

HELM_MISSING = shutil.which("helm") is None


class TestSimulatorChart:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[4]
    CHART: ClassVar[Path] = ROOT / "deploy" / "charts" / "simulator"
    NAMESPACE: ClassVar[str] = "cell-test"
    NAME: ClassVar[str] = "simulator"
    CONFIG_MAP: ClassVar[str] = "simulator-config"
    CONFIG_FILE: ClassVar[str] = "app.yaml"
    DRONES: ClassVar[str] = "synthetic-drones"
    SITL: ClassVar[str] = "px4-sitl"
    SECRET_NAME: ClassVar[str] = "simulator-nats-credentials"
    OPERATOR_ID: ClassVar[str] = "0190a5c4-7b1e-7c3a-9d2e-4f5a6b7c8d9e"
    OPERATOR_VALUE: ClassVar[str] = "operatorId"
    IMAGE_TAG_VALUE: ClassVar[str] = "image.tag"
    SITL_TAG_VALUE: ClassVar[str] = "px4Sitl.image.tag"
    IMAGE_REPOSITORY: ClassVar[str] = "ghcr.io/gpbcom/swarm/simulator"
    TAGS: ClassVar[List[Tuple[str, str]]] = [(IMAGE_TAG_VALUE, "1.2.3"), (SITL_TAG_VALUE, "1.14.0")]
    COUNT: ClassVar[int] = 10
    BASE_PORT: ClassVar[int] = 14600
    SITL_PORT: ClassVar[int] = 18570
    SUBJECT_PREFIX: ClassVar[str] = f"op.{OPERATOR_ID}.mission."
    UDP: ClassVar[str] = "UDP"
    TCP: ClassVar[str] = "TCP"
    NAME_LABEL: ClassVar[str] = "app.kubernetes.io/name"
    COMMAND_KEYS: ClassVar[List[str]] = ["command", "args"]
    SECRET_PATTERN: ClassVar[Pattern[str]] = re.compile(r"seed|jwt|password|secret", re.IGNORECASE)
    DOCKERFILE: ClassVar[Path] = ROOT / "services" / "simulator" / "Dockerfile"
    PARSER: ClassVar[Path] = (
        ROOT / "services" / "simulator" / "src" / "simulator" / "api" / "cli" / "simulator_argument_parser.py"
    )
    WORKDIR_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^WORKDIR\s+(\S+)", re.MULTILINE)
    DEFAULT_CONFIG_PATTERN: ClassVar[Pattern[str]] = re.compile(r'DEFAULT_CONFIG: ClassVar\[str\] = "([^"]+)"')
    CONFIG_OPTION: ClassVar[str] = "--config"
    SEMVER_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$")

    def _load(self, name: str) -> JsonValue:
        return cast(JsonValue, yaml.safe_load((self.CHART / name).read_text(encoding="utf-8")))

    def _section(self, document: JsonValue, key: str) -> JsonValue:
        assert isinstance(document, dict)
        return document[key]

    def _mapping(self, document: JsonValue, key: str) -> Dict[str, JsonValue]:
        section = self._section(document, key)
        assert isinstance(section, dict)
        return section

    def _items(self, document: JsonValue, key: str) -> List[JsonValue]:
        section = self._section(document, key)
        assert isinstance(section, list)
        return section

    def _values(self, *path: str) -> JsonValue:
        node = self._load("values.yaml")
        for key in path:
            node = self._section(node, key)
        return node

    def _helm(self, tmp_path: Path, sets: List[Tuple[str, str]]) -> subprocess.CompletedProcess[str]:
        copy = tmp_path / self.NAME
        if not copy.exists():
            shutil.copytree(self.CHART, copy)
        command = ["helm", "template", self.NAME, str(copy), "--namespace", self.NAMESPACE]
        for name, value in sets:
            command.extend(["--set", f"{name}={value}"])
        return subprocess.run(command, capture_output=True, text=True, check=False)

    def _sets(self) -> List[Tuple[str, str]]:
        return [(self.OPERATOR_VALUE, self.OPERATOR_ID), *self.TAGS]

    def _render(self, tmp_path: Path) -> List[JsonValue]:
        result = self._helm(tmp_path, self._sets())
        assert result.returncode == 0, result.stderr
        return [cast(JsonValue, d) for d in yaml.safe_load_all(result.stdout) if d]

    def _find(self, tmp_path: Path, kind: str, name: str) -> JsonValue:
        found: Optional[JsonValue] = None
        for document in self._render(tmp_path):
            if self._section(document, "kind") == kind and self._mapping(document, "metadata")["name"] == name:
                found = document
        assert found is not None
        return found

    def _pod_spec(self, tmp_path: Path, name: str) -> JsonValue:
        spec = self._mapping(self._find(tmp_path, "Deployment", name), "spec")
        return self._mapping(spec, "template")["spec"]

    def _container(self, tmp_path: Path, name: str) -> JsonValue:
        return self._items(self._pod_spec(tmp_path, name), "containers")[0]

    def _command_line(self, tmp_path: Path, name: str) -> List[str]:
        container = self._container(tmp_path, name)
        assert isinstance(container, dict)
        words: List[str] = []
        for key in self.COMMAND_KEYS:
            listed = container.get(key, [])
            assert isinstance(listed, list)
            words.extend(str(word) for word in listed)
        return words

    def _app_config(self, tmp_path: Path) -> Dict[str, JsonValue]:
        config_map = self._find(tmp_path, "ConfigMap", self.CONFIG_MAP)
        text = self._mapping(config_map, "data")[self.CONFIG_FILE]
        assert isinstance(text, str)
        loaded = yaml.safe_load(text)
        assert isinstance(loaded, dict)
        return cast(Dict[str, JsonValue], loaded)

    def _ports(self, tmp_path: Path, name: str) -> List[Tuple[JsonValue, JsonValue]]:
        spec = self._mapping(self._find(tmp_path, "Service", name), "spec")
        found: List[Tuple[JsonValue, JsonValue]] = []
        for port in self._items(spec, "ports"):
            assert isinstance(port, dict)
            found.append((port["port"], port.get("protocol", self.TCP)))
        return found

    def test_chart_yaml_declares_an_application_chart(self) -> None:
        chart = self._load("Chart.yaml")
        assert self._section(chart, "apiVersion") == "v2"
        assert self._section(chart, "name") == self.NAME
        version = self._section(chart, "version")
        assert version == "0.1.0"
        assert isinstance(version, str)
        assert self.SEMVER_PATTERN.match(version)

    def test_values_leave_the_image_tags_empty(self) -> None:
        assert self._values("image", "repository")
        assert self._values("image", "tag") == ""
        assert self._values("px4Sitl", "image", "repository")
        assert self._values("px4Sitl", "image", "tag") == ""

    def test_the_image_is_the_one_images_workflow_pushes_and_signs(self) -> None:
        assert self._values("image", "repository") == self.IMAGE_REPOSITORY

    def test_values_fix_the_simulated_fleet(self) -> None:
        assert self._values("px4Sitl", "port") == self.SITL_PORT
        assert self._values("syntheticDrones", "count") == self.COUNT
        assert self._values("syntheticDrones", "basePort") == self.BASE_PORT
        assert self._values("syntheticDrones", "speedMS") == 10
        assert self._values("syntheticDrones", "tickMs") == 50

    def test_values_leave_the_operator_empty_and_name_the_credentials_secret(self) -> None:
        assert self._values(self.OPERATOR_VALUE) == ""
        assert self._values("nats", "servers")
        assert self._values("nats", "credentialsSecretName") == self.SECRET_NAME

    def test_values_hold_no_seed_jwt_or_password(self) -> None:
        text = (self.CHART / "values.yaml").read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.lstrip().startswith("#"):
                continue
            key = line.split(":")[0].strip()
            if self.SECRET_PATTERN.search(key) and key != "credentialsSecretName":
                assert line.partition(":")[2].strip().strip("\"'") == ""

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_configuration_names_the_operator_subject_and_credentials(self, tmp_path: Path) -> None:
        config = self._app_config(tmp_path)
        assert config["operator_id"] == self.OPERATOR_ID
        responder = config["responder"]
        assert isinstance(responder, dict)
        subject = responder["subject"]
        assert isinstance(subject, str)
        assert subject.startswith(self.SUBJECT_PREFIX)
        nats = config["nats"]
        assert isinstance(nats, dict)
        path = nats["credentials_path"]
        assert isinstance(path, str)
        mounts = self._items(self._container(tmp_path, self.NAME), "volumeMounts")
        paths = [m["mountPath"] for m in mounts if isinstance(m, dict)]
        assert any(isinstance(p, str) and path.startswith(p) for p in paths)

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_simulator_serves_with_the_credentials_secret_mounted(self, tmp_path: Path) -> None:
        assert "serve" in self._command_line(tmp_path, self.NAME)
        volumes = self._items(self._pod_spec(tmp_path, self.NAME), "volumes")
        secrets: List[JsonValue] = []
        for volume in volumes:
            if isinstance(volume, dict) and "secret" in volume:
                secrets.append(self._mapping(volume, "secret")["secretName"])
        assert self._values("nats", "credentialsSecretName") in secrets

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_synthetic_drones_run_ten_drones_bound_to_every_address(self, tmp_path: Path) -> None:
        words = self._command_line(tmp_path, self.DRONES)
        assert "swarm-synthetic-drones" in words
        assert words[words.index("--count") + 1] == str(self.COUNT)
        assert words[words.index("--bind") + 1] == "0.0.0.0"

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_synthetic_drones_service_opens_ten_udp_ports(self, tmp_path: Path) -> None:
        expected = [(self.BASE_PORT + index, self.UDP) for index in range(self.COUNT)]
        assert self._ports(tmp_path, self.DRONES) == expected

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_px4_sitl_runs_behind_a_udp_service(self, tmp_path: Path) -> None:
        assert self._pod_spec(tmp_path, self.SITL)
        assert self._ports(tmp_path, self.SITL) == [(self.SITL_PORT, self.UDP)]

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_only_the_simulator_pods_reach_the_simulated_drones(self, tmp_path: Path) -> None:
        policies = [d for d in self._render(tmp_path) if self._section(d, "kind") == "NetworkPolicy"]
        covered: List[JsonValue] = []
        for policy in policies:
            spec = self._mapping(policy, "spec")
            labels = self._mapping(self._mapping(spec, "podSelector"), "matchLabels")
            covered.append(labels.get(self.NAME_LABEL))
            for rule in self._items(spec, "ingress"):
                for source in self._items(rule, "from"):
                    assert isinstance(source, dict)
                    source_labels = self._mapping(self._mapping(source, "podSelector"), "matchLabels")
                    assert self.NAME in source_labels.values()
        assert self.DRONES in covered
        assert self.SITL in covered

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    @pytest.mark.parametrize(
        "omitted",
        [OPERATOR_VALUE, IMAGE_TAG_VALUE, SITL_TAG_VALUE],
    )
    def test_the_rendering_fails_naming_the_value(self, tmp_path: Path, omitted: str) -> None:
        sets = [(name, value) for name, value in self._sets() if name != omitted]
        result = self._helm(tmp_path, sets)
        assert result.returncode != 0
        assert omitted in result.stderr

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_mounted_configuration_is_the_file_the_simulator_reads(self, tmp_path: Path) -> None:
        words = self._command_line(tmp_path, self.NAME)
        workdirs = self.WORKDIR_PATTERN.findall(self.DOCKERFILE.read_text(encoding="utf-8"))
        assert workdirs
        default = self.DEFAULT_CONFIG_PATTERN.search(self.PARSER.read_text(encoding="utf-8"))
        assert default is not None
        read = default.group(1)
        if self.CONFIG_OPTION in words:
            read = words[words.index(self.CONFIG_OPTION) + 1]
        read = posixpath.normpath(posixpath.join(workdirs[-1], read))
        mounts = self._items(self._container(tmp_path, self.NAME), "volumeMounts")
        mounted = [m["mountPath"] for m in mounts if isinstance(m, dict) and m.get("subPath") == self.CONFIG_FILE]
        assert mounted == [read]
