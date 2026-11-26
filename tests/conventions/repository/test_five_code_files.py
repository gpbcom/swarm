from __future__ import annotations

# Standard library imports
import subprocess
from collections import Counter
from pathlib import PurePosixPath
from typing import ClassVar, FrozenSet, List, Tuple

# First-party imports
from tests.conventions.helpers import repo_root


class TestFiveCodeFiles:
    CODE_SUFFIXES: ClassVar[FrozenSet[str]] = frozenset({".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".rs"})
    ENTRY_FILES: ClassVar[FrozenSet[str]] = frozenset(
        {"__init__.py", "conftest.py", "index.ts", "index.js", "lib.rs", "main.rs", "mod.rs"}
    )
    LIMIT: ClassVar[int] = 5

    def tracked_files(self) -> List[str]:
        result = subprocess.run(
            ["git", "ls-files"], cwd=repo_root(), capture_output=True, text=True, check=True, encoding="utf-8"
        )
        return [line for line in result.stdout.splitlines() if line]

    def crowded_folders(self, files: List[str]) -> List[Tuple[str, int]]:
        counts: Counter[str] = Counter(
            str(PurePosixPath(name).parent)
            for name in files
            if PurePosixPath(name).suffix in self.CODE_SUFFIXES and PurePosixPath(name).name not in self.ENTRY_FILES
        )
        return sorted((folder, count) for folder, count in counts.items() if count > self.LIMIT)

    def test_no_folder_of_the_repository_holds_more_than_five_code_files(self) -> None:
        crowded = self.crowded_folders(self.tracked_files())
        assert crowded == [], "\n".join(f"{folder}: {count} code files" for folder, count in crowded)

    def test_entry_files_do_not_count_towards_the_five(self) -> None:
        files = [f"pkg/module_{n}.py" for n in range(5)] + ["pkg/__init__.py", "pkg/conftest.py", "pkg/index.ts"]
        assert self.crowded_folders(files) == []

    def test_a_sixth_code_file_of_any_language_breaks_the_rule(self) -> None:
        files = [f"pkg/module_{n}.py" for n in range(3)] + ["pkg/a.ts", "pkg/b.tsx", "pkg/c.rs"]
        assert self.crowded_folders(files) == [("pkg", 6)]
