# T0.12: Service skeletons with row-level security

**Status:** ✅ Done

## Roadmap

- **Ticket:** [T0.12](../../specs/roadmap/01-p0-foundations.md#s03) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S03](../../specs/roadmap/01-p0-foundations.md#s03), 1 to 12 February 2027: A person signs in; a service answers for one Operator only; simulated Drones fly
- **Epic:** [E0.5 Identity and Operators](../../specs/roadmap/01-p0-foundations.md#epics): Keycloak (global layer), `services/gateway`, `services/missions`, `services/fleet` (skeletons) and `frontends/back-office`, delivering UC-029, BR-008 and FS-012 AC-3

## What it delivers

- `services/gateway`, `services/missions` and `services/fleet` as AGENT.md services (layers, factories, logging), as [🗂️ Mono-repo](../../specs/technical/01-architecture.md#mono-repo).
- FastAPI `/v1` with `problem+json`, `Idempotency-Key` and `ETag`, as [🔌 REST](../../specs/technical/05-api.md#rest).
- One PostgreSQL schema per service with Alembic, and row-level security on `operator_id` against `swarm.operator_id`, as [🗄️ PostgreSQL and PostGIS](../../specs/technical/03-storage.md#postgresql).
- The OpenAPI document published and `packages/ts/api-client` generated, as [🔌 REST](../../specs/technical/05-api.md#rest).

## Features, use cases and business rules

- [📏 BR-008: Operator isolation](../../specs/functional/business-rules/BR-008-operator-isolation.md)
- [📘 FS-012: Operators, deployment and languages](../../specs/functional/features/FS-012-operators-deployment-and-languages.md) (AC-3, named by epic E0.5)
- [🎬 UC-029: Create an Operator](../../specs/functional/use-cases/UC-029-create-an-operator.md) (named by epic E0.5)

## Technical pages it builds on

- [🗄️ PostgreSQL and PostGIS](../../specs/technical/03-storage.md#postgresql): "row-level security policies compare it with the session setting `swarm.operator_id`, set by the service from the verified token on each transaction. A query that forgets the filter returns nothing".
- [🔌 REST](../../specs/technical/05-api.md#rest): "`ETag` and `If-Match` on updates, `Idempotency-Key` on every POST, errors as `application/problem+json`"; "the TypeScript client in `packages/ts/api-client` is generated from it in CI".
- [🔐 Security](../../specs/technical/06-security.md#identity): "PostgreSQL row-level security enforces the Operator on every row".

## Screens touched

- ➖ No screen: the ticket delivers service skeletons, a database policy and a generated client, and the roadmap row names no use case screen.

## Budgets touched

- The ticket touches no budget: the roadmap row names none.

## Acceptance criteria

1. **Given** a query that forgets the Operator filter, **when** it runs through a service of `services/gateway`, `services/missions` or `services/fleet`, **then** it returns nothing instead of another Operator's rows. ([📏 BR-008](../../specs/functional/business-rules/BR-008-operator-isolation.md), [🎬 UC-029](../../specs/functional/use-cases/UC-029-create-an-operator.md))
2. **Given** the generated OpenAPI document, **when** CI runs, **then** `packages/ts/api-client` is up to date. ([📏 BR-008](../../specs/functional/business-rules/BR-008-operator-isolation.md), [🎬 UC-029](../../specs/functional/use-cases/UC-029-create-an-operator.md))

## Out of scope

- Keycloak and the token checks of the gateway, see [T0.11](../../specs/roadmap/01-p0-foundations.md#s03).
- The creation of an Operator in the Back office and its test with two Operators, see [T0.16](../../specs/roadmap/01-p0-foundations.md#s04).

## Assumptions

- The roadmap row names only BR-008; FS-012 and UC-029 are taken from epic E0.5, and UC-029 serves as the use case in each criterion because the template requires one.
- The roadmap row names no budget, so none is listed, although the REST page states a p95 budget.
- The roadmap has no per-ticket anchor, so the ticket links to its sprint anchor `s03`.
- Criterion 2 restates the roadmap's "generated client is up to date in CI".
