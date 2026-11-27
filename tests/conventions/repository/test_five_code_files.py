from __future__ import annotations

# Standard library imports
import subprocess
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import ClassVar, FrozenSet, List, Tuple

# First-party imports
from tests.conventions.helpers import repo_root


class TestFiveCodeFiles:
    CODE_SUFFIXES: ClassVar[FrozenSet[str]] = frozenset({".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".rs"})
    ENTRY_FILES: ClassVar[FrozenSet[str]] = frozenset(
        {"__init__.py", "conftest.py", "index.ts", "index.js", "lib.rs", "main.rs", "mod.rs"}
    )
    LIMIT: ClassVar[int] = 5
    LIST_FILES: ClassVar[Tuple[str, ...]] = ("git", "ls-files", "--cached", "--others", "--exclude-standard")

    def repository_files(self, root: Path) -> List[str]:
        """List the files of the working tree git does not ignore, committed or not (L-60).

        The ticket checks copy a ticket's files into a clean tree without committing them, so a rule that counted only
        the tracked files never saw them. A tracked file deleted from the working tree no longer counts.
        """
        result = subprocess.run(
            list(self.LIST_FILES), cwd=root, capture_output=True, text=True, check=True, encoding="utf-8"
        )
        return sorted({line for line in result.stdout.splitlines() if line and (root / line).is_file()})

    def git(self, root: Path, *args: str) -> None:
        subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True)

    def crowded_folders(self, files: List[str]) -> List[Tuple[str, int]]:
        counts: Counter[str] = Counter(
            str(PurePosixPath(name).parent)
            for name in files
            if PurePosixPath(name).suffix in self.CODE_SUFFIXES and PurePosixPath(name).name not in self.ENTRY_FILES
        )
        return sorted((folder, count) for folder, count in counts.items() if count > self.LIMIT)

    def test_no_folder_of_the_repository_holds_more_than_five_code_files(self) -> None:
        crowded = self.crowded_folders(self.repository_files(repo_root()))
        assert crowded == [], "\n".join(f"{folder}: {count} code files" for folder, count in crowded)

    def test_entry_files_do_not_count_towards_the_five(self) -> None:
        files = [f"pkg/module_{n}.py" for n in range(5)] + ["pkg/__init__.py", "pkg/conftest.py", "pkg/index.ts"]
        assert self.crowded_folders(files) == []

    def test_a_sixth_code_file_of_any_language_breaks_the_rule(self) -> None:
        files = [f"pkg/module_{n}.py" for n in range(3)] + ["pkg/a.ts", "pkg/b.tsx", "pkg/c.rs"]
        assert self.crowded_folders(files) == [("pkg", 6)]

    def test_files_not_committed_yet_count_and_ignored_or_deleted_files_do_not(self, tmp_path: Path) -> None:
        self.git(tmp_path, "init", "-q")
        package = tmp_path / "pkg"
        package.mkdir()
        for n in range(5):
            (package / f"module_{n}.py").write_text("", encoding="utf-8")
        (tmp_path / ".gitignore").write_text("pkg/built.py\n", encoding="utf-8")
        (package / "built.py").write_text("", encoding="utf-8")
        self.git(tmp_path, "add", ".")
        self.git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "-m", "five")
        assert self.crowded_folders(self.repository_files(tmp_path)) == []

        (package / "new_module.py").write_text("", encoding="utf-8")
        assert self.crowded_folders(self.repository_files(tmp_path)) == [("pkg", 6)]

        (package / "module_0.py").unlink()
        assert self.crowded_folders(self.repository_files(tmp_path)) == []
