from __future__ import annotations

# Standard library imports
import re
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue


class TestImageAdmission:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    PLATFORM: ClassVar[Path] = ROOT / "deploy" / "environments" / "dev" / "platform"
    APPLICATION: ClassVar[Path] = PLATFORM / "policy-controller.yaml"
    POLICY: ClassVar[Path] = PLATFORM / "cluster-image-policy.yaml"

    ENCODING: ClassVar[str] = "utf-8"
    SEMVER: ClassVar[re.Pattern[str]] = re.compile(r"^v?\d+(\.\d+)+$")
    WAVE_KEY: ClassVar[str] = "argocd.argoproj.io/sync-wave"
    OPTIONS_KEY: ClassVar[str] = "argocd.argoproj.io/sync-options"
    SKIP_DRY_RUN: ClassVar[str] = "SkipDryRunOnMissingResource=true"
    CREATE_NAMESPACE: ClassVar[str] = "CreateNamespace=true"
    IMAGES_GLOB: ClassVar[str] = "ghcr.io/gpbcom/swarm/**"
    FULCIO_URL: ClassVar[str] = "https://fulcio.sigstore.dev"
    ISSUER: ClassVar[str] = "https://token.actions.githubusercontent.com"
    SUBJECT_PREFIX: ClassVar[str] = r"^https://github\.com/gpbcom/swarm/\.github/workflows/images\.yml@"
    KEY_MATERIAL_KEYS: ClassVar[List[str]] = ["key", "data", "secret"]

    def load(self, path: Path) -> Dict[str, JsonValue]:
        loaded = yaml.safe_load(path.read_text(encoding=self.ENCODING))
        assert isinstance(loaded, dict)
        return loaded

    def section(self, document: Dict[str, JsonValue], name: str) -> Dict[str, JsonValue]:
        value = document[name]
        assert isinstance(value, dict)
        return value

    def annotations(self, document: Dict[str, JsonValue]) -> Dict[str, JsonValue]:
        return self.section(self.section(document, "metadata"), "annotations")

    def key_values(self, value: JsonValue, names: List[str]) -> List[JsonValue]:
        found: List[JsonValue] = []
        if isinstance(value, dict):
            for key, child in value.items():
                if str(key).lower() in names:
                    found.append(child)
                found.extend(self.key_values(child, names))
        elif isinstance(value, list):
            for child in value:
                found.extend(self.key_values(child, names))
        return found

    def test_the_application_is_an_argo_application_in_the_argo_namespace(self) -> None:
        document = self.load(self.APPLICATION)
        assert document["apiVersion"] == "argoproj.io/v1alpha1"
        assert document["kind"] == "Application"
        assert self.section(document, "metadata")["namespace"] == "argocd"

    def test_the_application_installs_a_pinned_policy_controller_chart(self) -> None:
        source = self.section(self.section(self.load(self.APPLICATION), "spec"), "source")
        assert source["repoURL"] == "https://sigstore.github.io/helm-charts"
        assert source["chart"] == "policy-controller"
        assert self.SEMVER.match(str(source["targetRevision"]))

    def test_the_application_syncs_automatically_into_its_own_namespace(self) -> None:
        spec = self.section(self.load(self.APPLICATION), "spec")
        assert self.section(spec, "destination")["namespace"] == "cosign-system"
        policy = self.section(spec, "syncPolicy")
        assert "automated" in policy
        options = policy["syncOptions"]
        assert isinstance(options, list)
        assert self.CREATE_NAMESPACE in options

    def test_the_webhook_only_warns_for_resources_no_policy_matches(self) -> None:
        source = self.section(self.section(self.load(self.APPLICATION), "spec"), "source")
        values = self.section(self.section(source, "helm"), "valuesObject")
        webhook = self.section(values, "webhook")
        assert self.section(webhook, "configData")["no-match-policy"] == "warn"

    def test_the_policy_is_an_enforcing_cluster_image_policy(self) -> None:
        document = self.load(self.POLICY)
        assert document["apiVersion"] == "policy.sigstore.dev/v1beta1"
        assert document["kind"] == "ClusterImagePolicy"
        assert self.section(document, "spec")["mode"] == "enforce"

    def test_the_policy_covers_the_swarm_images(self) -> None:
        images = self.section(self.load(self.POLICY), "spec")["images"]
        assert isinstance(images, list)
        assert any(isinstance(image, dict) and image.get("glob") == self.IMAGES_GLOB for image in images)

    def test_the_policy_trusts_the_images_workflow_through_keyless_signing(self) -> None:
        authorities = self.section(self.load(self.POLICY), "spec")["authorities"]
        assert isinstance(authorities, list)
        keyless = [self.section(a, "keyless") for a in authorities if isinstance(a, dict) and "keyless" in a]
        assert any(k["url"] == self.FULCIO_URL for k in keyless)
        identities = [i for k in keyless for i in k["identities"]]
        assert any(isinstance(i, dict) and i["issuer"] == self.ISSUER for i in identities)
        subjects = [str(i["subjectRegExp"]) for i in identities if isinstance(i, dict) and "subjectRegExp" in i]
        assert subjects
        assert all(subject.startswith(self.SUBJECT_PREFIX) for subject in subjects)

    def test_the_policy_skips_the_dry_run_before_its_crd_exists(self) -> None:
        options = str(self.annotations(self.load(self.POLICY))[self.OPTIONS_KEY])
        assert self.SKIP_DRY_RUN in options

    def test_the_policy_syncs_after_the_application(self) -> None:
        application_wave = self.annotations(self.load(self.APPLICATION)).get(self.WAVE_KEY)
        policy_wave = self.annotations(self.load(self.POLICY))[self.WAVE_KEY]
        if application_wave is not None:
            assert int(str(policy_wave)) > int(str(application_wave))

    @pytest.mark.parametrize("path", [APPLICATION, POLICY])
    def test_no_file_holds_key_material(self, path: Path) -> None:
        for value in self.key_values(self.load(path), self.KEY_MATERIAL_KEYS):
            assert not isinstance(value, str) or "BEGIN" not in value
            assert not isinstance(value, (str, int, float)) or not str(value).strip()
