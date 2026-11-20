# T0.09: NATS JetStream and Operator accounts

**Status:** ✅ Done

## Roadmap

- **Ticket:** [T0.09](../../specs/roadmap/01-p0-foundations.md#s02) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S02](../../specs/roadmap/01-p0-foundations.md#s02), 18 to 29 January 2027: shared code, dev cell and pipeline
- **Epic:** [E0.4](../../specs/roadmap/01-p0-foundations.md#epics): Dev cell and data platform. A cell to run and measure everything on.

## What it delivers

- The NATS cluster of 3 with JetStream replicas 3, in `deploy/charts`, as [🔲 Architecture: cells and the global layer](../../specs/technical/01-architecture.md#cells) and [🗄️ Storage: overview](../../specs/technical/03-storage.md#overview).
- One NATS account per Operator, limited to `op.<operator_id>.…`, as [👥 Security: roles and Operator isolation](../../specs/technical/06-security.md#authorisation) and [📨 Data models: events and proposals](../../specs/technical/02-data-models.md#events).
- Separate credentials for simulated Squads, as [🕹️ Engine and services: simulator](../../specs/technical/04-engine.md#simulator).
- The leaf node configuration for an edge, as [🌐 Architecture: edge and core](../../specs/technical/01-architecture.md#edge-and-core) and [📡 Security: links](../../specs/technical/06-security.md#links).
- The shared async NATS client in `packages/python/`: request-reply with deadlines and idempotency keys, and durable consumers, as [🔁 API layer: internal calls](../../specs/technical/05-api.md#internal).

## Features, use cases and business rules

- [📏 BR-008: Operator isolation](../../specs/functional/business-rules/BR-008-operator-isolation.md)
- [📏 BR-014: Simulation isolation](../../specs/functional/business-rules/BR-014-simulation-isolation.md)

## Technical pages it builds on

- [🔲 Architecture: cells and the global layer](../../specs/technical/01-architecture.md#cells): a cell holds "its NATS cluster, databases, Valkey and object storage buckets".
- [🌐 Architecture: edge and core](../../specs/technical/01-architecture.md#edge-and-core): "When the edge loses the core, it keeps flying, buffers its messages in JetStream and its Flight log in SQLite, and replays them in order when the link returns."
- [📨 Data models: events and proposals](../../specs/technical/02-data-models.md#events): "NATS subjects follow `op.<operator_id>.mission.<mission_id>.<event>` and `op.<operator_id>.fleet.<event>`, so permissions and streams split by Operator."
- [🗄️ Storage: overview](../../specs/technical/03-storage.md#overview): events and work queues are on "NATS JetStream (replicated streams)".
- [🌐 Storage: the edge store and synchronisation](../../specs/technical/03-storage.md#edge-store): the leaf node "buffers while the core is unreachable and replays in order".
- [🔌 API layer: internal calls](../../specs/technical/05-api.md#internal): "Request-reply over NATS for commands and queries between services, with Pydantic payloads, deadlines and idempotency keys", and durable, idempotent consumers.
- [👥 Security: roles and Operator isolation](../../specs/technical/06-security.md#authorisation): "NATS accounts per Operator: a service acting for one Operator can only publish and subscribe on `op.<operator_id>.…`."
- [📡 Security: links](../../specs/technical/06-security.md#links): "Edge to cell: NATS leaf node over mTLS, credentials per edge node, revocable from the Back office."
- [🕹️ Engine and services: simulator](../../specs/technical/04-engine.md#simulator): "simulated Squads use separate NATS credentials".

## Screens touched

- The ticket touches no screen.

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

The "done when" of the roadmap row. The roadmap names no Given, when, then criterion of a feature for this ticket.

1. **Given** an Operator's NATS account, **when** a test publishes on another Operator's subject, **then** the publication is refused. ([📏 BR-008](../../specs/functional/business-rules/BR-008-operator-isolation.md))
2. **Given** a leaf node of an edge, **when** its link is cut for one minute and then restored, **then** its messages are replayed in order. ([📏 BR-008](../../specs/functional/business-rules/BR-008-operator-isolation.md))
3. **Given** simulated Squads with their own credentials, **when** they connect to NATS, **then** they use credentials separate from those of real Squads. ([📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md))

## Out of scope

- The dev cell platform on k3s (Argo CD, databases, Valkey, MinIO, vault), see [T0.08](../../specs/roadmap/01-p0-foundations.md#s02).
- The simulator service and its adapter registry, see [T0.13](../../specs/roadmap/01-p0-foundations.md#s03).
- Keycloak and gateway authentication, see [T0.11](../../specs/roadmap/01-p0-foundations.md#s03).
- Signed images, see [T0.10](../../specs/roadmap/01-p0-foundations.md#s02).

## Assumptions

- The roadmap row names no feature, use case or business rule. [📏 BR-008](../../specs/functional/business-rules/BR-008-operator-isolation.md) and [📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md) are linked because the roadmap names them for the Operator isolation and simulator epics that this ticket's accounts and credentials serve, and the criteria cite them as the most conservative link.
- The row names no row of the budgets table, so the ticket touches no budget.
- The row says "one minute" for the cut leaf node and quantifies nothing else, so no other duration is asserted.
- The row gives no mechanism for creating accounts (operator JWTs, decentralised auth or a configuration file), so the plan chooses the most conservative option and records it.
