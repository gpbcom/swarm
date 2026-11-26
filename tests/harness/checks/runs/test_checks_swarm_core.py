from __future__ import annotations

# Standard library imports
import os
import subprocess
from pathlib import Path

# First-party imports
from tests.harness.checks.helpers import ROOT, call

GIT_ENV = {
    "GIT_AUTHOR_NAME": "T",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "T",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}


class TestChecksSwarmCore:
    def test_a_service_importing_swarm_core_is_detected(self, tmp_path: Path) -> None:
        source = tmp_path / "services" / "engine" / "src" / "engine"
        source.mkdir(parents=True)
        (source / "core.py").write_text("from swarm_core import plan\n", encoding="utf-8")
        assert call(f"checks.imports_swarm_core(Path({str(tmp_path)!r}))") is True

    def test_a_tree_without_the_import_is_not_detected(self, tmp_path: Path) -> None:
        source = tmp_path / "services" / "engine" / "src" / "engine"
        source.mkdir(parents=True)
        (source / "core.py").write_text("import os\n", encoding="utf-8")
        assert call(f"checks.imports_swarm_core(Path({str(tmp_path)!r}))") is False

    def test_the_wheel_is_skipped_when_no_python_code_imports_it(self, tmp_path: Path) -> None:
        manifest = tmp_path / "rust" / "swarm-core" / "python"
        manifest.mkdir(parents=True)
        (manifest / "Cargo.toml").write_text("", encoding="utf-8")
        setup = (
            f"checks.ROOT = Path({str(tmp_path)!r}); c = checks.Checks('T9.02', Path({str(tmp_path)!r}))\n"
            "checks.install_swarm_core(c)"
        )
        skipped = call("c.not_applicable + c.passed + [str(f) for f in c.failures]", setup)
        assert skipped == ["swarm_core wheel: no Python code imports swarm_core"]

    def test_a_copied_file_has_a_newer_modification_time_than_its_source(self, tmp_path: Path) -> None:
        repo = tmp_path / "repo"
        repo.mkdir()
        env = {**os.environ, **GIT_ENV}
        for args in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "x"]):
            subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)
        source = repo / "changed.txt"
        source.write_text("a", encoding="utf-8")
        os.utime(source, (1_000_000, 1_000_000))
        setup = f"tree = checks.isolated_tree(['changed.txt'], Path({str(repo)!r}))"
        try:
            copied = call("(tree / 'changed.txt').stat().st_mtime", setup)
        finally:
            subprocess.run(["git", "worktree", "prune"], cwd=repo, check=False, capture_output=True)
        assert isinstance(copied, float) and copied > source.stat().st_mtime + 1000
        assert ROOT.exists()
