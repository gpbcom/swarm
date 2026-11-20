# T0.05: Lifecycle and logging packages

**Status:** ✅ Done

## Roadmap

- **Ticket:** [T0.05](../../specs/roadmap/01-p0-foundations.md#s01) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S01](../../specs/roadmap/01-p0-foundations.md#s01), 4 to 15 January 2027: repository and harness
- **Epic:** [E0.3](../../specs/roadmap/01-p0-foundations.md#epics): Shared packages. One model per object, one lifecycle, one logging, one Rust core.

## What it delivers

- `Runnable` and `AsyncRunnable` with `initialize`, `run`, `close` and `execute`, as [🔩 Engine and services](../../specs/technical/04-engine.md#overview) (runnables with `initialize`, `run`, `close`).
- The abstract factories, as [🔩 Engine and services](../../specs/technical/04-engine.md#overview) (factories).
- The logging configuration of [AGENT.md](../../../AGENT.md): coloured console, coloured rotating file, and JSON in production, as [🩺 Observability: signals](../../specs/technical/08-observability.md#signals).
- The `YamlCatalog` base.
- Where: `packages/python/`, as [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo).

## Features, use cases and business rules

- The roadmap names no feature, use case or business rule for this ticket.

## Technical pages it builds on

- [🔩 Engine and services](../../specs/technical/04-engine.md#overview): "Every Python service follows AGENT.md: layers `api`, `service`, `storage`, `models`; runnables with `initialize`, `run`, `close`; factories; logging rules."
- [🩺 Observability: signals](../../specs/technical/08-observability.md#signals): logs follow the "AGENT.md logging rules: coloured on the console, JSON in production".
- [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo): `packages/python/` holds "shared Python: models, lifecycle, logging, NATS client".
- [🧅 Architecture: layers inside each service](../../specs/technical/01-architecture.md#layers): the layers the factories and base classes sit in, with a test in `tests/conventions/` failing on any other import.

## Screens touched

- The ticket touches no screen.

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

The "done when" of the roadmap row, in two parts. The roadmap names no Given, when, then criterion of a feature, and no business rule or use case, for this ticket.

1. **Given** the service skeletons of P0, **when** they are built, **then** every one uses the lifecycle and logging packages.
2. **Given** the packages, **when** their own tests run, **then** they pass.
3. **Given** the packages, **when** the convention tests of `tests/conventions/` run, **then** they accept them.

## Out of scope

- The service skeletons that use the packages, see [T0.12](../../specs/roadmap/01-p0-foundations.md#s03).
- The shared models and the `Event` envelope, see [T0.06](../../specs/roadmap/01-p0-foundations.md#s02).
- The shared async NATS client, see [T0.09](../../specs/roadmap/01-p0-foundations.md#s02).
- OpenTelemetry and the observability stack, see [T0.17](../../specs/roadmap/01-p0-foundations.md#s04).

## Assumptions

- The roadmap row names no feature, use case or business rule, so the acceptance criteria cite none.
- "Every service skeleton of P0 uses them" is checked only for the skeletons that exist when the ticket is done; later skeletons are built by their own tickets.
- The exact behaviour of `YamlCatalog` (`load(path)`, raising the model's `UNREADABLE` exception) and of the factories is taken from [AGENT.md](../../../AGENT.md), the most conservative source.
- The production switch to JSON logs is not specified beyond "JSON in production"; how production is detected is left to the plan.
