# 🚢 Deployment

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ Observability](08-observability.md) · 📄 **Page 104 / 120** · [GUI and WebUI ▶️](10-frontends.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> Where Swarm runs and how it gets there: sovereign EU providers and self-hosted k3s cells, Helm and Argo CD, rollout waves, the edge appliance, the on-premises bundle, the CI pipeline and the environments. Decisions T28 to T31, T37 and T38.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🌐 Where it runs](#providers)
2. [🧰 Infrastructure as code](#iac)
3. [🚢 Delivery](#delivery)
4. [🛸 Edge appliance](#edge)
5. [🏢 On-premises bundle](#on-premises)
6. [🧰 CI/CD](#ci)
7. [🌱 Environments](#environments)
8. [🔗 Features implemented](#features)
<!-- /spec:summary -->

## <a id="providers"></a>🌐 Where it runs

| Target | Kubernetes | Object storage | Used for |
| --- | --- | --- | --- |
| OVHcloud | Managed Kubernetes | OVHcloud Object Storage (S3) | EU cells |
| Scaleway | Kapsule | Scaleway Object Storage (S3) | EU cells |
| Self-hosted | k3s (or the company's Kubernetes) | MinIO | US cells, on-premises installs, staging |

- **Same software everywhere:** no provider-only service sits in the critical path; PostgreSQL runs through the CloudNativePG operator with PostGIS and TimescaleDB, NATS and Valkey as charts, so a cell moves between providers unchanged.
- **Global layer:** Keycloak and the Operator directory run in two EU regions, active and standby.
- **GPU:** a GPU node pool per cell where the provider offers it, scaled to zero when idle; on premises, at least one GPU server for processing and the open-weight model.

## <a id="iac"></a>🧰 Infrastructure as code

- **Terraform** (decision T43) provisions every cell and the global layer: Kubernetes clusters (OVHcloud Managed Kubernetes, Scaleway Kapsule, k3s on self-hosted machines), node pools including GPU, networks, load balancers, object storage buckets, DNS, and the vault.
- One Terraform module per building block in `infra/terraform/modules/`, one root per cell in `infra/terraform/cells/<cell>/`; state kept remotely in the object storage of the global layer, with locking.
- Terraform creates the empty cell; Helm and Argo CD then deploy Swarm on it. A new cell is a new root and a pull request.
- `terraform plan` runs in CI on every change under `infra/terraform/`; `apply` is manual, after review.

## <a id="delivery"></a>🚢 Delivery

- **Helm charts** per service in `infra/charts`, one umbrella chart per cell; values per provider and environment.
- **KEDA** is installed in every cell (and in the on-premises bundle) with its NATS JetStream and Prometheus scalers and the HTTP add-on; each chart ships its `ScaledObject`. The `agents` chart deploys `agents-mcp`, `agents-a2a` and `agents-worker`, each with its Kubernetes Service and `ScaledObject`.
- **GitOps with Argo CD:** the desired state of every cell lives in `infra/environments`; a release is a pull request that bumps image tags.
- **Waves:** a canary cell first, then the other cells of the region in waves; an SLO burn during a wave stops it and rolls back.
- **Migrations:** expand and contract; the expand step runs before the new pods, the contract step one release later.

## <a id="edge"></a>🛸 Edge appliance

- **What runs:** flight-engine, video-relay, a NATS leaf node, the local OpenTelemetry collector and the SFU, as containers on the Ground control machine (through the Tauri desktop app) or on a rugged edge box; Dock PCs run a minimal edge.
- **Updates:** over the air from the cell, signed, **never during a Mission**; the previous version is kept for rollback; edges update in rings (internal, early Operators, everyone).
- **Offline:** maps (PMTiles), Drone model data and the last known Missions are cached so a field laptop can prepare and fly without network where the Jurisdiction allows.

## <a id="on-premises"></a>🏢 On-premises bundle

- One cell on k3s or the company's Kubernetes, installed from a **signed offline bundle**: images, charts, base maps, detection models, the open-weight model.
- Updates are new bundles, verified and applied by the company's IT administrator (the Swarm administrator on premises).
- Sizing guide: a 3-node cluster for up to 20 Missions in flight, plus one GPU server.

## <a id="ci"></a>🧰 CI/CD

GitHub Actions, following the steps of AGENT.md, each step passing before the next:

1. **Detect changes** per service, front end and package; a change in `packages/` or a lock file runs everything that depends on it.
2. **Check:** ruff, mypy, pytest (Python); cargo fmt, clippy, tests and benchmarks (Rust); eslint, tsc, Vitest (TypeScript); generated types and the specifications (`specs.py check`) up to date.
3. **Build** one image per changed service and front end (multi-stage, repository root as context), with remote caches (uv, Cargo, Turborepo).
4. **Scan and sign:** Trivy and OSV-Scanner, SBOM, cosign signature; push to GHCR.
5. **Test the images:** Playwright against the real images started by `infra/compose/e2e.yaml`; visual comparison with the specification mock-ups.
6. **Publish** images tagged with the commit SHA, from `develop` and `master` only (GitFlow); Argo CD takes it from there.

## <a id="environments"></a>🌱 Environments

| Environment | What | Drones |
| --- | --- | --- |
| dev | One ephemeral cell per branch, created on demand, deleted when the branch closes | Simulated only |
| staging | One full cell, nightly load tests, monthly restore drills | Simulated, plus real Drones on a test field every week |
| beta (from S24 to S46) | An OVHcloud cell for the design partner, and a self-hosted beta cell as the second cell (on-premises rehearsal and fallback) | Real |
| production | Cells per region, canary cell first | Real |
| simulation | An always-on simulated fleet for demos, training sessions (Instructors) and compatibility tests | Simulated only, isolated credentials |

## <a id="features"></a>🔗 Features implemented

[📘 FS-010](../functional/features/FS-010-simulator-and-training.md), [📘 FS-011](../functional/features/FS-011-drone-adapters.md), [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md), [📘 FS-017](../functional/features/FS-017-mission-assistant.md) (models on premises).

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ Observability](08-observability.md) · 📄 **Page 104 / 120** · [GUI and WebUI ▶️](10-frontends.md)
<!-- /spec:nav-bottom -->
