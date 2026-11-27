# Backend

The Python backend of Swarm: a kernel of libraries, five layer packages with a folder per domain inside each, and one
thin app per Docker image. The rules are in [AGENT.md](../AGENT.md#layout), and the tests of
[tests/conventions/backend/](../tests/conventions/backend/) check them.

## Layers as packages

| Package | Import name | Holds |
| --- | --- | --- |
| [libs/](libs/) | `swarm_lifecycle`, `swarm_logging`, `swarm_catalog`, `swarm_nats`, `swarm_web` | The kernel: Runnable, AsyncRunnable and the abstract factories; the logging configuration; YamlCatalog; the NATS connector; the FastAPI app builder, the server runnable, the runner of an AsyncRunnable, `ETag` and `If-Match` |
| [swarm-models/](swarm-models/) | `swarm_models` | Layer 0: every Pydantic model, enum and exception, by concept; the enums in `swarm_models/enums.py`; each app's configuration in `swarm_models/config/<app>/`; the JSON Schema bundle in `schemas/` |
| [swarm-storage/](swarm-storage/) | `swarm_storage` | Layer 1: one repository per entity, and the other stores |
| [swarm-clients/](swarm-clients/) | `swarm_clients` | Layer 1: one client per remote system (other apps, NATS, MAVLink, Keycloak) |
| [swarm-service/](swarm-service/) | `swarm_service` | Layer 2: the business rules and every runnable, bus responders and consumers included, with their factories |
| [swarm-api/](swarm-api/) | `swarm_api` | Layer 3: the FastAPI endpoints only, the routers in `swarm_api/v1/<domain>/`, the `Depends` providers, the middlewares, the exception handlers and the `/v1/live` WebSocket |
| [apps/](apps/) | `swarm_<app>` | Layer 4: one thin app per image |

Inside `swarm_storage`, `swarm_clients` and `swarm_service`, each domain has its folder (`gateway`, `flight`,
`simulation`...), and `shared/` holds what every domain uses: PostgreSQL, the outbox, idempotency, the bus, the live
fan-out, the messages.

## What each package may import

| Package | May import |
| --- | --- |
| The kernel (`libs/`) | The kernel only |
| `swarm_models` | Itself, `swarm_catalog`, `swarm_lifecycle`, and the models of `swarm_web` and `swarm_nats`. Never `swarm_logging` |
| `swarm_storage`, `swarm_clients` | Itself, `swarm_models` and the kernel |
| `swarm_service` | Itself, `swarm_storage`, `swarm_clients`, `swarm_models` and the kernel |
| `swarm_api` | Itself, `swarm_service`, `swarm_models`, `swarm_web` and the rest of the kernel |
| `swarm_<app>` | `swarm_api`, `swarm_service`, `swarm_web`, `swarm_models.config.<app>` and `swarm_logging` |
| `scripts/` | `swarm_service`, `swarm_api`, `swarm_web`, `swarm_models` and the kernel |

`swarm_service.<domain>` uses only `swarm_storage.<domain>`, `swarm_clients.<domain>` and the `shared` folders. Each
package declares in its `pyproject.toml` the workspace packages it imports.

## The apps

| App | Domain | Console script | PostgreSQL schema |
| --- | --- | --- | --- |
| [gateway](apps/gateway/) | `gateway` | `swarm-gateway-serve` | Yes |
| [fleet](apps/fleet/) | `fleet` | `swarm-fleet-serve` | Yes |
| [missions](apps/missions/) | `missions` | `swarm-missions-serve` | Yes |
| [simulator](apps/simulator/) | `simulation` | `swarm-simulator-serve` | No |
| [flight-engine](apps/flight-engine/) | `flight` | `swarm-flight-engine-serve` | No |

An app folder holds its `pyproject.toml` (its console script, and `[tool.swarm] domains`, the domains it owns), its
`Dockerfile`, its `conf/` (`app.yaml`, `logger.yaml`, `catalogs/`), its Alembic `migrations/` when it owns a schema,
and `src/swarm_<app>/main.py`. The argument-free `main()` reads `conf/app.yaml` in the folder `SWARM_APP_ROOT` names
(the current one without it), configures logging, builds the application with the app's router of `swarm_api` and
serves it. An app has no command line, and wires only the domains it lists.

Build an image from the repository root, which is the build context:

```bash
docker build -f backend/apps/<app>/Dockerfile -t <name>:local .
```

The image sets `SWARM_APP` and `SWARM_APP_ROOT`, so the same image migrates its schema when run with the entrypoint
`swarm-migrations-migrate`.

## The gateway's Operator directory

The `gateway` domain holds the Operator directory, used by the Swarm administrator to create Operators and by their
people to read their own Operator. It is served by `swarm-gateway-serve` under `/v1/operators` and
`/v1/operators/{id}`.

- The `operators` and `cell_assignments` tables are global: they are not filtered by Operator, and they hold no
  person data.
- The `people` table is under row-level security: a unit of work sets `swarm.operator_id`, so a person is visible only
  inside the transaction of its own Operator.
- The `operators` entry of `conf/app.yaml` names the cell the Operators are assigned to and the Keycloak admin client
  used to create their organisations and invite their first Mission planner.
- The client secret of that Keycloak admin client is not in `conf/app.yaml`. It comes from the environment entry
  `SWARM_GATEWAY_KEYCLOAK_CLIENT_SECRET`, filled from the vault.

## Add a domain

1. Create the domain's folder in each layer it needs: `swarm_models/<domain>/`, `swarm_storage/<domain>/`,
   `swarm_clients/<domain>/`, `swarm_service/<domain>/` (with its `factories/`) and `swarm_api/v1/<domain>/`, with one
   class per entity per layer.
2. List the domain in the `[tool.swarm] domains` of the one app that owns it.
3. Write its tests in `tests/swarm_<layer>/<domain>/`, mirroring the import paths.
4. Regenerate the contracts if they change: `uv run swarm-openapi-export` for the routes, `uv run swarm-schemas-export`
   for the shared models.

## Add an app

1. Create `apps/<app>/` like the others: `pyproject.toml` with its console script `swarm-<app>-serve` and its
   `[tool.swarm] domains`, `Dockerfile`, `conf/app.yaml` and `conf/logger.yaml`, and `src/swarm_<app>/main.py`.
2. Add its configuration model in `swarm_models/config/<app>/`, on the `AppConfig` base, and its member in the
   `AppName` enum of `swarm_models/enums.py`.
3. Add the app to `SwarmApps` of [scripts/](../scripts/README.md), so that the OpenAPI scripts (and the migration
   script, when it owns a schema) cover it.
4. Add `swarm_<app>` to `known-first-party` and its `src/` to the mypy paths of the root `pyproject.toml`, and write
   its tests in `tests/swarm_<app>/`.

The uv workspace takes every folder of `apps/`, and CI builds every folder of `apps/` that holds a `Dockerfile`,
under the folder's name.
