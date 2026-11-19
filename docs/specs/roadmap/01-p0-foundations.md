# 🛣️ P0: Foundations

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ Roadmap](README.md) · 📄 **Page 96 / 109** · [P1: First flight ▶️](02-p1-first-flight.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Sprints:** S01 to S04 · **Dates:** 4 Jan to 26 Feb 2027 · **Tickets:** about 20

> [!NOTE]
> P0 builds what every later ticket stands on: the mono-repo and its CI/CD, the Claude Code ticket harness that lets one person run several agents in parallel from S02, the shared packages, identity, one dev cell with NATS and the databases, the [⚙️ Simulator](../glossary.md#sys-simulator) base, the design tokens and the observability base; it comes first because nothing can fly, be reviewed quickly or be measured without it.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🎯 Goal](#goal)
2. [🧺 Scope](#scope)
3. [🪜 Epics](#epics)
4. [🗓️ Sprint plan](#sprints)
5. [🎤 Demo](#demo)
6. [🚪 Exit criteria](#exit)
7. [⛓️ Dependencies](#dependencies)
8. [🎲 Risks](#risks)
9. [🧑‍💻 Work split](#work-split)
<!-- /spec:summary -->

## <a id="goal"></a>🎯 Goal

At the end of P0, on Friday 26 February 2027 (milestone **M0**), the repository, the pipeline and one dev cell are ready for the flight work of [🛣️ P1: First flight](02-p1-first-flight.md):

- **One person, many agents.** The Claude Code ticket harness is in the repository in S01: a ticket names its phase, sprint, features, use cases and business rules; the agents split it into parallel tasks (code, tests, mock-ups, documentation), each in its own git worktree, and hand back one reviewed branch. From S02 on, the person reviews and decides while the agents build, which is what makes about 5 merged tickets per sprint possible ([🎲 R-01](12-risks.md#r-01)).
- **One repository for every language.** The layout of [🏗️ Architecture](../technical/01-architecture.md#mono-repo): `services/`, `frontends/`, `packages/` (Python, Rust, TypeScript), `deploy/`, `tests/`, with one lock file per toolchain, and the rules of [AGENT.md](../../../AGENT.md) enforced by `tests/conventions/` on every service, present and future.
- **CI/CD green on every language.** The six steps of [🚢 Deployment](../technical/09-deployment.md#ci): change detection, checks (Python, Rust, TypeScript, generated types, `specs.py check`), image builds, scans and signatures, Playwright against the real images, publication from `develop` and `master`.
- **A dev cell that looks like production.** Provisioned with Terraform from S01 (decision T43: machines, k3s cluster, network, object storage, DNS), on self-hosted machines ([🤝 P-06](11-hardware-and-partners.md#p-06)), then deployed by Helm and Argo CD: k3s with Keycloak, NATS JetStream, PostgreSQL with PostGIS and TimescaleDB, Valkey, MinIO, a vault, and the OpenTelemetry stack, deployed by Argo CD from `deploy/environments`.
- **The first use case.** A [👤 Swarm administrator](../glossary.md#per-swarm-administrator) creates an [🗃️ Operator](../glossary.md#ent-operator) and invites its first [👤 Mission planner](../glossary.md#per-mission-planner) in the [⚙️ Back office](../glossary.md#sys-back-office) ([🎬 UC-029](../functional/use-cases/UC-029-create-an-operator.md)), isolated from every other Operator ([📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md)), in any of the four languages ([📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md)).
- **A simulated Squad on the map.** The Simulator flies a simulated [🗃️ Squad](../glossary.md#ent-squad) of 10 [🗃️ Drones](../glossary.md#ent-drone) (synthetic Rust Drones, plus one PX4 SITL Drone), isolated from any real Drone ([📏 BR-014](../functional/business-rules/BR-014-simulation-isolation.md)); its [🔤 Telemetry](../glossary.md#term-telemetry) crosses a first flight engine, the NATS leaf node, the cell and the gateway, and moves on the map of [⚙️ Ground control](../glossary.md#sys-ground-control) in the browser. This is the proof of M0 in the [🛣️ Roadmap](README.md#milestones).

## <a id="scope"></a>🧺 Scope

**📘 Features**

| Feature | Delivered in P0 | Acceptance criteria closed |
| --- | --- | --- |
| [📘 FS-012: Operators, deployment and languages](../functional/features/FS-012-operators-deployment-and-languages.md) | Creating an Operator and its first Mission planner in the cloud deployment ([🎬 UC-029](../functional/use-cases/UC-029-create-an-operator.md)); Operator isolation in every layer; the language framework for four languages. Inviting Clients comes in P2, Notifications in P3, production cells and on premises in P7 | AC-3 |
| [📘 FS-010: Simulator and training](../functional/features/FS-010-simulator-and-training.md) | The Simulator base only: PX4 SITL in containers, synthetic Rust Drones, isolated credentials and the simulated mark on the Flight log. Training sessions come in P1 | None yet: AC-1 closes in P1 with [🎬 UC-013](../functional/use-cases/UC-013-train-on-the-simulator.md) |

**🎬 Use cases**

| Use case | In P0 | Screens moved to 📸 Screenshot |
| --- | --- | --- |
| [🎬 UC-029: Create an Operator](../functional/use-cases/UC-029-create-an-operator.md) | Delivered: every step, alternative flows A1 (name taken) and A2 (required field missing). A3 (on premises) is designed for but installed in P7 | A1, KO, A2, OK |

**📏 Business rules**

| Rule | In P0 |
| --- | --- |
| [📏 BR-008: Operator isolation](../functional/business-rules/BR-008-operator-isolation.md) | Delivered as a foundation: Keycloak organisations, the Operator in every token, the gateway check, PostgreSQL row-level security on `swarm.operator_id`, NATS accounts per Operator (`op.<operator_id>.…`), one object storage bucket per Operator. Every later table and subject inherits it |
| [📏 BR-014: Simulation isolation](../functional/business-rules/BR-014-simulation-isolation.md) | Delivered as a foundation: separate NATS credentials for simulated Squads, an adapter registry that cannot address a real Drone, every simulated Flight log marked simulated |
| [📏 BR-017: Every screen in four languages](../functional/business-rules/BR-017-every-screen-in-four-languages.md) | Delivered as a framework: English, French, German and Spanish messages in `packages/ts/i18n` and in Python, a language per person, and a CI check that fails on a missing translation. Every later screen is born in four languages |

**🛠️ Technical pages**

| Page | What P0 builds from it |
| --- | --- |
| [🏗️ Architecture: mono-repo](../technical/01-architecture.md#mono-repo) | The folder layout, the uv, Cargo and pnpm workspaces, one image per service and front end |
| [🏗️ Architecture: cells and the global layer](../technical/01-architecture.md#cells) | Keycloak and the Operator directory as the global layer; one dev cell holding the services, NATS, the databases, Valkey and object storage |
| [🧱 Data models: conventions](../technical/02-data-models.md#conventions) | `packages/python/swarm-models`: UUIDv7, UTC in microseconds, units in names, GeoJSON, states as `StrEnum` with glossary names |
| [🧱 Data models: events](../technical/02-data-models.md#events) | The `Event` envelope and the NATS subjects `op.<operator_id>.…` |
| [🧱 Data models: versioning](../technical/02-data-models.md#versioning) | JSON Schema export, `typify` structs for Rust, TypeScript types for `packages/ts/live` and `packages/ts/api-client`; CI fails on a stale generated file |
| [🗄️ Storage: PostgreSQL and PostGIS](../technical/03-storage.md#postgresql) | One schema per service, row-level security, PgBouncer, Alembic migrations (expand then contract) |
| [🗄️ Storage: TimescaleDB](../technical/03-storage.md#timescaledb) | The extension installed and the first hypertable for the walking skeleton |
| [🗄️ Storage: object storage](../technical/03-storage.md#object-storage) | MinIO in the dev cell, one bucket per Operator |
| [🔩 Engine and services: simulator](../technical/04-engine.md#simulator) | PX4 SITL (headless Gazebo) and synthetic Rust Drones, isolated |
| [🔌 API layer: REST](../technical/05-api.md#rest) | FastAPI `/v1`, `problem+json`, `Idempotency-Key`, cursor pagination, the generated OpenAPI document |
| [🔌 API layer: live data](../technical/05-api.md#live) | The `/v1/live` WebSocket with MessagePack and one subscription per Mission |
| [🔐 Security: identity](../technical/06-security.md#identity) | Keycloak realm, Operators as organisations, multi-factor authentication, PKCE clients |
| [🔐 Security: roles and isolation](../technical/06-security.md#authorisation) | Roles per persona, checks in the gateway and in PostgreSQL |
| [🔐 Security: secrets and keys](../technical/06-security.md#secrets) | A vault in the dev cell; configuration holds names, never secrets |
| [🔐 Security: supply chain](../technical/06-security.md#supply-chain) | OSV-Scanner, Trivy, Semgrep, cargo-audit, SBOM, cosign signatures |
| [🩺 Observability: signals](../technical/08-observability.md#signals) | OpenTelemetry SDKs in Python, Rust and TypeScript; Prometheus, Loki, Tempo and Grafana in the dev cell |
| [🚢 Deployment: CI/CD](../technical/09-deployment.md#ci) | The six steps on GitHub Actions |
| [🚢 Deployment: delivery](../technical/09-deployment.md#delivery) | Helm charts in `deploy/charts`, one umbrella chart per cell, Argo CD |
| [🚢 Deployment: environments](../technical/09-deployment.md#environments) | The dev environment: one ephemeral cell per branch, simulated Drones only |
| [🖥️ GUI and WebUI: apps and packages](../technical/10-frontends.md#apps) | The shells of the four apps and the Tauri 2 desktop shell; `ui`, `tokens`, `i18n`, `live`, `api-client`, `maps` |
| [🖥️ GUI and WebUI: design system](../technical/10-frontends.md#design-system) | Tokens generated from [🎨 the visual identity](../visual-identity.md#colours) into `packages/ts/tokens`, and the visual tests against the mock-ups |

## <a id="epics"></a>🪜 Epics

| ID | Epic | Delivers | Where | Tickets | Parallel tasks for the agents |
| --- | --- | --- | --- | --- | --- |
| E0.1 | Mono-repo, Terraform base and ticket harness | The working method of the whole roadmap; [AGENT.md](../../../AGENT.md) rules enforced; the dev cell's infrastructure as code | Repository root, `deploy/terraform`, `.claude/` (agents, skills, rules, hooks), `tests/conventions/` | 3: T0.01 to T0.03 | Move the current `src/` layout into `services/`; workspace files for uv, Cargo and pnpm; Terraform modules for a self-hosted cell; agent definitions; the ticket skill; the hooks; convention tests per rule |
| E0.2 | CI/CD | Every merge checked, built, scanned, signed and tested | `.github/workflows/`, `compose.e2e.yaml`, `deploy/` | 2: T0.04, T0.10 | Change detection; Python, Rust and TypeScript check steps; multi-stage Dockerfiles; scans and signatures; Playwright scaffold |
| E0.3 | Shared packages | One model per object, one lifecycle, one logging, one Rust core | `packages/python/` (`swarm-models`, lifecycle, logging, NATS client), `packages/rust/` (`swarm-core`) | 3: T0.05 to T0.07 | `Runnable` and `AsyncRunnable` with factories; logging configuration; base models and `Event`; JSON Schema export and generated types; PyO3 and maturin wheels; criterion benchmark gate |
| E0.4 | Dev cell and data platform | A cell to run and measure everything on | `deploy/terraform`, `deploy/charts`, `deploy/environments`, the dev cell on self-hosted k3s | 3: T0.08, T0.09, T0.17 | CloudNativePG with PostGIS and TimescaleDB; Valkey; MinIO; vault; NATS JetStream and accounts; OpenTelemetry collector, Prometheus, Loki, Tempo, Grafana |
| E0.5 | Identity and Operators | [🎬 UC-029](../functional/use-cases/UC-029-create-an-operator.md), [📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md), [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md) AC-3 | Keycloak (global layer), `services/gateway`, `services/missions`, `services/fleet` (skeletons), `frontends/back-office` | 3: T0.11, T0.12, T0.16 | Realm and roles; token checks in the gateway; row-level security and its tests; Operator directory; UC-029 screens in four languages; isolation test with two Operators |
| E0.6 | Simulator and live path | [📏 BR-014](../functional/business-rules/BR-014-simulation-isolation.md); the M0 proof | `services/simulator`, `services/flight-engine` (skeleton), `services/gateway` (live), `frontends/ground-control` | 3: T0.13, T0.18, T0.19 | PX4 SITL container; synthetic Rust Drones speaking MAVLink; isolated credentials; Mission actor skeleton; `SquadFrame` over NATS; WebSocket fan-out; map with deck.gl layer and Web Worker decoding |
| E0.7 | Front-end foundation | [📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md); every later screen | `packages/ts/` (`tokens`, `ui`, `i18n`, `maps`), `frontends/*`, `frontends/desktop` | 3: T0.14, T0.15, T0.20 | Token generation; Radix components; frames of the four parts of Swarm; Tauri 2 shell; FormatJS messages and Babel catalogues; visual test pipeline |

## <a id="sprints"></a>🗓️ Sprint plan

P0 has no overlap with another phase: its four sprints carry its 20 tickets, 5 per sprint. S01 is the only sprint without parallel agents, because the harness is what it builds.

| Sprint | Dates | Tickets | Sprint goal | What can be shown |
| --- | --- | --- | --- | --- |
| [S01](#s01) | 4 to 15 Jan 2027 | T0.01 Mono-repo layout and Terraform base · T0.02 Claude Code ticket harness · T0.03 Convention tests and linters · T0.04 CI checks for every language · T0.05 Lifecycle and logging packages | The repository, its rules and its first CI checks; the dev cell's infrastructure provisioned by Terraform; the harness ready to run agents in parallel | A ticket file handed to the harness: the agents split it into tasks, each in its own worktree, and the merged branch passes the checks |
| [S02](#s02) | 18 to 29 Jan 2027 | T0.06 Shared models and generated types · T0.07 Rust core and benchmark gate · T0.08 Dev cell on k3s · T0.09 NATS JetStream and Operator accounts · T0.10 Images, scans, signatures and Playwright | The dev cell runs; every image is built, scanned and signed | Argo CD shows the dev cell in sync; a pull request shows its signed images and a failing benchmark gate on purpose |
| [S03](#s03) | 1 to 12 Feb 2027 | T0.11 Keycloak and gateway authentication · T0.12 Service skeletons with row-level security · T0.13 Simulator base · T0.14 Design tokens, components and app shells · T0.15 Four languages | A person signs in; a service answers for one Operator only; simulated Drones fly | A test Mission planner signs in with multi-factor authentication; a query for another Operator's rows returns nothing; 10 synthetic Drones fly in the Simulator |
| [S04](#s04) | 15 to 26 Feb 2027 | T0.16 Create an Operator (UC-029) · T0.17 Observability base · T0.18 Flight engine skeleton and live WebSocket · T0.19 Simulated Squad on the Ground control map · T0.20 Visual tests and UC-029 screenshots | M0: Foundations ready | The [demo](#demo) of this page |

**Total: 20 tickets** (S01 5, S02 5, S03 5, S04 5).

### <a id="s01"></a>S01, 4 to 15 January 2027: repository and harness

| Ticket | Delivers | Where | Done when |
| --- | --- | --- | --- |
| T0.01 Mono-repo layout and Terraform base | The layout of [🏗️ Architecture](../technical/01-architecture.md#mono-repo): `services/`, `frontends/`, `packages/python`, `packages/rust`, `packages/ts`, `deploy/`, `tests/`; the uv workspace (one `uv.lock`), the Cargo workspace with maturin, the pnpm workspace with Turborepo; the current root `src/` moved to its service as the Mono-repo section of [AGENT.md](../../../AGENT.md) plans; `deploy/terraform` (decision T43) with one module per provider, the self-hosted k3s module used first, provisioning the dev cell's machines, k3s cluster, network, object storage and DNS, with its state kept outside the repository and checked by `terraform plan` in CI | Repository root, `deploy/terraform` | Every workspace installs from a clean clone; `terraform apply` creates the dev cell's empty k3s cluster from nothing; the README says how to start |
| T0.02 Claude Code ticket harness | The working method of the roadmap, versioned in `.claude/` like the specification harness: a ticket template (phase, sprint, 📘 FS, 🎬 UC and 📏 BR IDs, acceptance criteria in **Given**, **when**, **then**, screens touched, budgets touched); a skill that reads a ticket, checks its IDs against `docs/specs/`, writes the task split and starts one agent per task in its own git worktree; agent definitions per kind of task (Python service, Rust core, front end, tests, mock-ups and screens, specifications and documentation, reviewer); hooks that format only the edited files and run the checks of the touched layer before a task is handed back; a reviewer agent that reads the merged branch against AGENT.md, the SPEC rules and the ticket's acceptance criteria and writes a short review note for the person | `.claude/agents/`, `.claude/skills/`, `.claude/rules/`, `.claude/settings.json` | A sample ticket runs end to end: split into at least three parallel tasks, merged into one branch, review note written, checks green; the person's review of it takes under an hour |
| T0.03 Convention tests and linters | `tests/conventions/` enforcing the rules a test enforces in AGENT.md (one class per file, five files per folder, no `Any`, no nested function, allowed layer imports, lifecycle base classes, Pydantic models only in `models/`) against every service found under `services/`, so a new service needs no change; rustfmt and clippy settings; eslint and `tsc` strict settings | `tests/conventions/`, `packages/rust`, `packages/ts` | A deliberately broken sample service fails each rule once; adding an empty service needs no change to the tests |
| T0.04 CI checks for every language | Steps 1 and 2 of [🚢 Deployment: CI/CD](../technical/09-deployment.md#ci): change detection per service, front end and package (a change in `packages/` or a lock file runs everything that depends on it); ruff, `ruff format --check`, mypy and pytest; cargo fmt, clippy and tests; eslint, `tsc` and Vitest; `specs.py check` | `.github/workflows/` | A pull request touching one service runs only that service's checks; a change in `packages/` runs all of them |
| T0.05 Lifecycle and logging packages | `Runnable` and `AsyncRunnable` (`initialize`, `run`, `close`, `execute`), the abstract factories, the logging configuration of AGENT.md (coloured console, coloured rotating file, JSON in production), the `YamlCatalog` base | `packages/python/` | Every service skeleton of P0 uses them; their own tests pass and the convention tests accept them |

### <a id="s02"></a>S02, 18 to 29 January 2027: shared code, dev cell and pipeline

From S02, every ticket goes through the harness: the person writes or approves the ticket, the agents work in parallel, the person reviews one branch per ticket.

| Ticket | Delivers | Where | Done when |
| --- | --- | --- | --- |
| T0.06 Shared models and generated types | `packages/python/swarm-models` with the conventions of [🧱 Data models](../technical/02-data-models.md#conventions); the `Event` envelope; first versions of `Operator`, `Person`, `Role`, `CellAssignment`, `TelemetryFrame`, `SquadFrame` and `Command`; JSON Schema export; `typify` structs for Rust; TypeScript types into `packages/ts/live` | `packages/python/swarm-models`, `packages/rust`, `packages/ts/live` | Each model has the six model tests of AGENT.md; CI fails when a generated file is stale |
| T0.07 Rust core and benchmark gate | The `swarm-core` Cargo workspace with its `safety`, `planner` and `mavlink` crates (empty shells with one function each), PyO3 bindings built as wheels by maturin, criterion benchmarks run on every pull request, a regression of more than 5 % failing the build ([🚀 Scalability and performance](../technical/07-scalability.md#load-tests)) | `packages/rust/` | A Python service imports a Rust function from a wheel; a slowed-down function fails the benchmark gate |
| T0.08 Dev cell on k3s | The platform of the dev cell, deployed by Helm and Argo CD on the k3s cluster Terraform provisioned in T0.01 ([🤝 P-06](11-hardware-and-partners.md#p-06)): Argo CD, the umbrella chart of a cell, CloudNativePG with PostGIS and TimescaleDB, PgBouncer, Valkey, MinIO, the vault (HashiCorp Vault or OpenBao), KEDA; one ephemeral cell per branch on demand, its infrastructure created and destroyed by Terraform ([🚢 Deployment: environments](../technical/09-deployment.md#environments)) | `deploy/terraform`, `deploy/charts`, `deploy/environments` | A branch gets its cell in minutes and loses it when it closes; a database credential comes from the vault, never from a file |
| T0.09 NATS JetStream and Operator accounts | The NATS cluster of 3 with JetStream replicas 3; one NATS account per Operator limited to `op.<operator_id>.…`; separate credentials for simulated Squads; the leaf node configuration for an edge; the shared async NATS client (request-reply with deadlines and idempotency keys, durable consumers) | `deploy/charts`, `packages/python/` | A test publishing on another Operator's subject is refused; a leaf node cut for one minute replays its messages in order |
| T0.10 Images, scans, signatures and Playwright | Steps 3 to 6 of [🚢 Deployment: CI/CD](../technical/09-deployment.md#ci): one multi-stage image per service and front end with the repository root as context, remote caches, Trivy and OSV-Scanner, SBOM, cosign, push to GHCR; `compose.e2e.yaml` and the Playwright scaffold; publication tagged with the commit SHA from `develop` and `master` only | `.github/workflows/`, `compose.e2e.yaml`, each `Dockerfile` | An unsigned image is refused by the dev cell; Playwright runs against the real images and uploads its HTML report on a failure |

### <a id="s03"></a>S03, 1 to 12 February 2027: identity, services and Simulator

| Ticket | Delivers | Where | Done when |
| --- | --- | --- | --- |
| T0.11 Keycloak and gateway authentication | The global layer of [🔐 Security: identity](../technical/06-security.md#identity): one realm, each Operator an organisation, roles per persona, multi-factor authentication for Pilots, Mission planners, Fleet maintainers, Instructors and Swarm administrators, 5-minute access tokens and rotated refresh tokens, PKCE clients for the four apps and the desktop shell; the gateway checks the role and the Operator of every call | Keycloak (global layer), `services/gateway` | A call without a token, with an expired token or with another Operator's identifier is refused and logged |
| T0.12 Service skeletons with row-level security | `services/gateway`, `services/missions` and `services/fleet` as AGENT.md services (layers, factories, logging); FastAPI `/v1` with `problem+json`, `Idempotency-Key`, `ETag`; one PostgreSQL schema per service with Alembic; row-level security on `operator_id` against `swarm.operator_id`; the OpenAPI document published and `packages/ts/api-client` generated | `services/gateway`, `services/missions`, `services/fleet`, `packages/ts/api-client` | A query that forgets the Operator filter returns nothing ([📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md)); the generated client is up to date in CI |
| T0.13 Simulator base | `services/simulator`: PX4 SITL in containers (headless Gazebo) and synthetic Drones written in Rust that speak MAVLink and follow a route; an adapter registry that cannot address a real Drone; separate NATS credentials; every Flight log it produces marked simulated ([📏 BR-014](../functional/business-rules/BR-014-simulation-isolation.md)) | `services/simulator`, `packages/rust` | 10 synthetic Drones and one PX4 SITL Drone fly a square route in the dev cell; a command from simulated credentials to a Drone outside the registry is refused and logged |
| T0.14 Design tokens, components and app shells | `packages/ts/tokens` generated from [🎨 the visual identity](../visual-identity.md#colours) by the same pipeline as `visual-identity.css`, light and dark; `packages/ts/ui` on Radix primitives with the components of the component sheet; the frame of each part of Swarm (title bar, side bar, status bar) as layout components; empty shells of `ground-control`, `mission-studio`, `back-office` and `client-portal`; the Tauri 2 desktop shell building on Windows, macOS and Linux | `packages/ts/`, `frontends/` | Changing a token on the visual identity page changes the apps and the mock-ups after one build; the four shells open in light and dark mode |
| T0.15 Four languages | `packages/ts/i18n` with FormatJS messages in English, French, German and Spanish; Babel catalogues for Python messages; the language of each person stored with the person and applied at sign-in; a CI check that fails when a message lacks one of the four languages ([📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md)) | `packages/ts/i18n`, `packages/python/`, `.github/workflows/` | A message added in English only fails CI; the shells switch language without reloading |

### <a id="s04"></a>S04, 15 to 26 February 2027: first use case and M0

| Ticket | Delivers | Where | Done when |
| --- | --- | --- | --- |
| T0.16 Create an Operator (UC-029) | [🎬 UC-029](../functional/use-cases/UC-029-create-an-operator.md) in the Back office: ➕ Create an Operator (name, deployment, Jurisdictions, LLM provider and Anchoring with their defaults), the checks of step 3 (name taken, required field missing), the Operator directory and its cell assignment, the invitation of the first Mission planner by e-mail, her first sign-in | `frontends/back-office`, `services/gateway`, Keycloak, the Operator directory | [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md) AC-3 passes as an automated test with two Operators; A1 and A2 refuse as specified |
| T0.17 Observability base | OpenTelemetry SDKs in Python, Rust and TypeScript; the collector; Prometheus, Loki, Tempo and Grafana in the dev cell; trace context carried in NATS headers; `operator_id`, `mission_id` and `cell` as resource attributes, `drone_id` never a metric label ([🩺 Observability](../technical/08-observability.md#signals)) | `packages/python/`, `packages/rust`, `packages/ts`, `deploy/charts` | One trace follows a Telemetry frame from the Simulator to the browser; no secret or personal data appears in a signal |
| T0.18 Flight engine skeleton and live WebSocket | `services/flight-engine` as an AGENT.md service: one asyncio process with uvloop, one actor per Mission, MAVLink frames read through `swarm-core`, one `SquadFrame` per tick to the local WebSocket and to the leaf node; the gateway `/v1/live` WebSocket with MessagePack, one NATS subscription per Mission, one-slot mailboxes per client ([🔌 API layer: live data](../technical/05-api.md#live)) | `services/flight-engine`, `services/gateway`, `packages/rust` | 10 simulated Drones reach a WebSocket client through the cell; a slow client skips frames instead of growing a queue |
| T0.19 Simulated Squad on the Ground control map | The first screen of `ground-control` in the browser: MapLibre with self-hosted PMTiles, a deck.gl layer of Drones fed by `packages/ts/live` (MessagePack decoded in a Web Worker, typed arrays), the frame of Ground control with ✋ Hold the Squad and 🛑 Abort shown but not yet wired | `frontends/ground-control`, `packages/ts/live`, `packages/ts/maps` | 10 simulated Drones move on the map in the dev cell; the Telemetry latency from Drone to screen through the cell is measured and shown in Grafana |
| T0.20 Visual tests and UC-029 screenshots | Playwright renders each screen with the sample data of [🎨 the visual identity](../visual-identity.md#screens) and compares it with the mock-up PNG in light and dark mode; a large difference fails the build; the four screens of UC-029 captured as 📸 Screenshot and their mock-ups deleted | `frontends/back-office`, `tests/`, `docs/specs/screens/` | `specs.py check` prints nothing with the UC-029 screenshots in place |

## <a id="demo"></a>🎤 Demo

The M0 demonstration, on Friday 26 February 2027, in the dev cell, with the sample cast of [🎨 the visual identity](../visual-identity.md#screens): the Operator Aerowing Services, the Mission planner Léa Martin, the Swarm administrator (shown by role only) and the Drones Alpha to Foxtrot.

1. **The harness at work.** The person opens ticket T0.19 in Claude Code: the harness shows the task split (map layer, Web Worker decoder, live client, Playwright test, mock-up check, translations), the agents' worktrees and the reviewer agent's note. The merged branch is the one running in the dev cell.
2. **The pipeline.** The last pull request of the sprint: change detection, the Python, Rust and TypeScript checks, `specs.py check`, the images built, scanned with Trivy and OSV-Scanner, signed with cosign, and Playwright run against them. Everything is green.
3. **Create an Operator.** The Swarm administrator opens ➕ Operators in the Back office and creates Aerowing Services: cloud, EU (EASA), the default LLM provider and the default Anchoring. A second attempt with the same name is refused: the name is taken (UC-029 A1). An attempt without a Jurisdiction is refused and names the missing field (A2).
4. **The first Mission planner.** The Swarm administrator invites Léa Martin. She accepts, signs in with multi-factor authentication, chooses French, and the Back office is in French ([📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md)). She sees Aerowing Services only: the Operator created for the isolation test is invisible to her, through the Back office and through the REST API ([📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md), FS-012 AC-3).
5. **A simulated Squad.** The Simulator starts a Squad of 10 simulated Drones for Aerowing Services above Les Vignes solar farm: synthetic Rust Drones named Alpha to Foxtrot and four more, and one PX4 SITL Drone. Ground control, in the browser, shows them moving on the map. The banner of the Simulator is on every screen.
6. **Isolation of the Simulator.** A command sent with the Simulator's credentials to a Drone outside its registry is refused and logged ([📏 BR-014](../functional/business-rules/BR-014-simulation-isolation.md)).
7. **Measured.** Grafana shows the trace of one Telemetry frame from the Simulator through the flight engine, the leaf node, the cell and the gateway to the browser, its latency drawn against the budget of [🚀 Scalability and performance](../technical/07-scalability.md#budgets), and the REST latencies of the Operator calls.

## <a id="exit"></a>🚪 Exit criteria

**Acceptance criteria**

- [ ] [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md) AC-3: given a new drone service company, when the Swarm administrator creates its Operator, then its first Mission planner is invited and sees no other Operator's data ([📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md), [🎬 UC-029](../functional/use-cases/UC-029-create-an-operator.md)). Automated with two Operators, through the Back office and the REST API.
- [ ] UC-029 alternative flows A1 and A2 have automated tests.
- [ ] [📏 BR-014](../functional/business-rules/BR-014-simulation-isolation.md): an automated test proves that simulated credentials cannot address a Drone outside the Simulator's registry and that every simulated Flight log is marked simulated. [📘 FS-010](../functional/features/FS-010-simulator-and-training.md) AC-1 closes in P1.
- [ ] [📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md): every P0 screen exists in English, French, German and Spanish, and CI fails on a missing translation.

**Budgets** ([🚀 Scalability and performance](../technical/07-scalability.md#budgets))

- [ ] REST inside a cell: p95 under 100 ms for reads and under 250 ms for writes on the Operator and person calls of the dev cell.
- [ ] Telemetry, Drone to screen through the cell: measured for 10 simulated Drones and under 400 ms at p95. The edge budget (under 150 ms) is asserted from P1, when Ground control talks to its local flight engine.
- [ ] The safety tick benchmark runs on every pull request with its 5 % regression gate; the budget itself (under 5 ms for 500 Drones) is asserted in P1.

**CI/CD and harness**

- [ ] CI is green on Python, Rust and TypeScript, with every step of [🚢 Deployment: CI/CD](../technical/09-deployment.md#ci).
- [ ] `tests/conventions/` passes on every service and covers a new service without change.
- [ ] The dev cell accepts only signed images.
- [ ] From S02 to S04, at least 13 of the 15 tickets went through the harness with parallel tasks.

**Screens and specifications**

- [ ] The four screens of UC-029 (A1, KO, A2, OK) moved from ✏️ Mock-up to 📸 Screenshot, in light and dark mode, and their mock-ups deleted.
- [ ] `python3 .claude/skills/write-specs/scripts/specs.py check` prints nothing.

**Load tests** ([🚀 Scalability and performance](../technical/07-scalability.md#load-tests))

- [ ] A first k6 script runs against the dev cell: 100 WebSocket clients watching the simulated Squad, without a frame queue growing. The nightly full-cell run starts in P1 with the staging cell.

**Milestone M0**

- [ ] A simulated Squad of 10 Drones is visible in Ground control in the dev cell, and CI is green on every language.

## <a id="dependencies"></a>⛓️ Dependencies

**Previous phases**

None: P0 is the first phase. It starts from the approved specification in `docs/specs/` and the decisions of the [🛠️ technical interview](../../research/interview-technical.md).

**Regulatory, hardware, partners and campaigns**

| Item | Due | Why P0 needs it |
| --- | --- | --- |
| [🤝 P-06](11-hardware-and-partners.md#p-06) | S01 | The self-hosted machines Terraform provisions for the dev cell (and the staging cell from P1); OVHcloud and Scaleway production cells only come in P7 |
| [🏛️ G-01](09-regulatory-track.md#g-01) | S02 | Operator registration: not used by the software in P0, but started now because the certificates of [🏛️ G-02](09-regulatory-track.md#g-02) and the flights of [🛫 C-01](10-flight-test-campaigns.md#c-01) depend on it |

No hardware and no flight test are needed in P0: every Drone is simulated.

**What P0 hands to the next phases**

| Phase | Takes from P0 |
| --- | --- |
| [🛣️ P1: First flight](02-p1-first-flight.md) | The harness, the pipeline, the dev cell, NATS, the databases, `swarm-models`, `swarm-core`, the Simulator, the flight engine skeleton, the Ground control shell and map, the tokens and the four languages |
| Every later phase | The convention tests, Operator isolation in every layer, the observability base, the visual tests that move screens to 📸 Screenshot |

## <a id="risks"></a>🎲 Risks

| Risk | Why it matters in P0 | Response in P0 |
| --- | --- | --- |
| [🎲 R-01](12-risks.md#r-01) Review bottleneck | One person reviews everything; without the harness the plan of about 5 tickets per sprint does not hold | The harness is the first ticket that ships (S01); the reviewer agent writes a short note per ticket; every check that can be a test is a test (conventions, `specs.py check`, benchmarks), so the person reviews design and behaviour, not style |
| [🎲 R-08](12-risks.md#r-08) Scope too large for 24 months | Foundations can grow without end | P0 builds only what P1 needs to fly and what M0 proves; production cells, on premises and the edge appliance wait for P7; each P0 ticket names the later ticket that uses it |
| [🎲 R-10](12-risks.md#r-10) Security incident or key compromise | Secrets and signing habits set in P0 last the whole roadmap | A vault from the first cell; configuration holds names only; images signed and refused unsigned; scans in CI; no secret in logs, enforced by review and by the logging rules |
| [🎲 R-03](12-risks.md#r-03) Safety tick budget missed | The budget is only met if every tick is measured from the start | The benchmark gate of T0.07 runs on every pull request from S02, before the safety code exists |
| [🎲 R-13](12-risks.md#r-13) Browser API gaps for full web Ground control | Ground control must be full in the web browser too | The shell of T0.14 and the map of T0.19 are built for the browser first and wrapped by Tauri, so any gap shows from S03 |

## <a id="work-split"></a>🧑‍💻 Work split

**The person**

- **S01, alone with one agent at a time:** writes the ticket template, the agent definitions and the hooks with Claude Code, and tests the harness on T0.03 to T0.05 before trusting it.
- **Reviews from S02:** about 5 tickets per sprint, one branch each, starting from the reviewer agent's note; line by line for identity, isolation and the Simulator's isolation (T0.09, T0.11, T0.12, T0.13), on tests and screens for the rest.
- **Decisions:** the agent definitions and their limits (what an agent may change without asking), the Terraform module layout and where its state is kept, the k3s machines of the dev cell, Vault or OpenBao, the sample data of the walking skeleton.
- **Outside the code:** operator registration ([🏛️ G-01](09-regulatory-track.md#g-01)) and the preparation of the EU A2 certificate ([🏛️ G-02](09-regulatory-track.md#g-02)); ordering the X500 Drones of [🤝 H-01](11-hardware-and-partners.md#h-01) for delivery in S06.

**The agents, in parallel**

- **S02:** models and generated types, the Rust core, the dev cell charts, NATS and the image pipeline are five independent tickets, each split again into tasks (for T0.08: database chart, Valkey and MinIO charts, vault, Argo CD application, ephemeral cell script).
- **S03:** Keycloak and the gateway, the service skeletons, the Simulator, the front-end packages and the languages run side by side; the interfaces between them (token claims, `Event`, `SquadFrame`) are fixed in the tickets first.
- **S04:** UC-029, observability, the flight engine skeleton, the map and the visual tests; translations in four languages, mock-up checks and technical page updates run alongside every ticket.

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ Roadmap](README.md) · 📄 **Page 96 / 109** · [P1: First flight ▶️](02-p1-first-flight.md)
<!-- /spec:nav-bottom -->
