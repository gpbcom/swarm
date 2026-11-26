from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List, Tuple, cast

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from tests.ci.release.helpers import runs, steps, workflow


class TestReleaseWorkflow:
    SUITES: ClassVar[List[str]] = ["python", "rust", "typescript", "specs"]
    REPORTS: ClassVar[List[Tuple[str, str, str]]] = [
        ("python.yml", "services", "test-report-python-service-"),
        ("python.yml", "repository", "test-report-python-repository"),
        ("python.yml", "packages", "test-report-python-packages"),
        ("rust.yml", "check", "test-report-rust"),
        ("typescript.yml", "check", "test-report-ts-"),
        ("specs.yml", "check", "test-report-specs"),
    ]

    def jobs(self) -> Dict[str, Dict[str, JsonValue]]:
        return cast(Dict[str, Dict[str, JsonValue]], workflow("release.yml")["jobs"])

    def test_a_release_is_started_by_hand_from_develop_only(self) -> None:
        data = workflow("release.yml")
        triggers = cast(Dict[str, JsonValue], data.get("on", data.get(True)))
        assert list(triggers) == ["workflow_dispatch"]
        assert self.jobs()["version"]["if"] == "github.ref == 'refs/heads/develop'"

    def test_no_release_starts_without_its_token(self) -> None:
        assert "RELEASE_TOKEN is missing" in runs("release.yml", "version")

    def test_every_suite_of_ci_runs_with_everything_selected(self) -> None:
        assert "detect_changes.py --all" in runs("release.yml", "changes")
        for suite in self.SUITES:
            assert self.jobs()[suite]["uses"] == f"./.github/workflows/{suite}.yml"

    def test_the_release_is_written_only_when_every_suite_passed(self) -> None:
        prepare = self.jobs()["prepare"]
        assert set(cast(List[str], prepare["needs"])) >= {"version", "changes", *self.SUITES}
        condition = str(prepare["if"])
        assert "!contains(needs.*.result, 'failure')" in condition
        assert "!contains(needs.*.result, 'cancelled')" in condition

    def test_the_changelog_notes_and_test_reports_go_to_master_by_a_pull_request(self) -> None:
        script = runs("release.yml", "prepare")
        downloads = [step for step in steps("release.yml", "prepare") if "download-artifact" in str(step.get("uses"))]
        assert cast(Dict[str, str], downloads[0]["with"])["pattern"] == "test-report-*"
        assert 'release_notes.py write --version "$VERSION" --reports reports' in script
        assert 'git add CHANGELOG.md "docs/releases/v$VERSION"' in script
        assert 'git push --quiet origin "release/$VERSION"' in script
        assert '--base master --head "release/$VERSION" --label automerge' in script

    def test_the_pull_requests_are_opened_with_the_release_token_so_that_ci_runs(self) -> None:
        create = [step for step in steps("release.yml", "prepare") if "gh pr create" in str(step.get("run", ""))]
        assert cast(Dict[str, str], create[0]["env"])["GH_TOKEN"] == "${{ secrets.RELEASE_TOKEN }}"

    def test_no_script_interpolates_inputs_or_event_values(self) -> None:
        for job in self.jobs():
            if "steps" in self.jobs()[job]:
                script = runs("release.yml", job)
                assert "${{ inputs" not in script
                assert "${{ github.event" not in script

    @pytest.mark.parametrize(("name", "job", "artifact"), REPORTS)
    def test_every_suite_keeps_its_test_report_even_when_it_fails(self, name: str, job: str, artifact: str) -> None:
        uploads = [step for step in steps(name, job) if "upload-artifact" in str(step.get("uses", ""))]
        assert len(uploads) == 1
        assert uploads[0]["if"] == "always()"
        assert str(cast(Dict[str, str], uploads[0]["with"])["name"]).startswith(artifact)

    @pytest.mark.parametrize("job", ["services", "repository"])
    def test_pytest_writes_junit_reports(self, job: str) -> None:
        assert "--junitxml=" in runs("python.yml", job)

    def test_the_packages_job_runs_no_tests_since_every_python_test_sits_in_the_central_tree(self) -> None:
        assert "uv run pytest" not in runs("python.yml", "packages")
