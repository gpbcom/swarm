from __future__ import annotations

from pathlib import Path

import pytest

from tests.harness.write_specs.helpers import (
    BUILD,
    ENCODING,
    IDENTITY_RELATIVE,
    MOCKUP_CSS_RELATIVE,
    TOKENS_CSS_RELATIVE,
    TOKENS_DIR_RELATIVE,
    copy_project,
    run_specs,
    tokens_lines,
)

LIGHT_BACKGROUND = "--color-background: #f8fafc;"
DARK_BACKGROUND = "--color-background: #0b1220;"
DARK_QUERY = "@media (prefers-color-scheme: dark)"
OLD_PRIMARY = "| `color.primary` | `#4338ca` |"
NEW_PRIMARY = "| `color.primary` | `#3730a3` |"
NEW_PRIMARY_CSS = "--color-primary: #3730a3;"
STALE_MARKER = "SPEC-11"
HAND_EDIT = "/* by hand */\n"


@pytest.fixture
def root(tmp_path: Path) -> Path:
    return copy_project(tmp_path)


@pytest.fixture
def built(root: Path) -> Path:
    run_specs(root, BUILD)
    return root


class TestTokensPackage:
    def test_build_writes_the_tokens_beside_the_mock_up_stylesheet(self, built: Path) -> None:
        tokens = built / TOKENS_CSS_RELATIVE
        assert tokens.is_file()
        mockups = (built / MOCKUP_CSS_RELATIVE).read_text(encoding=ENCODING)
        assert tokens.read_text(encoding=ENCODING) == mockups

    def test_the_tokens_hold_a_light_and_a_dark_value(self, built: Path) -> None:
        text = (built / TOKENS_CSS_RELATIVE).read_text(encoding=ENCODING)
        light, _, dark = text.partition(DARK_QUERY)
        assert LIGHT_BACKGROUND in light
        assert DARK_BACKGROUND in dark

    def test_a_changed_token_reaches_both_stylesheets_in_one_build(self, root: Path) -> None:
        page = root / IDENTITY_RELATIVE
        text = page.read_text(encoding=ENCODING)
        assert OLD_PRIMARY in text
        page.write_text(text.replace(OLD_PRIMARY, NEW_PRIMARY), encoding=ENCODING)
        run_specs(root, BUILD)
        assert NEW_PRIMARY_CSS in (root / TOKENS_CSS_RELATIVE).read_text(encoding=ENCODING)
        assert NEW_PRIMARY_CSS in (root / MOCKUP_CSS_RELATIVE).read_text(encoding=ENCODING)

    def test_check_has_nothing_to_say_about_fresh_tokens(self, built: Path) -> None:
        assert tokens_lines(built) == []

    def test_a_hand_edited_tokens_file_is_reported_as_stale(self, built: Path) -> None:
        tokens = built / TOKENS_CSS_RELATIVE
        tokens.write_text(tokens.read_text(encoding=ENCODING) + HAND_EDIT, encoding=ENCODING)
        lines = tokens_lines(built)
        assert lines
        assert any(STALE_MARKER in line for line in lines)

    def test_a_deleted_tokens_file_is_reported(self, built: Path) -> None:
        (built / TOKENS_CSS_RELATIVE).unlink()
        lines = tokens_lines(built)
        assert lines
        assert any(STALE_MARKER in line for line in lines)

    def test_build_creates_the_missing_source_folder(self, root: Path) -> None:
        assert not (root / TOKENS_DIR_RELATIVE).exists()
        run_specs(root, BUILD)
        assert (root / TOKENS_DIR_RELATIVE).is_dir()
