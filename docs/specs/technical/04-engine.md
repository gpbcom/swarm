# 🔩 Engine and services

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ Storage](03-storage.md) · 📄 **Page 88 / 108** · [API layer ▶️](05-api.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> What each service does and how its hot paths meet their budgets: the flight engine and its safety loop, the Drone adapters, the planner, processing, the AI agents with MCP and A2A, evidence, notifications and the simulator. Decisions T2, T9 to T12.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🔭 Overview](#overview)
2. [🔩 Flight engine](#flight-engine)
3. [🛡️ Safety loop](#safety-loop)
4. [🧷 Drone adapters](#adapters)
5. [🧮 Planner](#planner)
6. [🏭 Processing](#processing)
7. [💬 Agents, MCP and A2A](#agents)
8. [🔏 Evidence](#evidence)
9. [🔔 Notifier](#notifier)
10. [🕹️ Simulator](#simulator)
<!-- /spec:summary -->

## <a id="overview"></a>🔭 Overview

| Service | Runs at | Language | Scales by | Main features |
| --- | --- | --- | --- | --- |
| flight-engine | Edge | Python + Rust core | One process per edge, one actor per Mission; sectors for big shows | [📘 FS-002](../functional/features/FS-002-pre-flight-check-and-launch.md), [📘 FS-003](../functional/features/FS-003-live-supervision.md), [📘 FS-004](../functional/features/FS-004-fail-safes-and-emergencies.md) |
| video-relay | Edge | Python + GStreamer | One per edge | [📘 FS-021](../functional/features/FS-021-ground-control-monitoring.md) |
| gateway | Cell | Python (FastAPI, uvloop) | Stateless pods, HPA on connections and CPU | [📘 FS-008](../functional/features/FS-008-client-portal.md) |
| missions, fleet | Cell | Python | Stateless pods | [📘 FS-001](../functional/features/FS-001-mission-design.md), [📘 FS-005](../functional/features/FS-005-fleet-and-readiness.md), [📘 FS-006](../functional/features/FS-006-authorisations-and-compliance.md) |
| planner | Cell and edge (library) | Rust core, Python service | Pods, CPU-bound | [📘 FS-001](../functional/features/FS-001-mission-design.md), [📘 FS-013](../functional/features/FS-013-light-shows.md), [📘 FS-014](../functional/features/FS-014-agriculture.md) |
| processing | Cell | Python workers | GPU pool, KEDA on queue depth | [📘 FS-007](../functional/features/FS-007-data-processing-and-deliverables.md), [📘 FS-016](../functional/features/FS-016-inspection.md) |
| agents | Cell | Python (LangGraph) | Three Deployments (MCP, A2A, worker), each behind a Kubernetes Service and scaled by KEDA | [📘 FS-017](../functional/features/FS-017-mission-assistant.md), [📘 FS-018](../functional/features/FS-018-live-co-pilot.md), [📘 FS-019](../functional/features/FS-019-mission-reports.md) |
| evidence | Cell | Python + Rust hashing | Pods; one writer per Operator chain | [📘 FS-009](../functional/features/FS-009-evidence-ledger-and-anchoring.md) |
| notifier | Cell | Python | Pods | [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md) |
| simulator | Cell and staging | Rust + PX4 SITL | Nodes | [📘 FS-010](../functional/features/FS-010-simulator-and-training.md), [📘 FS-011](../functional/features/FS-011-drone-adapters.md) |

Every Python service follows AGENT.md: layers `api`, `service`, `storage`, `models`; runnables with `initialize`, `run`, `close`; factories; logging rules.

## <a id="flight-engine"></a>🔩 Flight engine

- **One asyncio process per edge** (uvloop), one **actor per Mission** holding its Squad state. CPU-heavy steps run in the Rust core (`packages/rust/swarm-core`, PyO3), which releases the GIL.
- **Input:** each Drone adapter writes the latest frame of each Drone into a lock-free ring buffer in Rust; the actor never waits for a slow Drone.
- **Output:** one `SquadFrame` per tick to Ground control (local WebSocket) and to the leaf node; Alerts; commands.
- **Command lanes:** the safety lane (Hold the Squad, abort, Return home, manual control) is served before anything else and acknowledged per Drone; the Pilot's command reaches the adapter without crossing the core.
- **Pre-flight check** ([📏 BR-007](../functional/business-rules/BR-007-launch-only-after-a-passed-pre-flight-check.md)): checks that need the core (U-space grant, Authorisation validity, weather) are fetched while online and expire with the 30-minute validity; without them the check fails.

## <a id="safety-loop"></a>🛡️ Safety loop

Two layers (decision T10):

| Layer | Holds | Acts when |
| --- | --- | --- |
| On board, uploaded by the adapter before take-off | Geofence and Altitude ceiling, Link-loss Fail-safe (Return home after 5 s), battery Fail-safe at the landing reserve, Return home altitude | Always, even if the edge stops |
| At the edge, a deterministic tick per Mission (20 Hz, 50 Hz for Light shows) | Separation, Geofence margin, weather, landing reserve, Link timers, deviation from the Choreography, Alert thresholds | Every tick |

Each tick, in the Rust core:

1. **Separation:** a uniform spatial hash grid with a cell the size of the Separation distance; each Drone is compared only with Drones in its own and neighbouring cells, so the cost grows with the number of Drones, not with its square.
2. **Geofence:** prepared polygons in an R-tree, plus the ceiling; the margin before the edge triggers a Hold, then Return home ([📏 BR-001](../functional/business-rules/BR-001-geofence-and-altitude-ceiling.md)).
3. **Energy:** remaining battery against the energy needed to reach home with the landing reserve, per Drone model ([📏 BR-012](../functional/business-rules/BR-012-pilot-override-always-available.md)).
4. **Light shows:** distance between each Drone and its Choreography position at the current time code; beyond tolerance, the Fail-safe of [📏 BR-006](../functional/business-rules/BR-006-fail-safe-per-activity.md).
5. **Decisions:** Alerts, Fail-safe commands, and Re-plan triggers handed to the planner library at the edge, so supervised autonomy works offline.

**Budget:** a tick takes less than 5 ms for 500 Drones and less than 10 ms per sector of 1,000 Drones; measured by benchmarks on every pull request.

## <a id="adapters"></a>🧷 Drone adapters

| Family | Order | Implementation |
| --- | --- | --- |
| MAVLink (PX4, ArduPilot) | 1 | Rust MAVLink 2 parser and signer in the flight engine; radio, cellular (WireGuard) and mesh links |
| Parrot | 2 | Sidecar process using Parrot's SDK, bridged to the flight engine over a local socket |
| DJI, Skydio | Later | Sidecars using the vendors' SDKs or cloud APIs, same interface |

Every adapter implements one interface: connect, upload (Geofence, Fail-safes, route), arm and take off, go to, Hold, Return home, land, Payload control, Telemetry stream. A Drone model is approved only after the compatibility test suite passes, first against the simulator, then in one real flight ([📏 BR-015](../functional/business-rules/BR-015-approved-drone-models-only.md)).

## <a id="planner"></a>🧮 Planner

Written in Rust, used both as a library (in the flight engine, for offline Re-plans) and as the `planner` service (design time, through NATS request-reply).

- **Coverage paths** (Inspection, Agriculture): boustrophedon decomposition of the area, then assignment balanced by each Drone's Payload, speed and battery ([📏 BR-022](../functional/business-rules/BR-022-payload-compatibility.md)).
- **Choreography checks** (Light shows): every frame checked in parallel (rayon) for separation, speed, acceleration and battery; 1,000 Drones over 10 minutes in under 30 seconds.
- **Re-plans:** share the remaining area of a lost or returning Drone between the others, plan refills for Agriculture, reroute patrols to an Alarm.
- **Prescription maps:** Shapefile and ISOXML parsed into zones with a dose each ([📏 BR-018](../functional/business-rules/BR-018-dose-follows-the-prescription-map.md)).

## <a id="processing"></a>🏭 Processing

- **Work queue:** NATS JetStream with priorities (detection before photogrammetry, interactive before batch).
- **Workers:** photogrammetry (OpenDroneMap through NodeODM, GPU, large Sites split into sub-models and merged), detection (ONNX Runtime on GPU, one model per target, Operators' own models from their registry), tiling (Cloud Optimized GeoTIFF, 3D Tiles), video (clips, face blurring for Client-visible video).
- **Training:** PyTorch training runs on the same GPU pool for the Swarm models and for Operators' own models, scoped to the Operator's data.
- **Output:** each Deliverable goes Processing, then In review; a person publishes it ([📏 BR-020](../functional/business-rules/BR-020-defects-confirmed-by-a-person.md)).

## <a id="agents"></a>💬 Agents, MCP and A2A

- **Graphs:** one LangGraph graph per agent (Mission assistant, Co-pilot, Report writer), nodes as AGENT.md `TaskNode` classes; the chat model comes from the Operator's LLM provider (Claude by default in the cloud, an open-weight model on premises).
- **Tools:** typed Python functions that read through the services (NATS request-reply, read replicas) or create `Proposal` objects. The Co-pilot reads 1-second aggregates and Alerts, never the raw stream, and is never in the safety loop.
- **MCP server:** the same tools exposed with the MCP Python SDK, per Operator, OAuth 2.1 from Keycloak, off until the Operator enables it.
- **A2A:** each agent published with an Agent Card; outside agents can delegate tasks to them, and Swarm's agents can call outside agents the Operator registered.
- **Outside agents** get the rights of the person they act for; the human gate of [📏 BR-021](../functional/business-rules/BR-021-ai-agents-propose-people-decide.md) is enforced in the gateway and the missions service, not in the agent (see [🔐 Security](06-security.md#human-gate)).
- **Evaluations:** prompts, tools and test sets are versioned in the repository and run in CI; a drop in score fails the build.

**Deployment of the agents (decision T39).** The `agents` service builds one image run as three Kubernetes Deployments, **each behind its own Kubernetes Service and scaled by KEDA**:

| Deployment | Kubernetes Service | Serves | KEDA scaler | Replicas (production) |
| --- | --- | --- | --- | --- |
| `agents-mcp` | `agents-mcp` (ClusterIP, port 8080) | The MCP server, Streamable HTTP, one endpoint per Operator | Prometheus: in-flight MCP requests per pod (target 50), plus CPU | 2 to 40 |
| `agents-a2a` | `agents-a2a` (ClusterIP, port 8080) | The A2A endpoints and Agent Cards of the Mission assistant, Co-pilot and Report writer | Prometheus: in-flight A2A requests and open task streams per pod (target 50), plus CPU | 2 to 40 |
| `agents-worker` | `agents-worker` (ClusterIP, health and metrics only) | Long agent runs: graphs started by MCP, A2A, Ground control or the Back office, taken from a JetStream work queue | NATS JetStream: consumer lag (target 10 runs per pod) | 0 to 100 |

- The gateway routes `/mcp/…`, `/a2a/…` and `/.well-known/agent.json` to these Services; nothing reaches an agent pod directly.
- **Stateless pods:** MCP sessions (`Mcp-Session-Id`) and A2A task state live in Valkey and JetStream, so any pod serves any request and KEDA can add or remove pods at any time; scale-in waits for in-flight requests to finish (graceful drain of 60 seconds).
- **Minimum two replicas** of `agents-mcp` and `agents-a2a` in production keep them answering without a cold start; in dev and simulation they scale to zero through the KEDA HTTP add-on.

## <a id="evidence"></a>🔏 Evidence

- **Chain:** one append-only chain per Operator; each Evidence record holds the SHA-256 of its content, the hash of the previous record and an Ed25519 signature with the cell's key from the vault.
- **Anchoring:** every hour, a Merkle tree of the hour's records; its root is anchored with the Operator's choice: a qualified timestamping authority (RFC 3161, default) or a public blockchain through an aggregator. Receipts are stored with the records.
- **Verification:** an API and a Client portal page recompute the hash, walk the chain and check the receipt ([📏 BR-009](../functional/business-rules/BR-009-evidence-integrity.md)).

## <a id="notifier"></a>🔔 Notifier

- **Channels:** in-app (stored and pushed over WebSocket), e-mail (SMTP relay), push to mobiles as Web Push (the web apps are installable), so no native mobile app is needed.
- **Rules:** deduplication per event, rate limits per person, quiet hours except safety; texts translated with Babel in the person's language ([📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md)).

## <a id="simulator"></a>🕹️ Simulator

- **Fidelity:** PX4 SITL in containers (headless Gazebo), about 50 Drones per node, for Mission tests, training and compatibility tests.
- **Volume:** synthetic Drones written in Rust that speak MAVLink and follow routes, thousands per node, for load tests and big Light shows.
- **Isolation:** simulated Squads use separate NATS credentials and an adapter registry that cannot address a real Drone, and every Flight log is marked simulated ([📏 BR-014](../functional/business-rules/BR-014-simulation-isolation.md)).

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ Storage](03-storage.md) · 📄 **Page 88 / 108** · [API layer ▶️](05-api.md)
<!-- /spec:nav-bottom -->
