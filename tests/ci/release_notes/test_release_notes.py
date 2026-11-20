from __future__ import annotations

from pathlib import Path

import pytest

from tests.ci.release_notes.helpers import FEATURE, RULE, TICKET, TICKET_TITLE, git, make_repo, run, write_reports

VERSION = "0.2.0"
FOLDER = Path("docs/releases/v0.2.0")


class TestVersion:
    def test_the_first_release_is_0_1_0(self, tmp_path: Path) -> None:
        git(tmp_path, "init", "-q", "-b", "develop")
        git(tmp_path, "commit", "-q", "--allow-empty", "-m", "Initial commit")
        assert run(tmp_path, "version").stdout.strip() == "version=0.1.0"

    def test_the_next_release_bumps_the_minor_version_of_the_last_tag(self, tmp_path: Path) -> None:
        root = make_repo(tmp_path)
        assert run(root, "version").stdout.strip() == f"version={VERSION}"

    def test_a_requested_version_is_taken_as_it_is(self, tmp_path: Path) -> None:
        root = make_repo(tmp_path)
        assert run(root, "version", "--requested", "v1.0.0").stdout.strip() == "version=1.0.0"

    def test_a_version_already_released_is_refused(self, tmp_path: Path) -> None:
        root = make_repo(tmp_path)
        result = run(root, "version", "--requested", "0.1.0")
        assert result.returncode == 1
        assert "already released" in result.stderr

    @pytest.mark.parametrize("requested", ["1.0", "one", "1.0.0-rc"])
    def test_a_malformed_version_is_refused(self, tmp_path: Path, requested: str) -> None:
        root = make_repo(tmp_path)
        assert run(root, "version", "--requested", requested).returncode == 2


class TestWrite:
    def test_the_changelog_lists_each_commit_of_each_pull_request_by_kind(self, tmp_path: Path) -> None:
        root = make_repo(tmp_path)
        result = run(
            root, "write", "--version", VERSION, "--reports", str(write_reports(tmp_path)), "--date", "2026-11-20"
        )
        assert result.returncode == 0, result.stderr
        changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
        assert f"## [v{VERSION}](docs/releases/v{VERSION}/RELEASE_NOTES.md) - 2026-11-20" in changelog
        assert "### 🎫 Tickets" in changelog
        assert f"- {TICKET}: {TICKET_TITLE} (#7)" in changelog
        assert "### 🧰 Harness" in changelog
        assert "- Harness: every branch gets a verdict (#8)" in changelog
        assert "an old change" not in changelog

    def test_a_new_release_goes_on_top_of_the_previous_ones(self, tmp_path: Path) -> None:
        root = make_repo(tmp_path)
        (root / "CHANGELOG.md").write_text("# 📜 Changelog\n\nIntro.\n\n## [v0.1.0](x) - 2026-11-01\n\n- old\n")
        assert run(root, "write", "--version", VERSION, "--reports", str(write_reports(tmp_path))).returncode == 0
        changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
        assert changelog.startswith("# 📜 Changelog\n\nIntro.\n\n## [v0.2.0]")
        assert changelog.index("## [v0.2.0]") < changelog.index("## [v0.1.0]")

    def test_the_release_notes_name_the_tickets_delivered_and_their_features(self, tmp_path: Path) -> None:
        root = make_repo(tmp_path)
        assert run(root, "write", "--version", VERSION, "--reports", str(write_reports(tmp_path))).returncode == 0
        notes = (root / FOLDER / "RELEASE_NOTES.md").read_text(encoding="utf-8")
        assert notes.startswith(f"# 🚀 Swarm v{VERSION}")
        assert f"| [{TICKET}](../../tickets/{TICKET}/EXPLAIN.md) | {TICKET_TITLE} | {FEATURE}<br>{RULE} |" in notes
        assert "[🧪 Full test report](TEST_REPORT.md)" in notes
        assert "v0.1.0" in notes

    def test_the_test_report_sums_every_suite_of_ci(self, tmp_path: Path) -> None:
        root = make_repo(tmp_path)
        assert run(root, "write", "--version", VERSION, "--reports", str(write_reports(tmp_path))).returncode == 0
        report = (root / FOLDER / "TEST_REPORT.md").read_text(encoding="utf-8")
        assert "✅ Every test passed" in report
        assert "| ✅ python-repository/repository | 9 | 0 | 1 | 2.5 s |" in report
        assert "| ✅ rust/rust-cargo-test | 10 | 0 | 2 |" in report
        assert "| ✅ ts-frontends-ground-control/typescript | 12 | 0 | 0 |" in report
        assert "specs.py check printed nothing" in report
        assert "| ✅ ts-packages-ts-live/packages-ts-live | 8 | 0 | 1 |" in report
        assert "| ➖ ts-packages-ts-config/packages-ts-config (no test ran) | 0 | 0 | 0 |" in report
        assert (root / FOLDER / "tests" / "test-report-rust" / "rust-cargo-test.log").is_file()

    def test_a_failed_test_shows_in_the_report(self, tmp_path: Path) -> None:
        root = make_repo(tmp_path)
        assert (
            run(root, "write", "--version", VERSION, "--reports", str(write_reports(tmp_path, errors=2))).returncode
            == 0
        )
        report = (root / FOLDER / "TEST_REPORT.md").read_text(encoding="utf-8")
        assert "❌ 2 failed" in report
        assert "| ❌ python-repository/repository | 7 | 2 | 1 |" in report

    def test_no_release_without_its_test_reports(self, tmp_path: Path) -> None:
        root = make_repo(tmp_path)
        (tmp_path / "empty").mkdir()
        result = run(root, "write", "--version", VERSION, "--reports", str(tmp_path / "empty"))
        assert result.returncode == 1
        assert "without its tests" in result.stderr
        assert not (root / "CHANGELOG.md").exists()
        assert not (root / FOLDER).exists()

    def test_the_first_release_starts_after_master(self, tmp_path: Path) -> None:
        root = make_repo(tmp_path)
        git(root, "tag", "-d", "v0.1.0")
        assert run(root, "write", "--version", "0.1.0", "--reports", str(write_reports(tmp_path))).returncode == 0
        changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
        assert "an old change (#1)" in changelog
