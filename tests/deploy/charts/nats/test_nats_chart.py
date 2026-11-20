from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Pattern, Tuple, cast

import pytest
import yaml
from pydantic import JsonValue

HELM_MISSING = shutil.which("helm") is None


class TestNatsChart:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[4]
    CHART: ClassVar[Path] = ROOT / "deploy" / "charts" / "nats"
    NAMESPACE: ClassVar[str] = "cell-test"
    NAME: ClassVar[str] = "nats"
    HEADLESS: ClassVar[str] = "nats-headless"
    CONFIG_MAP: ClassVar[str] = "nats-config"
    CONFIG_FILE: ClassVar[str] = "nats.conf"
    LEAF_SECRET: ClassVar[str] = "nats-leafnodes-tls"
    CLIENT_PORT: ClassVar[int] = 4222
    CLUSTER_PORT: ClassVar[int] = 6222
    LEAF_PORT: ClassVar[int] = 7422
    MONITOR_PORT: ClassVar[int] = 8222
    REPLICAS: ClassVar[int] = 3
    FAKE_JWT: ClassVar[str] = "eyJhbGciOiJlZDI1NTE5In0.eyJzdWIiOiJ4In0.c2lnbmF0dXJl"
    FAKE_ACCOUNT: ClassVar[str] = "A" + "B" * 55
    OPERATOR_VALUE: ClassVar[str] = "auth.operatorJwt"
    ACCOUNT_VALUE: ClassVar[str] = "auth.systemAccount"
    ACCOUNT_JWT_VALUE: ClassVar[str] = "auth.systemAccountJwt"
    REPLICAS_VALUE: ClassVar[str] = "replicas"
    LEAF_VALUE: ClassVar[str] = "leafnodes.enabled"
    AUTH_VALUES: ClassVar[List[Tuple[str, str]]] = [
        (OPERATOR_VALUE, FAKE_JWT),
        (ACCOUNT_VALUE, FAKE_ACCOUNT),
        (ACCOUNT_JWT_VALUE, FAKE_JWT),
    ]
    LEAF_FILES: ClassVar[List[str]] = ["tls.crt", "tls.key", "ca.crt"]
    SEED_PATTERN: ClassVar[Pattern[str]] = re.compile(r"S[OAU][A-Z2-7]{56}")
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

    def _sets(self, leafnodes: bool) -> List[Tuple[str, str]]:
        sets = list(self.AUTH_VALUES)
        if leafnodes:
            sets.append((self.LEAF_VALUE, "true"))
        return sets

    def _render(self, tmp_path: Path, leafnodes: bool) -> List[JsonValue]:
        result = self._helm(tmp_path, self._sets(leafnodes))
        assert result.returncode == 0, result.stderr
        return [cast(JsonValue, d) for d in yaml.safe_load_all(result.stdout) if d]

    def _find(self, tmp_path: Path, kind: str, name: str, leafnodes: bool = False) -> JsonValue:
        found: Optional[JsonValue] = None
        for document in self._render(tmp_path, leafnodes):
            if self._section(document, "kind") == kind and self._mapping(document, "metadata")["name"] == name:
                found = document
        assert found is not None
        return found

    def _conf(self, tmp_path: Path, leafnodes: bool = False) -> str:
        config_map = self._find(tmp_path, "ConfigMap", self.CONFIG_MAP, leafnodes)
        conf = self._mapping(config_map, "data")[self.CONFIG_FILE]
        assert isinstance(conf, str)
        return conf

    def _pod_spec(self, tmp_path: Path, leafnodes: bool = False) -> JsonValue:
        spec = self._mapping(self._find(tmp_path, "StatefulSet", self.NAME, leafnodes), "spec")
        return self._mapping(spec, "template")["spec"]

    def _container(self, tmp_path: Path) -> JsonValue:
        return self._items(self._pod_spec(tmp_path), "containers")[0]

    def _field(self, items: List[JsonValue], key: str) -> List[JsonValue]:
        found: List[JsonValue] = []
        for item in items:
            if isinstance(item, dict) and key in item:
                found.append(item[key])
        return found

    def _allowed_ports(self, tmp_path: Path, leafnodes: bool) -> List[JsonValue]:
        policy = self._mapping(self._find(tmp_path, "NetworkPolicy", self.NAME, leafnodes), "spec")
        allowed: List[JsonValue] = []
        for rule in self._items(policy, "ingress"):
            allowed.extend(self._field(self._items(rule, "ports"), "port"))
        return allowed

    def test_chart_yaml_declares_an_application_chart(self) -> None:
        chart = self._load("Chart.yaml")
        assert self._section(chart, "apiVersion") == "v2"
        assert self._section(chart, "name") == self.NAME
        assert self._section(chart, "type") == "application"
        version = self._section(chart, "version")
        assert isinstance(version, str)
        assert self.SEMVER_PATTERN.match(version)
        app_version = self._section(chart, "appVersion")
        assert app_version
        assert app_version != "latest"

    def test_values_describe_a_cluster_of_three_with_jetstream(self) -> None:
        assert self._values("replicas") == self.REPLICAS
        assert self._values("image", "repository") == self.NAME
        tag = self._values("image", "tag")
        assert tag
        assert tag != "latest"
        assert self._values("jetstream", "domain") == "cell"
        assert self._values("jetstream", "fileStorage", "size")

    def test_values_leave_the_operator_credentials_empty(self) -> None:
        assert self._values("auth", "operatorJwt") == ""
        assert self._values("auth", "systemAccount") == ""
        assert self._values("auth", "systemAccountJwt") == ""

    def test_values_keep_the_leaf_node_listener_off_and_name_its_secret(self) -> None:
        assert self._values("leafnodes", "enabled") is False
        assert self._values("leafnodes", "tls", "secretName") == self.LEAF_SECRET

    def test_values_fix_the_ports(self) -> None:
        assert self._values("ports", "client") == self.CLIENT_PORT
        assert self._values("ports", "cluster") == self.CLUSTER_PORT
        assert self._values("ports", "leafnodes") == self.LEAF_PORT
        assert self._values("ports", "monitor") == self.MONITOR_PORT

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_statefulset_runs_three_nodes_with_a_volume_claim(self, tmp_path: Path) -> None:
        spec = self._mapping(self._find(tmp_path, "StatefulSet", self.NAME), "spec")
        assert spec["replicas"] == self.REPLICAS
        assert spec["serviceName"] == self.HEADLESS
        claims = self._items(spec, "volumeClaimTemplates")
        assert len(claims) >= 1
        requests = self._mapping(self._mapping(claims[0], "spec"), "resources")["requests"]
        assert isinstance(requests, dict)
        assert requests["storage"] == self._values("jetstream", "fileStorage", "size")
        container = self._container(tmp_path)
        ports = self._field(self._items(container, "ports"), "containerPort")
        for port in (self.CLIENT_PORT, self.CLUSTER_PORT, self.MONITOR_PORT):
            assert port in ports
        arguments = self._items(container, "args")
        assert any(isinstance(a, str) and "--config" in a for a in arguments)

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_configuration_enables_jetstream_in_the_cell_domain(self, tmp_path: Path) -> None:
        conf = self._conf(tmp_path)
        assert re.search(r"jetstream\s*\{", conf)
        assert re.search(r"domain:\s*\"?cell\"?", conf)

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_configuration_routes_the_three_nodes_together(self, tmp_path: Path) -> None:
        conf = self._conf(tmp_path)
        for index in range(self.REPLICAS):
            assert f"nats-{index}.{self.HEADLESS}" in conf
        assert str(self.CLUSTER_PORT) in conf

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_configuration_runs_in_operator_mode(self, tmp_path: Path) -> None:
        conf = self._conf(tmp_path)
        assert re.search(rf"operator:\s*\"?{re.escape(self.FAKE_JWT)}", conf)
        assert re.search(rf"system_account:\s*\"?{re.escape(self.FAKE_ACCOUNT)}", conf)
        assert re.search(r"type:\s*full", conf)
        assert "resolver_preload" in conf
        assert self.FAKE_ACCOUNT in conf[conf.index("resolver_preload") :]

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_configuration_has_no_leaf_node_listener_by_default(self, tmp_path: Path) -> None:
        assert "leafnodes" not in self._conf(tmp_path)

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_services_expose_the_client_port_and_the_headless_peers(self, tmp_path: Path) -> None:
        service = self._mapping(self._find(tmp_path, "Service", self.NAME), "spec")
        assert self.CLIENT_PORT in self._field(self._items(service, "ports"), "port")
        headless = self._mapping(self._find(tmp_path, "Service", self.HEADLESS), "spec")
        assert headless["clusterIP"] == "None"

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_disruption_budget_allows_one_node_down(self, tmp_path: Path) -> None:
        budget = self._find(tmp_path, "PodDisruptionBudget", self.NAME)
        assert self._section(budget, "apiVersion") == "policy/v1"
        assert self._mapping(budget, "spec")["maxUnavailable"] == 1

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_network_policy_allows_the_client_and_cluster_ports(self, tmp_path: Path) -> None:
        allowed = self._allowed_ports(tmp_path, False)
        assert self.CLIENT_PORT in allowed
        assert self.CLUSTER_PORT in allowed

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_leaf_node_listener_is_configured_with_mutual_tls(self, tmp_path: Path) -> None:
        conf = self._conf(tmp_path, leafnodes=True)
        assert "leafnodes" in conf
        block = conf[conf.index("leafnodes") :]
        assert str(self.LEAF_PORT) in block
        assert "tls" in block
        assert "verify: true" in block
        for name in self.LEAF_FILES:
            assert name in block

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    def test_the_leaf_node_listener_mounts_its_secret_and_opens_its_port(self, tmp_path: Path) -> None:
        volumes = self._items(self._pod_spec(tmp_path, leafnodes=True), "volumes")
        secrets: List[JsonValue] = []
        for volume in self._field(volumes, "secret"):
            secrets.extend(self._field([volume], "secretName"))
        assert self.LEAF_SECRET in secrets
        service = self._mapping(self._find(tmp_path, "Service", self.NAME, leafnodes=True), "spec")
        assert self.LEAF_PORT in self._field(self._items(service, "ports"), "port")
        assert self.LEAF_PORT in self._allowed_ports(tmp_path, True)

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    @pytest.mark.parametrize(
        ("omitted", "replicas", "named"),
        [
            (OPERATOR_VALUE, "", OPERATOR_VALUE),
            (ACCOUNT_VALUE, "", ACCOUNT_VALUE),
            (ACCOUNT_JWT_VALUE, "", ACCOUNT_JWT_VALUE),
            ("", "1", REPLICAS_VALUE),
        ],
    )
    def test_the_rendering_fails_naming_the_value(
        self, tmp_path: Path, omitted: str, replicas: str, named: str
    ) -> None:
        sets = [(name, value) for name, value in self.AUTH_VALUES if name != omitted]
        if replicas:
            sets.append((self.REPLICAS_VALUE, replicas))
        result = self._helm(tmp_path, sets)
        assert result.returncode != 0
        assert named in result.stderr

    @pytest.mark.skipif(HELM_MISSING, reason="helm is not installed")
    @pytest.mark.parametrize("leafnodes", [False, True])
    def test_no_document_holds_a_password_or_a_seed(self, tmp_path: Path, leafnodes: bool) -> None:
        result = self._helm(tmp_path, self._sets(leafnodes))
        assert result.returncode == 0, result.stderr
        assert "password" not in result.stdout.lower()
        assert not self.SEED_PATTERN.search(result.stdout)
