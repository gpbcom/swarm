from __future__ import annotations

# Standard library imports
from typing import ClassVar

# First-party imports
from swarm_web.models.config.signals_config import SignalsConfig
from swarm_web.signals.signals_configurator import SignalsConfigurator
from tests.fakes.otlp.otlp_stand_in_server import OtlpStandInServer


class TestRedactingSpanExporter:
    AUTHORIZATION: ClassVar[str] = "http.request.header.authorization"
    EMAIL: ClassVar[str] = "user.email"
    URL: ClassVar[str] = "url.full"
    KEPT: ClassVar[str] = "http.request.method"
    KEPT_VALUE: ClassVar[str] = "GET"
    LIVE_URL: ClassVar[str] = "https://x/v1/live?token=s3cret"
    LIVE_URL_WITHOUT_QUERY: ClassVar[str] = "https://x/v1/live"
    SECRET: ClassVar[str] = "s3cret"
    EVENT: ClassVar[str] = "an-event"
    ADDRESS: ClassVar[str] = "someone@example.org"

    def received(self, server: OtlpStandInServer) -> OtlpStandInServer:
        provider = SignalsConfigurator(SignalsConfig(endpoint=server.url)).tracer_provider()
        with provider.get_tracer("test").start_as_current_span("redacted") as span:
            span.set_attribute(self.AUTHORIZATION, "Bearer " + self.SECRET)
            span.set_attribute(self.EMAIL, self.ADDRESS)
            span.set_attribute(self.URL, self.LIVE_URL)
            span.set_attribute(self.KEPT, self.KEPT_VALUE)
            span.add_event(self.EVENT, {self.EMAIL: self.ADDRESS, self.KEPT: self.KEPT_VALUE})
        assert provider.force_flush()
        provider.shutdown()
        return server

    def test_attributes_whose_key_holds_a_fragment_do_not_arrive(self, otlp_stand_in: OtlpStandInServer) -> None:
        span = self.received(otlp_stand_in).spans[0]
        attributes = OtlpStandInServer.attributes(span.attributes)
        assert self.AUTHORIZATION not in attributes
        assert self.EMAIL not in attributes
        assert attributes[self.KEPT] == self.KEPT_VALUE

    def test_the_query_string_of_a_url_is_cut(self, otlp_stand_in: OtlpStandInServer) -> None:
        span = self.received(otlp_stand_in).spans[0]
        attributes = OtlpStandInServer.attributes(span.attributes)
        assert attributes[self.URL] == self.LIVE_URL_WITHOUT_QUERY
        assert self.SECRET not in str(span)

    def test_event_attributes_are_redacted_too(self, otlp_stand_in: OtlpStandInServer) -> None:
        span = self.received(otlp_stand_in).spans[0]
        assert [event.name for event in span.events] == [self.EVENT]
        attributes = OtlpStandInServer.attributes(span.events[0].attributes)
        assert self.EMAIL not in attributes
        assert attributes[self.KEPT] == self.KEPT_VALUE
