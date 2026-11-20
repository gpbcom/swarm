# T0.06: Shared models and generated types

**Status:** ✅ Done

## Roadmap

- **Ticket:** [T0.06](../../specs/roadmap/01-p0-foundations.md#s02) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S02](../../specs/roadmap/01-p0-foundations.md#s02), 18 to 29 January 2027: shared code, dev cell and pipeline
- **Epic:** [E0.3](../../specs/roadmap/01-p0-foundations.md#epics): Shared packages. One model per object, one lifecycle, one logging, one Rust core.

## What it delivers

- `packages/python/swarm-models` with the conventions of the data models, as [🧱 Data models: conventions](../../specs/technical/02-data-models.md#conventions).
- The `Event` envelope, as [🧱 Data models: events](../../specs/technical/02-data-models.md#events).
- First versions of `Operator`, `Person`, `Role` and `CellAssignment`, as [🧱 Data models: main models](../../specs/technical/02-data-models.md#models).
- First versions of `TelemetryFrame`, `SquadFrame` and `Command`, as [🧱 Data models: telemetry frames and commands](../../specs/technical/02-data-models.md#telemetry).
- The JSON Schema export, `typify` structs for Rust in `packages/rust`, and TypeScript types into `packages/ts/live`, as [🧱 Data models: versioning](../../specs/technical/02-data-models.md#versioning).

## Features, use cases and business rules

- The roadmap names no feature, use case or business rule for this ticket.

## Technical pages it builds on

- [🧱 Data models: conventions](../../specs/technical/02-data-models.md#conventions): "Pydantic v2, under the rules of AGENT.md", UUIDv7 identifiers, UTC in microseconds, units in names, GeoJSON, states as `StrEnum`, and "`packages/python/swarm-models`, imported by every service; services never redefine a model."
- [🧱 Data models: main models](../../specs/technical/02-data-models.md#models): `Operator`, `Person`, `Role` and `CellAssignment` are the global models; `TelemetryFrame`, `SquadFrame` and `Command` belong to flight-engine.
- [🧱 Data models: telemetry frames and commands](../../specs/technical/02-data-models.md#telemetry): the fields of `TelemetryFrame`, the `SquadFrame` per tick, the `Command` lanes, and "the Rust core uses structs generated from the JSON Schema of these models (`typify`), so Pydantic stays the single source."
- [🧱 Data models: events](../../specs/technical/02-data-models.md#events): the `Event` fields (`id`, `type`, `version`, `operator_id`, `mission_id`, `occurred_at`, `actor`, `payload`).
- [🧱 Data models: versioning](../../specs/technical/02-data-models.md#versioning): JSON Schema exported from the Pydantic models, TypeScript types generated (`json-schema-to-typescript`) into `packages/ts/live`, and "CI fails when a generated file is out of date".
- [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo): `packages/python/`, `packages/rust` and `packages/ts` are where the shared code and generated types sit.

## Screens touched

- The ticket touches no screen.

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

The "done when" of the roadmap row. The roadmap names no Given, when, then criterion of a feature, and no business rule or use case, for this ticket.

1. **Given** each model of the ticket, **when** its tests run, **then** it has the six model tests of [AGENT.md](../../../AGENT.md) (defaults, full valid construction, `None` becomes the default, rejected bad values, rejected unknown keys, round trip).
2. **Given** a generated file (JSON Schema, Rust structs or TypeScript types) that is stale against the models, **when** CI runs, **then** it fails.

## Out of scope

- The Rust core crates and the benchmark gate, see [T0.07](../../specs/roadmap/01-p0-foundations.md#s02).
- The shared async NATS client, see [T0.09](../../specs/roadmap/01-p0-foundations.md#s02).
- The REST client generated into `packages/ts/api-client`, see [T0.12](../../specs/roadmap/01-p0-foundations.md#s03).
- The other models of the main models table (Mission, Drone and so on), taken by later tickets.

## Assumptions

- The roadmap row names no feature, use case or business rule, so the acceptance criteria cite none.
- The roadmap lists `Event` but not `Proposal`, so `Proposal` is not built here.
- Fields of `Operator`, `Person`, `Role`, `CellAssignment` and `SquadFrame` are not listed in the specifications beyond their names. The plan takes the most conservative set, and records it.
- Where the CI check of stale generated files runs is not specified beyond the T0.04 workflows. The plan reuses them.
