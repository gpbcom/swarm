from __future__ import annotations

# Standard library imports
import threading
from http.server import ThreadingHTTPServer
from types import TracebackType
from typing import ClassVar, Dict, List, Optional, Self, Type

# Third-party imports
from google.protobuf.message import Message
from opentelemetry.proto.common.v1.common_pb2 import KeyValue
from opentelemetry.proto.logs.v1.logs_pb2 import ResourceLogs
from opentelemetry.proto.metrics.v1.metrics_pb2 import ResourceMetrics
from opentelemetry.proto.trace.v1.trace_pb2 import ResourceSpans, Span

# First-party imports
from tests.fakes.otlp.otlp_request_handler import OtlpRequestHandler


class OtlpStandInServer:
    """A local OTLP/HTTP collector: keeps the resource spans, metrics and logs it receives.

    Attributes:
        HOST (str): The address the server listens on.
        URL_TEMPLATE (str): The base URL of the server.
        VALUE_KIND (str): The name of the protobuf ``oneof`` of an attribute value.
        requests (Dict[str, List[Message]]): The decoded requests, by path.
    """

    HOST: ClassVar[str] = "127.0.0.1"
    URL_TEMPLATE: ClassVar[str] = "http://{host}:{port}"
    VALUE_KIND: ClassVar[str] = "value"

    def __init__(self) -> None:
        self.requests: Dict[str, List[Message]] = {}
        self.lock = threading.Lock()
        self.server: Optional[ThreadingHTTPServer] = None
        self.thread: Optional[threading.Thread] = None

    ############################
    # Publicly Exposed Methods #
    ############################

    def __enter__(self) -> Self:
        server = ThreadingHTTPServer((self.HOST, 0), OtlpRequestHandler)
        server.stand_in = self  # type: ignore[attr-defined]
        self.server = server
        self.thread = threading.Thread(target=server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(
        self,
        error_type: Optional[Type[BaseException]],
        error: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()
        if self.thread is not None:
            self.thread.join()

    @property
    def url(self) -> str:
        assert self.server is not None
        return self.URL_TEMPLATE.format(host=self.HOST, port=self.server.server_address[1])

    def receive(self, path: str, request: Message) -> None:
        with self.lock:
            self.requests.setdefault(path, []).append(request)

    def received(self, path: str) -> List[Message]:
        with self.lock:
            return list(self.requests.get(path, []))

    @property
    def resource_spans(self) -> List[ResourceSpans]:
        return [group for request in self.received(OtlpRequestHandler.TRACES_PATH) for group in request.resource_spans]  # type: ignore[attr-defined]

    @property
    def resource_metrics(self) -> List[ResourceMetrics]:
        return [
            group for request in self.received(OtlpRequestHandler.METRICS_PATH) for group in request.resource_metrics
        ]  # type: ignore[attr-defined]

    @property
    def resource_logs(self) -> List[ResourceLogs]:
        return [group for request in self.received(OtlpRequestHandler.LOGS_PATH) for group in request.resource_logs]  # type: ignore[attr-defined]

    @property
    def spans(self) -> List[Span]:
        return [span for group in self.resource_spans for scope in group.scope_spans for span in scope.spans]

    @classmethod
    def attributes(cls, key_values: List[KeyValue]) -> Dict[str, str]:
        """Give attributes as a dict of text, whatever the type of each value."""
        found: Dict[str, str] = {}
        for key_value in key_values:
            kind = key_value.value.WhichOneof(cls.VALUE_KIND)
            found[key_value.key] = str(getattr(key_value.value, kind)) if kind else ""
        return found
