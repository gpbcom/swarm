# T0.17: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🎯 Constraints

- One trace must follow a Telemetry frame from the Simulator to the browser, and no signal may hold a secret or personal data ([TICKET.md](TICKET.md), [08-observability](../../specs/technical/08-observability.md#signals)).
- The package import table of AGENT.md stays unchanged ([`AGENT.md`](../../../AGENT.md)), and a model never logs.
- Cost per tick per Mission, never per Drone: no `drone_id` on metrics ([PLAN.md](PLAN.md)).
- MAVLink carries no trace context, and a WebSocket message has no headers ([PLAN.md](PLAN.md)).
- The dev cell charts are hand-written so that `helm dependency build` needs no network ([PLAN.md](PLAN.md)).

## ⚖️ Choices at a glance

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | How the trace reaches the browser | `trace_parent` field in the SquadFrame | A separate channel | A shared model changes and three generated files are regenerated |
| [D2](#d2) | Where the Python setup lives | Kernel library `swarm_web` | A new library or the layer packages | `swarm_web` grows |
| [D3](#d3) | `operator_id` and `mission_id` | Baggage copied onto spans | Resource attributes | Edge baggage is trusted for labelling |
| [D4](#d4) | Where secrets are removed | SDK exporters and the collector | One of the two | The same list is kept in several places |
| [D5](#d5) | Sampling | Tail sampling in the collector, 250 ms slow threshold | Head sampling in each SDK | Collector holds spans in memory |
| [D6](#d6) | Dev cell charts | One hand-written chart per block | Upstream charts | More YAML to maintain |
| [D7](#d7) | Proof of criterion 1 | Tests along the path | Check in the dev cell | Not checked end to end in the cell yet |
| [D8](#d8) | Fixes to files owned by T0.19 and tests | Decoder and `connz_users` join this ticket | Wait for owners | Wider diff |

## <a id="d1"></a>D1: How the trace reaches the browser

**Chosen:** an optional `trace_parent` field in `SquadFrame` · **Where:** [`squad_frame.py:55`](../../../backend/swarm-models/src/swarm_models/telemetry/squad_frame.py#L55) and [`squad-frame-decoder.ts:80`](../../../frontend/packages/live/src/protocol/squad-frame-decoder.ts#L80) · **Source:** PLAN.md

| Option | For | Against |
| --- | --- | --- |
| ✅ Field in the frame | A WebSocket message has no headers; the field is optional, so older frames still decode | Schema, Rust and TypeScript are regenerated; the decoder must keep the field (round 1's blocking finding) |
| Another channel | No change to the model | Nothing in the plan or the specifications names one |

**Trade-off:** a shared model grows by one field, in exchange for a trace that needs no new transport.

**Revisit when:** the live socket gains message headers.

## <a id="d2"></a>D2: Where the Python setup lives

**Chosen:** `swarm_web` · **Where:** [`signals_configurator.py`](../../../backend/libs/swarm-web/src/swarm_web/signals/signals_configurator.py) · **Source:** PLAN.md

| Option | For | Against |
| --- | --- | --- |
| ✅ `swarm_web` | App configs may already import `swarm_web.models`, and every app imports `swarm_web`, so the import table and its convention test stay unchanged | The library holds more than the web |
| A new kernel library or a layer package | A separate home | The plan names no such option; it would change the import table |

**Trade-off:** `swarm_web` takes on signals to avoid touching the import rules.

**Revisit when:** a non-web process needs signals without FastAPI.

## <a id="d3"></a>D3: `operator_id` and `mission_id` as span attributes

**Chosen:** baggage copied onto spans by [`MissionSpanProcessor`](../../../backend/libs/swarm-web/src/swarm_web/signals/mission_span_processor.py#L43); only `service.name` and `cell` on the resource · **Source:** PLAN.md, review

| Option | For | Against |
| --- | --- | --- |
| ✅ Baggage to span attributes | One process serves several Operators and Missions | Baggage from incoming requests is trusted; it only labels and grants no access |
| Resource attributes | Matches the wording of 08-observability | A resource is fixed per process |

**Trade-off:** a label that a caller could set, in exchange for correct per-Operator data. NATS subjects stay `op.<operator_id>...`.

**Revisit when:** the review follow-up "stop trusting edge baggage" is done, and the spec is reworded.

## <a id="d4"></a>D4: Where secrets are removed

**Chosen:** a catalogue of sensitive keys applied in the SDKs ([`RedactingSpanExporter`](../../../backend/libs/swarm-web/src/swarm_web/signals/redacting_span_exporter.py#L112), [`MetricLabelGuard`](../../../backend/libs/swarm-web/src/swarm_web/signals/metric_label_guard.py#L170), the Rust and TypeScript equivalents) and again in the collector ([`configmap.yaml:28-40`](../../../infra/charts/otel-collector/templates/configmap.yaml#L28-L40)) · **Source:** PLAN.md

| Option | For | Against |
| --- | --- | --- |
| ✅ Both levels | Acceptance criterion 2 holds even if one level misses a key; the catalogue is data, not code | The key list exists in several places and the TypeScript list differs from the Python one (a follow-up) |
| SDK only | One place per language | A missed key leaves the process |
| Collector only | One list | Data leaves the process before it is cleaned |

**Trade-off:** duplication for defence in depth.

**Revisit when:** a shared generated list replaces the copies.

## <a id="d5"></a>D5: Sampling

**Chosen:** tail sampling in the collector: 100 % of errors and slow requests, 5 % of the rest, "slow" at 250 ms ([`configmap.yaml:48-59`](../../../infra/charts/otel-collector/templates/configmap.yaml#L48-L59)) · **Source:** PLAN.md

| Option | For | Against |
| --- | --- | --- |
| ✅ Tail sampling | Errors and slow traces can be kept whole | The collector keeps spans in memory until a trace is decided |
| Head sampling in each SDK | No collector memory | A trace cannot be kept because it failed |

The 250 ms threshold is the REST write budget of 07-scalability, taken because the spec gives no number for "slow".

**Revisit when:** the specification fixes a threshold, or the collector's memory becomes a problem.

## <a id="d6"></a>D6: Dev cell charts

**Chosen:** one hand-written chart per block (collector, Prometheus, Loki, Tempo, Grafana), as the existing charts · **Where:** [`infra/charts/otel-collector`](../../../infra/charts/otel-collector/values.yaml) · **Source:** PLAN.md

| Option | For | Against |
| --- | --- | --- |
| ✅ Hand-written | `helm dependency build` needs no network; same style as existing charts; NetworkPolicy and Secret-based Grafana password are explicit | More YAML |
| Upstream charts | Less to write | Needs the network at build; no reason is recorded beyond the plan's no-network note |

Retention follows the spec (Tempo 14 days, Prometheus 15, Loki 30). **Revisit when:** upstream charts are accepted in the cell.

## <a id="d7"></a>D7: Proof of acceptance criterion 1

**Chosen:** automated tests along the path (tick span, `trace_parent`, NATS producer and consumer spans, browser span) · **Source:** PLAN.md, review

| Option | For | Against |
| --- | --- | --- |
| ✅ Tests along the path | The gateway and the flight engine are not deployed in the dev cell | The two browser unit tests passed alone while the decoder dropped the field; a worker-level test is a follow-up |
| Check in the dev cell | A real end-to-end proof | Not possible yet |

**Revisit when:** those services are deployed in the dev cell.

## <a id="d8"></a>D8: Fixes outside the planned files

**Chosen:** the decoder and its test ([`squad-frame-decoder.ts`](../../../frontend/packages/live/src/protocol/squad-frame-decoder.ts)) and [`connz_users`](../../../tests/infra/nats/helpers.py#L163) join this ticket as a recorded plan change · **Source:** review, round 1 and the checks

| Option | For | Against |
| --- | --- | --- |
| ✅ Fix here | Both blocked this ticket (criterion 1, and its checks); no task owned them | The diff touches T0.19's decoder and a shared test helper |
| Leave to a later ticket | Narrow diff | The trace would break at the browser, and the suite stayed flaky |

**Revisit when:** TKT-19 is applied earlier, so the owner fixes it.

## 📝 Assumptions behind the choices

- The trace starts at the flight engine tick, because MAVLink carries no trace context: supports [D1](#d1).
- No feature, use case or business rule, no budget and no screen are touched: supports [D2](#d2), [D5](#d5).
- The gateway and flight engine are not in the dev cell yet: supports [D7](#d7).
- Collector endpoint in Ground control and CORS are left to a front-end ticket: supports [D6](#d6).
