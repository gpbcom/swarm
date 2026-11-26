from __future__ import annotations

# Standard library imports
import re
from pathlib import Path
from typing import Callable, ClassVar, Dict, List, Optional, Union

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue


class TestImagesWorkflow:
    READ_ONLY_PERMISSIONS: ClassVar[Dict[str, str]] = {"contents": "read"}
    PUSH_PERMISSIONS: ClassVar[Dict[str, str]] = {"contents": "read", "packages": "write", "id-token": "write"}
    JOB_NAMES: ClassVar[List[str]] = ["scan-dependencies", "image", "e2e", "publish"]
    LOCKFILES: ClassVar[List[str]] = ["uv.lock", "pnpm-lock.yaml", "rust/Cargo.lock"]
    OIDC_ISSUER: ClassVar[str] = "https://token.actions.githubusercontent.com"
    UNTRUSTED_EXPRESSIONS: ClassVar[List[str]] = ["${{ github.event", "${{ inputs.", "${{ matrix."]
    PINNED_REFERENCE: ClassVar[re.Pattern[str]] = re.compile(r"@(v\d|[0-9a-f]{40}$)")
    TEXT_KEYS: ClassVar[List[str]] = ["uses", "with", "run", "env", "if"]

    def workflow(self) -> Dict[Union[str, bool], JsonValue]:
        root = Path(__file__).resolve().parents[3]
        path = root / ".github" / "workflows" / "images.yml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        return data

    def trigger(self) -> Dict[str, JsonValue]:
        data = self.workflow()
        trigger = data.get("on", data.get(True))
        assert isinstance(trigger, dict)
        return trigger

    def jobs(self) -> Dict[str, Dict[str, JsonValue]]:
        jobs = self.workflow()["jobs"]
        assert isinstance(jobs, dict)
        return jobs

    def job(self, name: str) -> Dict[str, JsonValue]:
        return self.jobs()[name]

    def steps(self, name: str) -> List[Dict[str, JsonValue]]:
        return list(self.job(name)["steps"])

    def text(self, step: Dict[str, JsonValue]) -> str:
        return " ".join(str(step.get(key, "")) for key in self.TEXT_KEYS)

    def job_text(self, name: str) -> str:
        return " ".join(self.text(step) for step in self.steps(name))

    def runs(self, name: str) -> List[str]:
        return [str(step["run"]) for step in self.steps(name) if "run" in step]

    def uses_step(self, name: str, action: str) -> Optional[Dict[str, JsonValue]]:
        for step in self.steps(name):
            if str(step.get("uses", "")).startswith(action):
                return step
        return None

    def index_where(self, name: str, matches: Callable[[Dict[str, JsonValue]], bool], after: int = -1) -> int:
        for index, step in enumerate(self.steps(name)):
            if index > after and matches(step):
                return index
        pytest.fail(f"No matching step after {after} in job {name}.")

    def with_of(self, step: Dict[str, JsonValue]) -> Dict[str, JsonValue]:
        value = step.get("with", {})
        assert isinstance(value, dict)
        return value

    def test_it_is_a_reusable_workflow_only(self) -> None:
        assert list(self.trigger()) == ["workflow_call"]

    def test_its_inputs_are_the_images_and_the_publish_switch(self) -> None:
        inputs = self.trigger()["workflow_call"]["inputs"]
        assert set(inputs) == {"images", "publish"}
        assert inputs["images"]["type"] == "string"
        assert inputs["images"]["required"] is True
        assert inputs["publish"]["type"] == "boolean"
        assert inputs["publish"].get("required", False) is False
        assert inputs["publish"]["default"] is False

    def test_it_only_reads_the_repository_by_default(self) -> None:
        assert self.workflow()["permissions"] == self.READ_ONLY_PERMISSIONS

    @pytest.mark.parametrize("name", ["image", "publish"])
    def test_the_jobs_that_push_and_sign_have_the_permissions_to_do_so(self, name: str) -> None:
        assert self.job(name)["permissions"] == self.PUSH_PERMISSIONS

    def test_it_has_exactly_the_four_jobs(self) -> None:
        assert sorted(self.jobs()) == sorted(self.JOB_NAMES)

    @pytest.mark.parametrize(
        "name, needed",
        [("image", "scan-dependencies"), ("e2e", "image"), ("publish", "e2e")],
    )
    def test_the_jobs_run_in_order(self, name: str, needed: str) -> None:
        needs = self.job(name)["needs"]
        assert needs == needed or needs == [needed]

    def test_publishing_depends_on_the_publish_input(self) -> None:
        assert "inputs.publish" in str(self.job("publish")["if"])

    def test_the_dependency_scan_runs_osv_scanner_on_every_lock_file(self) -> None:
        text = self.job_text("scan-dependencies")
        assert "google/osv-scanner-action" in text or "osv-scanner" in " ".join(self.runs("scan-dependencies"))
        for lockfile in self.LOCKFILES:
            assert lockfile in text

    def test_the_image_job_is_a_matrix_over_the_images_input(self) -> None:
        matrix = self.job("image")["strategy"]["matrix"]
        assert "fromJSON(inputs.images)" in str(matrix)

    def test_the_image_job_logs_in_to_ghcr_with_buildx(self) -> None:
        assert self.uses_step("image", "docker/setup-buildx-action") is not None
        login = self.uses_step("image", "docker/login-action")
        assert login is not None
        assert self.with_of(login)["registry"] == "ghcr.io"

    def test_the_build_uses_the_root_context_and_the_remote_cache(self) -> None:
        build = self.uses_step("image", "docker/build-push-action")
        assert build is not None
        options = self.with_of(build)
        assert options["context"] == "."
        assert str(options["file"]).endswith("/Dockerfile")
        assert "type=gha" in str(options["cache-from"])
        assert "type=gha" in str(options["cache-to"])
        assert "mode=max" in str(options["cache-to"])

    def test_trivy_fails_the_build_on_high_and_critical_findings(self) -> None:
        action = self.uses_step("image", "aquasecurity/trivy-action")
        if action is not None:
            options = self.with_of(action)
            assert "HIGH" in str(options["severity"])
            assert "CRITICAL" in str(options["severity"])
            assert str(options["exit-code"]) == "1"
            return
        runs = [run for run in self.runs("image") if "trivy image" in run]
        assert runs
        assert "HIGH" in runs[0]
        assert "CRITICAL" in runs[0]
        assert "--exit-code 1" in runs[0] or "--exit-code=1" in runs[0]

    def test_an_sbom_is_produced_in_cyclonedx_format(self) -> None:
        text = self.job_text("image").lower()
        assert "cyclonedx" in text
        assert "sbom" in text

    def test_the_image_is_signed_attested_and_verified_by_digest(self) -> None:
        assert self.uses_step("image", "sigstore/cosign-installer") is not None
        runs = "\n".join(self.runs("image"))
        assert "cosign sign --yes" in runs
        assert "@" in runs[runs.index("cosign sign --yes") :].splitlines()[0]
        assert "cosign attest" in runs
        assert "--type cyclonedx" in runs
        assert "cosign verify" in runs
        assert f"--certificate-oidc-issuer {self.OIDC_ISSUER}" in runs

    def test_the_steps_run_build_then_trivy_then_push_then_sign(self) -> None:
        def is_build(step: Dict[str, JsonValue]) -> bool:
            return "docker/build-push-action" in str(step.get("uses", "")) or "docker build" in str(step.get("run", ""))

        def is_trivy(step: Dict[str, JsonValue]) -> bool:
            return "aquasecurity/trivy-action" in str(step.get("uses", "")) or "trivy image" in str(step.get("run", ""))

        def is_push(step: Dict[str, JsonValue]) -> bool:
            if "docker/build-push-action" in str(step.get("uses", "")):
                return str(self.with_of(step).get("push", "")).lower() in ("true", "${{ true }}")
            run = str(step.get("run", ""))
            return "docker push" in run or "imagetools create" in run

        def is_sign(step: Dict[str, JsonValue]) -> bool:
            return "cosign sign --yes" in str(step.get("run", ""))

        build = self.index_where("image", is_build)
        trivy = self.index_where("image", is_trivy, build)
        push = self.index_where("image", is_push, trivy)
        self.index_where("image", is_sign, push)

    def test_no_image_step_tags_with_the_commit_sha(self) -> None:
        for step in self.steps("image"):
            text = self.text(step)
            assert "github.sha" not in text
            assert "GITHUB_SHA" not in text

    def test_the_run_tag_uses_the_run_id(self) -> None:
        text = self.job_text("image")
        assert "github.run_id" in text or "GITHUB_RUN_ID" in text

    def test_e2e_starts_the_compose_stack_with_the_image_tag(self) -> None:
        assert "infra/compose/e2e.yaml" in " ".join(self.runs("e2e"))
        assert "SWARM_IMAGE_TAG" in self.job_text("e2e")

    def test_e2e_runs_playwright_through_pnpm(self) -> None:
        runs = [run for run in self.runs("e2e") if "pnpm" in run and "./qa/e2e" in run]
        assert any("e2e" in run.split("./qa/e2e")[1] for run in runs)

    def test_e2e_uploads_the_report_on_failure(self) -> None:
        upload = self.uses_step("e2e", "actions/upload-artifact")
        assert upload is not None
        assert "failure()" in str(upload["if"])
        assert "playwright-report" in str(self.with_of(upload)["path"])

    def test_e2e_always_brings_the_stack_down(self) -> None:
        downs = [
            step
            for step in self.steps("e2e")
            if "docker compose" in str(step.get("run", "")) and "down" in str(step.get("run", ""))
        ]
        assert downs
        assert "always()" in str(downs[-1]["if"])

    def test_publish_tags_with_the_commit_sha_and_verifies_the_signature(self) -> None:
        text = self.job_text("publish")
        assert "github.sha" in text or "GITHUB_SHA" in text
        assert "cosign verify" in " ".join(self.runs("publish"))

    def test_no_run_interpolates_an_untrusted_expression(self) -> None:
        for name in self.jobs():
            for run in self.runs(name):
                for expression in self.UNTRUSTED_EXPRESSIONS:
                    assert expression not in run

    def test_every_action_is_pinned_to_a_version(self) -> None:
        for name in self.jobs():
            for step in self.steps(name):
                if "uses" in step:
                    assert self.PINNED_REFERENCE.search(str(step["uses"])), step["uses"]
