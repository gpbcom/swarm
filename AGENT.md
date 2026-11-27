# AGENT.md

How code is written in Swarm. See `README.md` for what it does and how to use it.

When you edit a file, follow these rules even where a neighbouring file does not.

## Commands

Run every command from the repository root unless it says otherwise.

```bash
uv sync
uv run ruff check backend scripts tests
uv run ruff format <the files you edited>
uv run mypy
uv run pytest tests/swarm_<module>/<folder> -n 2
```

`uv run mypy` checks every `src/` folder of `backend/` and `scripts/`, listed in the root `pyproject.toml`; give it one
folder, such as `uv run mypy backend/apps/gateway/src`, to check only that one.

The operations are argument-free scripts of `scripts/` (see [Layout](#layout)):

```bash
uv run swarm-schemas-export
uv run swarm-schemas-check
uv run swarm-openapi-export
uv run swarm-openapi-check
uv run swarm-migrations-migrate
uv run swarm-i18n-check
```

- `swarm-schemas-export` writes `backend/swarm-models/schemas/swarm_models.schema.json`, and `swarm-schemas-check`
  checks it is current.
- `swarm-openapi-export` writes `frontend/packages/api-client/openapi/<app>.json` for every app of `backend/apps/`, or
  for the one the environment entry `SWARM_APP` names, and `swarm-openapi-check` checks they are current.
- `swarm-migrations-migrate` applies the migrations of every app that owns a PostgreSQL schema, or of the one
  `SWARM_APP` names. The DSN of an app is read from the environment entry `SWARM_<APP>_POSTGRES_DSN`. In an image,
  `SWARM_APP` and `SWARM_APP_ROOT` already name its app and its folder, so a job runs the same image with the
  entrypoint `swarm-migrations-migrate`.
- `swarm-i18n-check` fails when a Python message lacks one of the four languages (English, French, German and
  Spanish). It reads the catalogues shipped with `swarm_storage`, or the folder the environment entry
  `SWARM_I18N_LOCALES` names. `pnpm --filter ./frontend/packages/i18n run check-messages` does the same for the
  FormatJS messages of `frontend/packages/i18n/src/messages/`.

Each app runs with its console script `swarm-<app>-serve` (`swarm-gateway-serve`, `swarm-fleet-serve`,
`swarm-missions-serve`, `swarm-simulator-serve`, `swarm-flight-engine-serve`), which takes no argument.

For a front end or a TypeScript package, run its scripts from the root with the pnpm filter of its name,
`pnpm --filter @swarm/<project> test|lint|typecheck|build`, for example `pnpm --filter @swarm/ground-control test`. The
desktop shell is built from the root with `pnpm --filter @swarm/desktop tauri build --no-bundle`. In
`frontend/apps/desktop/src-tauri`, which is its own Cargo workspace, run `cargo fmt --check` and
`cargo clippy --all-targets --locked -- -D warnings`.

To build the image of an app locally, run this from the repository root, because the build context is the root:

```bash
docker build -f backend/apps/<app>/Dockerfile -t <name>:local .
```

The Playwright tests of the Back office run against its image, from the root:

```bash
docker build -f frontend/apps/back-office/Dockerfile -t ghcr.io/gpbcom/swarm/back-office:local .
SWARM_IMAGE_TAG=local pnpm --filter @swarm/back-office run e2e
SWARM_IMAGE_TAG=local pnpm --filter @swarm/back-office run capture
```

To run the Playwright suite of `qa/e2e` against the images of a pipeline run, give the tag of those images:

```bash
SWARM_IMAGE_TAG=<tag> pnpm --filter ./qa/e2e run e2e
```

The end-to-end test of Ground control runs against its own image the same way. It starts the ground-control service of
`infra/compose/e2e.yaml` (port 8180) and feeds it a stand-in live socket:

```bash
SWARM_IMAGE_TAG=<tag> pnpm --filter @swarm/ground-control run e2e
```

Ground control reads its runtime configuration from `config.json`, beside `index.html`: the live URL, the Mission, the
tiles, the metrics endpoint, the cell, and the edge or cell path. The image serves the PMTiles files from `/tiles/`,
mounted by the deployment. The Grafana dashboards sit in `infra/charts/observability/dashboards/`, the first one being
the Telemetry latency.

For Rust (`rust/`, a Cargo workspace whose crates opt in to the workspace lints with `[lints] workspace = true`)
and TypeScript (`frontend/packages`, a pnpm workspace), run these from their workspace folder:

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
pnpm -r --if-present lint
pnpm -r --if-present typecheck
```

Run `cargo bench --workspace --bench '*'` from `rust/` to run the criterion benchmarks, and build the
`swarm_core` wheel with:

```bash
uv run maturin build --release --manifest-path rust/swarm-core/python/Cargo.toml --out dist
```

TypeScript packages and front ends extend `@swarm/config` (`frontend/packages/config`), which holds the strict
`tsconfig.base.json` and the eslint configuration.

After any change to a shared model of `backend/swarm-models`, regenerate the generated types in this order:

```bash
uv run swarm-schemas-export
cargo run -p swarm-models-codegen
pnpm --filter ./frontend/packages/live run generate
```

- `cargo run -p swarm-models-codegen`, run in `rust/`, writes `rust/swarm-models/src/generated.rs`.
- `pnpm --filter ./frontend/packages/live run generate` writes `frontend/packages/live/src/generated/models.ts`.

After any change to the routes of an app, regenerate the REST contract:

```bash
uv run swarm-openapi-export
pnpm --filter ./frontend/packages/api-client run generate
```

- `pnpm --filter ./frontend/packages/api-client run generate` writes the TypeScript client from the documents of
  `frontend/packages/api-client/openapi/`.
- CI checks both: the tests of `tests/scripts/openapi/` compare each published document with its app, and the `test`
  script of `frontend/packages/api-client` runs `generate.ts --check`.

CI:

- `.github/workflows/ci.yml` runs on every push and pull request.
- Its first job runs `.github/scripts/detect_changes.py`, which selects the apps, front ends and packages that
  changed. It prints six lines, including `images`, the JSON array of the image folders to build.
- Then the reusable workflows `python.yml`, `rust.yml`, `typescript.yml` and `specs.yml` run the checks of this section
  for what was selected:
  - for each selected app of `backend/apps/`: `ruff check`, `ruff format --check`, `mypy` on its `src`, and `pytest` on
    its tests and those of the domains it lists;
  - the job of an app installs the pinned nats-server, and builds and installs the `swarm_core` wheel when the app's
    code (its `main()` and its domains) imports it;
  - the `repository` job of `python.yml` also builds and installs the `swarm_core` wheel, and runs every test under
    `tests/`;
  - another job of `python.yml` runs ruff and mypy on `backend` and `scripts`, `swarm-schemas-check` and
    `swarm-i18n-check`;
  - for Rust: `cargo fmt`, `clippy` and `cargo test`;
    - `rust.yml` has a `bench` job that runs only on pull requests, after `check`. It saves criterion benchmarks of the
      base commit as the baseline `pr-base`, runs them on the pull request, and `.github/scripts/bench_gate.py` fails
      the build when a benchmark's mean is more than 5 % slower;
  - for each TypeScript project: its `lint`, `typecheck` and `test` scripts, and its `check-messages` script when it
    has one;
  - `specs.py check`.
- After step 2, `.github/workflows/images.yml` runs for the selected images, and each step must pass before the next:
  - OSV-Scanner scans the lock files `uv.lock`, `pnpm-lock.yaml` and `rust/Cargo.lock`;
  - the image is built from its `Dockerfile` with the gha remote cache, under the run tag `run-<id>-<attempt>`;
  - Trivy fails the build on a fixable HIGH or CRITICAL vulnerability, then writes the CycloneDX SBOM, kept as an artifact;
  - the run tag is pushed to `ghcr.io/gpbcom/swarm/<name>`;
  - the image is signed with keyless cosign, its SBOM is attached as an attestation, and the signature is verified;
  - Playwright runs through `infra/compose/e2e.yaml` against those images, and the HTML report is uploaded when a test fails;
  - the commit SHA tag is added only on pushes to `develop` and `master`, to the same digest, and its signature is verified.
- All of them must pass.
- `.github/workflows/terraform.yml` still checks `infra/terraform/` on its own. `.github/workflows/dev-cell.yml` creates
  a branch's dev cell on demand and destroys it when the branch is deleted.
- Run tests one file or one folder at a time.
- Format only the files you edited, never a whole folder.

## Layout

The backend is made of layers, each one a package, with the domains as folders inside them, a kernel of libraries, and
one thin app per image. The operations are scripts, and the tests sit in one central folder.

| Path | Holds |
| --- | --- |
| `backend/libs/<lib>/` | The kernel: `swarm-lifecycle`, `swarm-logging`, `swarm-catalog`, `swarm-nats` (the connector), `swarm-web` (the app builder, the server runnable, the entity tags). Its models, enums and exceptions sit in each library's `models/` |
| `backend/swarm-models/` | Layer 0, `swarm_models`: every Pydantic model, enum and exception, by concept (`swarm_models/<concept>/`), its enums in `swarm_models/enums.py`, and each app's configuration in `swarm_models/config/<app>/`. They only load and validate, and never log |
| `backend/swarm-storage/` | Layer 1, `swarm_storage`: reading and writing data, and nothing else. One repository per entity, a folder per domain and a `shared/` folder |
| `backend/swarm-clients/` | Layer 1, `swarm_clients`: calls to other apps and to external systems, one client per remote system, a folder per domain and a `shared/` folder |
| `backend/swarm-service/` | Layer 2, `swarm_service`: the business rules and every runnable (bus responders and consumers included), a folder per domain and a `shared/` folder |
| `backend/swarm-api/` | Layer 3, `swarm_api`: the FastAPI endpoints only (see below), with the routers in `swarm_api/v1/<domain>/` |
| `backend/apps/<app>/` | Layer 4: one image each, with its `Dockerfile`, `pyproject.toml`, `conf/`, `migrations/` when it owns a PostgreSQL schema, and `src/swarm_<app>/main.py`; `[tool.swarm] domains` lists the domains it owns |
| `backend/apps/<app>/conf/` | `app.yaml`, the configuration with every default written out; `logger.yaml`, the logging (coloured console and coloured rotating file, written to `logs/`); `catalogs/`, data that would otherwise be hard-coded |
| `scripts/` | The operations, in `scripts/src/swarm_scripts/<area>/`, run with `uv run swarm-<area>-<action>` and taking no arguments: OpenAPI export and check, migrations, schema export and check, the message check |
| `tests/swarm_<module>/` | The Python tests, mirroring each package's import path; `tests/scripts/` for the scripts, `tests/fakes/` for the stand-ins |
| `docs/` | The `specs/` (functional and technical), the `research/`, the `tickets/` and the `releases/` |

In this file, `src/` means the `src/` folder of any package of `backend/` or `scripts/`, and `models` means
`swarm_models` and the `models/` folder of a kernel library.

**The layers.** Each layer only calls the ones below it: `swarm_api` calls `swarm_service`, and `swarm_service` calls
`swarm_storage` and `swarm_clients`. All of them import `swarm_models`, which imports none of them. `swarm_api` never
imports `swarm_storage` or `swarm_clients`, `swarm_storage` and `swarm_clients` never import each other, and no layer
imports one above it. Every endpoint lives in `swarm_api`, every business rule in `swarm_service`.

**The api layer holds only endpoints.** `swarm_api` holds FastAPI endpoints and their versioned routers (`/v1/...`),
their `Depends` providers (`swarm_api/dependencies/`; a class whose `__call__` takes a request or a WebSocket counts as
one), the middlewares (`swarm_api/middleware/`), the exception handlers (`swarm_api/handlers/`) and the `/v1/live`
WebSocket endpoint (`swarm_api/v1/live/`). Anything that exposes no endpoint (a command, a factory, a runnable, a bus
handler, the server runner, the app builder) belongs to the service layer or to the kernel.

**No command line in the product.** `backend/` and `scripts/` never import `argparse`, `click` or `typer`, never read
`sys.argv`, and hold no folder or module named `cli` or `commands`. An app's `main()` reads its `conf/app.yaml` and its
environment, then runs. Only the harness (`.claude/`) and CI (`.github/`) keep command lines.

**`scripts/` holds the operations.** OpenAPI generation and checking, migrations, the schema export and check and the
message check are Python scripts in `scripts/src/swarm_scripts/<area>/`, exposed as `uv run swarm-<area>-<action>`,
taking no arguments: a script covers every app, or the one named by the environment entry `SWARM_APP`.

**One class per entity per layer.** Within a layer, an entity has exactly one responsible class: one `<Entity>Repository`
in storage, one `<Entity>Client` in clients, one `<Entity>Service` in service, one `<Entity>Router` in api. Classes that
split one entity's work in the same layer are merged. Factories and exceptions keep their own files.

**Package imports.** Each package imports only these first-party packages:

| Package | May import |
| --- | --- |
| The kernel (`backend/libs/`) | The kernel only |
| `swarm_models` | Itself, `swarm_catalog`, `swarm_lifecycle`, and the models of `swarm_web` and `swarm_nats` (`swarm_web.models`, `swarm_nats.models`). Never `swarm_logging` |
| `swarm_storage`, `swarm_clients` | Itself, `swarm_models` and the kernel |
| `swarm_service` | Itself, `swarm_storage`, `swarm_clients`, `swarm_models` and the kernel |
| `swarm_api` | Itself, `swarm_service`, `swarm_models`, `swarm_web` and the rest of the kernel |
| `swarm_<app>` | `swarm_api`, `swarm_service`, `swarm_web`, `swarm_models.config.<app>` and `swarm_logging` |
| `scripts/` | `swarm_service`, `swarm_api`, `swarm_web`, `swarm_models` and the kernel |

**Domains are owned.** Inside these rules, `swarm_service.<d>` uses only `swarm_storage.<d>`, `swarm_clients.<d>` or
the `shared` folders, each domain has exactly one owning app, and an app wires only the domains of its `[tool.swarm]
domains`.

## Mono-repo

Swarm is a mono-repo of backend apps and front ends, each with its own Docker image. The tests in
`tests/conventions/mono_repo/` enforce part of this section: the uv workspace, the Cargo and pnpm workspaces, and the
Terraform layout. The CI/CD change detection and check workflows are tested by `tests/ci/`. The Dockerfiles are tested
by `tests/infra/images/`, and `infra/compose/e2e.yaml` by `tests/ci/e2e/`.
`tests/conventions/mono_repo/frontend/` checks the front-end workspace layout and the desktop shell, and the Docker
rules of the front ends are not tested yet. `tests/infra/` checks the charts, the dev environment, the PostgreSQL image
and the dev-cell script, and `tests/ci/dev_cell/` checks the dev-cell workflow.

| Path | Holds |
| --- | --- |
| `pyproject.toml` | The uv workspace root (`backend/libs/*`, `backend/swarm-*`, `backend/apps/*` and `scripts`), with one `uv.lock` for the whole repository |
| `backend/` | The kernel, the layer packages and the apps of [Layout](#layout); see `backend/README.md` |
| `scripts/` | The operations; see `scripts/README.md` |
| `frontend/apps/<frontend>/` | One front end: its `Dockerfile`, `src/`, and its Playwright tests in `e2e/` |
| `frontend/packages/` | The shared TypeScript packages, a pnpm workspace |
| `rust/` | The Cargo workspace: the Rust core and its PyO3 bindings, the generated models and the synthetic Drones |
| `qa/e2e/` | The shared Playwright configuration and the suite that checks the images; see `qa/README.md` |
| `infra/terraform/` | The Terraform modules per provider and building block, and one root per cell |
| `infra/charts/` | The Helm charts, one per building block of a cell, and the `cell` umbrella chart |
| `infra/environments/` | The desired state of each environment that Argo CD applies |
| `infra/images/` | The images that are not an app or a front end, such as the PostgreSQL image |
| `infra/scripts/` | The scripts that request and close a branch's dev cell |
| `infra/compose/e2e.yaml` | Starts the real images for Playwright |
| `tests/conventions/` | The [rules a test enforces](#rules-a-test-enforces) |
| `.github/workflows/` | The CI/CD pipeline |
| `.github/scripts/` | The scripts the pipeline runs, such as change detection |

The front-end packages of `frontend/packages/` are `frontend/packages/tokens` (`@swarm/tokens`), whose `src/tokens.css` is generated by
`specs.py build` from `docs/specs/visual-identity.md` and never edited by hand; and `frontend/packages/ui` (`@swarm/ui`), the components on
Radix primitives, styled with `var(--...)` tokens only and using the class names of the mock-ups' `components.css`. The
frames of each part of Swarm sit in `frontend/packages/ui/src/frames/`, and `frontend/packages/ui/src/frames/parts.ts` holds their message ids, whose words are in the catalogues of `@swarm/i18n`.
`frontend/packages/live` (`@swarm/live`) holds the generated models, the MessagePack protocol, and the Web Worker that owns
the live socket and posts typed-array snapshots at most 30 times a second to the main thread, where `LiveClient` reads
them; it also holds the `Telemetry` latency histograms, exported as OTLP/HTTP JSON. `frontend/packages/maps` (`@swarm/maps`)
holds the MapLibre base style on self-hosted PMTiles, and the deck.gl Drone layer, with binary attributes, and the
`SquadMap` component, coloured from the tokens.
The four app shells are `frontend/apps/ground-control`, `frontend/apps/mission-studio`, `frontend/apps/back-office` and
`frontend/apps/client-portal`. `frontend/apps/desktop` (`@swarm/desktop`) is the Tauri 2 shell that wraps Ground control and
Mission studio. Its Rust code is in `src-tauri/`, a Cargo workspace of its own, and `.github/workflows/desktop.yml`
builds it on Windows, macOS and Linux.

The Rust core is `rust/swarm-core/`. It holds the crates `safety`, `planner` and `mavlink` (`swarm-core-safety`,
`swarm-core-planner`, `swarm-core-mavlink`), each with its criterion benchmark in `benches/`. It also holds the PyO3
bindings `swarm-core/python` (Python module `swarm_core`, which releases the GIL), built as a wheel by maturin. The
bindings are not a uv workspace member, so `uv sync` never builds Rust. `tests/rust/swarm_core/` checks the layout and
imports the functions from a wheel it builds.

`rust/swarm-synthetic-drones/` is a workspace crate outside `swarm-core`. It is a library (the route follower and
the MAVLink state machine) and a binary, `swarm-synthetic-drones`, which flies up to 255 synthetic Drones per process
over UDP MAVLink 2, for example `cargo run -p swarm-synthetic-drones -- --count 10`. Its criterion benchmark is `step`.

**The apps.** The apps `gateway`, `fleet`, `missions`, `simulator` and `flight-engine` sit in `backend/apps/<app>/`,
each with one console script, `swarm-<app>-serve`, whose argument-free `main()` reads `conf/app.yaml` in the folder
`SWARM_APP_ROOT` names (the current one without it), configures logging and serves the app; a relative path of the
configuration is read in that folder. Their routes, services, clients and models sit in the layer packages, under the
domain the app lists in `[tool.swarm] domains`: `simulation` for the simulator and `flight` for the flight engine, the
others under their own name. The apps `gateway`, `missions` and `fleet` each have their own PostgreSQL schema and their
Alembic migrations in `backend/apps/<app>/migrations/`, outside `src/` because Alembic needs module-level functions.

`backend/apps/simulator/` is the simulator app, of the `simulation` domain. It has no command line: `swarm-simulator-serve`
reads `conf/app.yaml` and serves `POST /v1/simulations`, whose body names the Mission and which answers `202 Accepted`
with the Drones that fly, then flies the Squad of `conf/catalogs/simulated_squad.yaml` on a square route in the
background (`409 Conflict` while a flight flies). In the background of its application it also answers Commands on
NATS, and it refuses to start without simulated credentials. Its adapter registry holds only simulated Drones, and its
Flight log, in SQLite, is marked simulated
([📏 BR-014](docs/specs/functional/business-rules/BR-014-simulation-isolation.md)). Its acceptance tests are in
`tests/swarm_simulator/main/`. They need cargo and `nats-server`, and for PX4, docker with the image built by
`docker build -f infra/images/px4-sitl/Dockerfile -t swarm-px4-sitl:local .`. They skip without them.

The flight engine app (`backend/apps/flight-engine`, of the `flight` domain) imports `swarm_core`, through the MAVLink
listener of `swarm_clients/flight/mavlink/`, from the wheel built from `rust/swarm-core/python`, not from the uv
workspace. After `uv sync`, build and install it with:

```bash
uv run maturin build --release --manifest-path rust/swarm-core/python/Cargo.toml --out dist
uv pip install --no-deps dist/swarm_core-*.whl
```

`uv sync` removes it again, so run these two commands after every sync. Tests that need the wheel skip without it, as the
NATS tests skip without nats-server. mypy reads `rust/swarm-core/python/swarm_core.pyi` through the root
`mypy_path`.

**The kernel.** The libraries of `backend/libs/` are `swarm-lifecycle` (`swarm_lifecycle`), with Runnable,
AsyncRunnable and the abstract factories; `swarm-logging` (`swarm_logging`), with the logging configuration;
`swarm-catalog` (`swarm_catalog`), with YamlCatalog; `swarm-nats` (`swarm_nats`), the NATS connector with its
configuration, the message headers and the bus errors; and `swarm-web` (`swarm_web`), the FastAPI app builder, the
uvicorn server runnable, the runner that drives an `AsyncRunnable` from synchronous code (`swarm_web.runners`), `ETag`
and `If-Match`, with the REST configuration and the REST errors. Their tests are in `tests/swarm_<module>/`.

**Shared NATS and REST code** sits in the layer packages:

- the JetStream admin, the event publisher, request-reply with deadlines and idempotency keys, and the account
  resolver client are in `swarm_clients/shared/nats/`;
- the AsyncRunnable responder and durable consumer, with their factories, are in `swarm_service/shared/bus/`, and
  the issuers of the NATS operator, of the per-Operator accounts and of the credentials (service, edge, simulated,
  system) in `swarm_service/shared/accounts/`;
- the `problem+json` handlers are in `swarm_api/handlers/` and the `Idempotency-Key` middleware in
  `swarm_api/middleware/`, with its service in `swarm_service/shared/idempotency/` and its store in
  `swarm_storage/shared/idempotency/`;
- their models are in `swarm_models`: `accounts/`, `streams/`, `subjects/`, `config/nats/`, `rest/problems/` and
  `rest/idempotency/`, and their enums in `swarm_models/enums.py`.

The NATS tests need a nats-server binary on PATH and skip without it, and CI installs a pinned one; their fixtures
are in `tests/conftest.py`. An app's router of `swarm_api/v1/<domain>/` builds its application with
`ProblemHandlers.application` of `swarm_api`, which hands the problem model to `swarm_web`'s `RestAppBuilder`, then
installs the idempotency middleware.

**Messages.** The Babel catalogues of Python messages, in English, French, German and Spanish, are package data of the
storage layer, in `swarm_storage/shared/i18n/locales/` (`swarm.pot` and `<en|fr|de|es>/LC_MESSAGES/swarm.po`), read
by its `PoCatalogStore`. `swarm_service/shared/i18n/` holds `Translator`, which gives a message in a person's language,
and the `CatalogChecker` of `uv run swarm-i18n-check`. Their models are in `swarm_models/i18n/`, and `Language` and
`MessageProblem` in `swarm_models/enums.py`.

**PostgreSQL.** `swarm_storage/shared/postgres/` holds the PostgreSQL pool, the unit of work that sets
`swarm.operator_id` on each transaction for row-level security, the `PostgresRepository` base and the outbox
repository, the row-level security and outbox DDL, and the Alembic migrator.

**Live.** The live fan-out shared by the gateway and the flight engine is in `swarm_service/shared/live/`: the one-slot
mailbox and the hub (`hub/`), the live sources (`sources/`), the MessagePack codec, and the `LiveSession`
AsyncRunnable, built by its factory, behind the `/v1/live` socket of `swarm_api/v1/live/`. Its errors are in
`swarm_models/live/exceptions/`.

The Python rules in this file apply to `backend/` and `scripts/`, and to the central `tests/`. The front ends use React
and TypeScript with a Tauri desktop shell, images go to GHCR, and Argo CD deploys them; see `docs/specs/technical/`.

**Shared models**

- **The models:** every Pydantic model lives in `backend/swarm-models`, under `swarm_models/<concept>/`, or in the
  `models/` of a kernel library, and nothing redefines one.
- **The single source:** the JSON Schema bundle, the Rust structs and the TypeScript types are generated from those
  models, and are never edited by hand.
- **The CI checks:** CI fails when one of them is stale. Three checks enforce it:
  - `python.yml` runs `swarm-schemas-check`;
  - `cargo test` runs `generated_is_current` in `rust/swarm-models`;
  - the `test` script of `frontend/packages/live` runs `generate.ts --check`.

**Apps and packages**

- NEVER add a top-level `api`, `service`, `storage`, `clients` or `models` package. The packages share one uv
  environment, so they would overwrite each other: the layers are `swarm_api`, `swarm_service`, `swarm_storage`,
  `swarm_clients` and `swarm_models`.
- An app never imports another app. The code apps share sits in the layers and the kernel, by domain or in `shared/`.
- Adding an app or a domain must not need a change to `tests/conventions/`, so that its rules cover new code
  automatically.

**Docker images**

- Each app and front end has exactly one image, built by a multi-stage `Dockerfile` in its own folder.
- The build context is the repository root, because the shared `uv.lock` is there.
- Images are pushed to `ghcr.io/gpbcom/swarm/<name>`, and each one is signed with keyless cosign.
- The dev cell refuses an unsigned `ghcr.io/gpbcom/swarm/**` image: the Sigstore policy-controller admits only images
  signed by the `images.yml` workflow, and `infra/scripts/dev-cell.sh up` checks that it refuses an unsigned image.

**Front-end tests**

- Front-end tests use Playwright, and live in `frontend/apps/<frontend>/e2e/`.
- They run against the real images started by `infra/compose/e2e.yaml`, never a development server, so that they test what
  ships.
- The shared Playwright configuration is `@swarm/e2e` in `qa/e2e`. It refuses a `webServer`, and it needs
  `SWARM_IMAGE_TAG`, the tag of the images to test.
- The visual tests compare each screen with its PNG of `docs/specs/screens` in light and dark mode, and a capture
  replaces a mock-up with the screen the application shows: see [`qa/README.md`](qa/README.md#visual-tests-and-the-capture-of-screens).

**CI/CD**

Each step must pass before the next one starts:

1. Detect what changed, and run jobs only for those apps, front ends and packages. A change in the kernel, `scripts/`,
   `rust/`, `frontend/packages/`, `qa/e2e/`, a lock file (`uv.lock`, `Cargo.lock`, `pnpm-lock.yaml`), a root workspace
   file or the pipeline itself runs all of them; a change in a layer package runs the apps that own its domain, and a
   change in its `shared/` folder runs them all.
2. Run `ruff check`, `ruff format --check`, `mypy` and `pytest` for each changed app; `cargo fmt`, `clippy` and
   `cargo test` for Rust, and `cargo bench` with the 5 % gate on pull requests; eslint, `tsc` and Vitest for
   TypeScript; and `specs.py check`.
3. Build each changed image.
4. Run Playwright against those images, and upload the HTML report if a test fails.
5. Publish the images tagged with the commit SHA, from `develop` or `master` only.

## Rules a test enforces

`tests/conventions/` fails on any of these, in `src/` and `tests/` unless stated. Each rule is one class in
`tests/conventions/rules/`, and the environment variable `SWARM_CONVENTIONS_BACKEND_ROOT` runs the tests against another
repository root.

`tests/conventions/backend/test_backend_conventions.py` runs the code rules against every package of `backend/` and
`scripts/` (the kernel libraries, the layer packages, the apps and the scripts), and against the central tests of the
backend (`tests/swarm_*`, `tests/scripts` and `tests/fakes`): more than one top-level class in a file; more than five
Python files in a folder; a nested function; `Any`; the lifecycle rule (`start` or `stop`, or `run` without a
lifecycle base class); a Pydantic model outside `models`; a module docstring; an import outside its group
(`tests/conventions/imports/` also checks the root `tests/`); and a logger handed to a new object or to
`super().__init__`, checked in `src/` only. The lifecycle rule accepts the definitions of `Runnable` and
`AsyncRunnable` themselves. `@staticmethod`, attributes starting with an underscore and the node rules are not tested
yet.

The same file runs the rules of [Layout](#layout): the package import table (`PackageImports`), the dependencies each
layer package declares (`PackageDependencies`), domain ownership (`DomainOwnership`), thin apps (`ThinApp`), the tests
mirror (`TestsMirror`), unique test base names (`UniqueTestBasenames`) and no `Path(__file__).parents[N]` lookup
(`NoFileDepthPath`). `tests/conventions/backend/test_layout_rules.py` runs the api layer holding only endpoints
(`ApiOnlyEndpoints`), no command line (`NoCommandLine`) and one class per entity per layer (`OneClassPerEntity`) on
`backend/` and `scripts/`.

- More than one top-level class in a file, whatever the kind of class, except several enums in an `enums.py`.
- More than five Python files in a folder, not counting `__init__.py` and `conftest.py`. The rule of [File shape](#file-shape)
  also counts JavaScript, TypeScript and Rust files, in every folder of the repository, checked by
  `tests/conventions/repository/test_five_code_files.py`.
- A nested function.
- `@staticmethod`. Use an instance method or a `@classmethod`.
- `Any`. See [Typing](#typing).
- An attribute starting with an underscore: `self.process`, never `self._process`. Methods may start with one. The only
  exception is a name a third-party protocol owns, listed in `tests/conventions/helpers.py`.
- An import that the package import table of [Layout](#layout) does not allow, checked in `src/` only.
- A Pydantic model outside `models`.
- A class outside `models` with `start` or `stop`, or with `run` but no lifecycle base class.
- A node without `__call__`, or with `run`.
- A file that starts with a docstring (a module docstring).
- An import outside the group of its kind, a group without its comment, or groups out of order (`src/` and `tests/`,
  except `__init__.py`).
- A call in `src/` that hands a logger to a new object or to `super().__init__` (`logger=`, `self.logger`,
  `getLogger(...)`).
- In `backend/` and `scripts/`: an endpoint-less class in `swarm_api`, a command line, or two classes for one entity in
  one layer.

## File shape

**NEVER more than one class in one file, whatever the kind of class.** It covers Pydantic models, `TypedDict`,
exceptions, helpers and test classes, in `src/` and in `tests/`. Each class has its own file, named after the class:
`CustomerService` in `customer_service.py`, `CustomerModel` in `customer_model.py`. **The one exception is the enums:**
all the enums of a module sit together in its `enums.py` (see [Data and enums](#data-and-enums)), which holds
nothing else.

**Classes that share a method name share a base class.** `TaskNode` has `__call__`, and `YamlCatalog` has `load`. If two
methods only happen to share a name and mean different things, rename one instead.

**NEVER more than five code files in one folder,** whatever their language: Python, JavaScript, TypeScript and Rust
together (`.py`, `.js`, `.jsx`, `.mjs`, `.cjs`, `.ts`, `.tsx`, `.rs`). When a folder would go past five, create sub-folders
and dispatch its files by entity type or by theme: `swarm_storage/customers/repositories/` for the repositories,
`swarm_models/customers/exceptions/` for the exceptions, `.claude/scripts/tickets/` for the ticket scripts. This applies to every
folder of the repository: `backend/`, `scripts/` and `tests/`, `frontend/apps/`, `frontend/packages/`, `rust/`,
the harness under `.claude/` and the CI scripts, including `exceptions/` folders. The entry files of a folder do not count
towards the five: `__init__.py` and `conftest.py`, `index.ts` and `index.js`, and Rust's `lib.rs`, `main.rs` and `mod.rs`.

An `exceptions/` package's `__init__.py` re-exports everything under it, so callers keep importing from the package. Other code is imported by its full path: `from swarm_service.customers.customer_service import CustomerService`.

Nothing else sits at module level, so there are no module constants, helper functions or module-level loggers. The
exceptions are a `main()` for a console script and `__all__`. Constants become `ClassVar` attributes in `UPPER_CASE`,
above the constructor.

**NEVER declare a dict with hard-coded keys inside a method or function,** in `src/` and in `tests/`, whether a literal
(`{"level": ...}`) or a `dict(level=...)` call. A dict whose keys and values are fixed is an `UPPER_CASE` `ClassVar`
(`JSON_FORMATTER_ENTRY: ClassVar[Dict[str, str]] = {...}`), copied before a method changes it. When the values are
computed at run time, the keys are `UPPER_CASE` `ClassVar[str]` constants (`TIME_KEY: ClassVar[str] = "time"`) and the
method builds `{self.TIME_KEY: ...}`. In a test `helpers.py` made of functions, the constants sit at module level.

Inside a class, the order is: constants and fields, `__init__`, validators, then these two banners. Leave out a banner
whose section would be empty.

```python
    ############################
    # Internal Helpers Methods #
    ############################

    def _active_customers(self, customers: List[Customer]) -> List[Customer]: ...

    ############################
    # Publicly Exposed Methods #
    ############################

    def create(self, customer: Customer) -> Customer: ...
```

`@property` and `@classmethod` constructors such as `load` are public, so they go under the second banner.

A task graph node subclasses `TaskNode`, and its work is in `async def __call__(self, state)`, never a `run` method. The
graph adds the instance itself: `graph.add_node(NodeName.CHECK.value, self.check)`. `__call__` goes under the second
banner.

## Lifecycle and factories

Every runnable class except the nodes subclasses `Runnable` or `AsyncRunnable`, and has exactly these methods:

| Method | Does |
| --- | --- |
| `initialize()` | Acquires what the work needs. A service is already serving when it returns |
| `run()` | Does the work. A service blocks here until it is closed, and a job returns when it is done |
| `close()` | Releases everything, and must be safe after a failed or partial `initialize` |

- `execute()` on the base class calls all three, and closes whatever happens. Use it unless something runs alongside.
  On an `AsyncRunnable` it is an async generator: read it with `async for status in runnable.execute()`.
- They take no arguments. Inputs go to the constructor, and results are read from attributes afterwards, such as
  `SchemaMigration.exit_code`.
- Runnables are created by a factory in the `factories/` package of their domain, with sub-folders by theme:
  `SquadFlightFactory` in `swarm_service/simulation/factories/flights/`, `RestServerFactory` in
  `swarm_web/factories/`. Do not call a runnable's constructor in `src/` outside a factory.
- The base classes are `swarm_lifecycle.runnables.runnable.Runnable` and `swarm_lifecycle.runnables.async_runnable.AsyncRunnable`.
  A subclass calls `super().__init__()`, or `super().__init__(config.status_interval_s)` for an `AsyncRunnable`, with
  no logger, then sets its own `self.logger = logger if logger else getLogger(__name__)`.
- An abstract factory of a layer subclasses `swarm_lifecycle.factories.runnable_factory.RunnableFactory[...]` or
  `swarm_lifecycle.factories.async_runnable_factory.AsyncRunnableFactory[...]`. A concrete factory implements `_build()`,
  and callers call `create()`.
- **A long-running async task ALWAYS yields its status.** All async work that can last runs in an `AsyncRunnable`,
  never in a bare coroutine or task, and its `execute()` is an async generator of `RunnableStatus`, a `StrEnum` of
  `swarm_lifecycle.models.enums`: it yields `INITIALISING` or `RUNNING` every `status_interval_s` while the work goes
  on, then `EXECUTED` when the work succeeds, and `runnable.status` holds the current one. Each status is also logged
  at `INFO` with the time elapsed. When the caller stops reading, the work is cancelled and `close` still runs. `status_interval_s` is a required
  constructor argument taken from the runnable's configuration (with its default written out in `conf/app.yaml`),
  and a value that is not a positive number raises `SEAsyncRunnableInvalidStatusIntervalError`.

## Imports

`from __future__ import annotations` comes first in every non-empty file: a file never starts with a docstring
(see [Docstrings and comments](#docstrings-and-comments)).
Then come up to three groups, **in this order, each under its own comment, and each import in its own group**:

```python
from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import List, Optional

# Third-party imports
import yaml

# First-party imports
from swarm_models.customers.exceptions import SECustomerCatalogUnreadable
```

- Imports are absolute, at the top of the file, never inside a function.
- Import exceptions from their package (`swarm_models.customers.exceptions`), not from the file that defines them.
- **Every module of `src/` and `tests/` has its groups,** exception files and test files included. Only `__init__.py`
  files, which only re-export, have none. A group with no import is left out with its comment.
- **An import sits in the group of what it imports,** whatever ruff's isort thinks: the standard library, a third-party
  distribution, or the repository's own code (a package of `backend/` or `scripts/`, `tests`, or a name of
  `known-first-party`). Where isort would move an import into another group, it stays in its AGENT.md group, marked
  `# isort: skip` on its line. Adding the module to `known-first-party` in `pyproject.toml` is better when it is
  first-party code.

## Typing

- Annotate every signature, including `-> None`.
- Use `Optional`, `List`, `Dict`, `Tuple`, `Set` and `Union` from `typing`, not `X | None` or `list[str]`.
- Use `JsonValue` for raw input in validators.
- **NEVER `Any` or `object` as a type,** in a signature, a variable, a generic parameter or a `cast`: both are too
  generic. Write the real type instead: `JsonValue` (from `pydantic`) for parsed JSON, YAML or TOML, a `Union` for a
  value with several known types, a `Callable[...]` with its real signature, a generic with its real parameter
  (`Factory[Runnable]`, never `Factory[object]`).

## Naming

- Exceptions start with `SE` (see [Exceptions](#exceptions)). Other classes write acronyms in title case: `HttpClient`,
  `SqlConfig`.
- Durations and sizes carry their unit: `start_timeout_s`, `poll_interval_ms`, `page_width_px`.
- Bounds on a field are `ClassVar`s named `<FIELD>_MIN` and `<FIELD>_MAX`.
- A field ending in `_key` names a secret store entry and never holds a secret.
- Use `error` for a caught exception and `value` for a validator's input.

## Docstrings and comments

**NEVER a file docstring,** in `src/` and in `tests/`, `__init__.py` and console scripts included: no module starts
with a docstring. A file holds one class, and that class's docstring says what the file is for.

Every class and method in `src/` has a Google-style docstring, private ones included. Types go in parentheses.

```python
class CustomerService:
    """Everything the application does with a customer.

    Attributes:
        repository (CustomerRepository): Where customers are stored.
        logger (Logger): Logger instance.

    Notes:
        Callers go through this class rather than the repository, so that each rule about a customer lives in one
        place.
    """
```

- A class summary says what the class is. A method summary starts with a verb: `Create one customer.`
- List every attribute under `Attributes:`, constants included.
- Use `Args:`, `Returns:` and `Raises:` wherever they apply.
- Put the reasoning in `Notes:`, after the other sections. Use bullets for several points, and bold the ones that would
  cause harm if missed.
- Write ``` ``double_backticks`` ``` around code.
- Avoid inline comments: `src/` has almost none. A reason belongs in `Notes:`.

## Exceptions

Each exception has its own file, and the package's `exceptions/__init__.py` re-exports it through a sorted `__all__`.

| Kind | Name | Docstring |
| --- | --- | --- |
| Layer base | `SE<Domain>Error` | `Base class for every error raised while storing a customer.` |
| Layer | `SE<Domain><Problem>Error` | `Raised when a customer cannot be found.` |
| Model base | `SEInvalid<Model>Exception` | `Exception raised when an invalid DatabaseConfig is provided.` |
| Model field | `SE<Model>Invalid<Field>` | `Exception raised when an invalid ``port`` is provided.` |
| Model, other | `SE<Model><Problem>` | `SECustomerCatalogUnreadable`, `SEDatabaseConfigNoHost` |

- Each file is the class name in snake case: `se_database_config_invalid_port.py`.
- Keep the cause: `raise SECustomerCatalogUnreadable(...) from error`.
- Outside `models`, log at `ERROR` just before raising.
- **Every `try` has at least one `except`,** even when it only logs: a `try` with only a `finally` is forbidden. An
  `except` that cannot handle the error logs it at `ERROR` (with `type(error).__name__`) and raises it again with a bare
  `raise`. `finally` may follow the `except` for the clean-up.
- Catch specific types. A broad `except Exception` exists only where any failure must be reported: rather than end the
  process, or logged and raised again unchanged, as `Runnable.execute` does.

## Messages

**Use the `exception-and-log-messages` skill whenever you write a `raise` or a log call.** A message with two or more
sentences has one sentence per source line, with no comma between them, and the first line ends with `# noqa: E501`:

```python
raise SEDatabaseConfigInvalidPort(
    f"Invalid port: {value}. "  # noqa: E501
    f"Must be in [{cls.PORT_MIN}, {cls.PORT_MAX}]."
)
```

- A field error reads `Invalid <field>: {value!r}.` then `Must be ...`
- Write full sentences that end with a full stop, and no semicolons.

## Logging

Classes outside `models` that log take the logger as their last constructor argument:

```python
def __init__(self, config: DatabaseConfig, logger: Optional[Logger] = None) -> None:
    self.config = config
    self.logger = logger if logger else getLogger(__name__)
```

**NEVER hand a logger to a new object.** The logger parameter keeps its `None` default, and code that creates the
object leaves it out, so that each class logs under its own module's name: `DurableConsumer(connection, config)`, never
`DurableConsumer(connection, config, self.logger)` or `GreetingCommand(logger=self.logger)`. **Nor does a subclass hand
it to its base class:** it calls `super().__init__()` without it, then sets its own `self.logger`. Tests may pass a
logger to an object they test, to test that parameter or to capture the logs.

- Use lazy arguments, never an f-string: `self.logger.info("Created customer %s in %d ms.", name, duration_ms)`.
- Use the levels this way:

  | Level | For |
  | --- | --- |
  | `DEBUG` | Decisions and small steps |
  | `INFO` | What was actually done |
  | `WARNING` | A degraded result the code recovers from |
  | `ERROR` | A failure, just before raising |

- **Every method logs, at each level that applies to it, except in `tests/` and `models`.** Not every method has a
  failure to report, so do not invent one, but every failure path has its `WARNING` or `ERROR`.
- **EVERY logical branch logs**, in `src/` outside `models/`: each `if`, `elif` and `else` body, each `case` of a
  `match`, and each `except`. A branch that returns early, skips an item or picks a default says so at `DEBUG`, and a
  branch that raises logs at `ERROR` first. Add the `else` when the path it covers means something (a missing section,
  a file not written). A conditional expression that chooses what the code does (`a if c else b`) is written as an
  `if`/`else` with a log in each branch. In code that runs for every event, the branches log at `DEBUG`.
- Two places cannot follow it, and stay silent: the `logger if logger else getLogger(__name__)` of a constructor,
  because no logger exists yet, and the code the logging system calls itself (formatters, handlers, filters), because
  a log there would call it again. One-line getters, predicates and data holders have no branch, so they have nothing
  to log either.
- The log file holds colour codes. Read it with `tail -f` or `less -R`.
- `DEBUG` lines are written by default, because the root level in `conf/logger.yaml` is `DEBUG`. Keep them short.
- **Never log a secret or a typed value.** If an error might quote one, log `type(error).__name__`.
- `models` never logs. It raises.
- Only `scripts/` uses `print`, because that output is for the person at the terminal.

An app configures logging once, in its `main()`, with `swarm_logging.configurators.logging_configurator.LoggingConfigurator(LoggingConfig(...)).configure()`.
`LoggingConfig.path` names the app's `conf/logger.yaml`, and None uses the reference `logger.yaml` shipped in
swarm_logging. `LoggingConfig.format` is `coloured` by default and `json` in production, which writes one JSON object
per line on every handler.

## Pydantic models

Every field has a `Field(description=...)` and a `@field_validator` that raises its own exception. Fields with the same
rule may share a validator.

```python
class DatabaseConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_default=True)

    PORT_FIELD: ClassVar[str] = "port"
    BEFORE: ClassVar[Literal["before"]] = "before"

    port: int = Field(default=5432, description="The port the database listens on.")

    @field_validator(PORT_FIELD, mode=BEFORE)
    def validate_port(cls, value: JsonValue) -> JsonValue:
        """Validate ``port``. ..."""
        if value is None:
            return cls.model_fields[cls.PORT_FIELD].get_default(call_default_factory=True)
        if isinstance(value, bool) or not isinstance(value, int):
            raise SEDatabaseConfigInvalidPort(...)
        return value
```

- Validators are named `validate_<field>` and use `mode="before"`. Do not add `@classmethod`: ruff is configured for
  `field_validator`.
- `None` becomes the default, if the field has one.
- Reject `bool` where a number is expected, because Python treats it as an `int`.
- Strip strings, and reject empty ones.
- Check rules across fields in `@model_validator(mode="after")`.
- Use `extra="forbid"`. Configuration sections add `validate_default=True`. Models that must not change use
  `frozen=True`.

## Data and enums

- Do not hard-code data in Python. It goes in the app's `conf/catalogs/*.yaml`, loaded by a model that subclasses `YamlCatalog`,
  which provides `load(path)` and raises the model's `UNREADABLE` exception. YamlCatalog is
  `swarm_catalog.models.yaml_catalog.YamlCatalog`, and a subclass sets `UNREADABLE` to its own exception.
- A string that selects behaviour is a `StrEnum` with `@unique`, with its members listed under `Attributes:`.
- **ALL the enums of a module are in ONE `enums.py`, at the root of its `models` module:**
  `swarm_models/enums.py` for the models layer, `src/<module>/models/enums.py` for a kernel library, imported as
  `from swarm_lifecycle.models.enums import RunnableStatus`. There is no `enums/` folder and no enum anywhere else,
  and `enums.py` holds only enums.
- **NO hyphen in an enum's values.** A value is lower case words joined by underscores: `NOT_STARTED = "not_started"`,
  never `"not-started"`.
- **NO raw string in the code of `src/`.** A string that means something (a status, a phase, a kind, a mode, a key, a
  field name, an encoding, an option) is a member of a `StrEnum` in `models/enums.py`, or an `UPPER_CASE` `ClassVar` of
  its class: `self.ENCODING`, `cls.FORMAT_FIELD`, `RunnableStatus.RUNNING`. A method never compares with, returns or
  yields a literal string. Only the text of log, exception and `print` messages, docstrings, and the values of the
  constants themselves are literal. Where a third-party signature takes a `Literal`, the constant is typed with it:
  `BEFORE: ClassVar[Literal["before"]] = "before"`. Tests compare with these enums and constants, never with their
  raw values.
- Use `match`/`case` to branch on an enum.
- Open files with the `ENCODING: ClassVar[str] = "utf-8"` of their class.
- Secrets live in a secret store. They never appear in configuration or logs.

## Tests

- Name files `test_<subject>.py`, in the folder that mirrors the source. There are no `__init__.py` files.
- Put each file's tests in one `Test<Subject>` class. A helper class, such as a stand-in server, gets its own file.
- When a source file needs several test classes, give it a folder of its name:
  `tests/swarm_service/customers/customer_service/`.
- In that folder, `helpers.py` holds the functions and constants several classes share, and `conftest.py` the fixtures.
  Import them by their full path: `from tests.swarm_service.customers.customer_service.helpers import a_customer`.
- Scripts that tests run as child processes load their helpers by path, so keep them in place.
- Name tests as sentences: `test_a_customer_without_a_name_is_refused`.
- Tests need no docstrings, banners or import comments. Add a docstring only if the purpose is not obvious.
- Assert the specific exception: `pytest.raises(SEDatabaseConfigInvalidPort)`.
- Use `pytest.mark.parametrize` for cases of the same behaviour.
- Async tests need no marker, because `asyncio_mode` is `auto`.
- Prefer real things to mocks. `unittest.mock` is not used: tests use real services, such as a local test server.
- PostgreSQL tests: the fixtures `postgres_server` and `postgres_dsn` of the root `conftest.py` start a throwaway server
  from the local PostgreSQL binaries (`pg_ctl`, `initdb` and `psql`), found on `PATH`, in `SWARM_POSTGRES_BIN_DIR` or in
  `/usr/lib/postgresql/*/bin`. The tests connect as the role `swarm_app`, which is neither superuser nor `BYPASSRLS`, so
  that row-level security applies. They skip when the binaries are missing, as the NATS tests do.
- Test file names are unique across the whole uv workspace, because pytest imports test modules by their base name, so
  an app's tests carry its name: `test_swarm_simulator_main.py`.

Every model gets this set of tests:

```python
class TestDatabaseConfig:
    def test_defaults(self) -> None: ...
    def test_full_valid_construction(self) -> None: ...
    def test_none_becomes_the_default(self, name: str) -> None: ...
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None: ...
    def test_rejects_unknown_keys(self) -> None: ...
    def test_round_trip(self) -> None: ...
```

## Formatting and prose

- Ruff handles formatting, with lines up to 120 characters and double quotes.
- Write docstrings, messages and documentation in plain British English: `Initialise`, `normalised`, `colour`,
  `catalogue`. Identifiers use `catalog`.
- Do not use em dashes.