# T0.17: Review note

**Verdict:** ✅ Approved · **Branch:** `feature/tickets`

## What changed

- Every Python app can now export traces, metrics and logs over OTLP/HTTP. This is set in the `signals` section of each app's `app.yaml`, which is off by default and gives each app its own `service_name`. The synthetic Drones get the same through the Rust crate `swarm-observability`, and the browser through `@swarm/observability`.
- Every event, request, Command and SquadFrame sent over NATS carries a W3C trace context. Each flight engine tick starts a root span. Its `traceparent` goes into the new optional `trace_parent` field of the SquadFrame, and the browser worker now decodes that field and continues the trace in a `squad_frame receive` span.
- Secrets and personal data are removed at three levels: a catalogue of sensitive key names in the services, cut URL query strings, and a `drone_id` guard on metrics. The collector deletes the same keys again.
- `operator_id` and `mission_id` are span attributes taken from baggage, not resource attributes, because one process serves several Operators. Only `service.name` and `cell` are on the resource.
- The dev cell gains five charts: the collector (tail sampling), Prometheus, Loki, Tempo and Grafana. Each has a NetworkPolicy, and Grafana's admin password comes from a Secret.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. Given the dev cell with the observability base running, when a Telemetry frame goes from the Simulator to the browser, then one trace follows it | `test_mission_actor.py::test_each_tick_produces_one_root_span_with_the_operator_and_the_mission`, `test_mission_feed_client.py::test_a_frame_with_a_trace_context_is_delivered_inside_a_consumer_span_of_its_trace`, `squad-frame-decoder.test.ts` "keeps the trace parent of the frame", `frame_tracing.test.ts` "keeps the trace and the parent span of the frame", `tests-evidences/pytest.txt`, `tests-evidences/test.txt` | ✅ Pass |
| 2. Given the signals the services produce, when they are inspected, then no secret or personal data appears in any of them | `test_redacting_span_exporter.py`, `test_metric_label_guard.py`, `test_rest_app_builder.py`, `test_mission_actor.py::test_no_span_or_metric_attribute_is_a_drone_or_a_position`, `frontend/packages/observability/test/redaction.test.ts`, `rust/swarm-observability/tests/signals.rs`, `test_otel_collector_chart.py` | ✅ Pass |

## Look at first

- **The browser end of the trace (round 1's blocking finding, now fixed).** The decoder keeps `trace_parent` when it is text, leaves it out when it is null and refuses any other type. The worker runs each decoded frame through `traceSquadFrame`. See `frontend/packages/live/src/protocol/squad-frame-decoder.ts` and `frontend/packages/live/src/worker/live-worker-core.ts`.
- **How the trace is carried.** The tick span opens with fresh baggage, the builder writes the `traceparent` into the frame, and producer and consumer spans continue it over NATS. See `backend/swarm-service/src/swarm_service/flight/missions/mission_actor.py`, `backend/swarm-service/src/swarm_service/flight/missions/squad_frame_builder.py`, `backend/swarm-clients/src/swarm_clients/flight/leaf/squad_frame_publisher.py`, `backend/swarm-clients/src/swarm_clients/gateway/nats/mission_feed_client.py` and `backend/libs/swarm-nats/src/swarm_nats/tracing/nats_trace_context.py`.
- **Identity and Operator isolation (read line by line).** `MissionSpanProcessor` copies `operator_id` from baggage, and baggage from incoming requests is trusted. This only labels spans and grants no access. NATS subjects stay `op.<operator_id>...`. See `backend/libs/swarm-web/src/swarm_web/signals/mission_span_processor.py` and `backend/libs/swarm-web/src/swarm_web/signals/signals_configurator.py`.
- **Secrets.** Check the redaction catalogue and its exporter, the query cut on REST spans, the `drone_id` guard and the collector's processors. See `backend/libs/swarm-web/src/swarm_web/conf/signal_redactions.yaml`, `backend/libs/swarm-web/src/swarm_web/signals/redacting_span_exporter.py`, `backend/libs/swarm-web/src/swarm_web/rest/rest_app_builder.py`, `backend/libs/swarm-web/src/swarm_web/signals/metric_label_guard.py` and `infra/charts/otel-collector/templates/configmap.yaml`.
- **Simulator isolation.** The simulator chart adds a `signals` block and OTLP variables only when signals are on. The synthetic Drones keep flying when no collector is reachable, and no simulated credential changed. See `infra/charts/simulator/templates/configmap.yaml`, `infra/charts/simulator/templates/synthetic-drones.yaml` and `rust/swarm-synthetic-drones/tests/signals.rs`.
- **Test helper fix.** `connz_users` now skips connections that have not authenticated yet, which removes the flaky `KeyError: 'authorized_user'` seen with two workers. See `tests/infra/nats/helpers.py`.

## Assumptions accepted

- No feature, use case or business rule: accepted, because 08-observability#signals settles what is built.
- No budget touched: accepted. The cost is per tick per Mission and never per Drone, and the browser span has no per-Drone attribute.
- No screen touched: accepted, because only `frontend/packages` change.
- The trace starts at the flight engine tick: accepted, because MAVLink carries no trace context.
- Criterion 1 is proven by tests along the path until the gateway and the flight engine are deployed in the dev cell: accepted, now that the browser decode step is tested.
- Ground control's collector endpoint and the collector's CORS origins are left to a front-end ticket: accepted, because that is outside this ticket's area.

## Follow-ups

- Add a worker-level test that feeds encoded bytes with a `trace_parent` through `LiveWorkerCore` into an in-memory exporter. The two unit tests pass on their own and missed round 1's defect.
- On a new connect and on `close()`, shut down the previous browser signals instead of just dropping them (`live-worker-core.ts`).
- Use the same sensitive keys in TypeScript as in the Python catalogue, and also redact span event attributes in TypeScript.
- Raise the OTLP log handler to INFO, or filter the exporter's HTTP loggers, so DEBUG lines stop reaching Loki.
- Stop trusting edge baggage for `operator_id`.
- Reword 08-observability to say that `operator_id` and `mission_id` are span attributes, not resource attributes.
- Fix small AGENT.md gaps:
  - logs in the branches of `MetricLabelGuard._guard`;
  - the docstring of `NatsTraceContext.__init__`;
  - the message form of `SESquadFrameInvalidTraceParent`;
  - the missing attributes of `JsonFormatter`.
- End the synthetic Drones' run span so that it gets exported.
- Read `RestAppBuilder.URL_KEYS` from the redaction catalogue.
- Pass the collector endpoint from Ground control and set the collector's CORS origins (front-end ticket).
