from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar

# Third-party imports
import pytest
from PIL import Image
from PIL.PngImagePlugin import PngInfo

# First-party imports
from tests.harness.write_specs.helpers import CHECK, PALETTISE, SPECS_RELATIVE, copy_project, output_lines, run_specs

SCREENS_RELATIVE = SPECS_RELATIVE / "screens"
GROUP = "UC-029"
OTHER_GROUP = "UC-001"
UNKNOWN_GROUP = "UC-999"
SCREEN_NAME = "a1.png"
SCREEN_SIZE = (1280, 800)
COLOUR_TYPE_OFFSET = 25
PALETTE_COLOUR_TYPE = 3
RGB_COLOUR_TYPE = 2
TEXT_KEY = "swarm-render"
TEXT_VALUE = "a hash of the source"
NOT_PALETTE = "not a 256-colour palette PNG"
MOCKUPS = "mockups"


def colour_type(path: Path) -> int:
    return path.read_bytes()[COLOUR_TYPE_OFFSET]


def write_rgb_screen(path: Path) -> None:
    """Write a 1280 x 800 RGB PNG with a gradient, so that it holds more than 256 colours, and one tEXt chunk."""
    width, height = SCREEN_SIZE
    red = Image.linear_gradient("L").resize(SCREEN_SIZE)
    green = Image.linear_gradient("L").rotate(90).resize(SCREEN_SIZE)
    blue = Image.new("L", SCREEN_SIZE, 0)
    blue.putdata([(x * 7 + y * 3) % 256 for y in range(height) for x in range(width)])
    image = Image.merge("RGB", (red, green, blue))
    info = PngInfo()
    info.add_text(TEXT_KEY, TEXT_VALUE)
    image.save(path, pnginfo=info)


class TestPalettise:
    SCREEN_PATH: ClassVar[Path] = SCREENS_RELATIVE / GROUP / SCREEN_NAME
    OTHER_PATH: ClassVar[Path] = SCREENS_RELATIVE / OTHER_GROUP / SCREEN_NAME

    @pytest.fixture
    def root(self, tmp_path: Path) -> Path:
        project = copy_project(tmp_path)
        write_rgb_screen(project / self.SCREEN_PATH)
        write_rgb_screen(project / self.OTHER_PATH)
        return project

    def test_the_fixture_screen_is_an_rgb_png_with_many_colours(self, root: Path) -> None:
        assert colour_type(root / self.SCREEN_PATH) == RGB_COLOUR_TYPE
        assert len(Image.open(root / self.SCREEN_PATH).getcolors(maxcolors=10**7) or []) > 256

    def test_a_group_screen_becomes_a_palette_png_of_the_same_size(self, root: Path) -> None:
        result = run_specs(root, PALETTISE, GROUP)
        assert result.returncode == 0
        assert colour_type(root / self.SCREEN_PATH) == PALETTE_COLOUR_TYPE
        assert Image.open(root / self.SCREEN_PATH).size == SCREEN_SIZE

    def test_the_text_chunks_are_kept(self, root: Path) -> None:
        run_specs(root, PALETTISE, GROUP)
        assert Image.open(root / self.SCREEN_PATH).text[TEXT_KEY] == TEXT_VALUE

    def test_another_group_is_left_untouched(self, root: Path) -> None:
        before = (root / self.OTHER_PATH).read_bytes()
        run_specs(root, PALETTISE, GROUP)
        assert (root / self.OTHER_PATH).read_bytes() == before
        assert colour_type(root / self.OTHER_PATH) == RGB_COLOUR_TYPE

    def test_no_group_palettises_every_screen(self, root: Path) -> None:
        result = run_specs(root, PALETTISE)
        assert result.returncode == 0
        assert colour_type(root / self.SCREEN_PATH) == PALETTE_COLOUR_TYPE
        assert colour_type(root / self.OTHER_PATH) == PALETTE_COLOUR_TYPE

    def test_the_mock_ups_folder_is_left_alone(self, root: Path) -> None:
        stray = root / SCREENS_RELATIVE / MOCKUPS / SCREEN_NAME
        write_rgb_screen(stray)
        before = stray.read_bytes()
        run_specs(root, PALETTISE)
        assert stray.read_bytes() == before

    def test_the_output_names_each_file_it_palettised(self, root: Path) -> None:
        result = run_specs(root, PALETTISE, GROUP)
        assert self.SCREEN_PATH.as_posix() in result.stdout
        assert self.OTHER_PATH.as_posix() not in result.stdout

    def test_a_second_run_rewrites_nothing_and_says_nothing(self, root: Path) -> None:
        run_specs(root, PALETTISE)
        before = (root / self.SCREEN_PATH).read_bytes()
        second = run_specs(root, PALETTISE)
        assert second.returncode == 0
        assert second.stdout.strip() == ""
        assert (root / self.SCREEN_PATH).read_bytes() == before

    def test_check_no_longer_reports_a_palettised_screen(self, root: Path) -> None:
        screen = self.SCREEN_PATH.as_posix()
        before = [line for line in output_lines(run_specs(root, CHECK)) if NOT_PALETTE in line and screen in line]
        assert before
        run_specs(root, PALETTISE, GROUP)
        after = [line for line in output_lines(run_specs(root, CHECK)) if NOT_PALETTE in line and screen in line]
        assert after == []

    def test_an_unknown_group_exits_with_one_and_says_so_on_standard_error(self, root: Path) -> None:
        result = run_specs(root, PALETTISE, UNKNOWN_GROUP)
        assert result.returncode == 1
        assert UNKNOWN_GROUP in result.stderr
