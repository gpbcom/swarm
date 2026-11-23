# T0.10: Images, scans, signatures and Playwright

**Status:** ✅ Done

## Roadmap

- **Ticket:** [T0.10](../../specs/roadmap/01-p0-foundations.md#s02) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S02](../../specs/roadmap/01-p0-foundations.md#s02), 18 to 29 January 2027: shared code, dev cell and pipeline
- **Epic:** [E0.2](../../specs/roadmap/01-p0-foundations.md#epics): CI/CD. Every merge checked, built, scanned, signed and tested.

## What it delivers

- One multi-stage image per service and front end, with the repository root as context, and remote caches (uv, Cargo, Turborepo), as [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci) steps 3.
- Trivy and OSV-Scanner scans, an SBOM, a cosign signature and the push to GHCR, as [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci) step 4 and [🛡️ Security: supply chain and testing](../../specs/technical/06-security.md#supply-chain).
- `compose.e2e.yaml` and the Playwright scaffold, run against the real images, uploading its HTML report on a failure, as [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci) step 5.
- Publication tagged with the commit SHA, from `develop` and `master` only, as [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci) step 6.

## Features, use cases and business rules

- The roadmap names no feature, use case or business rule for this ticket.

## Technical pages it builds on

- [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci): "Build one image per changed service and front end (multi-stage, repository root as context), with remote caches", "Trivy and OSV-Scanner, SBOM, cosign signature; push to GHCR", Playwright "against the real images started by `compose.e2e.yaml`", and publication "tagged with the commit SHA, from `develop` and `master` only".
- [🛡️ Security: supply chain and testing](../../specs/technical/06-security.md#supply-chain): "Images built from minimal bases, signed with cosign, with an SBOM; Kubernetes admission accepts only signed images."
- [🚢 Deployment: delivery](../../specs/technical/09-deployment.md#delivery): "a release is a pull request that bumps image tags", taken by Argo CD from `deploy/environments`.
- [🌱 Deployment: environments](../../specs/technical/09-deployment.md#environments): the dev environment is "one ephemeral cell per branch", where an unsigned image must be refused.

## Screens touched

- The ticket touches no screen.

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

The "done when" of the roadmap row. The roadmap names no Given, when, then criterion of a feature for this ticket.

1. **Given** an unsigned image, **when** the dev cell is asked to run it, **then** the dev cell refuses it. (No business rule or use case is named by the roadmap.)
2. **Given** the real images started by `compose.e2e.yaml`, **when** Playwright runs against them, **then** it tests those images and not a development server. (No business rule or use case is named by the roadmap.)
3. **Given** a Playwright test that fails, **when** the run ends, **then** its HTML report is uploaded. (No business rule or use case is named by the roadmap.)
4. **Given** a commit on a branch other than `develop` or `master`, **when** the pipeline runs, **then** no image is published tagged with the commit SHA. (No business rule or use case is named by the roadmap.)

## Out of scope

- Steps 1 and 2 of the pipeline, change detection and the language checks, see [T0.04](../../specs/roadmap/01-p0-foundations.md#s01).
- The dev cell platform on k3s and its Argo CD, see [T0.08](../../specs/roadmap/01-p0-foundations.md#s02).
- Visual comparison with the specification mock-ups and the UC-029 screenshots, see [T0.20](../../specs/roadmap/01-p0-foundations.md#s04).
- Signing of the edge appliance and the on-premises bundle, see [🛡️ Security: supply chain and testing](../../specs/technical/06-security.md#supply-chain).

## Assumptions

- The roadmap row names no feature, use case or business rule, so the acceptance criteria cite none and the ticket links the technical page sections that settle what it builds.
- The roadmap has no per-ticket anchor, so the ticket link points to the sprint section `#s02`, as the other tickets of the phase do.
- The row names no row of the budgets table, so the ticket touches no budget.
- The row says the dev cell refuses an unsigned image, and the security page says Kubernetes admission accepts only signed images. The row gives no admission mechanism, so the plan chooses the most conservative option and records it.
- The row names no front end screen, so the Playwright scaffold shows none and the ticket touches no screen.
