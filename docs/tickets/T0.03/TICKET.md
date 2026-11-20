# T0.03: Convention tests and linters

**Status:** ✅ Done

## Roadmap

- **Ticket:** [T0.03](../../specs/roadmap/01-p0-foundations.md#s01) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S01](../../specs/roadmap/01-p0-foundations.md#s01), 4 to 15 January 2027: repository and harness
- **Epic:** [E0.1](../../specs/roadmap/01-p0-foundations.md#epics): Mono-repo, Terraform base and ticket harness. It delivers the working method of the whole roadmap, the [AGENT.md](../../../AGENT.md) rules enforced and the dev cell's infrastructure as code.

## What it delivers

- `tests/conventions/` enforcing the rules a test enforces in [AGENT.md](../../../AGENT.md): one class per file, five files per folder, no `Any`, no nested function, allowed layer imports, lifecycle base classes, Pydantic models only in `models/`. They run against every service found under `services/`, so a new service needs no change to the tests, as [🧅 Architecture: layers inside each service](../../specs/technical/01-architecture.md#layers).
- rustfmt and clippy settings, in `packages/rust`.
- eslint and `tsc` strict settings, in `packages/ts`.
- Where: `tests/conventions/`, `packages/rust`, `packages/ts`.

## Features, use cases and business rules

- The roadmap names no feature, use case or business rule for this ticket.

## Technical pages it builds on

- [🧅 Architecture: layers inside each service](../../specs/technical/01-architecture.md#layers): every Python service has the same five modules under `services/<service>/src/<service>/`, each only calling the ones below it, and a test in `tests/conventions/` fails on any other import.
- [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo): the layout of `services/`, `packages/` (Python, Rust, TypeScript) and `tests/`, which the convention tests walk and the Rust and TypeScript settings sit in.
- [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci): the check step runs cargo fmt, clippy, eslint and tsc, which the settings of this ticket configure.

## Screens touched

- The ticket touches no screen.

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

The "done when" of the roadmap row, in two parts. The roadmap names no Given, when, then criterion of a feature for this ticket.

1. **Given** a deliberately broken sample service, **when** the convention tests run against it, **then** each rule of the ticket fails once.
2. **Given** an empty service added under `services/`, **when** the convention tests run, **then** they need no change and pass for it.

## Out of scope

- Running these checks on every push and pull request, see [T0.04](../../specs/roadmap/01-p0-foundations.md#s01).
- The lifecycle base classes and logging packages themselves, see [T0.05](../../specs/roadmap/01-p0-foundations.md#s01).

## Assumptions

- The rules to enforce are those listed in the roadmap row, as written in the "Rules a test enforces" section of AGENT.md; the other rules of that section are not added here.
- The exact rustfmt, clippy, eslint and `tsc` options are not settled by the specifications; the most conservative option (strict) is taken, as the roadmap says "strict" only for `tsc`.
- The tests under `tests/conventions/mono_repo/` already exist from T0.01 and are left as they are.
