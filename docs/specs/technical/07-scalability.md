# 🚀 Scalability and performance

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ Security](06-security.md) · 📄 **Page 102 / 120** · [Observability ▶️](08-observability.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> The targets Swarm must hold, how cells and a partitioned edge reach them, the techniques used on every hot path, and the budgets that load tests enforce. Decisions T21 to T25 and T27.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🎯 Targets](#targets)
2. [🔲 Cells](#cells)
3. [🌐 Partitioned edge for big Light shows](#big-shows)
4. [🧮 Techniques on the hot paths](#techniques)
5. [⏱️ Budgets](#budgets)
6. [🏋️ Load tests](#load-tests)
7. [🔗 Features implemented](#features)
<!-- /spec:summary -->

## <a id="targets"></a>🎯 Targets

| Dimension | Target (decision T21) |
| --- | --- |
| Operators | 10,000 |
| Missions in flight at once | 2,000 |
| Drones connected | 50,000 |
| Drones per Mission | up to 50 (Inspection, Agriculture, Patrol), up to 5,000 (Light show) |
| Telemetry | 20 Hz per Drone, 50 Hz in Light shows: about 1,000,000 frames per second across the platform |
| People connected | 50,000, of which 5,000 watching live video |
| On premises | 1 Operator, 20 Missions in flight (one cell) |

## <a id="cells"></a>🔲 Cells

| One cell holds | Limit | With |
| --- | --- | --- |
| Missions in flight | 200 | flight-engine edges connected through leaf nodes |
| Telemetry into the cell | 100,000 frames/s (about 5 MB/s MessagePack) | NATS cluster of 3, TimescaleDB primary with batched `COPY` |
| Live viewers | 5,000 WebSocket clients, 500 video viewers | gateway pods (about 1,000 sockets each), SFU nodes |
| Operators | about 1,000 | PostgreSQL primary and 2 replicas |

- **Count:** 2,000 Missions in flight need 10 cells; with 30 % headroom, **13 cells** across the regions at full target.
- **Placement:** the global layer maps each Operator to a cell; a growing Operator can be moved between cells during a planned window (data copied, edges re-pointed between flights).
- **Inside a cell:** stateless pods scale with the Kubernetes horizontal autoscaler (CPU, sockets); processing scales on queue depth with KEDA; every MCP server and A2A agent sits behind a Kubernetes Service and is scaled by KEDA (in-flight requests for `agents-mcp` and `agents-a2a`, queue lag for `agents-worker`); the GPU pool scales to zero when idle.
- **Blast radius:** a failing cell affects its Operators only; edges keep flying.

## <a id="big-shows"></a>🌐 Partitioned edge for big Light shows

- A show of more than 1,000 Drones is split into **sectors of up to 1,000 Drones**, each run by its own edge node with its own radios; sectors overlap at their borders, and each node checks separation across the overlap.
- A **show coordinator** at the edge keeps the time code for every sector and sends Hold the Squad or land to all sectors within 100 ms.
- The Choreography was checked offline by the planner, so the live tick only measures each Drone's deviation from its planned position.
- To protect the cell, a show sends Telemetry to the core at 5 Hz; the full-rate log is kept at the edge and uploaded after landing.

## <a id="techniques"></a>🧮 Techniques on the hot paths

| Path | Technique |
| --- | --- |
| Safety tick | Rust core, spatial hash grid (cost grows linearly with Drones), no allocation per tick, GIL released |
| Telemetry encoding | MessagePack via `ormsgpack` (Rust), integers for coordinates, delta encoding, 50 ms batches |
| Event loop | uvloop in every Python service; CPU-bound work in Rust or in worker processes |
| Bus | NATS subjects per Operator and Mission, so consumers read only what they need; JetStream replicas 3 |
| Fan-out | One NATS subscription per Mission per gateway, one-slot mailboxes per client, per-client rate |
| Database writes | Batched `COPY` into TimescaleDB, compression after 7 days, partitions by time and Mission |
| Database reads | Replicas, partial and spatial indexes, continuous aggregates for dashboards and the Co-pilot |
| Connections | PgBouncer (transaction mode), small async pools, HTTP/2 between gateway and clients |
| Static and media | CDN for Deliverables and LL-HLS, Cloud Optimized GeoTIFF and 3D Tiles fetched by range |
| Front ends | Web Worker decoding, typed arrays, deck.gl GPU layers, rendering at most 30 to 60 times per second ([🖥️ GUI and WebUI](10-frontends.md#live-data)) |

## <a id="budgets"></a>⏱️ Budgets

| Path | Budget (decision T22) |
| --- | --- |
| Pilot command to Drone, at the edge on a local link | p99 < 50 ms |
| Hold the Squad or abort, to every Drone | < 100 ms |
| Safety tick | < 5 ms for 500 Drones; < 10 ms per sector of 1,000 |
| Telemetry, Drone to Pilot's screen | p95 < 150 ms at the edge, < 400 ms through the cell |
| REST inside a cell | p95 < 100 ms reads, < 250 ms writes |
| WebRTC video | < 300 ms glass to glass |
| Choreography check, 1,000 Drones over 10 minutes | < 30 s |
| Orthomosaic of 1,000 images on one GPU worker | < 30 min |
| Cell rebuild (RTO) | < 1 hour; data loss (RPO) < 5 minutes |

## <a id="load-tests"></a>🏋️ Load tests

- **Per pull request:** Rust benchmarks (criterion) of the safety tick, the planner and the encoders; a regression of more than 5 % fails the build.
- **Nightly in staging:** one full cell at target load: 200 Missions of simulated Drones (synthetic Rust Drones for volume, PX4 SITL for a sample), k6 for REST and WebSocket clients, a 5,000-Drone show on a partitioned edge. Every budget above is an assertion; a miss fails the run and blocks releases.
- **Chaos:** pods killed, the edge link cut mid-flight, a database failover; Fail-safes, buffering and recovery must hold.

## <a id="features"></a>🔗 Features implemented

[📘 FS-003](../functional/features/FS-003-live-supervision.md), [📘 FS-004](../functional/features/FS-004-fail-safes-and-emergencies.md), [📘 FS-013](../functional/features/FS-013-light-shows.md), [📘 FS-021](../functional/features/FS-021-ground-control-monitoring.md), [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md).

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ Security](06-security.md) · 📄 **Page 102 / 120** · [Observability ▶️](08-observability.md)
<!-- /spec:nav-bottom -->
