# 🗄️ Storage

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ Data models](02-data-models.md) · 📄 **Page 98 / 120** · [Engine and services ▶️](04-engine.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> Where each kind of data lives, how Operators are kept apart, how long data is kept and how a cell recovers. Decisions T5 to T8, T36 and T37.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🔭 Overview](#overview)
2. [🗄️ PostgreSQL and PostGIS](#postgresql)
3. [🗄️ Repositories](#repositories)
4. [🕰️ TimescaleDB for Telemetry](#timescaledb)
5. [🪣 Object storage](#object-storage)
6. [🌐 The edge store and synchronisation](#edge-store)
7. [🗑️ Retention](#retention)
8. [💾 Backups and recovery](#backups)
9. [🔗 Features implemented](#features)
<!-- /spec:summary -->

## <a id="overview"></a>🔭 Overview

| Data | Store | Why |
| --- | --- | --- |
| Operators, Missions, Fleet, Authorisations, Geofences, routes, Defects, Scorecards | PostgreSQL 16 + PostGIS | Relations, transactions, spatial indexes |
| Telemetry, Flight log entries, Alerts | TimescaleDB (in the same PostgreSQL) | Time series with compression and aggregates, joins with Missions |
| Images, video, point clouds, Deliverables, evidence files, Parquet archives | S3-compatible object storage | Cheap, scalable, object lock |
| Cache, presence of Pilots on duty, rate limits, live fan-out state | Valkey | Sub-millisecond, ephemeral |
| Everything a flight needs at the edge | SQLite (WAL mode) | Embedded, survives power loss, no server |
| Events and work queues | NATS JetStream (replicated streams) | Ordered, replayable, edge buffering |

## <a id="postgresql"></a>🗄️ PostgreSQL and PostGIS

- **One schema per service** (`missions`, `fleet`, `processing`, `evidence`, `notifier`); a service reads and writes only its own schema. Cross-service data comes through events.
- **Operator isolation:** every Operator-owned table has `operator_id`; row-level security policies compare it with the session setting `swarm.operator_id`, set by the service from the verified token on each transaction. A query that forgets the filter returns nothing instead of another Operator's rows ([📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md)).
- **Indexes:** B-tree on `(operator_id, id)` and on foreign keys; GiST on geometries (Geofences, routes, Fields, Prescription map zones, Defect positions); partial indexes on active states (`state IN ('planned','verified','flying')`).
- **Large tables** (Defects, Notifications, Flight log entries outside TimescaleDB) are partitioned by month.
- **Connections:** PgBouncer in transaction mode in front of each primary; services use an async client library (`asyncpg`) with small pools.
- **Reads:** one or two streaming replicas per cell serve the Client portal, the Back office lists and the agents' read tools.
- **Migrations:** Alembic per service, run by a pre-deploy step; expand then contract (never a breaking migration in one release).

## <a id="repositories"></a>🗄️ Repositories

**Every entity stored in PostgreSQL has its own repository** (decision T42), in the `storage/postgres/` module of the service that owns it, one class per file (AGENT.md), grouped in sub-packages of at most five files.

| Service | Repositories (`storage/postgres/…`) |
| --- | --- |
| missions | `MissionRepository`, `SquadMemberRepository`, `GeofenceRepository`, `RouteRepository`, `ChoreographyRepository`, `FieldRepository`, `PrescriptionMapRepository`, `PatrolRouteRepository`, `SiteRepository`, `AlarmRepository`, `AuthorisationRepository`, `PreFlightCheckRepository`, `ReplanRepository`, `AcceptanceCriterionRepository`, `ScorecardRepository`, `WorkspaceRepository`, `PilotSettingsRepository` |
| fleet | `DroneRepository`, `DroneModelRepository`, `PayloadRepository`, `BatteryRepository`, `DockRepository`, `FieldKitRepository`, `MaintenanceRecordRepository`, `CompatibilityTestRepository` |
| processing | `ProcessingTaskRepository`, `DeliverableRepository`, `DefectRepository`, `DetectionModelRepository` |
| agents | `ProposalRepository`, `AgentSessionRepository`, `DelegationRepository` |
| evidence | `EvidenceRecordRepository`, `AnchorReceiptRepository` |
| notifier | `NotificationRepository`, `DeliveryAttemptRepository` |
| gateway | `ApiTokenRepository`, `WebhookSubscriptionRepository` |
| global layer | `OperatorRepository`, `ClientAccountRepository`, `CellAssignmentRepository` |
| TimescaleDB (missions, flight data) | `TelemetryFrameRepository` (batched `COPY` writes, time-window reads), `FlightLogEntryRepository`, `AlertRepository` |

How every repository works:

- **One base class**, `PostgresRepository[Model]` in `packages/python/swarm-storage`: maps rows to the Pydantic model and back, sets `swarm.operator_id` on the transaction for row-level security, pages with cursors, and checks a `version` column on update (optimistic concurrency, which the REST layer exposes as `ETag`).
- **Methods named after what the service needs**, beyond `get`, `list`, `add`, `update` and `delete`: `MissionRepository.flying_in_cell()`, `DroneRepository.ready_for(drone_model_id)`, `DefectRepository.suspected_for(deliverable_id)`, `AuthorisationRepository.expiring_within(days)`.
- **Unit of work:** a service opens one `UnitOfWork` per business operation; every repository it uses shares the same transaction, and events go into an **outbox** table in that transaction, published to NATS JetStream by a relay afterwards, so a change and its event never disagree.
- **No SQL outside repositories**; queries are written with SQLAlchemy Core expressions or plain SQL in the repository, measured in the query budget of the service.
- **Tests** run each repository against a real PostgreSQL with PostGIS and TimescaleDB (AGENT.md: real things, no mocks), including a test that another Operator's rows are never returned.

## <a id="timescaledb"></a>🕰️ TimescaleDB for Telemetry

| Hypertable | Chunk | Compression | Kept |
| --- | --- | --- | --- |
| `telemetry_frames` (one row per Drone per tick) | 1 hour, space-partitioned by `mission_id` | after 7 days, segment by `drone_id`, order by `t_us` (10 to 20 times smaller) | 90 days, then archived |
| `flight_log_entries` (commands, Alerts, decisions) | 1 day | after 7 days | as long as the Evidence record |
| `telemetry_1s`, `telemetry_1min` (continuous aggregates) | | | 5 years |

- **Writes:** the cell's telemetry writer consumes JetStream in batches of up to 5,000 frames or 200 ms and inserts with `COPY`; one writer per partition of Missions keeps order and saturates no lock.
- **Reads:** Replay and the Debrief read the full-rate table for one Mission and time window (chunk exclusion makes it fast); dashboards, plan-against-actual and the Co-pilot read the aggregates.
- **Archive:** after 90 days, frames are exported per Mission to Parquet in object storage, fingerprinted in the Evidence record, then dropped from TimescaleDB.

## <a id="object-storage"></a>🪣 Object storage

```text
op-<operator_id>/                      one bucket per Operator, encrypted, versioned
├── missions/<mission_id>/raw/<drone_id>/…        images, video segments (90 days)
├── missions/<mission_id>/telemetry/*.parquet     archived frames
├── deliverables/<deliverable_id>/…               orthomosaics (COG), 3D Tiles, reports
├── evidence/<record_id>/…                        object lock (WORM), retention per Operator
└── models/<model_id>/…                           the Operator's own detection models
```

- **Uploads from the edge:** resumable multipart uploads with SHA-256 checksums, which the Evidence records reuse.
- **Delivery:** signed URLs with short expiry; a CDN in front for Deliverables and LL-HLS segments in the cloud.
- **On premises:** MinIO with the same layout.

## <a id="edge-store"></a>🌐 The edge store and synchronisation

- When the Pre-flight check starts, the flight engine copies into SQLite everything the flight needs: the Mission, its Squad members, Geofence, routes or Choreography, Authorisation, Drone model limits and Alert thresholds. From then on, **the edge is authoritative for the flight**.
- The Flight log is written to SQLite first (fsync per batch of 100 ms), then published to JetStream through the leaf node. The leaf node buffers while the core is unreachable and replays in order; the core deduplicates by `(drone_id, seq)`.
- Changes made in the core during a flight (a new Authorisation, a Mission edit) reach the edge as events and apply only between flights, except Alerts and Notifications.
- The edge SQLite file is encrypted (SQLCipher) because the field laptop can be lost.

## <a id="retention"></a>🗑️ Retention

| Data | Kept | Then |
| --- | --- | --- |
| Full-rate Telemetry | 90 days in TimescaleDB | Parquet archive for the life of its Evidence record (Operator setting, default 5 years) |
| Telemetry aggregates | 5 years | Deleted |
| Raw images and video | 90 days (GDPR default, Operator setting) | Deleted, fingerprints kept |
| Deliverables, evidence files, Flight logs | 5 years, object lock | Deleted at the end of the lock |
| Data of a deleted Operator | 30 days | Erased; fingerprints kept |

## <a id="backups"></a>💾 Backups and recovery

- **PostgreSQL and TimescaleDB:** continuous WAL archiving to object storage with pgBackRest, daily full backups, point-in-time recovery; **RPO 5 minutes**.
- **Object storage:** replicated to a second availability zone (or a second MinIO site on premises).
- **NATS JetStream:** streams replicated three times inside the cell.
- **Rebuild:** a cell is rebuilt from GitOps and its backups in **under 1 hour (RTO)**; the edges keep flying meanwhile and resynchronise afterwards.
- **Drills:** a full restore in staging every month; a failed drill is an incident.

## <a id="features"></a>🔗 Features implemented

[📘 FS-005](../functional/features/FS-005-fleet-and-readiness.md), [📘 FS-007](../functional/features/FS-007-data-processing-and-deliverables.md), [📘 FS-009](../functional/features/FS-009-evidence-ledger-and-anchoring.md), [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md), [📘 FS-022](../functional/features/FS-022-debrief-and-assessment.md).

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ Data models](02-data-models.md) · 📄 **Page 98 / 120** · [Engine and services ▶️](04-engine.md)
<!-- /spec:nav-bottom -->
