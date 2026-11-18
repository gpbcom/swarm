# 🩺 Observability

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ Scalability and performance](07-scalability.md) · 📄 **Page 92 / 108** · [Deployment ▶️](09-deployment.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> How the people who run Swarm see its health: OpenTelemetry signals from every service, self-hosted backends, SLOs and alerting. System telemetry is kept apart from Drone Telemetry, which is business data. Decision T26.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [📨 Signals](#signals)
2. [🌐 The edge](#edge)
3. [🎯 Service level objectives](#slos)
4. [📊 Dashboards and alerting](#dashboards)
5. [🔗 Features implemented](#features)
<!-- /spec:summary -->

## <a id="signals"></a>📨 Signals

| Signal | Produced by | Stored in | Kept |
| --- | --- | --- | --- |
| Traces | OpenTelemetry SDKs (Python, Rust, TypeScript) | Tempo | 14 days, sampled (100 % of errors and slow requests, 5 % of the rest) |
| Metrics | OpenTelemetry and Prometheus exporters | Prometheus per cell, Mimir for long-term and cross-cell views | 15 days per cell, 13 months in Mimir |
| Logs | AGENT.md logging rules: coloured on the console, JSON in production | Loki | 30 days |
| Profiles | Continuous profiling of the hot services (flight-engine, gateway, planner) | Pyroscope | 7 days |

- **Correlation:** every request, event and command carries a trace context; `operator_id`, `mission_id` and `cell` are resource attributes; `drone_id` stays in traces and logs, never as a metric label (cardinality).
- **No secrets, no personal data** in signals (AGENT.md); faces, names and coordinates of people never appear.
- **Drone Telemetry is not system telemetry:** it goes to TimescaleDB as business data; only counts and latencies of its pipeline are metrics.

## <a id="edge"></a>🌐 The edge

- The flight engine exports its signals to a local OpenTelemetry collector, which buffers on disk while the cell is unreachable and forwards when the link returns.
- Edge health (tick duration, Link quality, buffered messages, disk) is shown to the Pilot in Ground control as well as to operations.

## <a id="slos"></a>🎯 Service level objectives

| Service | SLO | Measured on |
| --- | --- | --- |
| REST API (per cell) | 99.9 % of requests succeed, p95 within budget | gateway |
| Live data stream | 99.95 % of minutes with frames delivered within the budget | gateway and flight-engine |
| Safety tick | 99.99 % of ticks within budget | flight-engine (edge) |
| Processing | 95 % of Deliverables within their budget | processing |
| Notifications | 99 % delivered within 1 minute | notifier |

Error budgets are reviewed every week; a spent budget freezes feature releases for that service.

## <a id="dashboards"></a>📊 Dashboards and alerting

- **Grafana dashboards** per cell, per service, per Operator and per Mission; the [⏱️ budgets](07-scalability.md#budgets) are drawn as thresholds on every latency panel.
- **Alerting** through Alertmanager to the on-call rota: burn-rate alerts on SLOs, saturation (NATS, TimescaleDB ingest, GPU queue depth), certificate and key expiry, failed backups and restore drills.
- **Runbooks** are linked from every alert and kept in the repository.
- **On premises:** the same stack ships in the bundle, so an air-gapped site has the same dashboards.

## <a id="features"></a>🔗 Features implemented

Supports every feature; directly [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md) (Operators on cloud and on premises) and [📘 FS-021](../functional/features/FS-021-ground-control-monitoring.md) (edge health shown to the Pilot).

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ Scalability and performance](07-scalability.md) · 📄 **Page 92 / 108** · [Deployment ▶️](09-deployment.md)
<!-- /spec:nav-bottom -->
