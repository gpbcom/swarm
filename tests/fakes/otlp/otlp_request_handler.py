from __future__ import annotations

# Standard library imports
import gzip
from http.server import BaseHTTPRequestHandler
from typing import ClassVar, Dict, Type

# Third-party imports
from google.protobuf.message import Message
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest, ExportLogsServiceResponse
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import (
    ExportMetricsServiceRequest,
    ExportMetricsServiceResponse,
)
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
    ExportTraceServiceRequest,
    ExportTraceServiceResponse,
)


class OtlpRequestHandler(BaseHTTPRequestHandler):
    """Decode the OTLP/HTTP protobuf bodies posted to the stand-in server, and 404 every other path."""

    TRACES_PATH: ClassVar[str] = "/v1/traces"
    METRICS_PATH: ClassVar[str] = "/v1/metrics"
    LOGS_PATH: ClassVar[str] = "/v1/logs"
    REQUESTS: ClassVar[Dict[str, Type[Message]]] = {
        TRACES_PATH: ExportTraceServiceRequest,
        METRICS_PATH: ExportMetricsServiceRequest,
        LOGS_PATH: ExportLogsServiceRequest,
    }
    RESPONSES: ClassVar[Dict[str, Type[Message]]] = {
        TRACES_PATH: ExportTraceServiceResponse,
        METRICS_PATH: ExportMetricsServiceResponse,
        LOGS_PATH: ExportLogsServiceResponse,
    }
    OK_STATUS: ClassVar[int] = 200
    NOT_FOUND_STATUS: ClassVar[int] = 404
    CONTENT_TYPE_HEADER: ClassVar[str] = "Content-Type"
    CONTENT_LENGTH_HEADER: ClassVar[str] = "Content-Length"
    CONTENT_ENCODING_HEADER: ClassVar[str] = "Content-Encoding"
    GZIP_ENCODING: ClassVar[str] = "gzip"
    PROTOBUF_CONTENT_TYPE: ClassVar[str] = "application/x-protobuf"
    EMPTY_LENGTH: ClassVar[str] = "0"

    def do_POST(self) -> None:
        if self.path not in self.REQUESTS:
            self.send_response(self.NOT_FOUND_STATUS)
            self.send_header(self.CONTENT_LENGTH_HEADER, self.EMPTY_LENGTH)
            self.end_headers()
            return
        body = self.rfile.read(int(self.headers[self.CONTENT_LENGTH_HEADER]))
        if self.headers.get(self.CONTENT_ENCODING_HEADER) == self.GZIP_ENCODING:
            body = gzip.decompress(body)
        request = self.REQUESTS[self.path]()
        request.ParseFromString(body)
        self.server.stand_in.receive(self.path, request)  # type: ignore[attr-defined]
        answer = self.RESPONSES[self.path]().SerializeToString()
        self.send_response(self.OK_STATUS)
        self.send_header(self.CONTENT_TYPE_HEADER, self.PROTOBUF_CONTENT_TYPE)
        self.send_header(self.CONTENT_LENGTH_HEADER, str(len(answer)))
        self.end_headers()
        self.wfile.write(answer)

    def log_message(self, format: str, *args: str) -> None:
        return
