from __future__ import annotations

# Standard library imports
import re
from pathlib import Path
from typing import ClassVar, Dict, List, Tuple

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue


class TestDevEnvironment:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    DEV: ClassVar[Path] = ROOT / "infra" / "environments" / "dev"
    PLATFORM: ClassVar[Path] = DEV / "platform"
    VALUES: ClassVar[Path] = DEV / "values.yaml"
    CHARTS: ClassVar[Path] = ROOT / "infra" / "charts"
    ENVIRONMENTS: ClassVar[Path] = ROOT / "infra" / "environments"

    ENCODING: ClassVar[str] = "utf-8"
    SEMVER: ClassVar[re.Pattern[str]] = re.compile(r"^v?\d+(\.\d+)+$")
    ARGO_NAMESPACE: ClassVar[str] = "argocd"
    API_VERSION: ClassVar[str] = "argoproj.io/v1alpha1"
    KIND: ClassVar[str] = "Application"
    CREATE_NAMESPACE: ClassVar[str] = "CreateNamespace=true"
    SERVER_SIDE_APPLY: ClassVar[str] = "ServerSideApply=true"
    CLOUDNATIVE_PG_FILE: ClassVar[str] = "cloudnative-pg.yaml"
    IMAGE_NAME_KEY: ClassVar[str] = "imageName"

    APPLICATIONS: ClassVar[List[Tuple[str, str, str, str]]] = [
        ("cloudnative-pg.yaml", "cloudnative-pg", "https://cloudnative-pg.github.io/charts", "cnpg-system"),
        ("keda.yaml", "keda", "https://kedacore.github.io/charts", "keda"),
        ("keda-http-add-on.yaml", "keda-add-ons-http", "https://kedacore.github.io/charts", "keda"),
    ]
    SERVICES: ClassVar[List[str]] = ["missions", "fleet", "processing", "evidence", "notifier"]
    ALLOWED_TOP_KEYS: ClassVar[List[str]] = ["global", "database", "valkey", "objectStorage", "vaultConfig", "nats"]
    FORBIDDEN_KEYS: ClassVar[List[str]] = [
        "password",
        "rootpassword",
        "token",
        "roottoken",
        "devroottoken",
        "secretkey",
        "accesskey",
        "seed",
        "nkey",
        "creds",
    ]
    NATS_JWT_KEYS: ClassVar[List[str]] = ["operatorJwt", "systemAccount", "systemAccountJwt"]

    def load(self, path: Path) -> Dict[str, JsonValue]:
        loaded = yaml.safe_load(path.read_text(encoding=self.ENCODING))
        assert isinstance(loaded, dict)
        return loaded

    def section(self, document: Dict[str, JsonValue], name: str) -> Dict[str, JsonValue]:
        value = document[name]
        assert isinstance(value, dict)
        return value

    def sync_options(self, document: Dict[str, JsonValue]) -> List[JsonValue]:
        policy = self.section(self.section(document, "spec"), "syncPolicy")
        options = policy["syncOptions"]
        assert isinstance(options, list)
        return options

    def keys_of(self, value: JsonValue) -> List[str]:
        keys: List[str] = []
        if isinstance(value, dict):
            for key, child in value.items():
                keys.append(str(key))
                keys.extend(self.keys_of(child))
        elif isinstance(value, list):
            for child in value:
                keys.extend(self.keys_of(child))
        return keys

    @pytest.mark.parametrize(("file", "chart", "repo", "namespace"), APPLICATIONS)
    def test_a_platform_application_is_a_pinned_automated_argo_application(
        self, file: str, chart: str, repo: str, namespace: str
    ) -> None:
        document = self.load(self.PLATFORM / file)
        assert document["apiVersion"] == self.API_VERSION
        assert document["kind"] == self.KIND
        assert self.section(document, "metadata")["namespace"] == self.ARGO_NAMESPACE
        spec = self.section(document, "spec")
        source = self.section(spec, "source")
        assert source["chart"] == chart
        assert source["repoURL"] == repo
        revision = source["targetRevision"]
        assert isinstance(revision, str)
        assert self.SEMVER.match(revision)
        assert self.section(spec, "destination")["namespace"] == namespace
        assert self.section(spec, "syncPolicy")["automated"] is not None
        assert self.CREATE_NAMESPACE in self.sync_options(document)

    def test_the_cloudnative_pg_application_uses_server_side_apply(self) -> None:
        document = self.load(self.PLATFORM / self.CLOUDNATIVE_PG_FILE)
        assert self.SERVER_SIDE_APPLY in self.sync_options(document)

    def test_the_dev_values_name_the_five_services_and_one_database_instance(self) -> None:
        values = self.load(self.VALUES)
        assert self.section(values, "global")["services"] == self.SERVICES
        assert self.section(values, "database")["instances"] == 1

    def test_the_dev_values_leave_the_image_name_to_terraform(self) -> None:
        assert self.IMAGE_NAME_KEY not in self.keys_of(self.load(self.VALUES))

    def test_the_dev_values_only_use_known_sections(self) -> None:
        assert set(self.load(self.VALUES)) <= set(self.ALLOWED_TOP_KEYS)

    def test_no_values_file_holds_a_secret(self) -> None:
        files = sorted(self.CHARTS.glob("*/values.yaml")) + sorted(self.ENVIRONMENTS.glob("**/*.yaml"))
        assert files
        for file in files:
            for document in yaml.safe_load_all(file.read_text(encoding=self.ENCODING)):
                found = {key.lower() for key in self.keys_of(document)} & set(self.FORBIDDEN_KEYS)
                assert not found, f"{file} holds {found}"

    def test_the_dev_values_hold_a_nats_section_with_a_jetstream_file_storage_size(self) -> None:
        nats = self.section(self.load(self.VALUES), "nats")
        file_storage = self.section(self.section(nats, "jetstream"), "fileStorage")
        size = file_storage["size"]
        assert isinstance(size, str)
        assert size.strip()

    def test_the_dev_values_leave_the_nats_operator_jwts_to_terraform(self) -> None:
        keys = self.keys_of(self.load(self.VALUES))
        for key in self.NATS_JWT_KEYS:
            assert key not in keys
