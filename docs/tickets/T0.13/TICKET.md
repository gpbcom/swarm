# T0.13: Simulator base

**Status:** ✅ Done

## Roadmap

- **Ticket:** [T0.13](../../specs/roadmap/01-p0-foundations.md#s03) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S03](../../specs/roadmap/01-p0-foundations.md#s03), 1 to 12 February 2027: identity, services and Simulator. A person signs in, a service answers for one Operator only, simulated Drones fly.
- **Epic:** [E0.6](../../specs/roadmap/01-p0-foundations.md#epics): Simulator and live path. [📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md) and the M0 proof.

## What it delivers

- `services/simulator`, an AGENT.md service, as [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo).
- PX4 SITL in containers (headless Gazebo), as [🕹️ Engine and services: simulator](../../specs/technical/04-engine.md#simulator) (fidelity).
- Synthetic Drones written in Rust, in `packages/rust`, that speak MAVLink and follow a route, as [🕹️ Engine and services: simulator](../../specs/technical/04-engine.md#simulator) (volume).
- An adapter registry that cannot address a real Drone, as [🕹️ Engine and services: simulator](../../specs/technical/04-engine.md#simulator) (isolation).
- Separate NATS credentials for simulated Squads, as [🕹️ Engine and services: simulator](../../specs/technical/04-engine.md#simulator) (isolation).
- Every Flight log the Simulator produces marked simulated, as [📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md).

## Features, use cases and business rules

- [📏 BR-014: Simulation isolation](../../specs/functional/business-rules/BR-014-simulation-isolation.md)
- [📘 FS-010: Simulator and training](../../specs/functional/features/FS-010-simulator-and-training.md): the Simulator base only. Training sessions and AC-1 come in P1.

## Technical pages it builds on

- [🕹️ Engine and services: simulator](../../specs/technical/04-engine.md#simulator): "PX4 SITL in containers (headless Gazebo)", "synthetic Drones written in Rust that speak MAVLink and follow routes", and "simulated Squads use separate NATS credentials and an adapter registry that cannot address a real Drone, and every Flight log is marked simulated".
- [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo): the layout of `services/` and `packages/rust` the Simulator sits in.

## Screens touched

- The ticket touches no screen.

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

The "done when" of the roadmap row. The roadmap names no Given, when, then criterion of a feature for this ticket.

1. **Given** the dev cell, **when** 10 synthetic Drones and one PX4 SITL Drone fly a square route, **then** all of them complete it. ([📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md), [🎬 UC-002](../../specs/functional/use-cases/UC-002-simulate-a-mission.md))
2. **Given** simulated credentials, **when** a command is sent to a Drone outside the adapter registry, **then** it is refused and logged. ([📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md), [🎬 UC-002](../../specs/functional/use-cases/UC-002-simulate-a-mission.md))
3. **Given** a flight of the Simulator, **when** its Flight log is produced, **then** it is marked simulated. ([📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md), [🎬 UC-002](../../specs/functional/use-cases/UC-002-simulate-a-mission.md))

## Out of scope

- Training sessions and [📘 FS-010](../../specs/functional/features/FS-010-simulator-and-training.md) AC-1, see [🎬 UC-013](../../specs/functional/use-cases/UC-013-train-on-the-simulator.md) in P1.
- The flight engine skeleton and the live WebSocket, see [T0.18](../../specs/roadmap/01-p0-foundations.md#s04).
- The simulated Squad on the Ground control map, see [T0.19](../../specs/roadmap/01-p0-foundations.md#s04).
- The NATS accounts and the simulated credentials' issuance, see [T0.09](../../specs/roadmap/01-p0-foundations.md#s02).

## Assumptions

- The roadmap row names only [📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md); [📘 FS-010](../../specs/functional/features/FS-010-simulator-and-training.md) is linked as the feature that BR-014 serves and the phase page scopes to the Simulator base.
- [🎬 UC-002](../../specs/functional/use-cases/UC-002-simulate-a-mission.md) is cited in the criteria because it also applies BR-014; the ticket builds no screen of it.
- The row names no row of the budgets table, so the ticket touches no budget.
- "A square route" and "refused and logged" are taken as written; no size or timing is asserted.
- Separate simulated NATS credentials are issued by the T0.09 package; this ticket uses them.
