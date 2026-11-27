from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Dict, Mapping, Optional, Sequence
from urllib.parse import urlsplit, urlunsplit

# Third-party imports
from opentelemetry.sdk.trace import Event, ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.util.types import AttributeValue

# First-party imports
from swarm_web.models.signals.signal_redaction_catalog import SignalRedactionCatalog


class RedactingSpanExporter(SpanExporter):
    """Exports copies of the spans, without the attributes that may hold a secret or personal data.

    Attributes:
        EMPTY (ClassVar[str]): The query string of a URL that has none.
        inner (SpanExporter): The exporter that receives the redacted spans.
        catalog (SignalRedactionCatalog): The fragments and URL keys to redact.
        logger (Logger): Logger instance.

    Notes:
        - An attribute whose key holds one fragment of the catalogue is removed, on the span and on its events.
        - The query string of the URL attributes is cut, so that a token in a query never leaves the process.
        - **The spans handed in are not changed**: the copies are exported.
    """

    EMPTY: ClassVar[str] = ""

    def __init__(self, inner: SpanExporter, catalog: SignalRedactionCatalog, logger: Optional[Logger] = None) -> None:
        """Initialise the exporter.

        Args:
            inner (SpanExporter): The exporter that receives the redacted spans.
            catalog (SignalRedactionCatalog): The fragments and URL keys to redact.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.inner = inner
        self.catalog = catalog
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _cut_query(self, value: str) -> str:
        """Cut the query string and the fragment of a URL.

        Args:
            value (str): The URL.

        Returns:
            str: The URL without its query string.
        """
        parts = urlsplit(value)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, self.EMPTY, self.EMPTY))

    def _redact(self, attributes: Optional[Mapping[str, AttributeValue]]) -> Dict[str, AttributeValue]:
        """Remove the attributes to redact and cut the URLs.

        Args:
            attributes (Optional[Mapping[str, AttributeValue]]): The attributes of a span or of an event.

        Returns:
            Dict[str, AttributeValue]: The attributes that may leave the process.
        """
        kept: Dict[str, AttributeValue] = {}
        for key, value in (attributes or {}).items():
            lowered = key.lower()
            if any(fragment in lowered for fragment in self.catalog.fragments):
                self.logger.debug("Removed the attribute %s.", key)
            elif lowered in self.catalog.url_keys and isinstance(value, str):
                kept[key] = self._cut_query(value)
                self.logger.debug("Cut the query of %s.", key)
            else:
                kept[key] = value
        return kept

    def _copy(self, span: ReadableSpan) -> ReadableSpan:
        """Copy a span with redacted attributes.

        Args:
            span (ReadableSpan): The finished span.

        Returns:
            ReadableSpan: The copy.
        """
        events = [Event(event.name, self._redact(event.attributes), event.timestamp) for event in span.events]
        return ReadableSpan(
            name=span.name,
            context=span.context,
            parent=span.parent,
            resource=span.resource,
            attributes=self._redact(span.attributes),
            events=events,
            links=span.links,
            kind=span.kind,
            status=span.status,
            start_time=span.start_time,
            end_time=span.end_time,
            instrumentation_scope=span.instrumentation_scope,
        )

    ############################
    # Publicly Exposed Methods #
    ############################

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export redacted copies of the spans.

        Args:
            spans (Sequence[ReadableSpan]): The finished spans.

        Returns:
            SpanExportResult: The result of the inner exporter.
        """
        result = self.inner.export([self._copy(span) for span in spans])
        self.logger.debug("Exported %d redacted spans.", len(spans))
        return result

    def shutdown(self) -> None:
        """Shut the inner exporter down."""
        self.logger.debug("Shut the redacting exporter down.")
        self.inner.shutdown()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Flush the inner exporter.

        Args:
            timeout_millis (int): The time allowed, in milliseconds.

        Returns:
            bool: The answer of the inner exporter.
        """
        self.logger.debug("Flushed the redacting exporter.")
        return self.inner.force_flush(timeout_millis)
