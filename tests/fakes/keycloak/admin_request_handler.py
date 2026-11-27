from __future__ import annotations

# Standard library imports
from http.server import BaseHTTPRequestHandler
from typing import ClassVar, Optional
from urllib.parse import urlsplit


class AdminRequestHandler(BaseHTTPRequestHandler):
    """Hand every request of the stand-in Keycloak admin API to its stand-in, and write its answer."""

    AUTHORIZATION_HEADER: ClassVar[str] = "Authorization"
    CONTENT_TYPE_HEADER: ClassVar[str] = "Content-Type"
    CONTENT_LENGTH_HEADER: ClassVar[str] = "Content-Length"
    LOCATION_HEADER: ClassVar[str] = "Location"
    JSON_CONTENT_TYPE: ClassVar[str] = "application/json"
    ZERO_LENGTH: ClassVar[str] = "0"

    def serve(self) -> None:
        length = int(self.headers.get(self.CONTENT_LENGTH_HEADER, self.ZERO_LENGTH))
        body = self.rfile.read(length) if length else b""
        parts = urlsplit(self.path)
        authorization: Optional[str] = self.headers.get(self.AUTHORIZATION_HEADER)
        status, location, payload = self.server.stand_in.respond(  # type: ignore[attr-defined]
            self.command, parts.path, parts.query, authorization, body
        )
        self.send_response(status)
        if location is not None:
            self.send_header(self.LOCATION_HEADER, location)
        self.send_header(self.CONTENT_TYPE_HEADER, self.JSON_CONTENT_TYPE)
        self.send_header(self.CONTENT_LENGTH_HEADER, str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        self.serve()

    def do_POST(self) -> None:
        self.serve()

    def do_PUT(self) -> None:
        self.serve()

    def do_DELETE(self) -> None:
        self.serve()

    def log_message(self, format: str, *args: str) -> None:
        return
