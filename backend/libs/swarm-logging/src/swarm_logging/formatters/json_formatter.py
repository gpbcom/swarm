from __future__ import annotations

# Standard library imports
import json
import logging
from datetime import UTC, datetime
from typing import ClassVar, Dict

# Third-party imports
from opentelemetry import trace


class JsonFormatter(logging.Formatter):
    """Format a log record as one line of JSON.

    Attributes:
        TIME_KEY (str): The key of the record's time, ISO 8601 in UTC with milliseconds.
        LEVEL_KEY (str): The key of the level name.
        LOGGER_KEY (str): The key of the logger name.
        MESSAGE_KEY (str): The key of the message.
        EXCEPTION_KEY (str): The key of the formatted exception, present only with ``exc_info``.
        TRACE_ID_KEY (str): The key of the trace id, present only inside a valid span.
        SPAN_ID_KEY (str): The key of the span id, present only inside a valid span.
        TIMESPEC (str): The precision of the time, as ``datetime.isoformat`` names it.

    Notes:
        - JSON is used in production because Loki stores one event per line and reads its fields.
        - ``json.dumps`` escapes newlines, so a multi-line message or traceback stays on one line.
        - **No colour code is written**, because a JSON consumer would read it as part of the text.
    """

    TIME_KEY: ClassVar[str] = "time"
    LEVEL_KEY: ClassVar[str] = "level"
    LOGGER_KEY: ClassVar[str] = "logger"
    MESSAGE_KEY: ClassVar[str] = "message"
    EXCEPTION_KEY: ClassVar[str] = "exception"
    TRACE_ID_KEY: ClassVar[str] = "trace_id"
    SPAN_ID_KEY: ClassVar[str] = "span_id"
    TIMESPEC: ClassVar[str] = "milliseconds"
    TRACE_ID_FORMAT: ClassVar[str] = "032x"
    SPAN_ID_FORMAT: ClassVar[str] = "016x"

    ############################
    # Publicly Exposed Methods #
    ############################

    def format(self, record: logging.LogRecord) -> str:
        """Format one record as a JSON object.

        Args:
            record (logging.LogRecord): The record to format.

        Returns:
            str: A JSON line with ``time``, ``level``, ``logger``, ``message`` and, with ``exc_info``, ``exception``, plus ``trace_id`` and ``span_id`` inside a valid span.
        """
        data: Dict[str, str] = {
            self.TIME_KEY: datetime.fromtimestamp(record.created, tz=UTC).isoformat(timespec=self.TIMESPEC),
            self.LEVEL_KEY: record.levelname,
            self.LOGGER_KEY: record.name,
            self.MESSAGE_KEY: record.getMessage(),
        }
        if record.exc_info:
            data[self.EXCEPTION_KEY] = self.formatException(record.exc_info)
        span_context = trace.get_current_span().get_span_context()
        if span_context.is_valid:
            data[self.TRACE_ID_KEY] = format(span_context.trace_id, self.TRACE_ID_FORMAT)
            data[self.SPAN_ID_KEY] = format(span_context.span_id, self.SPAN_ID_FORMAT)
        return json.dumps(data, ensure_ascii=False)
