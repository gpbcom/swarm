# T0.12: Review note

**Verdict:** ✅ Approved · **Branch:** `feature/tickets` (uncommitted, TKT-16)

No blocking finding is left. K33 resolves the four blocking findings of the last run: the images now find `conf/` and `migrations/` through `SWARM_<SERVICE>_HOME=/app`. The follow-ups below never hold the merge. **Read the first point of "Look at first" before you approve the push.**

## What changed

- Three services (gateway, missions, fleet) now follow the AGENT.md layers. Each has its own PostgreSQL schema, Alembic migrations and an outbox table. Row-level security on `operator_id` is FORCEd, so the table owner is bound too, and compares the column with `NULLIF(current_setting('swarm.operator_id', true), '')::uuid`, so an unset Operator matches no row.
- Two shared packages are added. `swarm-storage` holds the pool, the unit of work that sets `swarm.operator_id` per transaction, the repository base and the migrator. `swarm-rest` holds the `/v1` app builder, `problem+json`, the pure-ASGI `Idempotency-Key` middleware and `ETag`/`If-Match`.
- Each service publishes its OpenAPI document to `packages/ts/api-client/openapi/`, and the TypeScript client is generated from it. The `test` script runs `generate.ts --check`, and each service's pytest compares the published document with its app.
- One multi-stage image per service, running as a non-root user. `SWARM_<SERVICE>_HOME` points the installed (non-editable) package at the `conf/` and `migrations/` copied to `/app`.
- Decision (K33): the home resolution is copied into each `<Service>Config` rather than shared. This keeps each service independent, at the cost of three copies.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. Given a query that forgets the Operator filter, when it runs through gateway, missions or fleet, then it returns nothing instead of another Operator's rows | `test_a_query_that_forgets_the_operator_returns_nothing` (gateway), `test_a_query_without_an_operator_returns_nothing` (missions), `test_pending_without_a_known_operator_returns_nothing` (fleet), `test_a_query_never_returns_another_operators_events` (swarm-storage); tests-evidences/pytest.txt (3138 passed, 77 skipped) | ✅ Pass (the evidence does not show which tests skipped; see follow-ups) |
| 2. Given the generated OpenAPI document, when CI runs, then `packages/ts/api-client` is up to date | `test_the_published_openapi_document_is_up_to_date` (each service); `generate.ts --check` in tests-evidences/test.txt | ✅ Pass |

## Look at first

- **The uv.lock and pyproject.toml of T0.13**: `uv.lock` (manifest member `swarm-simulator`, plus pymavlink, lxml and fastcrc) and `pyproject.toml` (simulator testpaths, mypy paths, first-party, pymavlink override). Committed alone, T0.12 would fail `uv sync --locked` in every Python CI job. Push it together with T0.13, or re-lock without the simulator in the clean tree first.
- **Operator isolation, read line by line**: `packages/python/swarm-storage/src/swarm_storage/storage/postgres/ddl/row_level_security.py` (policy, FORCE), `.../unit_of_work.py` (transaction-local `set_config`, nothing set without an Operator), `.../repositories/postgres_repository.py` (no Operator filter by design; an RLS refusal becomes `SEStorageOperatorRefusedError`), `.../ddl/outbox_table.py`.
- **Image start-up**: `services/{gateway,missions,fleet}/Dockerfile` lines 37-49, and `service_folder()` in each `models/config/*_config.py`. The schema factories now take `<Service>Config.migrations_folder()`.
- **Idempotency**: `packages/python/swarm-rest/src/swarm_rest/api/rest/idempotency_middleware.py`. Keys are global, not per Operator, and the body is buffered with no size bound. Both are acceptable before T0.11.
- Identity and Simulator isolation are not touched by this ticket: token checks are T0.11, and the simulator is T0.13.

## Assumptions accepted

- TICKET.md: FS-012 and UC-029 come from epic E0.5. Accepted: the epic names them.
- TICKET.md: no budget is listed. Accepted: no business route yet.
- TICKET.md: the ticket links to the sprint anchor `s03`, and criterion 2 restates the roadmap. Accepted.
- K33: wrote the new tests itself. Accepted: the plan change was approved by the person.
- K33: the image test skips an image that does not copy `conf` from the build stage (the simulator). Accepted: that image is T0.13's.
- K33: `SERVICE_FOLDER_DEPTH = 4` in fleet. Accepted.
- K33: missions and fleet use `CONF_FOLDER_NAME` and `MIGRATIONS_FOLDER_NAME`. Accepted, and the naming is listed as a follow-up.

## Follow-ups

- Re-lock `uv.lock` and trim `pyproject.toml` of T0.13's lines at finish, or finish with T0.13. Add `uv lock --check` on the clean tree to the harness, with a test.
- `alembic_environment.py:35` hands a logger to `super().__init__`. Fix it, and teach `no_logger_argument.py` to catch an `IfExp` argument.
- Silent branches: `PostgresRepository.list`, `IdempotencyMiddleware._read_body` and `_key_of`, `RestAppBuilder._document`.
- `FleetConfig` lacks `extra="forbid"` and `frozen=True`. Align the constant names across the three configs.
- Idempotency: scope keys by Operator after T0.11, use a shared store before more than one replica, and bound the body size.
- Record `pytest -rs` in the evidence, and make CI fail rather than skip when no PostgreSQL binaries are found.
- Add a partial index for `OutboxRepository.PENDING_QUERY` when the relay lands.
- Move identifier checking into a `SqlIdentifier` class.
- Correct the `conf_folder` and `migrations_folder` docstrings of the gateway for the home override.
