# Scripts

The operations of Swarm. Each one is a Python script of `src/swarm_scripts/<area>/` with a `main()` and no argument,
exposed in [pyproject.toml](pyproject.toml) as a console script and run from the repository root with `uv run`. The
rules are in [AGENT.md](../AGENT.md#layout): no command line, no argument parser, the environment narrows a script when
it must.

| Command | Script | Does | Exit codes |
| --- | --- | --- | --- |
| `uv run swarm-schemas-export` | [schemas/export.py](src/swarm_scripts/schemas/export.py) | Writes the JSON Schema bundle of `swarm-models`, `backend/swarm-models/schemas/swarm_models.schema.json` | 0 written, 2 error |
| `uv run swarm-schemas-check` | [schemas/check.py](src/swarm_scripts/schemas/check.py) | Checks that bundle is up to date | 0 current, 1 stale, 2 error |
| `uv run swarm-openapi-export` | [openapi/export.py](src/swarm_scripts/openapi/export.py) | Writes the OpenAPI document of each app, `frontend/packages/api-client/openapi/<app>.json` | 0 written, 2 error |
| `uv run swarm-openapi-check` | [openapi/check.py](src/swarm_scripts/openapi/check.py) | Checks each published OpenAPI document against its app | 0 current, 1 stale, 2 error |
| `uv run swarm-migrations-migrate` | [migrations/migrate.py](src/swarm_scripts/migrations/migrate.py) | Upgrades the PostgreSQL schema of each app that owns one to its latest Alembic revision | 0 upgraded, 1 failed, 2 unknown app |
| `uv run swarm-i18n-check` | [i18n/check.py](src/swarm_scripts/i18n/check.py) | Checks that every Python message is in English, French, German and Spanish | 0 complete, 1 missing, 2 catalogue error |

## Environment

| Entry | Read by | Means |
| --- | --- | --- |
| `SWARM_APP` | OpenAPI and migration scripts | The one app to act on, by its name (`flight_engine`) or its folder (`flight-engine`). Without it, the script covers every app of `backend/apps/` |
| `SWARM_APP_ROOT` | Migration script | With `SWARM_APP`, the folder of that app (`/app` in its image). Without it, the app's folder of `backend/apps/` |
| `SWARM_<APP>_POSTGRES_DSN` | Migration script | The DSN of the app's schema, such as `SWARM_GATEWAY_POSTGRES_DSN`. It is never printed |
| `SWARM_I18N_LOCALES` | Message check | A folder of catalogues to check in place of those shipped with `swarm_storage` |

The OpenAPI scripts build each app's application with its router of `swarm_api`, as the app's `main()` does, so the
document is the one the app serves. The migration script skips the apps that own no schema (the simulator and the
flight engine). In an image, the migration runs as a job of the app's own image with the entrypoint
`swarm-migrations-migrate`: `SWARM_APP` and `SWARM_APP_ROOT` are already set.

`SwarmApps` ([swarm_apps.py](src/swarm_scripts/swarm_apps.py)) lists the apps a script acts on, and `RepositoryPaths`
([repository_paths.py](src/swarm_scripts/repository_paths.py)) the folders the scripts read and write. The tests are in
[tests/scripts/](../tests/scripts/).
