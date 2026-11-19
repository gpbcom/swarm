# T0.04: CI checks for every language

**Status:** 🟡 Planned

## Roadmap

- **Ticket:** [T0.04](../../specs/roadmap/01-p0-foundations.md#s01) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S01](../../specs/roadmap/01-p0-foundations.md#s01), 4 to 15 January 2027: repository and harness
- **Epic:** [E0.2](../../specs/roadmap/01-p0-foundations.md#epics): CI/CD. Every merge checked, built, scanned, signed and tested.

## What it delivers

- Step 1 of [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci): change detection per service, front end and package. A change in `packages/` or a lock file runs everything that depends on it.
- Step 2 of [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci), for Python: ruff, `ruff format --check`, mypy and pytest.
- Step 2 for Rust: cargo fmt, clippy and tests.
- Step 2 for TypeScript: eslint, `tsc` and Vitest.
- Step 2 for the specifications: `specs.py check`.
- Where: `.github/workflows/`.

## Features, use cases and business rules

- The roadmap names no feature, use case or business rule for this ticket.

## Technical pages it builds on

- [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci): GitHub Actions in six steps, each passing before the next; this ticket builds step 1 (detect changes) and step 2 (check).
- [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo): the layout of `services/`, `frontends/` and `packages/` that change detection walks.

## Screens touched

- The ticket touches no screen.

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

The "done when" of the roadmap row, in two parts. The roadmap names no Given, when, then criterion of a feature for this ticket.

1. **Given** a pull request touching one service, **when** the CI runs, **then** only that service's checks run.
2. **Given** a pull request changing `packages/`, **when** the CI runs, **then** the checks of all the services and front ends that depend on it run.

## Out of scope

- Steps 3 to 6 of the CI/CD (images, scans, signatures, Playwright, publication), see [T0.10](../../specs/roadmap/01-p0-foundations.md#s02).
- The Rust and TypeScript packages themselves, see [T0.07](../../specs/roadmap/01-p0-foundations.md#s02) and [T0.14](../../specs/roadmap/01-p0-foundations.md#s03).

## Assumptions

- A lock file change (`uv.lock`) runs all checks, as [AGENT.md](../../../AGENT.md) says; the other lock files are treated the same way, the most conservative option.
- Benchmarks and the generated-types check of step 2 are not in the roadmap row, so they are left to [T0.07](../../specs/roadmap/01-p0-foundations.md#s02) and [T0.06](../../specs/roadmap/01-p0-foundations.md#s02).
- Rust and TypeScript checks run only once those workspaces hold code; a target that does not exist yet is not applicable, never failed.
