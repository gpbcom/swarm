from __future__ import annotations

# Standard library imports
import json
import logging
import re
import sys
from datetime import datetime, timedelta
from typing import Dict

# Third-party imports
from opentelemetry.sdk.trace import TracerProvider

# First-party imports
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

        assert list(data) == [
            JsonFormatter.TIME_KEY,
            JsonFormatter.LEVEL_KEY,
            JsonFormatter.LOGGER_KEY,
            JsonFormatter.MESSAGE_KEY,
        ]
        assert data[JsonFormatter.LEVEL_KEY] == "INFO"
        assert data[JsonFormatter.LOGGER_KEY] == "swarm.test"
        assert data[JsonFormatter.MESSAGE_KEY] == "hello"

    def test_the_time_is_iso_8601_in_utc(self) -> None:
        data = self.parse(JsonFormatter().format(self.make_record()))

        parsed = datetime.fromisoformat(data[JsonFormatter.TIME_KEY])

        assert parsed.utcoffset() == timedelta(0)

    def test_a_message_with_a_newline_gives_a_single_line(self) -> None:
        line = JsonFormatter().format(self.make_record("first\nsecond"))

        assert "\n" not in line
        assert self.parse(line)[JsonFormatter.MESSAGE_KEY] == "first\nsecond"

    def test_the_exception_key_is_present_only_with_exc_info(self) -> None:
        without = self.parse(JsonFormatter().format(self.make_record()))
        with_info = self.parse(JsonFormatter().format(self.make_record(exc_info=True)))

        assert JsonFormatter.EXCEPTION_KEY not in without
        assert list(with_info)[-1] == JsonFormatter.EXCEPTION_KEY
        assert "ValueError" in with_info[JsonFormatter.EXCEPTION_KEY]

    def test_non_ascii_text_is_kept(self) -> None:
        line = JsonFormatter().format(self.make_record("drone prête à décoller"))

        assert "drone prête à décoller" in line

    def test_there_is_no_colour_code(self) -> None:
        line = JsonFormatter().format(self.make_record(exc_info=True))

        assert "\x1b" not in line

    def test_a_record_formatted_inside_a_span_carries_its_trace_and_span_ids(self) -> None:
        tracer = TracerProvider().get_tracer(__name__)

        with tracer.start_as_current_span("work") as span:
            context = span.get_span_context()
            data = self.parse(JsonFormatter().format(self.make_record()))

        assert data[JsonFormatter.TRACE_ID_KEY] == format(context.trace_id, "032x")
        assert data[JsonFormatter.SPAN_ID_KEY] == format(context.span_id, "016x")

    def test_the_trace_and_span_ids_are_lower_case_hexadecimal_of_the_right_length(self) -> None:
        tracer = TracerProvider().get_tracer(__name__)

        with tracer.start_as_current_span("work"):
            data = self.parse(JsonFormatter().format(self.make_record()))

        assert re.fullmatch("[0-9a-f]{32}", data[JsonFormatter.TRACE_ID_KEY])
        assert re.fullmatch("[0-9a-f]{16}", data[JsonFormatter.SPAN_ID_KEY])

    def test_a_record_formatted_in_a_child_span_keeps_the_trace_and_takes_the_child_span_id(self) -> None:
        tracer = TracerProvider().get_tracer(__name__)

        with tracer.start_as_current_span("parent"):
            outer = self.parse(JsonFormatter().format(self.make_record()))
            with tracer.start_as_current_span("child"):
                inner = self.parse(JsonFormatter().format(self.make_record()))

        assert inner[JsonFormatter.TRACE_ID_KEY] == outer[JsonFormatter.TRACE_ID_KEY]
        assert inner[JsonFormatter.SPAN_ID_KEY] != outer[JsonFormatter.SPAN_ID_KEY]

    def test_a_record_formatted_outside_any_span_has_neither_id(self) -> None:
        data = self.parse(JsonFormatter().format(self.make_record()))

        assert JsonFormatter.TRACE_ID_KEY not in data
        assert JsonFormatter.SPAN_ID_KEY not in data

    def test_a_record_formatted_after_its_span_ended_has_neither_id(self) -> None:
        tracer = TracerProvider().get_tracer(__name__)

        with tracer.start_as_current_span("work"):
            pass
        data = self.parse(JsonFormatter().format(self.make_record()))

        assert JsonFormatter.TRACE_ID_KEY not in data
        assert JsonFormatter.SPAN_ID_KEY not in data
