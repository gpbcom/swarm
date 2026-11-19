# T0.02: Claude Code ticket harness

**Status:** ✅ Done

## Roadmap

- **Ticket:** [T0.02](../../specs/roadmap/01-p0-foundations.md#s01) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S01](../../specs/roadmap/01-p0-foundations.md#s01), 4 to 15 January 2027: repository and harness
- **Epic:** [E0.1](../../specs/roadmap/01-p0-foundations.md#epics): Mono-repo, Terraform base and ticket harness. It delivers the working method of the whole roadmap, the [AGENT.md](../../../AGENT.md) rules enforced and the dev cell's infrastructure as code. Its parallel tasks for the agents include the agent definitions, the ticket skill and the hooks.

## What it delivers

The working method of the roadmap, versioned in `.claude/` like the specification harness:

- A ticket template: phase, sprint, 📘 FS, 🎬 UC and 📏 BR IDs, acceptance criteria in **Given**, **when**, **then**, screens touched, budgets touched.
- A skill that reads a ticket, checks its IDs against `docs/specs/`, writes the task split and starts one agent per task in its own git worktree.
- Agent definitions per kind of task: Python service, Rust core, front end, tests, mock-ups and screens, specifications and documentation, reviewer.
- Hooks that format only the edited files and run the checks of the touched layer before a task is handed back.
- A reviewer agent that reads the merged branch against [AGENT.md](../../../AGENT.md), the SPEC rules and the ticket's acceptance criteria, and writes a short review note for the person.
- Where: `.claude/agents/`, `.claude/skills/`, `.claude/rules/`, `.claude/settings.json`.

## Features, use cases and business rules

The roadmap names no feature, use case or business rule for T0.02. It closes no acceptance criterion of a feature.

## Technical pages it builds on

The roadmap row of T0.02 names no technical page. The sections below are linked because the harness builds on them, and the risk and phase page sections describe the work method:

- [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo): one repository holds the backend, the frontends, the shared code and the deployment, under `services/`, `frontends/`, `packages/` and `deploy/`. Each service and each front end builds exactly one image. The harness splits work along these folders and starts worktrees on this repository.
- [🧅 Architecture: layers inside each service](../../specs/technical/01-architecture.md#layers): every Python service has the same five modules under `services/<service>/src/<service>/`, each only calling the ones below it, and a test in `tests/conventions/` fails on any other import. The harness splits work per layer and runs the checks of the touched layer.
- [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci): the checks run per service, front end and package (ruff, mypy, pytest for Python; cargo fmt, clippy, tests for Rust; eslint, tsc, Vitest for TypeScript; `specs.py check`), and a change in `packages/` or a lock file runs everything that depends on it. The hooks run the same checks as CI.

- [🎲 R-01](../../specs/roadmap/12-risks.md#r-01) Review bottleneck: the harness is the first ticket that ships (S01), and the reviewer agent writes a short note per ticket.
- [🛣️ P0: Work split](../../specs/roadmap/01-p0-foundations.md#work-split): the person writes the ticket template, the agent definitions and the hooks with Claude Code in S01, and decides the agent definitions and their limits (what an agent may change without asking).
- [🛣️ P0: Goal](../../specs/roadmap/01-p0-foundations.md#goal): one person, many agents, each task in its own git worktree, one reviewed branch handed back.

## Acceptance criteria

The "done when" of the roadmap row, in three parts. The roadmap names no Given, when, then criterion of a feature for this ticket.

1. **Given** a sample ticket, **when** it runs end to end through the harness, **then** it is split into at least three parallel tasks and merged into one branch.
2. **Given** the merged branch of the sample ticket, **when** the run ends, **then** a review note is written and the checks are green.
3. **Given** the review note and the merged branch, **when** the person reviews them, **then** the review takes under an hour.

## Out of scope

- Using the harness on the tickets of P0 other than the sample ticket: from S02 every ticket goes through the harness ([T0.06](../../specs/roadmap/01-p0-foundations.md#s02) onward).
- The convention tests and linters: [T0.03](../../specs/roadmap/01-p0-foundations.md#s01).
- The CI checks for every language: [T0.04](../../specs/roadmap/01-p0-foundations.md#s01).
- The lifecycle and logging packages: [T0.05](../../specs/roadmap/01-p0-foundations.md#s01).

## Assumptions

- The roadmap names no feature, use case or business rule for T0.02, so none is listed.
- The roadmap row names no technical page for T0.02. The technical sections mono-repo and layers (architecture) and CI/CD (deployment) are linked because the harness splits work per service, layer and package, starts worktrees on the mono-repo, and runs the same checks as CI. The risk R-01 and the phase page sections Work split and Goal are linked because they describe the harness.
- The roadmap does not say which ticket is the "sample ticket"; the choice is left to the plan.
- The roadmap does not say how the "under an hour" review is measured; the person judges it.
