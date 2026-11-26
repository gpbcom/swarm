from __future__ import annotations

# Standard library imports
import shutil
import subprocess
from pathlib import Path
from typing import ClassVar, Dict, List, Optional

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue


class TestVaultConfigChart:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    CHART: ClassVar[Path] = ROOT / "deploy" / "charts" / "vault-config"
    ENCODING: ClassVar[str] = "utf-8"
    HELM: ClassVar[str] = "helm"
    NAME: ClassVar[str] = "vault-config"
    NAMESPACE: ClassVar[str] = "cell-test"
    SERVICES: ClassVar[List[str]] = ["missions", "fleet"]
    SET_SERVICES: ClassVar[str] = "global.services={missions,fleet}"
    HOOK_ANNOTATION: ClassVar[str] = "argocd.argoproj.io/hook"
    DELETE_ANNOTATION: ClassVar[str] = "argocd.argoproj.io/hook-delete-policy"
    POST_SYNC: ClassVar[str] = "PostSync"
    BEFORE_HOOK_CREATION: ClassVar[str] = "BeforeHookCreation"
    JOB: ClassVar[str] = "Job"
    CONFIG_MAP: ClassVar[str] = "ConfigMap"
    JOB_API_VERSION: ClassVar[str] = "batch/v1"
    ADDRESS: ClassVar[str] = "http://openbao:8200"
    ROOT_TOKEN_SECRET: ClassVar[str] = "vault-root-token"
    SUPERUSER_SECRET: ClassVar[str] = "database-superuser"
    BAO_ADDR: ClassVar[str] = "BAO_ADDR"
    BAO_TOKEN: ClassVar[str] = "BAO_TOKEN"
    SECRET_PATTERNS: ClassVar[List[str]] = ["token", "password"]
    VALUE: ClassVar[str] = "value"
    VALUE_FROM: ClassVar[str] = "valueFrom"
    SECRET_KEY_REF: ClassVar[str] = "secretKeyRef"
    SCRIPT_TERMS: ClassVar[List[str]] = [
        "auth/kubernetes",
        "secrets enable",
        "database",
        "database/config/swarm",
        "postgresql-database-plugin",
    ]

    ############################
    # Internal Helpers Methods #
    ############################

    def _values(self) -> Dict[str, JsonValue]:
        loaded = yaml.safe_load((self.CHART / "values.yaml").read_text(encoding=self.ENCODING))
        assert isinstance(loaded, dict)
        return loaded

    def _dig(self, value: JsonValue, *path: str) -> JsonValue:
        for step in path:
            assert isinstance(value, dict), step
            value = value[step]
        return value

    def _render(self) -> List[Dict[str, JsonValue]]:
        result = subprocess.run(
            [
                self.HELM,
                "template",
                self.NAME,
                str(self.CHART),
                "--namespace",
                self.NAMESPACE,
                "--set",
                self.SET_SERVICES,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return [document for document in yaml.safe_load_all(result.stdout) if isinstance(document, dict)]

    def _find(self, kind: str) -> Dict[str, JsonValue]:
        for document in self._render():
            if document.get("kind") == kind and self._dig(document, "metadata", "name") == self.NAME:
                return document
        raise AssertionError(kind)

    def _env(self) -> List[Dict[str, JsonValue]]:
        containers = self._dig(self._find(self.JOB), "spec", "template", "spec", "containers")
        assert isinstance(containers, list)
        first = containers[0]
        assert isinstance(first, dict)
        env = first["env"]
        assert isinstance(env, list)
        return [entry for entry in env if isinstance(entry, dict)]

    def _script(self) -> str:
        data = self._find(self.CONFIG_MAP)["data"]
        assert isinstance(data, dict)
        return "\n".join(str(content) for content in data.values())

    def _secret_ref(self, name: str) -> Optional[JsonValue]:
        for entry in self._env():
            if entry["name"] == name:
                return self._dig(entry, self.VALUE_FROM, self.SECRET_KEY_REF)
        return None

    ############################
    # Publicly Exposed Methods #
    ############################

    def test_chart_yaml_names_the_chart(self) -> None:
        chart = yaml.safe_load((self.CHART / "Chart.yaml").read_text(encoding=self.ENCODING))
        assert chart["name"] == self.NAME

    def test_values_set_the_vault_address_and_root_token_secret(self) -> None:
        values = self._values()
        assert values["address"] == self.ADDRESS
        assert values["rootTokenSecret"] == self.ROOT_TOKEN_SECRET

    def test_values_set_the_database(self) -> None:
        database = self._values()["database"]
        assert isinstance(database, dict)
        assert database["host"] == "database-rw"
        assert database["port"] == 5432
        assert database["name"] == "swarm"
        assert database["superuserSecret"] == self.SUPERUSER_SECRET

    def test_values_set_the_lease_durations(self) -> None:
        values = self._values()
        assert values["ttl"] == "1h"
        assert values["maxTtl"] == "24h"

    def test_values_pin_the_image(self) -> None:
        image = self._values()["image"]
        assert isinstance(image, dict)
        assert image["repository"] == "quay.io/openbao/openbao"
        assert image["tag"]
        assert image["tag"] != "latest"

    def test_values_list_no_service_by_default(self) -> None:
        assert self._dig(self._values(), "global", "services") == []

    @pytest.mark.skipif(shutil.which(HELM) is None, reason="helm is missing")
    def test_the_job_is_a_post_sync_hook_replaced_before_creation(self) -> None:
        job = self._find(self.JOB)
        assert job["apiVersion"] == self.JOB_API_VERSION
        assert self._dig(job, "metadata", "annotations", self.HOOK_ANNOTATION) == self.POST_SYNC
        assert self._dig(job, "metadata", "annotations", self.DELETE_ANNOTATION) == self.BEFORE_HOOK_CREATION

    @pytest.mark.skipif(shutil.which(HELM) is None, reason="helm is missing")
    def test_the_job_reads_the_vault_address_from_the_values(self) -> None:
        entries = [entry for entry in self._env() if entry["name"] == self.BAO_ADDR]
        assert [entry[self.VALUE] for entry in entries] == [self.ADDRESS]

    @pytest.mark.skipif(shutil.which(HELM) is None, reason="helm is missing")
    def test_the_job_reads_the_vault_token_from_the_root_token_secret(self) -> None:
        reference = self._secret_ref(self.BAO_TOKEN)
        assert isinstance(reference, dict)
        assert reference["name"] == self.ROOT_TOKEN_SECRET
        assert reference["key"] == "token"

    @pytest.mark.skipif(shutil.which(HELM) is None, reason="helm is missing")
    @pytest.mark.parametrize("key", ["username", "password"])
    def test_the_job_reads_the_database_superuser_from_its_secret(self, key: str) -> None:
        references = [
            self._dig(entry, self.VALUE_FROM, self.SECRET_KEY_REF) for entry in self._env() if self.VALUE_FROM in entry
        ]
        matching = [ref for ref in references if isinstance(ref, dict) and ref["key"] == key]
        assert len(matching) == 1
        assert isinstance(matching[0], dict)
        assert matching[0]["name"] == self.SUPERUSER_SECRET

    @pytest.mark.skipif(shutil.which(HELM) is None, reason="helm is missing")
    @pytest.mark.parametrize("term", SCRIPT_TERMS)
    def test_the_script_configures_the_kubernetes_auth_and_the_database_engine(self, term: str) -> None:
        assert term in self._script()

    @pytest.mark.skipif(shutil.which(HELM) is None, reason="helm is missing")
    @pytest.mark.parametrize("service", SERVICES)
    def test_the_script_gives_each_service_its_role_policy_and_login(self, service: str) -> None:
        script = self._script()
        assert f"database/roles/{service}" in script
        assert f'IN ROLE "{service}"' in script
        assert "REASSIGN OWNED BY" in script
        assert f"database/creds/{service}" in script
        assert f"auth/kubernetes/role/{service}" in script
        assert f"bound_service_account_names={service}" in script

    @pytest.mark.skipif(shutil.which(HELM) is None, reason="helm is missing")
    def test_no_secret_is_a_literal_value_in_the_job(self) -> None:
        for entry in self._env():
            name = str(entry["name"]).lower()
            if any(pattern in name for pattern in self.SECRET_PATTERNS):
                assert self.VALUE not in entry, name
