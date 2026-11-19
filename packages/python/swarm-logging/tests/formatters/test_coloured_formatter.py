from __future__ import annotations

import logging
import sys
from typing import Tuple

import pytest

from swarm_logging.formatters.coloured_formatter import ColouredFormatter


class TestColouredFormatter:
    def make_record(self, level: int, message: str = "hello", args: Tuple[object, ...] = ()) -> logging.LogRecord:
        return logging.LogRecord("swarm.test", level, __file__, 1, message, args, None)

    @pytest.mark.parametrize(
        ("level", "code"),
        [
            (logging.DEBUG, "\x1b[36m"),
            (logging.INFO, "\x1b[32m"),
            (logging.WARNING, "\x1b[33m"),
            (logging.ERROR, "\x1b[31m"),
            (logging.CRITICAL, "\x1b[1;31m"),
        ],
    )
    def test_a_line_starts_with_its_level_code_and_ends_with_the_reset(self, level: int, code: str) -> None:
        line = ColouredFormatter().format(self.make_record(level))

        assert line.startswith(code)
        assert line.endswith("\x1b[0m")

    def test_a_custom_level_has_no_colour_code(self) -> None:
        line = ColouredFormatter().format(self.make_record(25))

        assert line == "hello"
        assert "\x1b" not in line

    def test_message_arguments_are_interpolated(self) -> None:
        line = ColouredFormatter().format(self.make_record(logging.INFO, "Created %s in %d ms.", ("alpha", 12)))

        assert "Created alpha in 12 ms." in line

    def test_a_traceback_is_included_for_exc_info(self) -> None:
        try:
            raise ValueError("boom")
        except ValueError:
            record = logging.LogRecord("swarm.test", logging.ERROR, __file__, 1, "failed", (), sys.exc_info())

        line = ColouredFormatter().format(record)

        assert "Traceback" in line
        assert "ValueError: boom" in line
        assert line.endswith("\x1b[0m")

    def test_the_fmt_argument_is_honoured(self) -> None:
        line = ColouredFormatter(fmt="%(levelname)s|%(name)s|%(message)s").format(self.make_record(logging.INFO))

        assert line == "\x1b[32mINFO|swarm.test|hello\x1b[0m"
