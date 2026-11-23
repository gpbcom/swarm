# T0.18: Flight engine skeleton and live WebSocket

**Status:** 🟡 Planned

## Roadmap

- **Ticket:** [T0.18](../../specs/roadmap/01-p0-foundations.md#s04) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S04](../../specs/roadmap/01-p0-foundations.md#s04), 15 to 26 February 2027: first use case and M0
- **Epic:** [E0.6](../../specs/roadmap/01-p0-foundations.md#epics): Simulator and live path. [📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md); the M0 proof.

## What it delivers

- `services/flight-engine` as an AGENT.md service: one asyncio process with uvloop, one actor per Mission, as [🔩 Engine and services: flight engine](../../specs/technical/04-engine.md#flight-engine).
- MAVLink frames read through `swarm-core` (`packages/rust`), as [🔩 Engine and services: flight engine](../../specs/technical/04-engine.md#flight-engine).
- One `SquadFrame` per tick to the local WebSocket and to the leaf node, as [🔩 Engine and services: flight engine](../../specs/technical/04-engine.md#flight-engine).
- The gateway `/v1/live` WebSocket with MessagePack, one NATS subscription per Mission and one-slot mailboxes per client, as [📨 API layer: live data over WebSocket](../../specs/technical/05-api.md#live).

## Features, use cases and business rules

- [📏 BR-014: Simulation isolation](../../specs/functional/business-rules/BR-014-simulation-isolation.md)

## Technical pages it builds on

- [🔩 Engine and services: flight engine](../../specs/technical/04-engine.md#flight-engine): "One asyncio process per edge (uvloop), one actor per Mission holding its Squad state", with the output "one `SquadFrame` per tick to Ground control (local WebSocket) and to the leaf node".
- [📨 API layer: live data over WebSocket](../../specs/technical/05-api.md#live): "the gateway subscribes once per Mission to NATS and fans out to every client watching it", and "a slow client skips intermediate frames instead of growing a queue".
- [🚀 Scalability and performance: budgets](../../specs/technical/07-scalability.md#budgets): the Telemetry path from Drone to screen, which the live path must serve.

## Screens touched

- The ticket touches no screen.

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

The "done when" of the roadmap row. The roadmap names no Given, when, then criterion of a feature for this ticket.

1. **Given** 10 simulated Drones flying in the cell, **when** a WebSocket client subscribes to their Mission on `/v1/live`, **then** the client receives their frames through the cell. ([📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md))
2. **Given** a slow WebSocket client, **when** frames arrive faster than it reads, **then** it skips frames instead of growing a queue. ([📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md))

## Out of scope

- The Simulator and its synthetic Drones, see [T0.13](../../specs/roadmap/01-p0-foundations.md#s03).
- The Ground control map screen, see [T0.19](../../specs/roadmap/01-p0-foundations.md#s04).
- Observability of the live path, see [T0.17](../../specs/roadmap/01-p0-foundations.md#s04).

## Assumptions

- The roadmap row names no feature or use case. [📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md) is linked because the roadmap names it for epic E0.6, which this ticket belongs to, and the criteria cite it as the most conservative link.
- The row names no row of the budgets table, so the ticket touches no budget, and no latency figure is asserted. The budgets page is linked as context only.
- The row names no screen and no use case, so the ticket touches no screen.
- The row says "10 simulated Drones" and quantifies nothing else, so no other number is asserted.
