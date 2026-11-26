from __future__ import annotations

# Standard library imports
from http.server import BaseHTTPRequestHandler
from typing import ClassVar

# First-party imports
from tests.fakes.keycloak.helpers import CERTS_PATH


class CertsRequestHandler(BaseHTTPRequestHandler):
    """Answer the certs path of the stand-in Keycloak, and 404 every other path."""

    OK_STATUS: ClassVar[int] = 200
    NOT_FOUND_STATUS: ClassVar[int] = 404
    CONTENT_TYPE_HEADER: ClassVar[str] = "Content-Type"
    CONTENT_LENGTH_HEADER: ClassVar[str] = "Content-Length"
    JSON_CONTENT_TYPE: ClassVar[str] = "application/json"
    EMPTY_LENGTH: ClassVar[str] = "0"

    def do_GET(self) -> None:
        if self.path != CERTS_PATH:
            self.send_response(self.NOT_FOUND_STATUS)
            self.send_header(self.CONTENT_LENGTH_HEADER, self.EMPTY_LENGTH)
            self.end_headers()
            return
        body = self.server.stand_in.certs_body()  # type: ignore[attr-defined]
        self.send_response(self.OK_STATUS)
        self.send_header(self.CONTENT_TYPE_HEADER, self.JSON_CONTENT_TYPE)
        self.send_header(self.CONTENT_LENGTH_HEADER, str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: str) -> None:
        return
