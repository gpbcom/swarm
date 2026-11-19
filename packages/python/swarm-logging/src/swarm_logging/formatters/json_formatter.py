from __future__ import annotations

# Standard library imports
import json
import logging
from datetime import UTC, datetime
from typing import Dict


class JsonFormatter(logging.Formatter):
    """Format a log record as one line of JSON.

    Notes:
        - JSON is used in production because Loki stores one event per line and reads its fields.
        - ``json.dumps`` escapes newlines, so a multi-line message or traceback stays on one line.
        - **No colour code is written**, because a JSON consumer would read it as part of the text.
    """

    ############################
    # Publicly Exposed Methods #
    ############################

    def format(self, record: logging.LogRecord) -> str:
        """Format one record as a JSON object.

        Args:
            record (logging.LogRecord): The record to format.

        Returns:
            str: A JSON line with ``time``, ``level``, ``logger``, ``message`` and, with ``exc_info``, ``exception``.
        """
        data: Dict[str, object] = {
            "time": datetime.fromtimestamp(record.created, tz=UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)
        return json.dumps(data, ensure_ascii=False)
