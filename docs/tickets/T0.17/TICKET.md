# T0.17: Observability base

**Status:** 🟡 Planned

## Roadmap

- **Ticket:** [T0.17](../../specs/roadmap/01-p0-foundations.md#s04) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S04](../../specs/roadmap/01-p0-foundations.md#s04), 15 to 26 February 2027: first use case and M0
- **Epic:** [E0.4](../../specs/roadmap/01-p0-foundations.md#epics): Dev cell and data platform. A cell to run and measure everything on.

## What it delivers

- OpenTelemetry SDKs in Python, Rust and TypeScript, in `packages/python/`, `packages/rust` and `packages/ts`, as [🩺 Observability: signals](../../specs/technical/08-observability.md#signals).
- The OpenTelemetry collector, and Prometheus, Loki, Tempo and Grafana in the dev cell, in `deploy/charts`, as [🩺 Observability: signals](../../specs/technical/08-observability.md#signals).
- Trace context carried in NATS headers, as [🩺 Observability: signals](../../specs/technical/08-observability.md#signals).
- `operator_id`, `mission_id` and `cell` as resource attributes, and `drone_id` never a metric label, as [🩺 Observability: signals](../../specs/technical/08-observability.md#signals).

## Features, use cases and business rules

- The roadmap names no feature, use case or business rule for this ticket.

## Technical pages it builds on

- [🩺 Observability: signals](../../specs/technical/08-observability.md#signals): "every request, event and command carries a trace context; `operator_id`, `mission_id` and `cell` are resource attributes; `drone_id` stays in traces and logs, never as a metric label (cardinality)", and "No secrets, no personal data in signals".

## Screens touched

- The ticket touches no screen.

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

The "done when" of the roadmap row. The roadmap names no Given, when, then criterion of a feature for this ticket.

1. **Given** the dev cell with the observability base running, **when** a Telemetry frame goes from the Simulator to the browser, **then** one trace follows it.
2. **Given** the signals the services produce, **when** they are inspected, **then** no secret or personal data appears in any of them.

## Out of scope

- The Simulator, see [T0.13](../../specs/roadmap/01-p0-foundations.md#s03).
- The flight engine skeleton and the live WebSocket, see [T0.18](../../specs/roadmap/01-p0-foundations.md#s04).
- The first Ground control map screen and the Telemetry latency panel in Grafana, see [T0.19](../../specs/roadmap/01-p0-foundations.md#s04).

## Assumptions

- The roadmap row names no feature, use case or business rule, so none is linked; the technical page section [🩺 Observability: signals](../../specs/technical/08-observability.md#signals) settles what the ticket builds.
- The row names no row of the budgets table, so the ticket touches no budget.
- The row names no use case, so the ticket touches no screen.
- The "done when" trace from the Simulator to the browser depends on tickets T0.13, T0.18 and T0.19, which the row does not list as prerequisites; the criterion is written as the roadmap states it.
