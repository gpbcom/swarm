from __future__ import annotations

# Standard library imports
from typing import Dict

# Third-party imports
from opentelemetry import baggage, trace
from opentelemetry import context as otel_context
from opentelemetry.sdk.trace import TracerProvider

# First-party imports
from swarm_nats.models.bus.nats_headers import NatsHeaders
from swarm_nats.tracing.nats_trace_context import NatsTraceContext


class TestNatsTraceContext:
    TRACER_NAME = "test_nats_trace_context"
    SPAN_NAME = "send"
    MISSION_KEY = "mission_id"
    MISSION_ID = "mission-7"
    DEADLINE_VALUE = "2026-01-01T00:00:00.000000+00:00"
    TRACE_ID_FORMAT = "032x"
    SPAN_ID_FORMAT = "016x"

    def test_inject_inside_a_span_adds_its_traceparent(self) -> None:
        tracer = TracerProvider().get_tracer(self.TRACER_NAME)
        with tracer.start_as_current_span(self.SPAN_NAME) as span:
            headers = NatsTraceContext().inject({})
            context = span.get_span_context()
        assert format(context.trace_id, self.TRACE_ID_FORMAT) in headers[NatsHeaders.TRACE_PARENT]
        assert format(context.span_id, self.SPAN_ID_FORMAT) in headers[NatsHeaders.TRACE_PARENT]

    def test_inject_keeps_the_given_headers_and_leaves_them_unchanged(self) -> None:
        tracer = TracerProvider().get_tracer(self.TRACER_NAME)
        given: Dict[str, str] = {NatsHeaders.DEADLINE: self.DEADLINE_VALUE}
        with tracer.start_as_current_span(self.SPAN_NAME):
            headers = NatsTraceContext().inject(given)
        assert headers[NatsHeaders.DEADLINE] == self.DEADLINE_VALUE
        assert NatsHeaders.TRACE_PARENT in headers
        assert NatsHeaders.TRACE_PARENT not in given

    def test_inject_outside_a_span_adds_no_traceparent(self) -> None:
        headers = NatsTraceContext().inject({})
        assert NatsHeaders.TRACE_PARENT not in headers

    def test_extract_gives_the_same_trace_as_a_remote_span(self) -> None:
        tracer = TracerProvider().get_tracer(self.TRACER_NAME)
        with tracer.start_as_current_span(self.SPAN_NAME) as span:
            headers = NatsTraceContext().inject({})
            sent = span.get_span_context()
        received = trace.get_current_span(NatsTraceContext().extract(headers)).get_span_context()
        assert received.trace_id == sent.trace_id
        assert received.is_remote

    def test_baggage_round_trips(self) -> None:
        tracer = TracerProvider().get_tracer(self.TRACER_NAME)
        token = otel_context.attach(baggage.set_baggage(self.MISSION_KEY, self.MISSION_ID))
        try:
            with tracer.start_as_current_span(self.SPAN_NAME):
                headers = NatsTraceContext().inject({})
        finally:
            otel_context.detach(token)
        assert NatsHeaders.BAGGAGE in headers
        extracted = NatsTraceContext().extract(headers)
        assert baggage.get_baggage(self.MISSION_KEY, extracted) == self.MISSION_ID

    def test_extract_without_headers_gives_an_invalid_span(self) -> None:
        span_context = trace.get_current_span(NatsTraceContext().extract(None)).get_span_context()
        assert not span_context.is_valid

    def test_extract_of_a_malformed_traceparent_gives_an_invalid_span(self) -> None:
        extracted = NatsTraceContext().extract({NatsHeaders.TRACE_PARENT: "bad"})
        assert not trace.get_current_span(extracted).get_span_context().is_valid
