# T0.08: Dev cell on k3s

**Status:** ✅ Done

## Roadmap

- **Ticket:** [T0.08](../../specs/roadmap/01-p0-foundations.md#s02) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S02](../../specs/roadmap/01-p0-foundations.md#s02), 18 to 29 January 2027: shared code, dev cell and pipeline
- **Epic:** [E0.4](../../specs/roadmap/01-p0-foundations.md#epics): Dev cell and data platform. A cell to run and measure everything on.

## What it delivers

- The platform of the dev cell, deployed by Helm and Argo CD on the k3s cluster Terraform provisioned in T0.01 ([🤝 P-06](../../specs/roadmap/11-hardware-and-partners.md#p-06)), as [🚢 Deployment: delivery](../../specs/technical/09-deployment.md#delivery).
- Argo CD, with the desired state of the cell in `deploy/environments`, as [🚢 Deployment: delivery](../../specs/technical/09-deployment.md#delivery).
- The umbrella chart of a cell and the charts of its data platform in `deploy/charts`: CloudNativePG with PostGIS and TimescaleDB, PgBouncer, Valkey, MinIO and KEDA, as [🚢 Deployment: providers](../../specs/technical/09-deployment.md#providers) and [🚢 Deployment: delivery](../../specs/technical/09-deployment.md#delivery).
- The vault (HashiCorp Vault or OpenBao), as [🔑 Security: secrets and keys](../../specs/technical/06-security.md#secrets).
- One ephemeral cell per branch on demand, its infrastructure created and destroyed by Terraform, as [🚢 Deployment: environments](../../specs/technical/09-deployment.md#environments) and [🚢 Deployment: infrastructure as code](../../specs/technical/09-deployment.md#iac).

## Features, use cases and business rules

- The roadmap names no feature, use case or business rule for this ticket.

## Technical pages it builds on

- [🚢 Deployment: providers](../../specs/technical/09-deployment.md#providers): "PostgreSQL runs through the CloudNativePG operator with PostGIS and TimescaleDB, NATS and Valkey as charts", and the self-hosted provider is k3s with MinIO.
- [🧰 Deployment: infrastructure as code](../../specs/technical/09-deployment.md#iac): "Terraform creates the empty cell; Helm and Argo CD then deploy Swarm on it", with one root per cell in `deploy/terraform/cells/<cell>/`.
- [🚢 Deployment: delivery](../../specs/technical/09-deployment.md#delivery): "Helm charts per service in `deploy/charts`, one umbrella chart per cell", KEDA installed in every cell, and the desired state of every cell in `deploy/environments` with Argo CD.
- [🌱 Deployment: environments](../../specs/technical/09-deployment.md#environments): dev is "One ephemeral cell per branch, created on demand, deleted when the branch closes", with simulated Drones only.
- [🔑 Security: secrets and keys](../../specs/technical/06-security.md#secrets): a "Vault (HashiCorp Vault or OpenBao) per cell for database credentials (dynamic)", and configuration "holds names, never secrets".
- [🗄️ Storage: PostgreSQL and PostGIS](../../specs/technical/03-storage.md#postgresql): "PgBouncer in transaction mode in front of each primary".

## Screens touched

- The ticket touches no screen.

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

The "done when" of the roadmap row. The roadmap names no Given, when, then criterion of a feature, and no business rule or use case, for this ticket.

1. **Given** a branch, **when** a cell is requested for it, **then** the branch gets its cell in minutes, with its infrastructure created by Terraform and the platform deployed by Argo CD.
2. **Given** a branch with a dev cell, **when** the branch closes, **then** the cell is lost, its infrastructure destroyed by Terraform.
3. **Given** a running dev cell, **when** a service needs a database credential, **then** the credential comes from the vault and never from a file.

## Out of scope

- The NATS JetStream cluster and Operator accounts, see [T0.09](../../specs/roadmap/01-p0-foundations.md#s02).
- Signed images and the refusal of unsigned images by the dev cell, see [T0.10](../../specs/roadmap/01-p0-foundations.md#s02).
- The OpenTelemetry collector, Prometheus, Loki, Tempo and Grafana, see [T0.17](../../specs/roadmap/01-p0-foundations.md#s04).
- The k3s cluster and its machines, already provisioned by T0.01, see [T0.01](../../specs/roadmap/01-p0-foundations.md#s01).
- Keycloak, see [T0.11](../../specs/roadmap/01-p0-foundations.md#s03).

## Assumptions

- The roadmap row names no feature, use case or business rule, so the acceptance criteria cite none.
- The row names no row of the budgets table, so the ticket touches no budget.
- "In minutes" is not quantified by the specifications, so no duration is asserted.
- Which events create and close a branch's cell (a command, a pull request label, a workflow) is not specified, so the plan chooses the most conservative option and records it.
- The choice between HashiCorp Vault and OpenBao is left open by the row, so either satisfies it.
