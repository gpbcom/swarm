# T0.01: Mono-repo layout and Terraform base

**Status:** ✅ Done

## Roadmap

- **Ticket:** [T0.01](../../specs/roadmap/01-p0-foundations.md#s01) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S01](../../specs/roadmap/01-p0-foundations.md#s01), 4 to 15 January 2027: repository and harness
- **Epic:** [E0.1](../../specs/roadmap/01-p0-foundations.md#epics): Mono-repo, Terraform base and ticket harness. It delivers the working method of the whole roadmap, the [AGENT.md](../../../AGENT.md) rules enforced and the dev cell's infrastructure as code.

## What it delivers

- The layout of [🏗️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo): `services/`, `frontends/`, `packages/python`, `packages/rust`, `packages/ts`, `deploy/`, `tests/`.
- The uv workspace (one `uv.lock`), the Cargo workspace with maturin, and the pnpm workspace with Turborepo.
- The current root `src/` moved to its service, as the Mono-repo section of [AGENT.md](../../../AGENT.md) plans.
- `deploy/terraform` (decision T43) with one module per provider, the self-hosted k3s module used first. It provisions the dev cell's machines, k3s cluster, network, object storage and DNS. Its state is kept outside the repository and checked by `terraform plan` in CI.
- Where: the repository root and `deploy/terraform`.

## Features, use cases and business rules

The roadmap names no feature, use case or business rule for T0.01. It closes no acceptance criterion of a feature.

## Technical pages it builds on

- [🏗️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo): the folder layout, the uv, Cargo and pnpm workspaces, one image per service and front end.
- [🏗️ Architecture: cells and the global layer](../../specs/technical/01-architecture.md#cells): the dev cell the infrastructure prepares.
- [🚢 Deployment: infrastructure as code](../../specs/technical/09-deployment.md#iac): Terraform (decision T43), one module per building block in `deploy/terraform/modules/`, one root per cell in `deploy/terraform/cells/<cell>/`, remote state with locking, `terraform plan` in CI, `apply` manual after review.
- [🚢 Deployment: where it runs](../../specs/technical/09-deployment.md#providers): self-hosted k3s with MinIO.
- [🤝 P-06](../../specs/roadmap/11-hardware-and-partners.md#p-06): the self-hosted machines Terraform provisions for the dev cell, due in S01.

## Acceptance criteria

The "done when" of the roadmap row, in three parts. The roadmap names no Given, when, then criterion of a feature for this ticket.

1. **Given** a clean clone of the repository, **when** each workspace (uv, Cargo, pnpm) is installed, **then** every workspace installs.
2. **Given** nothing provisioned, **when** `terraform apply` runs for the dev cell, **then** it creates the dev cell's empty k3s cluster from nothing.
3. **Given** the repository, **when** a person reads the README, **then** it says how to start.

## Out of scope

- The platform deployed on the cluster (Argo CD, databases, Valkey, MinIO, vault): [T0.08](../../specs/roadmap/01-p0-foundations.md#s02).
- The Claude Code ticket harness: [T0.02](../../specs/roadmap/01-p0-foundations.md#s01).
- The convention tests and linters: [T0.03](../../specs/roadmap/01-p0-foundations.md#s01).
- The CI checks for every language: [T0.04](../../specs/roadmap/01-p0-foundations.md#s01), beyond the `terraform plan` check named in this ticket.
- Production cells on OVHcloud and Scaleway: they come in P7 according to the phase page.

## Assumptions

- The roadmap names no feature, use case or business rule for T0.01, so none is listed.
- Where the specifications leave the Terraform state's location open ("outside the repository", "the object storage of the global layer"), the choice belongs to the person, as the phase page's work split says.
