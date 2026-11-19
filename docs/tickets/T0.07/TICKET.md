# T0.07: Rust core and benchmark gate

**Status:** 🟡 Planned

## Roadmap

- **Ticket:** [T0.07](../../specs/roadmap/01-p0-foundations.md#s02) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S02](../../specs/roadmap/01-p0-foundations.md#s02), 18 to 29 January 2027: shared code, dev cell and pipeline
- **Epic:** [E0.3](../../specs/roadmap/01-p0-foundations.md#epics): Shared packages. One model per object, one lifecycle, one logging, one Rust core.

## What it delivers

- The `swarm-core` Cargo workspace in `packages/rust/` with its `safety`, `planner` and `mavlink` crates, each an empty shell with one function, as [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo).
- PyO3 bindings built as wheels by maturin, so that a Python service imports a Rust function from a wheel, as [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo) and [🔩 Engine and services: flight engine](../../specs/technical/04-engine.md#flight-engine).
- criterion benchmarks run on every pull request, a regression of more than 5 % failing the build, as [🏋️ Scalability and performance: load tests](../../specs/technical/07-scalability.md#load-tests).

## Features, use cases and business rules

- The roadmap names no feature, use case or business rule for this ticket.

## Technical pages it builds on

- [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo): `packages/rust/` holds the "swarm-core crates (safety, planner, mavlink) with PyO3", and the Rust toolchain is a "Cargo workspace in `packages/rust`, wheels built with maturin".
- [🏋️ Scalability and performance: load tests](../../specs/technical/07-scalability.md#load-tests): "Per pull request: Rust benchmarks (criterion) of the safety tick, the planner and the encoders; a regression of more than 5 % fails the build."
- [🔩 Engine and services: flight engine](../../specs/technical/04-engine.md#flight-engine): "CPU-heavy steps run in the Rust core (`packages/rust/swarm-core`, PyO3), which releases the GIL."

## Screens touched

- The ticket touches no screen.

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

The "done when" of the roadmap row. The roadmap names no Given, when, then criterion of a feature, and no business rule or use case, for this ticket.

1. **Given** a Python service, **when** it imports a Rust function from a wheel built by maturin, **then** the function is called and returns.
2. **Given** a function of the `swarm-core` crates that has been slowed down by more than 5 %, **when** the criterion benchmark gate runs on a pull request, **then** the build fails.

## Out of scope

- The real safety, planner and MAVLink logic: the crates are empty shells with one function each. The safety code comes in later tickets, see [T0.18](../../specs/roadmap/01-p0-foundations.md#s04).
- The `typify` structs generated from the models into `packages/rust`, see [T0.06](../../specs/roadmap/01-p0-foundations.md#s02).
- Synthetic Rust Drones speaking MAVLink, see [T0.13](../../specs/roadmap/01-p0-foundations.md#s03).
- The nightly load tests and chaos tests of the same page, taken by later tickets.

## Assumptions

- The roadmap row names no feature, use case or business rule, so the acceptance criteria cite none.
- The row names the load tests section for the 5 % gate but no row of the budgets table, so the ticket touches no budget. The safety tick budget is not asserted here because the crates are empty shells.
- The load tests section also names benchmarks of the encoders, but the row lists only `safety`, `planner` and `mavlink` crates, so no encoder benchmark is built.
- Where the pull request job of the benchmark gate lives is not specified beyond the T0.04 workflows. The plan reuses them.
- How a regression is measured against a baseline (stored results or the base branch) is not specified. The plan takes the most conservative option and records it.
