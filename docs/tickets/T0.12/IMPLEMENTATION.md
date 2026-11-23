# T0.12: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🎯 Constraints

- A query that forgets the Operator filter returns nothing, in gateway, missions and fleet (criterion 1 of [TICKET.md](TICKET.md), BR-008).
- The OpenAPI documents are published and `packages/ts/api-client` is checked in CI (criterion 2 of [TICKET.md](TICKET.md)).
- Each service has one multi-stage image, built with `uv sync --no-editable` (AGENT.md, Docker images; [`services/gateway/Dockerfile`](../../../services/gateway/Dockerfile)).
- A service never imports another service, and shared code goes in `packages/` (AGENT.md, Services).
- No hard-coded strings, one class per file, every branch logs (CLAUDE.md code rules).

## ⚖️ Choices at a glance

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | Where an installed service finds `conf/` and `migrations/` | Copy the home resolution into each config | A shared base class or helper | Three copies of one method |
| [D2](#d2) | Where the schema factory gets the migrations folder | `<Service>Config.migrations_folder()` | A `Path(__file__)` chain in the factory | None noted |
| [D3](#d3) | How the images test checks the home variable | Parse each Dockerfile | Hard-code `/app`, or build and run the image | Does not run the image |
| [D4](#d4) | How the runtime `ENV` is written | Join the existing `ENV` instruction | A separate `ENV` line | None noted |
| [D5](#d5) | How the Operator is enforced | A forced policy on `operator_id` against a transaction-local setting | Filtering in each query | Needs a unit of work for every query |
| [D6](#d6) | Where idempotency keys live | A per-process memory store, global keys | A shared store, keys per Operator | Single replica, no Operator scope until T0.11 |

## <a id="d1"></a>D1: Where an installed service finds its folders

**Chosen:** copy `HOME_KEY`, `service_folder()`, `conf_folder()` and `migrations_folder()` of the gateway into [`missions_config.py`](../../../services/missions/src/missions/models/config/missions_config.py) and [`fleet_config.py`](../../../services/fleet/src/fleet/models/config/fleet_config.py) · **Where:** [`gateway_config.py:153-163`](../../../services/gateway/src/gateway/models/config/gateway_config.py#L153-L163) · **Source:** K33

| Option | For | Against |
| --- | --- | --- |
| ✅ Copy into each config | Stays inside the files the task owns. Each service stays independent. | The same code three times. |
| A shared base class or a `swarm-catalog` helper | One copy. | Needs a change to a package outside the task. |
| An editable install in the images | The path from `__file__` would be right with no variable. | Heavier, and contradicts `uv sync --no-editable` in the Dockerfiles. |

**Trade-off:** duplication for independence and a task that stays in its files. The review also lists the constant names that now differ.

**Revisit when:** a package can hold a home resolver (listed as a follow-up in [EXPLAIN.md](EXPLAIN.md)).

## <a id="d2"></a>D2: The migrations folder in the schema factory

**Chosen:** the factories call `<Service>Config.migrations_folder()` · **Where:** [`schema_service_factory.py:36-43`](../../../services/gateway/src/gateway/service/factories/schema_service_factory.py#L36-L43), [missions](../../../services/missions/src/missions/service/factories/schema_service_factory.py), [fleet](../../../services/fleet/src/fleet/service/factories/schema_service_factory.py) · **Source:** K33

| Option | For | Against |
| --- | --- | --- |
| ✅ `migrations_folder()` | One source, follows `SWARM_<SERVICE>_HOME`. The factory loses its path constants. | The factory depends on the config class. |
| `Path(__file__).parents[...]` in the factory | Nothing to import. | Wrong in a non-editable install, where the code is in the venv. |
| `conf_folder().parent` | No new method. | Reported as an alternative; no reason against is recorded. Open point. |

**Trade-off:** none recorded beyond the dependency on the config.

**Revisit when:** the home resolver is shared (D1).

## <a id="d3"></a>D3: The images test

**Chosen:** parse the runtime stage for `COPY --from=build .../conf` and require `ENV SWARM_<SERVICE>_HOME` equal to the destination minus `/conf`, for each Dockerfile of `services/` · **Where:** [`test_service_images.py:64-73`](../../../tests/deploy/images/test_service_images.py#L64-L73) · **Source:** K33

| Option | For | Against |
| --- | --- | --- |
| ✅ Parse the Dockerfile | A new service is covered with no test change (AGENT.md, Services). No Docker daemon needed. | Does not run the image. Skips images that copy `conf` another way, such as the simulator. |
| Hard-code `/app` per service | Simple. | Each new service needs a test change. |
| Build the image and run `python -c` | Proves the start-up. | Needs a Docker daemon. |

**Trade-off:** a static check, not a run of the image.

**Revisit when:** CI builds the images before the tests, or the simulator image of T0.13 needs the same check.

## <a id="d4"></a>D4: The runtime `ENV`

**Chosen:** add `SWARM_<SERVICE>_HOME=/app` to the existing `ENV` instruction · **Where:** [`services/gateway/Dockerfile:37-39`](../../../services/gateway/Dockerfile#L37-L39), [missions](../../../services/missions/Dockerfile#L39), [fleet](../../../services/fleet/Dockerfile#L39) · **Source:** K33

| Option | For | Against |
| --- | --- | --- |
| ✅ Join the existing `ENV` | No extra layer. Same shape in all three. | None recorded. |
| A separate `ENV` line | Easier to read in a diff. | One more layer. |

**Trade-off:** none recorded.

**Revisit when:** never expected.

## <a id="d5"></a>D5: How the Operator is enforced

**Chosen:** a policy on `operator_id`, forced on the owner, against a setting that a unit of work sets for each transaction · **Where:** [`row_level_security.py:41-45`](../../../packages/python/swarm-storage/src/swarm_storage/storage/postgres/ddl/row_level_security.py#L41-L45), [`unit_of_work.py:88-89`](../../../packages/python/swarm-storage/src/swarm_storage/storage/postgres/unit_of_work.py#L88-L89) · **Source:** PLAN.md and the technical page on PostgreSQL, read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ Forced row-level security | The specification says a query that forgets the filter returns nothing. `NULLIF` makes an unset setting match no row. `FORCE` binds the table owner too. The repository adds no filter ([`postgres_repository.py:205`](../../../packages/python/swarm-storage/src/swarm_storage/storage/postgres/repositories/postgres_repository.py#L205)). | Every query must run in a unit of work. A refused write needs mapping to `SEStorageOperatorRefusedError`. |
| An Operator filter in each query | No database setting. | A forgotten filter leaks rows, which is the failure criterion 1 forbids. |

**Trade-off:** the rule lives in the database, and the code pays for it with the unit of work.

**Revisit when:** a table needs a rule other than one Operator per row. Other alternatives the planner weighed are not recorded: open point.

## <a id="d6"></a>D6: Idempotency store

**Chosen:** a per-process memory store, keys global, body buffered whole · **Where:** [`idempotency_middleware.py:214`](../../../packages/python/swarm-rest/src/swarm_rest/api/rest/idempotency_middleware.py#L214), [`memory_idempotency_store.py`](../../../packages/python/swarm-rest/src/swarm_rest/storage/idempotency/memory_idempotency_store.py) · **Source:** read from the diff and the review

| Option | For | Against |
| --- | --- | --- |
| ✅ Memory store, global keys | The skeletons have no business route yet, and no verified token exists before T0.11. | Lost on restart, not shared between replicas, not scoped by Operator, no size bound on the body. |
| A shared store, keys per Operator | Correct with several replicas. | Needs the Operator from T0.11 and a shared backend. |

**Trade-off:** accepted by the review as fine before T0.11.

**Revisit when:** T0.11 lands, or before more than one replica runs. Why a memory store was preferred is not recorded: open point.

## 📝 Assumptions behind the choices

- K33 wrote the new tests itself, after the person approved the plan change: supports [D3](#d3).
- K33 skips an image with no `COPY --from=build .../conf`, since the simulator is T0.13's: supports [D3](#d3).
- Fleet's `SERVICE_FOLDER_DEPTH = 4` matches the gateway: supports [D1](#d1).
- The constant names differ between configs because existing tests use them: supports [D1](#d1).
- No budget is listed, as the skeletons have no business route: supports [D6](#d6).
