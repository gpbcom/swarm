from __future__ import annotations

# Standard library imports
import json
import re
from typing import List

# Third-party imports
import pytest

# First-party imports
from tests.harness.format_edited.helpers import CATALOGUE_RELATIVE, repo_root


class TestFormatEditedNewLayout:
    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("backend/swarm-service/src/swarm_service/drones/x.py", ["uv", "run", "ruff", "format", "{file}"]),
            ("backend/libs/lifecycle/src/x.py", ["uv", "run", "ruff", "format", "{file}"]),
            ("scripts/tool.py", ["uv", "run", "ruff", "format", "{file}"]),
            ("rust/core/src/lib.rs", ["rustfmt", "--edition", "2021", "{file}"]),
            ("infra/terraform/cells/dev/main.tf", ["terraform", "fmt", "{file}"]),
        ],
    )
    def test_the_catalogue_picks_the_formatter_of_the_new_folders(self, path: str, expected: List[str]) -> None:
        formatters = json.loads((repo_root() / CATALOGUE_RELATIVE).read_text(encoding="utf-8"))["formatters"]
        matching = [item for item in formatters if re.search(item["match"], path)]
        assert matching
        assert matching[0]["run"] == expected
