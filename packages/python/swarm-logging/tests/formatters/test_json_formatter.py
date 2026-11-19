from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict

from swarm_logging.formatters.json_formatter import JsonFormatter


class TestJsonFormatter:
    def make_record(self, message: str = "hello", exc_info: bool = False) -> logging.LogRecord:
        info = None
        if exc_info:
            try:
                raise ValueError("boom")
            except ValueError:
                info = sys.exc_info()
        return logging.LogRecord("swarm.test", logging.INFO, __file__, 1, message, (), info)

    def parse(self, line: str) -> Dict[str, str]:
        return json.loads(line)

    def test_the_output_is_json_with_the_four_keys_in_order(self) -> None:
        data = self.parse(JsonFormatter().format(self.make_record()))

        assert list(data) == ["time", "level", "logger", "message"]
        assert data["level"] == "INFO"
        assert data["logger"] == "swarm.test"
        assert data["message"] == "hello"

    def test_the_time_is_iso_8601_in_utc(self) -> None:
        data = self.parse(JsonFormatter().format(self.make_record()))

        parsed = datetime.fromisoformat(data["time"])

        assert parsed.utcoffset() == timedelta(0)

    def test_a_message_with_a_newline_gives_a_single_line(self) -> None:
        line = JsonFormatter().format(self.make_record("first\nsecond"))

        assert "\n" not in line
        assert self.parse(line)["message"] == "first\nsecond"

    def test_the_exception_key_is_present_only_with_exc_info(self) -> None:
        without = self.parse(JsonFormatter().format(self.make_record()))
        with_info = self.parse(JsonFormatter().format(self.make_record(exc_info=True)))

        assert "exception" not in without
        assert list(with_info)[-1] == "exception"
        assert "ValueError" in with_info["exception"]

    def test_non_ascii_text_is_kept(self) -> None:
        line = JsonFormatter().format(self.make_record("drone prête à décoller"))

        assert "drone prête à décoller" in line

    def test_there_is_no_colour_code(self) -> None:
        line = JsonFormatter().format(self.make_record(exc_info=True))

        assert "\x1b" not in line
