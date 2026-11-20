# 🛣️ P1: First flight

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ P0: Foundations](01-p0-foundations.md) · 📄 **Page 108 / 120** · [P2: Inspection product ▶️](03-p2-inspection-product.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Sprints:** S05 to S13 · **Dates:** 1 Mar to 2 Jul 2027 · **Tickets:** about 45

> [!NOTE]
> P1 takes Swarm from a simulated Squad on a map to a real X500 [🗃️ Drone](../glossary.md#ent-drone), one at a time as the Open category allows, flown through the full [🗃️ Squad](../glossary.md#ent-squad) pipeline with every [🔤 Fail-safe](../glossary.md#term-fail-safe) tested, while the same Mission flies as a Squad of 4 under supervised autonomy in the Simulator (milestone M1, 18 June 2027), and signs the design-partner [🗃️ Operator](../glossary.md#ent-operator) (M1b); it comes now because every later Activity flies on this flight engine, safety loop, Drone adapter and [⚙️ Ground control](../glossary.md#sys-ground-control).

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🎯 Goal](#goal)
2. [🧺 Scope](#scope)
3. [🪜 Epics](#epics)
4. [🗓️ Sprint plan](#sprints)
5. [🎤 Demo](#demo)
6. [🚪 Exit criteria](#exit)
7. [⛓️ Dependencies](#dependencies)
8. [🎲 Risks](#risks)
9. [🧑‍💻 Work split](#work-split)
<!-- /spec:summary -->

## <a id="goal"></a>🎯 Goal

Deliver the whole flight path of an [🔤 Inspection](../glossary.md#term-inspection), from design to landing, safe enough to fly real Drones, and prove it in the field:

- **Design.** The [👤 Mission planner](../glossary.md#per-mission-planner) draws the [🗃️ Geofence](../glossary.md#ent-geofence) of an Inspection in the [⚙️ Mission studio](../glossary.md#sys-mission-studio), builds a Squad where each Drone has its own [🗃️ Payload](../glossary.md#ent-payload) and task, lets the planner compute the coverage routes, and simulates the [🗃️ Mission](../glossary.md#ent-mission) in the [⚙️ Simulator](../glossary.md#sys-simulator) before it flies.
- **Fleet and Authorisations.** The [👤 Fleet maintainer](../glossary.md#per-fleet-maintainer) registers Drones, Payloads and Batteries ([🗃️ Battery](../glossary.md#ent-battery)) and tracks their readiness in the [⚙️ Back office](../glossary.md#sys-back-office); the Mission planner records the [🗃️ Authorisations](../glossary.md#ent-authorisation). Only Drones of an approved [🗃️ Drone model](../glossary.md#ent-drone-model) fly: the X500 (PX4, MAVLink) is approved through the Simulator, then one real flight.
- **Launch.** The [👤 Pilot](../glossary.md#per-pilot) configures each Drone on the [🗃️ Site](../glossary.md#ent-site), runs the [🗃️ Pre-flight check](../glossary.md#ent-pre-flight-check) (Geofence, weather from the [⚙️ Weather service](../glossary.md#sys-weather-service), Authorisation, [🔤 Pilot ratio](../glossary.md#term-pilot-ratio), readiness, [🔤 Links](../glossary.md#term-link), and the [⚙️ U-space service](../glossary.md#sys-u-space-service) where the Jurisdiction requires it), signs it with a PIN and launches.
- **Fly safely.** The flight engine runs at the edge with its Rust safety loop: Geofence and Fail-safes uploaded on board, a deterministic tick per Mission at 20 Hz for separation, Geofence margin, weather, landing reserve and Link timers. The Squad proposes [🗃️ Re-plans](../glossary.md#ent-re-plan) when a Drone returns or is lost; the Pilot approves them. The [⚙️ Co-pilot](../glossary.md#sys-co-pilot) comes in P5: in P1, Re-plans are proposed by the Squad and Alerts carry their facts and actions without the Co-pilot's explanation.
- **The Pilot always in command.** [🔤 Hold](../glossary.md#term-hold) the Squad and abort, held 1 second, on every screen; manual control with a gamepad; [🔤 Return home](../glossary.md#term-return-home) for one Drone or all.
- **Ground control.** The [🗃️ Workspace](../glossary.md#ent-workspace) over several screens, on the Tauri desktop app and in the web browser, with the map, the Squad, live video in the [🔤 Mosaic](../glossary.md#term-mosaic), the [🔤 Focus view](../glossary.md#term-focus-view), [🔤 Alerts](../glossary.md#term-alert) and progress; laptop and tablet layouts.
- **Training.** An [👤 Instructor](../glossary.md#per-instructor) runs a training session in the Simulator and injects failures for the trainee Pilot.
- **Milestones.** **M1, 18 June 2027 (S12):** during the flight test campaign [🛫 C-01](10-flight-test-campaigns.md#c-01), one real X500 at a time flies an Inspection through the full Squad pipeline (Pre-flight check, flight engine, safety loop, every Fail-safe, manual control), in visual line of sight under the Open category, while the same Mission is flown by a Squad of 4 under supervised autonomy in the Simulator (PX4 SITL). In the EU Open category the Pilot flies one real Drone at a time: the first real Squad flight (4 Drones, one Pilot) comes with [🛫 C-02](10-flight-test-campaigns.md#c-02) in [🛣️ P2: Inspection product](03-p2-inspection-product.md), after the Specific category Authorisation of [🏛️ G-05](09-regulatory-track.md#g-05). **M1b, 18 June 2027:** the design partner [🤝 P-01](11-hardware-and-partners.md#p-01), a drone service company, commits to the Inspection beta of [🛣️ P2: Inspection product](03-p2-inspection-product.md).

## <a id="scope"></a>🧺 Scope

**📘 Features**

| Feature | Delivered in P1 | Acceptance criteria closed |
| --- | --- | --- |
| [📘 FS-001: Mission design](../functional/features/FS-001-mission-design.md) | Inspection Missions designed and simulated ([🎬 UC-001](../functional/use-cases/UC-001-design-a-mission.md), [🎬 UC-002](../functional/use-cases/UC-002-simulate-a-mission.md)); the other Activities in their phases; the Mission assistant in P5 | AC-1, AC-2, AC-3 |
| [📘 FS-002: Pre-flight check and launch](../functional/features/FS-002-pre-flight-check-and-launch.md) | All of it | AC-1, AC-2, AC-3 |
| [📘 FS-003: Live supervision](../functional/features/FS-003-live-supervision.md) | Supervision and Re-plans proposed by the Squad; Re-plans proposed by the Co-pilot in P5 | AC-1, AC-2 |
| [📘 FS-004: Fail-safes and emergencies](../functional/features/FS-004-fail-safes-and-emergencies.md) | Fail-safes of Inspection, manual control, Hold the Squad, abort, Return to Squad; the whole-Squad Fail-safe of Light shows in P6 | AC-1, AC-3 (AC-2 closes in P6) |
| [📘 FS-005: Fleet and readiness](../functional/features/FS-005-fleet-and-readiness.md) | Drones, Payloads, Batteries, maintenance, readiness; Docks in P3 | AC-1, AC-2 |
| [📘 FS-006: Authorisations and compliance](../functional/features/FS-006-authorisations-and-compliance.md) | All of it | AC-1, AC-2 |
| [📘 FS-010: Simulator and training](../functional/features/FS-010-simulator-and-training.md) | Simulating a Mission and training sessions with an Instructor | AC-1 |
| [📘 FS-011: Drone adapters](../functional/features/FS-011-drone-adapters.md) | The MAVLink Drone adapter (PX4, ArduPilot) and the compatibility test, applied to the X500; Parrot in P3, DJI and Skydio in P7 | AC-1 (MAVLink) |
| [📘 FS-020: Ground control workspace and configuration](../functional/features/FS-020-ground-control-workspace-and-configuration.md) | All of it, on desktop, laptop, tablet and web browser | AC-1, AC-2, AC-3 |
| [📘 FS-021: Ground control monitoring](../functional/features/FS-021-ground-control-monitoring.md) | All of it except the Co-pilot's explanation of an Alert (P5) | AC-1, AC-3, AC-4; AC-2 without the Co-pilot's explanation (completed in P5) |

**🎬 Use cases**

Screens that show the Co-pilot (its line in the Alerts area, its explanation or its proposal) stay ✏️ Mock-up until P5 delivers it, so that no screenshot removes it from the specification.

| Use case | In P1 | Screens moved to 📸 Screenshot |
| --- | --- | --- |
| [🎬 UC-001: Design a Mission](../functional/use-cases/UC-001-design-a-mission.md) | Delivered for Inspection, every alternative flow | A1, A2, A3, OK, KO |
| [🎬 UC-002: Simulate a Mission](../functional/use-cases/UC-002-simulate-a-mission.md) | Delivered | A1, A2, A3, OK, KO |
| [🎬 UC-003: Run the Pre-flight check and launch](../functional/use-cases/UC-003-run-the-pre-flight-check-and-launch.md) | Delivered | A1, A2, A3, KO (OK in P5: it shows the Co-pilot) |
| [🎬 UC-004: Supervise a Squad and approve a Re-plan](../functional/use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md) | Delivered with Re-plans proposed by the Squad; the Co-pilot part in P5 | None: every screen shows the Co-pilot (P5) |
| [🎬 UC-005: Lose a Drone in flight](../functional/use-cases/UC-005-lose-a-drone-in-flight.md) | Delivered | KO (A1, A2, OK in P5) |
| [🎬 UC-006: Take manual control or abort](../functional/use-cases/UC-006-take-manual-control-or-abort.md) | Delivered | None: every screen shows the Co-pilot (P5) |
| [🎬 UC-007: Register a Drone and track its readiness](../functional/use-cases/UC-007-register-a-drone-and-track-its-readiness.md) | Delivered | A1, A2, KO1, A3, OK, KO2 |
| [🎬 UC-008: Record an Authorisation](../functional/use-cases/UC-008-record-an-authorisation.md) | Delivered | A1, KO1, OK, A2, KO2 |
| [🎬 UC-013: Train on the Simulator](../functional/use-cases/UC-013-train-on-the-simulator.md) | Delivered; the Replay of the session in the Debrief comes in P2 | A1, A2, A3, KO (OK in P2: it opens the Replay) |
| [🎬 UC-014: Connect a new Drone model](../functional/use-cases/UC-014-connect-a-new-drone-model.md) | Delivered for MAVLink Drone models: the X500 approved in the Simulator, then in one real flight | None: its screens show the ANAFI USA, captured in P3 with the Parrot adapter |
| [🎬 UC-023: Configure the Workspace of Ground control](../functional/use-cases/UC-023-configure-the-workspace-of-ground-control.md) | Delivered | A1, A2, A3, A4, OK, KO1, KO2 |
| [🎬 UC-024: Configure each Drone of the Squad on the Site](../functional/use-cases/UC-024-configure-each-drone-of-the-squad-on-the-site.md) | Delivered | A1, A2, A3, OK, KO |
| [🎬 UC-025: Monitor a Mission in Ground control](../functional/use-cases/UC-025-monitor-a-mission-in-ground-control.md) | Delivered without the Co-pilot | None: every screen shows the Co-pilot (P5) |
| [🎬 UC-026: Handle an Alert](../functional/use-cases/UC-026-handle-an-alert.md) | Delivered without step 2 (the Co-pilot explains the Alert, P5): the Alert shows its facts and the actions available | None: every screen shows the Co-pilot (P5) |
| [🎬 UC-030: Focus on a Drone](../functional/use-cases/UC-030-focus-on-a-drone.md) | Delivered | None: every screen shows the Co-pilot (P5) |

In all, 42 of the 79 states of these use cases move to 📸 Screenshot in P1; 31 wait for the Co-pilot (P5), 5 for the Parrot adapter (P3) and 1 for the Debrief (P2).

**📏 Business rules**

| Rule | In P1 |
| --- | --- |
| [📏 BR-001: Geofence and Altitude ceiling](../functional/business-rules/BR-001-geofence-and-altitude-ceiling.md) | Delivered: refused at design time, uploaded on board, Geofence margin checked every tick (Hold, then Return home) |
| [📏 BR-002: Separation distance](../functional/business-rules/BR-002-separation-distance.md) | Delivered for Squads of up to 50 Drones: in planning, in simulation and every tick at the edge; Choreographies in P6 |
| [📏 BR-003: Weather limits](../functional/business-rules/BR-003-weather-limits.md) | Delivered: weather check of the Pre-flight check, Return home in flight when the weather leaves the limits |
| [📏 BR-004: Pilot ratio](../functional/business-rules/BR-004-pilot-ratio.md) | Delivered: from the Authorisation to the Pre-flight check |
| [📏 BR-005: Autonomy level per Activity](../functional/business-rules/BR-005-autonomy-level-per-activity.md) | Delivered for Inspection (Supervised autonomy); the other Activities in their phases |
| [📏 BR-006: Fail-safe per Activity](../functional/business-rules/BR-006-fail-safe-per-activity.md) | Delivered for Inspection: the failing Drone Returns home or lands, the others share its work, the Mission is Held under the minimum; Light shows in P6 |
| [📏 BR-007: Launch only after a passed Pre-flight check](../functional/business-rules/BR-007-launch-only-after-a-passed-pre-flight-check.md) | Delivered: every check, the checklist per Activity, the PIN, the 30-minute validity |
| [📏 BR-010: Valid Authorisation for the Jurisdiction](../functional/business-rules/BR-010-valid-authorisation-for-the-jurisdiction.md) | Delivered, with Planned Missions back to Draft on expiry |
| [📏 BR-011: Drone readiness](../functional/business-rules/BR-011-drone-readiness.md) | Delivered |
| [📏 BR-012: Pilot override always available](../functional/business-rules/BR-012-pilot-override-always-available.md) | Delivered on the safety lane of the flight engine |
| [📏 BR-013: Re-plan approval](../functional/business-rules/BR-013-re-plan-approval.md) | Delivered for Re-plans proposed by the Squad, with the 60-second answer time |
| [📏 BR-015: Approved Drone models only](../functional/business-rules/BR-015-approved-drone-models-only.md) | Delivered: the compatibility test, the firmware rule; applied to the X500 |
| [📏 BR-022: Payload compatibility](../functional/business-rules/BR-022-payload-compatibility.md) | Delivered: at registration, at design time and on the Site |
| [📏 BR-023: Fixed safety controls](../functional/business-rules/BR-023-fixed-safety-controls.md) | Delivered on every platform of Ground control |
| [📏 BR-024: Alert thresholds within the Operator limits](../functional/business-rules/BR-024-alert-thresholds-within-the-operator-limits.md) | Delivered, in the Workspace and from the Alert itself |
| [📏 BR-025: On-site changes are checked again](../functional/business-rules/BR-025-on-site-changes-are-checked-again.md) | Delivered |
| [📏 BR-027: The Pilot's attention is preserved](../functional/business-rules/BR-027-the-pilot-s-attention-is-preserved.md) | Delivered |

**🛠️ Technical pages**

| Page | What P1 builds from it |
| --- | --- |
| [🏗️ Architecture: edge and core](../technical/01-architecture.md#edge-and-core) | The edge on the Pilot's machine: flight engine, video-relay, SQLite, NATS leaf node; Ground control on its local WebSocket |
| [🏗️ Architecture: main flows](../technical/01-architecture.md#flows) | Telemetry, Pilot command, Mission design, Mission to the edge |
| [🧱 Data models](../technical/02-data-models.md#models) | `Mission`, `SquadMember`, `Geofence`, `Route`, `Authorisation`, `PreFlightCheck`, `Replan`; `Drone`, `DroneModel`, `Payload`, `Battery`, `MaintenanceRecord`, `CompatibilityTest`; `Alert`, `FlightLogEntry` |
| [🧱 Data models: Telemetry frames](../technical/02-data-models.md#telemetry) | `TelemetryFrame`, delta-encoded `SquadFrame`, `Command` with its two lanes |
| [🗄️ Storage: the edge store](../technical/03-storage.md#edge-store) | What a flight needs copied to SQLite at the Pre-flight check; the Flight log written there first; SQLCipher |
| [🗄️ Storage: TimescaleDB](../technical/03-storage.md#timescaledb) | `telemetry_frames` and `flight_log_entries` written by batched `COPY` |
| [🔩 Engine and services: flight engine](../technical/04-engine.md#flight-engine) | One actor per Mission, the ring buffer, the command lanes, the Pre-flight check at the edge |
| [🔩 Engine and services: safety loop](../technical/04-engine.md#safety-loop) | The two layers: on board, and the 20 Hz tick in the Rust core |
| [🔩 Engine and services: Drone adapters](../technical/04-engine.md#adapters) | The MAVLink adapter in Rust and the adapter interface |
| [🔩 Engine and services: planner](../technical/04-engine.md#planner) | Coverage paths and Re-plans, as a service and as a library at the edge |
| [🔩 Engine and services: simulator](../technical/04-engine.md#simulator) | PX4 SITL for Missions, training and compatibility tests |
| [🔌 API layer: video](../technical/05-api.md#video) | WebRTC through LiveKit at the edge, simulcast for the Mosaic and the Focus view |
| [🔐 Security: links](../technical/06-security.md#links) | MAVLink 2 signing with one key per Drone, rotated per Mission; NATS leaf node over mTLS |
| [🔐 Security: identity](../technical/06-security.md#identity) | The Pre-flight PIN, hashed with Argon2id, locked after five failures |
| [🚀 Scalability and performance: budgets](../technical/07-scalability.md#budgets) | Command, Hold and abort, safety tick, Telemetry, REST and video budgets asserted |
| [🚀 Scalability and performance: load tests](../technical/07-scalability.md#load-tests) | The first nightly run in staging, and chaos runs |
| [🩺 Observability: the edge](../technical/08-observability.md#edge) | Edge health shown to the Pilot; the local collector buffering offline |
| [🚢 Deployment: edge appliance](../technical/09-deployment.md#edge) | The edge as containers on the Pilot's machine and on the rugged edge box; signed updates, never during a Mission |
| [🖥️ GUI and WebUI: desktop shell and inputs](../technical/10-frontends.md#desktop) | Tauri 2 windows per screen, gamepads through SDL2 and the Gamepad API, the Window Management API, the fixed inputs |
| [🖥️ GUI and WebUI: live data](../technical/10-frontends.md#live-data) | Web Worker decoding, deck.gl attributes updated in place |
| [🖥️ GUI and WebUI: front-end budgets](../technical/10-frontends.md#performance) | First load, 5,000 moving Drones, live frame to pixels, switch to the Focus view |

## <a id="epics"></a>🪜 Epics

| ID | Epic | Delivers | Where | Tickets | Parallel tasks for the agents |
| --- | --- | --- | --- | --- | --- |
| E1.1 | Flight engine and safety loop | [📏 BR-001](../functional/business-rules/BR-001-geofence-and-altitude-ceiling.md), [📏 BR-002](../functional/business-rules/BR-002-separation-distance.md), [📏 BR-012](../functional/business-rules/BR-012-pilot-override-always-available.md); the edge that keeps flying offline | `services/flight-engine`, `packages/rust` (`swarm-core` safety crate), SQLite at the edge | 5: T1.01, T1.03, T1.04, T1.15, T1.30 | Spatial hash grid; Geofence R-tree and ceiling; energy against the landing reserve; criterion benchmarks; Mission actor; command lanes; SQLite Flight log; leaf node buffering; chaos scenarios |
| E1.2 | MAVLink adapter and Drone model approval | [🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md), [📏 BR-015](../functional/business-rules/BR-015-approved-drone-models-only.md); [📘 FS-011](../functional/features/FS-011-drone-adapters.md) AC-1 | `packages/rust` (`swarm-core` mavlink crate), `services/flight-engine`, `services/fleet`, `services/simulator` | 3: T1.02, T1.12, T1.28 | MAVLink 2 parser; signing and key rotation; each adapter command against PX4 SITL; compatibility test steps; firmware tracking; the real test flight procedure |
| E1.3 | Fleet and Authorisations | [🎬 UC-007](../functional/use-cases/UC-007-register-a-drone-and-track-its-readiness.md), [🎬 UC-008](../functional/use-cases/UC-008-record-an-authorisation.md); [📏 BR-010](../functional/business-rules/BR-010-valid-authorisation-for-the-jurisdiction.md), [📏 BR-011](../functional/business-rules/BR-011-drone-readiness.md), [📏 BR-022](../functional/business-rules/BR-022-payload-compatibility.md) | `services/fleet`, `services/missions`, `frontends/back-office` | 3: T1.05 to T1.07 | Models and readiness computation; REST resources; Back office screens; PDF upload to object storage; expiry warnings; Missions back to Draft |
| E1.4 | Mission studio for Inspection | [🎬 UC-001](../functional/use-cases/UC-001-design-a-mission.md), [🎬 UC-002](../functional/use-cases/UC-002-simulate-a-mission.md); [📏 BR-005](../functional/business-rules/BR-005-autonomy-level-per-activity.md) | `frontends/mission-studio`, `services/missions`, `services/planner`, `packages/rust` (`swarm-core` planner crate), `packages/ts/maps` | 4: T1.08, T1.09, T1.11, T1.25 | Geofence drawing; Squad builder; boustrophedon coverage and balanced assignment in Rust; rule checks with the leg at fault; simulation runs and their report |
| E1.5 | Pre-flight check and launch | [🎬 UC-003](../functional/use-cases/UC-003-run-the-pre-flight-check-and-launch.md), [🎬 UC-024](../functional/use-cases/UC-024-configure-each-drone-of-the-squad-on-the-site.md); [📏 BR-003](../functional/business-rules/BR-003-weather-limits.md), [📏 BR-004](../functional/business-rules/BR-004-pilot-ratio.md), [📏 BR-007](../functional/business-rules/BR-007-launch-only-after-a-passed-pre-flight-check.md), [📏 BR-025](../functional/business-rules/BR-025-on-site-changes-are-checked-again.md) | `services/flight-engine`, `services/missions`, `frontends/ground-control` | 3: T1.13, T1.14, T1.26 | One task per automatic check; Weather service and U-space service clients; checklist per Activity; PIN; launch; on-site changes and the check again |
| E1.6 | Fail-safes, Re-plans and Pilot override | [🎬 UC-004](../functional/use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md), [🎬 UC-005](../functional/use-cases/UC-005-lose-a-drone-in-flight.md), [🎬 UC-006](../functional/use-cases/UC-006-take-manual-control-or-abort.md); [📏 BR-006](../functional/business-rules/BR-006-fail-safe-per-activity.md), [📏 BR-013](../functional/business-rules/BR-013-re-plan-approval.md), [📏 BR-023](../functional/business-rules/BR-023-fixed-safety-controls.md) | `services/flight-engine`, `packages/rust` (planner library at the edge), `frontends/ground-control`, `frontends/desktop` | 4: T1.16 to T1.19 | Drone: Lost after 5 s; area sharing in Rust; Re-plan countdown; Hold the Squad and abort on the safety lane; gamepad input in Rust (SDL2) and in the browser; Return to Squad with the separation check |
| E1.7 | Ground control monitoring | [🎬 UC-025](../functional/use-cases/UC-025-monitor-a-mission-in-ground-control.md), [🎬 UC-026](../functional/use-cases/UC-026-handle-an-alert.md), [🎬 UC-030](../functional/use-cases/UC-030-focus-on-a-drone.md); [📏 BR-024](../functional/business-rules/BR-024-alert-thresholds-within-the-operator-limits.md), [📏 BR-027](../functional/business-rules/BR-027-the-pilot-s-attention-is-preserved.md) | `frontends/ground-control`, `packages/ts` (`live`, `maps`, `ui`), `services/video-relay` | 5: T1.10, T1.20 to T1.23 | Frame and fixed controls; Squad panel virtualised; progress; Alerts area outside heavy panels; video-relay with GStreamer and LiveKit; Mosaic; Focus view and event queue |
| E1.8 | Workspace, platforms and edge | [🎬 UC-023](../functional/use-cases/UC-023-configure-the-workspace-of-ground-control.md); [📘 FS-020](../functional/features/FS-020-ground-control-workspace-and-configuration.md) | `frontends/desktop`, `frontends/ground-control`, `deploy/` (edge appliance) | 4: T1.24, T1.27, T1.34, T1.37 | Windows per screen in Tauri; Window Management API and `BroadcastChannel` in the browser; Control mapping; edge containers; offline maps; tablet and laptop layouts; the rugged edge box image |
| E1.9 | Training and the design partner | [🎬 UC-013](../functional/use-cases/UC-013-train-on-the-simulator.md); [📏 BR-014](../functional/business-rules/BR-014-simulation-isolation.md) applied; M1b | `services/simulator`, `frontends/ground-control`, the simulation environment | 2: T1.31, T1.38 | Training session; Instructor's second Ground control; failure injection; the always-on simulated fleet; the design partner's Operator |
| E1.10 | Flight tests, quality and exit | [🛫 C-01](10-flight-test-campaigns.md#c-01), M1; budgets, screenshots, acceptance suites | `tests/` (load, chaos, acceptance), the staging cell, every service and app touched | 12: T1.29, T1.32, T1.33, T1.35, T1.36, T1.39 to T1.45 | Staging cell; nightly load run; Telemetry writer; fixes from each flight day; translations; Fail-safe test pack; front-end budgets; screenshots; security; documentation |

## <a id="sprints"></a>🗓️ Sprint plan

P1 has no overlap with another phase: its nine sprints carry its 45 tickets, 5 per sprint. The flight test campaign [🛫 C-01](10-flight-test-campaigns.md#c-01) runs from S10 to S12; from S10 on, one ticket per sprint is kept for what the flight days teach.

| Sprint | Dates | Tickets | Sprint goal | What can be shown |
| --- | --- | --- | --- | --- |
| [S05](#s05) | 1 to 12 Mar 2027 | T1.01 Safety tick in Rust · T1.02 MAVLink 2 adapter · T1.03 Mission actor and command lanes · T1.04 Edge store and Flight log · T1.05 Fleet service | The flight engine flies a PX4 SITL Squad and keeps it safe | 4 PX4 SITL X500 fly a route from the flight engine; a Drone pushed towards the Geofence Holds, then Returns home; the safety tick benchmark under 5 ms for 500 Drones |
| [S06](#s06) | 15 to 26 Mar 2027 | T1.06 Fleet screens (UC-007) · T1.07 Authorisations (UC-008) · T1.08 Mission studio map and Geofence · T1.09 Coverage planner · T1.10 Ground control frame and local live data | The Fleet, the Authorisations and the first Mission studio screens; Ground control on its local flight engine | Noah Weber registers Alpha to Delta (X500) with their Payloads and Batteries; an Authorisation recorded with its PDF; a Geofence drawn above Les Vignes solar farm |
| [S07](#s07) | 29 Mar to 9 Apr 2027 | T1.11 Squad, tasks, routes and save (UC-001) · T1.12 Compatibility test in the Simulator (UC-014) · T1.13 Automatic checks of the Pre-flight check · T1.14 Checklist, PIN signature and launch · T1.15 Two-layer safety loop in flight | A Mission designed in the Mission studio, Verified and launched in the Simulator | Léa Martin designs M-2026-0412 Inspection of Les Vignes and it becomes Planned; Sam Carter signs the Pre-flight check with his PIN and launches the simulated Squad |
| [S08](#s08) | 12 to 23 Apr 2027 | T1.16 Lose a Drone (UC-005) · T1.17 Re-plans proposed by the Squad (UC-004) · T1.18 Hold the Squad and abort · T1.19 Manual control and Return to Squad (UC-006) · T1.20 Squad panel and progress (UC-025) | Every Fail-safe and every Pilot override, in the Simulator | Delta's Link cut: it Returns home on board, the Squad proposes to share its area, Sam Carter approves within 60 seconds; H held 1 second Holds the whole Squad |
| [S09](#s09) | 26 Apr to 7 May 2027 | T1.21 Alerts and Alert thresholds (UC-026) · T1.22 Live video and Mosaic · T1.23 Focus view (UC-030) · T1.24 Workspace configuration (UC-023) · T1.25 Simulate a Mission (UC-002) | Ground control complete on the desktop; Missions simulated before they fly | A two-screen Workspace saved and reopened; the Mosaic of four simulated cameras; Charlie's event queued while the Focus view stays on Alpha |
| [S10](#s10) | 10 to 21 May 2027 | T1.26 On-site changes (UC-024) · T1.27 Field edge on the Pilot's laptop · T1.28 X500 real compatibility flight · T1.29 Staging cell and nightly load run · T1.30 Chaos at the edge | Ready for the field; the X500 Approved; C-01 starts | The first real flight of C-01: one X500 runs the compatibility steps and the Drone model becomes Approved; then one X500 flies its part of an Inspection in visual line of sight |
| [S11](#s11) | 24 May to 4 Jun 2027 | T1.31 Training sessions (UC-013) · T1.32 Telemetry writer and Flight log upload · T1.33 Fixes from the first C-01 flight days · T1.34 Laptop and tablet layouts · T1.35 Four languages and safety-control accessibility | Each real X500 flies its part of the Inspection, one at a time; the Squad of 4 flies the same Mission in SITL; the Pilot trains on the Simulator | Alpha, then Bravo, inspect their part of the test field through the Squad pipeline; the Squad of 4 covers the whole field in SITL; an Instructor injects a Link loss on Delta in a training session |
| [S12](#s12) | 7 to 18 Jun 2027 | T1.36 Fail-safe test pack for M1 · T1.37 Rugged edge box · T1.38 Simulation environment and the design partner's Operator · T1.39 Fixes from the later C-01 flight days · T1.40 Front-end budgets | **M1** and **M1b** on 18 June 2027 | The M1 flight: one real X500 with every Fail-safe tested, and the Squad of 4 in SITL; the design partner signs and receives its Operator in the simulation environment |
| [S13](#s13) | 21 Jun to 2 Jul 2027 | T1.41 Screens to 📸 Screenshot · T1.42 Acceptance suites · T1.43 Security hardening · T1.44 Design partner's first requests · T1.45 Phase close and hand-over to P2 | Every exit criterion met | The [demo](#demo) of this page |

**Total: 45 tickets** (S05 5, S06 5, S07 5, S08 5, S09 5, S10 5, S11 5, S12 5, S13 5).

### <a id="s05"></a>S05, 1 to 12 March 2027: flight engine and safety core

| Ticket | Delivers | Where | Done when |
| --- | --- | --- | --- |
| T1.01 Safety tick in Rust | The safety crate of `swarm-core` ([🔩 Engine and services: safety loop](../technical/04-engine.md#safety-loop)): uniform spatial hash grid sized on the [🔤 Separation distance](../glossary.md#term-separation-distance), prepared Geofence polygons in an R-tree plus the [🔤 Altitude ceiling](../glossary.md#term-altitude-ceiling), energy to reach home with the landing reserve per Drone model, Link timers; decisions out as Alerts, Fail-safe commands and Re-plan triggers; no allocation per tick, the GIL released | `packages/rust` | Criterion benchmark under 5 ms for 500 Drones on every pull request; property tests on separation and Geofence margins ([📏 BR-001](../functional/business-rules/BR-001-geofence-and-altitude-ceiling.md), [📏 BR-002](../functional/business-rules/BR-002-separation-distance.md)) |
| T1.02 MAVLink 2 adapter | The mavlink crate: MAVLink 2 parser and signer, one key per Drone rotated per Mission; the adapter interface of [🔩 Engine and services: Drone adapters](../technical/04-engine.md#adapters) (connect, upload Geofence, Fail-safes and route, arm and take off, go to, Hold, Return home, land, Payload control, Telemetry stream) for PX4; each Drone's latest frame written to a lock-free ring buffer | `packages/rust`, `services/flight-engine` | Every interface call passes against PX4 SITL; an unsigned message is dropped and logged |
| T1.03 Mission actor and command lanes | The flight engine of [🔩 Engine and services: flight engine](../technical/04-engine.md#flight-engine): one actor per Mission holding its Squad state, one `SquadFrame` per tick to the local WebSocket and the leaf node, the safety lane (Hold the Squad, abort, Return home, manual control) served first and acknowledged per Drone, the normal lane for the rest | `services/flight-engine` | A Hold sent while the normal lane is saturated reaches every simulated Drone under 100 ms |
| T1.04 Edge store and Flight log | SQLite in WAL mode encrypted with SQLCipher; what a flight needs copied at the Pre-flight check; the [🗃️ Flight log](../glossary.md#ent-flight-log) written there first (fsync per 100 ms batch), then published to JetStream through the leaf node, replayed in order after an outage, deduplicated by `(drone_id, seq)` in the core ([🗄️ Storage: the edge store](../technical/03-storage.md#edge-store)) | `services/flight-engine` | Power cut in the middle of a SITL flight: the Flight log is whole after restart; one hour offline replays in order |
| T1.05 Fleet service | `Drone`, `DroneModel`, `Payload`, `Battery`, `MaintenanceRecord`, `CompatibilityTest` in `swarm-models`; the fleet service with `/v1/drones`, `/v1/drone-models`, `/v1/payloads`; readiness computed from maintenance, open faults, Battery health and Drone model approval ([📏 BR-011](../functional/business-rules/BR-011-drone-readiness.md)); Payloads registered with the Drone models they fit and their weight ([📏 BR-022](../functional/business-rules/BR-022-payload-compatibility.md)); maintenance intervals imported from the maker, shorter only | `services/fleet`, `packages/python/swarm-models` | Readiness changes are published as events; the six model tests of AGENT.md pass for each model |

### <a id="s06"></a>S06, 15 to 26 March 2027: Fleet, Authorisations, first design screens

The 4 X500 of [🤝 H-01](11-hardware-and-partners.md#h-01) arrive in S06; the person takes the EU A2 certificate of [🏛️ G-02](09-regulatory-track.md#g-02).

| Ticket | Delivers | Where | Done when |
| --- | --- | --- | --- |
| T1.06 Fleet screens (UC-007) | 🛸 Fleet in the Back office: register a Drone, add its Payloads and Batteries, refuse what does not fit (KO1), count flight hours and maintenance, show Drone: Ready or Drone: Grounded ([🎬 UC-007](../functional/use-cases/UC-007-register-a-drone-and-track-its-readiness.md)) | `frontends/back-office` | [📘 FS-005](../functional/features/FS-005-fleet-and-readiness.md) AC-1 and AC-2 pass as automated tests; the real X500 of H-01 registered as AW-001 to AW-004 in the staging data |
| T1.07 Authorisations (UC-008) | 📜 Authorisations in the Back office and the missions service: area, Altitude ceiling, Pilot ratio, Jurisdiction, validity dates, conditions; the PDF required, the operations manual and the SORA or ConOps file optional, stored in the Operator's bucket; warnings 30 and 7 days before the end date; on expiry, Planned Missions back to Draft and the Mission planner told ([🎬 UC-008](../functional/use-cases/UC-008-record-an-authorisation.md)) | `services/missions`, `frontends/back-office` | [📘 FS-006](../functional/features/FS-006-authorisations-and-compliance.md) AC-1 and AC-2 pass; the conditions C-01 flies under are recorded as settled on the regulatory track |
| T1.08 Mission studio map and Geofence | 🖊️ Design in the Mission studio: the map (MapLibre, self-hosted PMTiles, the Operator's licensed satellite layer when it has one), the Geofence and Altitude ceiling drawn, the [🔤 Activity](../glossary.md#term-activity) picked (Inspection in P1), the Mission saved as [🔄 Mission: Draft](../glossary.md#st-mission-draft) (UC-001 A1) | `frontends/mission-studio`, `services/missions`, `packages/ts/maps` | The Geofence round-trips as GeoJSON to PostGIS; the screen exists in four languages |
| T1.09 Coverage planner | The planner crate: boustrophedon decomposition of the area, routes per Drone balanced by Payload, speed and battery; the `planner` service answering over NATS request-reply; the same crate as a library in the flight engine for Re-plans ([🔩 Engine and services: planner](../technical/04-engine.md#planner)) | `packages/rust`, `services/planner` | Les Vignes solar farm covered by 4 Drones with balanced flight times; benchmark recorded |
| T1.10 Ground control frame and local live data | The Ground control frame with ✋ Hold the Squad and 🛑 Abort in the title bar of every screen; the connection to the local flight engine with the same protocol as the cell; the map of P0 fed by the edge; edge health (tick duration, Link quality, buffered messages, disk) in the status bar | `frontends/ground-control`, `packages/ts/live` | Telemetry from Drone to screen at the edge under 150 ms at p95 for a SITL Squad |

### <a id="s07"></a>S07, 29 March to 9 April 2027: design, approval and launch

| Ticket | Delivers | Where | Done when |
| --- | --- | --- | --- |
| T1.11 Squad, tasks, routes and save (UC-001) | The Squad builder (a Payload and a task per Drone), the routes from the planner, the rule checks on save: Geofence and Altitude ceiling with the leg at fault, Payload compatibility, a Valid Authorisation, the Autonomy level of the Activity; [🔄 Mission: Planned](../glossary.md#st-mission-planned) or Draft with the breaches shown (UC-001 A2, A3, OK, KO and every alternative flow) | `frontends/mission-studio`, `services/missions` | [📘 FS-001](../functional/features/FS-001-mission-design.md) AC-1, AC-2 and AC-3 pass |
| T1.12 Compatibility test in the Simulator (UC-014) | The compatibility test suite: take off, follow a route, Hold, Return home, land, stay inside the Geofence, control the Payload, each step shown as it runs in the Back office; [🔄 Drone model: Approved](../glossary.md#st-drone-model-approved) only for the tested firmware, back to [🔄 Drone model: Not approved](../glossary.md#st-drone-model-not-approved) on a new firmware ([🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md) steps 1 to 3, A2 to A5) | `services/fleet`, `services/simulator`, `services/flight-engine`, `frontends/back-office` | The X500 passes every step in PX4 SITL; a step forced to fail keeps the Drones Grounded ([📘 FS-011](../functional/features/FS-011-drone-adapters.md) AC-1) |
| T1.13 Automatic checks of the Pre-flight check | Each automatic check of [📏 BR-007](../functional/business-rules/BR-007-launch-only-after-a-passed-pre-flight-check.md) as its own step: Geofence, weather from the Weather service against every Drone model of the Squad ([📏 BR-003](../functional/business-rules/BR-003-weather-limits.md)), Valid Authorisation, Pilot ratio ([📏 BR-004](../functional/business-rules/BR-004-pilot-ratio.md)), readiness of every Drone and Payload, Links, the U-space service grant where the Jurisdiction requires it; checks that need the core fetched while online and expired with the 30-minute validity (UC-003 A1, KO) | `services/flight-engine`, `services/missions`, `frontends/ground-control` | [📘 FS-002](../functional/features/FS-002-pre-flight-check-and-launch.md) AC-2 and AC-3 pass |
| T1.14 Checklist, PIN signature and launch | The checklist per Activity set by the Operator (propellers, Payload fixed, area clear), every item ticked; the personal PIN, hashed with Argon2id and locked after five failures; [🔄 Mission: Verified](../glossary.md#st-mission-verified) valid 30 minutes; the launch, every Drone [🔄 Drone: Airborne](../glossary.md#st-drone-airborne) and the Mission [🔄 Mission: Flying](../glossary.md#st-mission-flying) (UC-003 A2, A3, OK) | `services/flight-engine`, `frontends/ground-control`, Keycloak | [📘 FS-002](../functional/features/FS-002-pre-flight-check-and-launch.md) AC-1 passes; a launch without signature is refused at the flight engine, not only on screen |
| T1.15 Two-layer safety loop in flight | The on-board layer uploaded before take-off (Geofence, Altitude ceiling, Link-loss Fail-safe after 5 s, battery Fail-safe at the landing reserve, Return home altitude) and the edge tick at 20 Hz of T1.01 wired into the Mission actor; Alerts and Fail-safe commands on the safety lane; weather in flight ([📏 BR-003](../functional/business-rules/BR-003-weather-limits.md)) | `services/flight-engine`, `packages/rust` | In SITL: Geofence margin gives Hold then Return home; the landing reserve of 20 % sends a Drone home in time; the edge process killed, the on-board Fail-safes still act |

### <a id="s08"></a>S08, 12 to 23 April 2027: Fail-safes and the Pilot's override

The thermal and RGB Payloads of [🤝 H-02](11-hardware-and-partners.md#h-02) arrive; the person starts the STS training of [🏛️ G-03](09-regulatory-track.md#g-03).

| Ticket | Delivers | Where | Done when |
| --- | --- | --- | --- |
| T1.16 Lose a Drone (UC-005) | [🔄 Drone: Lost](../glossary.md#st-drone-lost) after 5 seconds without any Link path (Operator setting, never below the Drone model minimum); the Lost Drone on its on-board Fail-safe; the others share its area; [🔄 Mission: Held](../glossary.md#st-mission-held) when fewer Drones remain than the minimum the Mission planner set, or when the Pilot loses the Link to the Squad ([🎬 UC-005](../functional/use-cases/UC-005-lose-a-drone-in-flight.md), [📏 BR-006](../functional/business-rules/BR-006-fail-safe-per-activity.md)) | `services/flight-engine`, `frontends/ground-control` | [📘 FS-004](../functional/features/FS-004-fail-safes-and-emergencies.md) AC-1 passes in SITL |
| T1.17 Re-plans proposed by the Squad (UC-004) | The planner library at the edge proposes a Re-plan when a Drone returns or is lost: its reason, the new area of each Drone, the effect on the duration; [🔄 Re-plan: Proposed](../glossary.md#st-re-plan-proposed) with the 60-second countdown (Operator setting), [🔄 Re-plan: Applied](../glossary.md#st-re-plan-applied) or [🔄 Re-plan: Rejected](../glossary.md#st-re-plan-rejected); smaller corrections inside the Geofence applied and logged ([📏 BR-013](../functional/business-rules/BR-013-re-plan-approval.md)) | `services/flight-engine`, `packages/rust`, `frontends/ground-control` | [📘 FS-003](../functional/features/FS-003-live-supervision.md) AC-1 passes; works with the core unreachable |
| T1.18 Hold the Squad and abort | ✋ Hold the Squad (H or both bumpers) and 🛑 Abort (Ctrl+Shift+A or Back and Start), held 1 second, no dialog, a hint when released early; from Mission: Held, resume (checks run again), Return home for every Drone, or abort; [🔄 Mission: Aborted](../glossary.md#st-mission-aborted) with every Drone Returning home or landing ([📏 BR-012](../functional/business-rules/BR-012-pilot-override-always-available.md), [📏 BR-023](../functional/business-rules/BR-023-fixed-safety-controls.md)) | `services/flight-engine`, `frontends/ground-control`, `frontends/desktop` | [📘 FS-003](../functional/features/FS-003-live-supervision.md) AC-2 and [📘 FS-004](../functional/features/FS-004-fail-safes-and-emergencies.md) AC-3 pass; Hold or abort reaches every Drone under 100 ms |
| T1.19 Manual control and Return to Squad (UC-006) | Select a Drone or the Squad, choose the input (XInput gamepads first, then generic USB joysticks, keyboard), [🔄 Pilot: In manual control](../glossary.md#st-pilot-in-manual-control), fly Bravo by hand while the others continue; Return to Squad after the Separation distance check, or stay in manual control with an Alert and a safe path proposed as a Re-plan ([🎬 UC-006](../functional/use-cases/UC-006-take-manual-control-or-abort.md)) | `frontends/ground-control`, `frontends/desktop` (SDL2), `services/flight-engine` | [📘 FS-021](../functional/features/FS-021-ground-control-monitoring.md) AC-3 passes with a gamepad, in Tauri and in the browser; command to Drone p99 under 50 ms at the edge |
| T1.20 Squad panel and progress (UC-025) | The always-visible Telemetry per Drone (state, battery %, Link quality, altitude, Payload) and the on-demand details (speed, heading, GNSS accuracy, motor and Battery temperatures, Payload status) in a virtualised Squad panel; progress against the plan (area covered, time left, battery left per Drone); [🔄 Pilot: Supervising](../glossary.md#st-pilot-supervising) ([🎬 UC-025](../functional/use-cases/UC-025-monitor-a-mission-in-ground-control.md) A1, OK) | `frontends/ground-control` | [📘 FS-021](../functional/features/FS-021-ground-control-monitoring.md) AC-1 passes on one screen |

### <a id="s09"></a>S09, 26 April to 7 May 2027: Ground control complete

The SORA 2.5 application of [🏛️ G-04](09-regulatory-track.md#g-04) is submitted this sprint, with the safety design and SITL results of S05 to S08.

| Ticket | Delivers | Where | Done when |
| --- | --- | --- | --- |
| T1.21 Alerts and Alert thresholds (UC-026) | The Alert: a banner, first in the Alerts area, the Drone highlighted on the map, its severity (Information, Warning, Critical), its facts and the actions available with their effect; the action chosen sent and recorded in the Flight log with the Pilot's name; the [🔤 Alert threshold](../glossary.md#term-alert-threshold) changed from the Alert within the Operator limits ([📏 BR-024](../functional/business-rules/BR-024-alert-thresholds-within-the-operator-limits.md)); critical Alerts never covered | `frontends/ground-control`, `services/flight-engine` | UC-026 A1, A3, OK and KO pass; [📘 FS-021](../functional/features/FS-021-ground-control-monitoring.md) AC-2 passes without the Co-pilot's explanation |
| T1.22 Live video and Mosaic | `services/video-relay` (GStreamer) and the LiveKit SFU at the edge; simulcast in three layers; the Mosaic takes the small layer, up to the Operator's maximum per platform (defaults: desktop 4, laptop 2, tablet 1, web browser 2); streams beyond it refused (UC-025 A2, A3, KO) | `services/video-relay`, `frontends/ground-control`, `packages/ts/live` | Video under 300 ms glass to glass at the edge with the H-02 cameras |
| T1.23 Focus view (UC-030) | The Focus view opened by an event the Drone detects at or above the Pilot's severity setting (default Warning and above), by a click on the map or on a Mosaic tile; one at a time, new events queued with a badge, the previous view one action away; the map and the Squad kept visible; in P1 the events a Drone detects are produced by the Simulator for the tests ([🎬 UC-030](../functional/use-cases/UC-030-focus-on-a-drone.md), [📏 BR-027](../functional/business-rules/BR-027-the-pilot-s-attention-is-preserved.md)) | `frontends/ground-control` | [📘 FS-021](../functional/features/FS-021-ground-control-monitoring.md) AC-4 passes; switching to the Focus view under 200 ms |
| T1.24 Workspace configuration (UC-023) | Panels arranged per screen and saved per Pilot and platform (Tauri windows, the Window Management API in the browser, one window per panel kept in sync by `BroadcastChannel` elsewhere); Alert thresholds within the Operator limits (Link 30 % to 70 %, wind 60 % to 90 % of the Drone model limit, low battery 25 % to 40 %); units, language and light or dark mode; the [🔤 Control mapping](../glossary.md#term-control-mapping), with the fixed inputs refused ([🎬 UC-023](../functional/use-cases/UC-023-configure-the-workspace-of-ground-control.md)) | `frontends/ground-control`, `frontends/desktop`, `services/missions` | [📘 FS-020](../functional/features/FS-020-ground-control-workspace-and-configuration.md) AC-1 and AC-2 pass |
| T1.25 Simulate a Mission (UC-002) | From the Mission studio, the Planned Mission flown by a virtual Squad in PX4 SITL with the real flight software; coverage, timing, battery and conflicts reviewed; the result accepted (stays Planned) or the Mission sent back to Draft with the conflict ([🎬 UC-002](../functional/use-cases/UC-002-simulate-a-mission.md)); Flight log marked simulated | `frontends/mission-studio`, `services/simulator`, `services/planner` | Every alternative flow of UC-002 has an automated test |

### <a id="s10"></a>S10, 10 to 21 May 2027: ready for the field, C-01 starts

[🛫 C-01](10-flight-test-campaigns.md#c-01) begins: the person flies as the Pilot, with the X500 of H-01, one real Drone at a time under the Open category, in visual line of sight, on a model-flying field in France. Each real flight goes through the full Squad pipeline; what needs several Drones at once (separation, area sharing, Re-plans) is proven in PX4 SITL on the same Mission.

| Ticket | Delivers | Where | Done when |
| --- | --- | --- | --- |
| T1.26 On-site changes (UC-024) | Review each Drone of the Squad on the Site; swap a Battery, replace Charlie by Echo; the Mission checked again against readiness and Payload compatibility; the Pre-flight check run and signed again; the Mission planner told and the change in the Flight log ([🎬 UC-024](../functional/use-cases/UC-024-configure-each-drone-of-the-squad-on-the-site.md), [📏 BR-025](../functional/business-rules/BR-025-on-site-changes-are-checked-again.md)) | `frontends/ground-control`, `services/flight-engine`, `services/missions` | [📘 FS-020](../functional/features/FS-020-ground-control-workspace-and-configuration.md) AC-3 passes |
| T1.27 Field edge on the Pilot's laptop | The edge appliance of [🚢 Deployment](../technical/09-deployment.md#edge) as containers started by the Tauri desktop app: flight engine, video-relay, NATS leaf node, local OpenTelemetry collector, SFU; maps (PMTiles), Drone model data and the last known Missions cached so the laptop prepares and flies without network; signed updates, never during a Mission | `frontends/desktop`, `deploy/`, `services/flight-engine` | A Mission prepared at the office flies on the field with the network off; an update offered during a Mission waits until landing |
| T1.28 X500 real compatibility flight | UC-014 step 4 for the X500: one real flight in a test area flown by the Pilot, the adapter running the same steps as in the Simulator, the Drone model Approved for its firmware; the procedure written as a checklist in the Back office | `services/fleet`, `services/flight-engine`, `frontends/back-office` | The X500 is [🔄 Drone model: Approved](../glossary.md#st-drone-model-approved); its Flight log is kept as the evidence of [📏 BR-015](../functional/business-rules/BR-015-approved-drone-models-only.md) |
| T1.29 Staging cell and nightly load run | The staging cell, provisioned with Terraform (decision T43: machines, k3s cluster, network, object storage, DNS) on self-hosted machines, then deployed by Helm and Argo CD ([🚢 Deployment: environments](../technical/09-deployment.md#environments)); the first nightly run: 20 Missions in flight (PX4 SITL for a sample, synthetic Rust Drones for the rest), one edge with 500 Drones for the safety tick, k6 for REST and WebSocket viewers; every P1 budget an assertion that blocks the release | `deploy/terraform`, `deploy/environments`, `tests/` (load), `services/simulator` | The staging cell is rebuilt from Terraform and Argo CD alone; the run passes every night for a week; a slowed release is blocked |
| T1.30 Chaos at the edge | Chaos runs in staging: the edge Link to the cell cut mid-flight, the flight engine restarted, a database failover in the cell; buffering, replay in order and Fail-safes must hold ([🚀 Scalability and performance: load tests](../technical/07-scalability.md#load-tests)) | `tests/` (chaos), `services/flight-engine` | Every scenario passes; no Telemetry frame or Flight log entry lost or duplicated |

### <a id="s11"></a>S11, 24 May to 4 June 2027: real Drones one at a time, training

| Ticket | Delivers | Where | Done when |
| --- | --- | --- | --- |
| T1.31 Training sessions (UC-013) | A training session on a Mission with a simulated Squad, the banner "🕹️ Simulator: no real Drone receives commands" on every screen; the Instructor's second Ground control on the same session, injecting failures (Link loss, and the other failures of the Simulator); a command addressed to a real Drone refused and logged; the Flight log marked simulated ([🎬 UC-013](../functional/use-cases/UC-013-train-on-the-simulator.md), [📏 BR-014](../functional/business-rules/BR-014-simulation-isolation.md)) | `services/simulator`, `frontends/ground-control` | [📘 FS-010](../functional/features/FS-010-simulator-and-training.md) AC-1 passes |
| T1.32 Telemetry writer and Flight log upload | The cell's Telemetry writer: JetStream consumed in batches of up to 5,000 frames or 200 ms, `COPY` into `telemetry_frames` and `flight_log_entries`; raw images and video uploaded after landing as resumable multipart uploads with SHA-256 checksums ([🗄️ Storage](../technical/03-storage.md#timescaledb)) | `services/missions`, `services/flight-engine` | Every C-01 Flight log and its images are in the cell, ready for the Debrief and processing of P2 |
| T1.33 Fixes from the first C-01 flight days | What the first flights teach: radio and RTK settings, Alert thresholds, screen readability outdoors, procedure changes; each fix with its test in SITL | Any service or app | Every issue raised on the flight days of S10 is fixed or moved to a named later ticket |
| T1.34 Laptop and tablet layouts | Ground control on a laptop (one screen) and a tablet: everything except manual control and multi-screen Workspaces on the tablet; Hold, abort, approve Re-plans on every platform ([📘 FS-020](../functional/features/FS-020-ground-control-workspace-and-configuration.md)) | `frontends/ground-control` | The Playwright suite runs on the three layouts; Hold the Squad and abort visible on every screen of each |
| T1.35 Four languages and safety-control accessibility | Every P1 screen, message and Alert reviewed in English, French, German and Spanish ([📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md)); contrast and size of Hold the Squad and abort checked outdoors and in dark mode | `packages/ts/i18n`, every P1 app | CI language check green; the safety controls pass the contrast check in both modes |

### <a id="s12"></a>S12, 7 to 18 June 2027: M1 and M1b

The rugged edge box of [🤝 H-03](11-hardware-and-partners.md#h-03) arrives; the design partner [🤝 P-01](11-hardware-and-partners.md#p-01) signs on 18 June 2027.

| Ticket | Delivers | Where | Done when |
| --- | --- | --- | --- |
| T1.36 Fail-safe test pack for M1 | One scripted procedure per Fail-safe for the real flight of one X500, rehearsed first in SITL: Geofence margin (Hold, then Return home), Link loss (on-board Return home after 5 s), landing reserve, weather limit, Hold the Squad and resume, manual control and Return to Squad, abort; the same Mission flown by the Squad of 4 in SITL for what needs several Drones (Separation distance, area of a Lost Drone shared, Re-plan approved); a C-01 report built from the real and simulated Flight logs | `tests/` (flight procedures), `services/flight-engine` | Every procedure has passed in SITL and once in a real flight of one X500 before 18 June; the Squad scenarios have passed in SITL on the same Mission |
| T1.37 Rugged edge box | The edge appliance image on the H-03 box: same containers as the laptop, signed, updated over the air in the internal ring; Ground control connects to it from a laptop or a tablet | `deploy/` (edge appliance) | A C-01 flight flown from the box; an update rolled back to the previous version |
| T1.38 Simulation environment and the design partner's Operator | The always-on simulation environment of [🚢 Deployment: environments](../technical/09-deployment.md#environments): a simulated fleet for demos, training sessions and compatibility tests, isolated credentials; the design partner's Operator created there with UC-029 and its first accounts | `deploy/environments`, `services/simulator` | The design partner's Mission planner designs and simulates a Mission without help |
| T1.39 Fixes from the later C-01 flight days | Same as T1.33, for the flight days of S11 and S12 | Any service or app | Nothing open blocks M1 |
| T1.40 Front-end budgets | The budgets of [🖥️ GUI and WebUI](../technical/10-frontends.md#performance): first load under 2.5 s on 4G with under 300 kB of JavaScript for the first route, 5,000 moving Drones at 60 frames per second, live frame to pixels under 50 ms, Focus view under 200 ms; measured in CI | `frontends/ground-control`, `frontends/mission-studio`, `tests/` | Each budget is a CI assertion |

### <a id="s13"></a>S13, 21 June to 2 July 2027: exit

| Ticket | Delivers | Where | Done when |
| --- | --- | --- | --- |
| T1.41 Screens to 📸 Screenshot | The 42 screens listed in [Scope](#scope) captured by the visual tests with the sample data, in light and dark mode, at `screen.width` x `screen.height`, replacing their mock-ups; the use case rows switched to 📸 Screenshot | `tests/`, `docs/specs/screens/`, `docs/specs/functional/use-cases/` | `specs.py check` prints nothing |
| T1.42 Acceptance suites | Every acceptance criterion closed in P1 as an automated test (pytest at the service level, Playwright against the real images), named after its feature and criterion; every alternative flow of the P1 use cases covered | `tests/`, each service's `tests/` | The suites run in CI and are linked from the exit checklist |
| T1.43 Security hardening | Multi-factor authentication enforced for Pilots, Mission planners, Fleet maintainers and Instructors; PIN lockout; MAVLink key rotation per Mission checked; leaf node credentials per edge revocable from the Back office; WireGuard for cellular links; scans clean ([🔐 Security](../technical/06-security.md#links)) | `services/gateway`, `services/flight-engine`, `frontends/back-office`, `deploy/` | A revoked edge cannot reach the cell; no high-severity issue open in Trivy or OSV-Scanner |
| T1.44 Design partner's first requests | The first requests of P-01 that fit the P1 scope (wording, checklists, Alert thresholds within the specified limits); anything new goes through the specification first | Any P1 app | The design partner has seen its requests answered or planned |
| T1.45 Phase close and hand-over to P2 | Runbooks for the edge and the staging cell, Grafana dashboards per Mission with the budgets as thresholds, technical pages updated, the list of what P2 starts from (Flight logs, images, Missions) | `docs/`, `deploy/` | Every exit criterion below is ticked |

## <a id="demo"></a>🎤 Demo

The end-of-phase demonstration, on 2 July 2027, uses the sample cast of [🎨 the visual identity](../visual-identity.md#screens): the Operator Aerowing Services, the Mission planner Léa Martin, the Fleet maintainer Noah Weber, the Pilot Sam Carter (the person who builds Swarm), an Instructor, the Client Helio Energy, the Site Les Vignes solar farm, the Drones Alpha to Echo (X500, AW-001 to AW-005) and the Mission M-2026-0412 Inspection of Les Vignes. Steps 1 to 7 run in the simulation environment; step 8 is the M1 flight, real for one X500 at a time and simulated for the Squad of 4. It is also the demonstration given to the design partner.

1. **Fleet.** Noah Weber opens 🛸 Fleet in the Back office. Alpha to Delta carry thermal and RGB Payloads; Echo is a spare. A thermal camera is registered with the Drone models it fits ([📘 FS-005](../functional/features/FS-005-fleet-and-readiness.md) AC-2). Foxtrot, with overdue maintenance, shows [🔄 Drone: Grounded](../glossary.md#st-drone-grounded) and cannot join a Squad (AC-1). The X500 shows Drone model: Approved, with its compatibility test from the Simulator and from its real flight.
2. **Authorisation.** Léa Martin opens 📜 Authorisations: the Authorisation with a Pilot ratio of 4 is [🔄 Authorisation: Valid](../glossary.md#st-authorisation-valid). An expired Authorisation refuses the Mission checked under it ([📘 FS-006](../functional/features/FS-006-authorisations-and-compliance.md) AC-1).
3. **Design.** In 🖊️ Design of the Mission studio, Léa Martin draws the Geofence of Les Vignes solar farm, picks Inspection, builds the Squad Alpha to Delta, and tries to give the thermal task to the RGB Drone: refused ([📘 FS-001](../functional/features/FS-001-mission-design.md) AC-2). A route above the Altitude ceiling keeps the Mission Draft and shows the leg at fault (AC-1). Corrected, the Mission becomes Planned (AC-3).
4. **Simulation.** She simulates M-2026-0412: the virtual Squad covers the solar farm, the coverage, timing and battery are within plan, and the Mission stays Planned.
5. **On the Site.** Sam Carter opens his two-screen Workspace in the Tauri desktop app. Charlie's Payload is loose: he replaces Charlie by Echo. The Mission is checked again and the Pre-flight check must be signed again ([📘 FS-020](../functional/features/FS-020-ground-control-workspace-and-configuration.md) AC-3). With gusts above the X500 limit, the weather check fails and launch stays disabled ([📘 FS-002](../functional/features/FS-002-pre-flight-check-and-launch.md) AC-2); once the wind drops, every check passes, he ticks the checklist, signs with his PIN and launches (AC-1). The Squad is Airborne and the Mission Flying.
6. **In flight.** Echo's low battery Alert appears with its actions; Sam Carter sends Echo home, and the Squad proposes to share Echo's area. He approves the Re-plan within 60 seconds ([📘 FS-003](../functional/features/FS-003-live-supervision.md) AC-1). The Simulator makes Alpha report a hot spot, which opens the Focus view; an event of Delta queues with a badge and does not replace it ([📘 FS-021](../functional/features/FS-021-ground-control-monitoring.md) AC-4). He takes Bravo with the gamepad and flies it by hand while the others continue, then returns it to the Squad (AC-3). Delta's Link is cut: after 5 seconds it is Lost, Returns home on board, and the others share its area ([📘 FS-004](../functional/features/FS-004-fail-safes-and-emergencies.md) AC-1). He holds H for 1 second: every Drone Holds and the Mission is Held ([📘 FS-003](../functional/features/FS-003-live-supervision.md) AC-2); he resumes, and the Mission ends Completed.
7. **Training.** In a training session on the same Mission, the Instructor injects a Link loss on Delta from a second Ground control; Sam Carter Holds the Squad and resumes. A command addressed to the real Alpha (AW-001) is refused and logged ([📘 FS-010](../functional/features/FS-010-simulator-and-training.md) AC-1).
8. **The M1 flight.** The video and the Flight log of the M1 flight of [🛫 C-01](10-flight-test-campaigns.md#c-01): one real X500 at a time, in visual line of sight under the Open category, flown from the rugged edge box through the full Squad pipeline (Pre-flight check signed with the PIN, flight engine, safety loop), with each Fail-safe of the test pack triggered in turn: Geofence margin, Link loss with the on-board Return home, landing reserve, Hold the Squad and resume, manual control and Return to Squad, and the final abort with the Drone [🔄 Drone: Landed](../glossary.md#st-drone-landed). Beside it, the Replay of the same Mission flown in PX4 SITL by the Squad of 4 under supervised autonomy: a Lost Drone's area shared and the Re-plan approved. The first real Squad flight comes in [🛫 C-02](10-flight-test-campaigns.md#c-02).

## <a id="exit"></a>🚪 Exit criteria

**Acceptance criteria** (automated by T1.42, and shown in the demo)

- [ ] [📘 FS-001](../functional/features/FS-001-mission-design.md) AC-1, AC-2, AC-3: a route above the Altitude ceiling keeps the Mission Draft with the leg at fault; a thermal task given to an RGB Drone is refused; a complete Mission that breaks no rule becomes Planned ([📏 BR-001](../functional/business-rules/BR-001-geofence-and-altitude-ceiling.md), [📏 BR-022](../functional/business-rules/BR-022-payload-compatibility.md), [📏 BR-010](../functional/business-rules/BR-010-valid-authorisation-for-the-jurisdiction.md); [🎬 UC-001](../functional/use-cases/UC-001-design-a-mission.md)).
- [ ] [📘 FS-002](../functional/features/FS-002-pre-flight-check-and-launch.md) AC-1, AC-2, AC-3: signing a passed Pre-flight check makes the Mission Verified; gusts above one Drone model's limit fail the weather check; a Squad of 6 under a Pilot ratio of 3 fails ([📏 BR-007](../functional/business-rules/BR-007-launch-only-after-a-passed-pre-flight-check.md), [📏 BR-003](../functional/business-rules/BR-003-weather-limits.md), [📏 BR-004](../functional/business-rules/BR-004-pilot-ratio.md); [🎬 UC-003](../functional/use-cases/UC-003-run-the-pre-flight-check-and-launch.md)).
- [ ] [📘 FS-003](../functional/features/FS-003-live-supervision.md) AC-1, AC-2: a Re-plan proposed by the Squad waits for the Pilot; Hold the Squad Holds every Drone ([📏 BR-013](../functional/business-rules/BR-013-re-plan-approval.md), [📏 BR-012](../functional/business-rules/BR-012-pilot-override-always-available.md); [🎬 UC-004](../functional/use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md)).
- [ ] [📘 FS-004](../functional/features/FS-004-fail-safes-and-emergencies.md) AC-1, AC-3: a Lost Drone follows its on-board Fail-safe and the others propose to share its area; abort Returns every Drone home and the Mission is Aborted ([📏 BR-006](../functional/business-rules/BR-006-fail-safe-per-activity.md), [📏 BR-012](../functional/business-rules/BR-012-pilot-override-always-available.md); [🎬 UC-005](../functional/use-cases/UC-005-lose-a-drone-in-flight.md), [🎬 UC-006](../functional/use-cases/UC-006-take-manual-control-or-abort.md)). AC-2 (Light shows) closes in P6.
- [ ] [📘 FS-005](../functional/features/FS-005-fleet-and-readiness.md) AC-1, AC-2 ([📏 BR-011](../functional/business-rules/BR-011-drone-readiness.md), [📏 BR-022](../functional/business-rules/BR-022-payload-compatibility.md); [🎬 UC-007](../functional/use-cases/UC-007-register-a-drone-and-track-its-readiness.md)).
- [ ] [📘 FS-006](../functional/features/FS-006-authorisations-and-compliance.md) AC-1, AC-2 ([📏 BR-010](../functional/business-rules/BR-010-valid-authorisation-for-the-jurisdiction.md), [📏 BR-004](../functional/business-rules/BR-004-pilot-ratio.md); [🎬 UC-008](../functional/use-cases/UC-008-record-an-authorisation.md)).
- [ ] [📘 FS-010](../functional/features/FS-010-simulator-and-training.md) AC-1: in a training session no real Drone receives a command and the Flight log is marked simulated ([📏 BR-014](../functional/business-rules/BR-014-simulation-isolation.md); [🎬 UC-013](../functional/use-cases/UC-013-train-on-the-simulator.md)).
- [ ] [📘 FS-011](../functional/features/FS-011-drone-adapters.md) AC-1 for MAVLink: a compatibility test failing on Return home keeps the Drones Grounded ([📏 BR-015](../functional/business-rules/BR-015-approved-drone-models-only.md); [🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md)); the X500 Approved after its Simulator test and its real flight.
- [ ] [📘 FS-020](../functional/features/FS-020-ground-control-workspace-and-configuration.md) AC-1, AC-2, AC-3 ([📏 BR-023](../functional/business-rules/BR-023-fixed-safety-controls.md), [📏 BR-024](../functional/business-rules/BR-024-alert-thresholds-within-the-operator-limits.md), [📏 BR-025](../functional/business-rules/BR-025-on-site-changes-are-checked-again.md); [🎬 UC-023](../functional/use-cases/UC-023-configure-the-workspace-of-ground-control.md), [🎬 UC-024](../functional/use-cases/UC-024-configure-each-drone-of-the-squad-on-the-site.md)).
- [ ] [📘 FS-021](../functional/features/FS-021-ground-control-monitoring.md) AC-1, AC-3, AC-4 ([📏 BR-023](../functional/business-rules/BR-023-fixed-safety-controls.md), [📏 BR-012](../functional/business-rules/BR-012-pilot-override-always-available.md), [📏 BR-027](../functional/business-rules/BR-027-the-pilot-s-attention-is-preserved.md); [🎬 UC-025](../functional/use-cases/UC-025-monitor-a-mission-in-ground-control.md), [🎬 UC-006](../functional/use-cases/UC-006-take-manual-control-or-abort.md), [🎬 UC-030](../functional/use-cases/UC-030-focus-on-a-drone.md)); AC-2 passes for the Alert and its actions, and closes in P5 with the Co-pilot's explanation ([🎬 UC-026](../functional/use-cases/UC-026-handle-an-alert.md)).
- [ ] Every alternative flow of UC-001 to UC-008, UC-013, UC-014, UC-023 to UC-026 and UC-030 has an automated test, except the steps that need the Co-pilot.

**Budgets** ([🚀 Scalability and performance](../technical/07-scalability.md#budgets))

- [ ] Pilot command to Drone, at the edge on a local link: p99 under 50 ms, in SITL and with the X500 on their radio.
- [ ] Hold the Squad or abort, to every Drone: under 100 ms.
- [ ] Safety tick: under 5 ms for 500 Drones, on every pull request; 99.99 % of ticks within budget in the nightly run ([🩺 Observability](../technical/08-observability.md#slos)).
- [ ] Telemetry, Drone to the Pilot's screen: p95 under 150 ms at the edge, under 400 ms through the cell.
- [ ] REST inside a cell: p95 under 100 ms for reads, under 250 ms for writes.
- [ ] WebRTC video: under 300 ms glass to glass at the edge.
- [ ] Front-end budgets of [🖥️ GUI and WebUI](../technical/10-frontends.md#performance): first load, 5,000 moving Drones at 60 frames per second, live frame to pixels, switch to the Focus view.

**Load tests** ([🚀 Scalability and performance](../technical/07-scalability.md#load-tests))

- [ ] The nightly staging run (20 Missions in flight, one edge with 500 Drones, k6 viewers) has passed every night of S12 and S13. The full cell at target load (200 Missions) is a later phase's exit.
- [ ] The chaos runs pass: edge Link cut mid-flight, flight engine restarted, database failover; Fail-safes, buffering and recovery hold.

**Screens and specifications**

- [ ] The 42 screens listed in [Scope](#scope) moved from ✏️ Mock-up to 📸 Screenshot, in light and dark mode, and their mock-ups deleted; the 37 others stay ✏️ Mock-up with the phase that captures them.
- [ ] `python3 .claude/skills/write-specs/scripts/specs.py check` prints nothing.

**Milestones**

- [ ] **M1:** during [🛫 C-01](10-flight-test-campaigns.md#c-01), one real X500 at a time flies an Inspection through the full Squad pipeline with every Fail-safe of the test pack tested and manual control used, and the same Mission is flown in PX4 SITL by a Squad of 4 under supervised autonomy. The first real Squad flight (4 Drones, one Pilot) is an exit criterion of P2 ([🛫 C-02](10-flight-test-campaigns.md#c-02)).
- [ ] **M1b:** [🤝 P-01](11-hardware-and-partners.md#p-01) has signed and has its Operator in the simulation environment.

## <a id="dependencies"></a>⛓️ Dependencies

**Previous phases**

| Phase | What P1 needs from it |
| --- | --- |
| [🛣️ P0: Foundations](01-p0-foundations.md) | M0: the ticket harness, CI/CD, the dev cell, NATS and the databases, `swarm-models` and `swarm-core`, the Simulator base, the flight engine skeleton, the Ground control shell and map, the tokens, the four languages, Operator isolation |

**Regulatory, hardware, partners and campaigns**

| Item | Due | Why P1 needs it |
| --- | --- | --- |
| [🏛️ G-01](09-regulatory-track.md#g-01) | S02 | Operator registration, before any real flight |
| [🏛️ G-02](09-regulatory-track.md#g-02) | S06 | The EU A2 certificate of the person, before C-01 |
| [🏛️ G-03](09-regulatory-track.md#g-03) | S08 to S10 | STS training and exam, for the Specific category flights of P2 |
| [🏛️ G-04](09-regulatory-track.md#g-04) | S09 | The SORA 2.5 application, built on the safety design and SITL results of P1, so that the Authorisation of [🏛️ G-05](09-regulatory-track.md#g-05) can arrive in S20 |
| [🏛️ G-06](09-regulatory-track.md#g-06) | Before S10 | Airspace and U-space checks for the C-01 field, and the conditions recorded as its Authorisation in T1.07 |
| [🤝 H-01](11-hardware-and-partners.md#h-01) | S06 | 4 X500 PX4 with RTK: the Drones of the compatibility flight and of M1 |
| [🤝 H-02](11-hardware-and-partners.md#h-02) | S08 | Thermal and RGB Payloads: Payload compatibility, video and the Inspection tasks |
| [🤝 H-03](11-hardware-and-partners.md#h-03) | S12 | The rugged edge box of T1.37 |
| [🤝 P-01](11-hardware-and-partners.md#p-01) | S12 | The design partner: M1b, the simulation environment Operator, its first requests |
| [🤝 P-06](11-hardware-and-partners.md#p-06) | From S01 | Self-hosted servers for the staging cell and the simulation environment |
| [🛫 C-01](10-flight-test-campaigns.md#c-01) | S10 to S12 | The first real flights, one X500 at a time under the Open category: the X500 compatibility flight, the Inspection flights through the Squad pipeline and the M1 flight |

**What P1 hands to the next phases**

| Phase | Takes from P1 |
| --- | --- |
| [🛣️ P2: Inspection product](03-p2-inspection-product.md) | Flight logs and images of C-01 in the cell, for processing, the Debrief and the evidence ledger; the Squad pipeline proven on one real X500 and on 4 in SITL, ready for the first real Squad flight of [🛫 C-02](10-flight-test-campaigns.md#c-02) once [🏛️ G-05](09-regulatory-track.md#g-05) is granted; the Mission studio and Ground control the design partner flies with |
| Later phases | The flight engine, the safety loop, the adapter interface (Parrot in P3, DJI and Skydio in P7), the planner library for Re-plans and refills (P4), the Alerts area the Co-pilot fills (P5), the 50 Hz tick of Light shows (P6) |

## <a id="risks"></a>🎲 Risks

| Risk | Why it matters in P1 | Response in P1 |
| --- | --- | --- |
| [🎲 R-03](12-risks.md#r-03) Safety tick budget missed | Every real flight depends on the tick and on the Hold and abort budgets | Benchmarks on every pull request from T1.01; no real flight while a safety budget is red in the nightly run; the on-board layer acts even if the edge tick stops |
| [🎲 R-11](12-risks.md#r-11) Crash or hardware loss in tests | C-01 flies the X500 of the Fleet, one at a time | Every procedure rehearsed in SITL first; one Drone per flight; wide Geofence margins on the field; a Fail-safe drill at the start of each flight day; repair parts and Batteries planned with H-01 |
| [🎲 R-07](12-risks.md#r-07) Weather and seasons | C-01 has three sprints of flight days; M1 has a fixed date | Flight days booked in S10, S11 and S12 with reserve days; the weather check of the Pre-flight check applies unchanged; SITL rehearsals fill the days lost to weather |
| [🎲 R-15](12-risks.md#r-15) Regulation changes | The Open category rules decide what C-01 and M1 may fly: one real Drone at a time, in visual line of sight | M1 is defined within them: one real X500 at a time, the Squad of 4 in SITL; the conditions of the C-01 field (area, height) are confirmed on the regulatory track before S10 ([🏛️ G-06](09-regulatory-track.md#g-06)); a rule change before C-02 is followed on the same track |
| [🎲 R-02](12-risks.md#r-02) Specific category Authorisation late | The first real Squad flight (4 Drones, one Pilot) of [🛫 C-02](10-flight-test-campaigns.md#c-02) and P2's flights at the partner's solar farm wait for it | The SORA application of [🏛️ G-04](09-regulatory-track.md#g-04) is submitted in S09 with the SITL evidence; the C-01 Flight logs are added when the authority asks |
| [🎲 R-05](12-risks.md#r-05) Design partner lost | M1b depends on one company signing | Demonstrations to candidate partners from S09 in the simulation environment; the M1 video and the demo of this page ready for 18 June |
| [🎲 R-13](12-risks.md#r-13) Browser API gaps for full web Ground control | Multi-screen Workspaces and gamepads in the browser rely on the Window Management API and the Gamepad API | The `BroadcastChannel` fallback is built with T1.24; the Pilot flies C-01 from the Tauri app; gaps found are listed for P2 |
| [🎲 R-14](12-risks.md#r-14) GDPR complaint about video | The X500 cameras film the field and anyone near it | Raw video kept 90 days by default; people on the field told before each flight day; no video shown outside the Operator |
| [🎲 R-01](12-risks.md#r-01) Review bottleneck | P1 is the densest safety code of the roadmap, and the person also flies and trains | Safety tickets (E1.1, E1.5, E1.6) reviewed line by line, the rest on tests and screens; the fixes tickets of S11 and S12 keep room for what the field teaches |
| [🎲 R-08](12-risks.md#r-08) Scope too large for 24 months | Ground control has many screens and platforms | Every P1 screen comes from a specified use case; nothing outside the use cases is built; screens that need the Co-pilot keep their mock-ups until P5 |

## <a id="work-split"></a>🧑‍💻 Work split

**The person**

- **Decisions:** the coverage pattern and its parameters for Inspection, the Alert thresholds within the Operator limits for C-01, the content of the Fail-safe test pack, go or no-go for each flight day and for M1, what a design partner's request becomes (a fix, a ticket, or a question for the specification).
- **Reviews:** about 5 tickets per sprint; the safety path (T1.01 to T1.04, T1.13 to T1.19, T1.30) line by line, with the SITL runs; the screens on their screenshots and Playwright reports.
- **Flights:** the X500 compatibility flight, the C-01 flight days and the M1 flight, as the Pilot; the Fail-safe drills at the start of each day.
- **Paperwork and partners:** the EU A2 certificate ([🏛️ G-02](09-regulatory-track.md#g-02)), the STS training ([🏛️ G-03](09-regulatory-track.md#g-03)), the SORA application ([🏛️ G-04](09-regulatory-track.md#g-04)), the field and its checks ([🏛️ G-06](09-regulatory-track.md#g-06)), the hardware of [🤝 H-01](11-hardware-and-partners.md#h-01) to [🤝 H-03](11-hardware-and-partners.md#h-03), and the meetings that lead to the signature of [🤝 P-01](11-hardware-and-partners.md#p-01).

**The agents, in parallel**

- **S05:** the safety crate, the mavlink crate, the Mission actor, the edge store and the fleet service are five independent tickets; the interfaces between them (ring buffer, `SquadFrame`, `Command`) are fixed in the tickets first.
- **S06 to S09:** for each ticket, one task per layer (Rust core, Python service, front end), one for the tests and SITL scenarios, one for the screens and their four languages; the automatic checks of T1.13 are one task each.
- **S10 to S12:** while the person flies, the agents turn each flight day's notes into fix tickets with a SITL reproduction, run the nightly load and chaos runs, and prepare the C-01 report from the Flight logs.
- **S13:** screenshots in light and dark mode, acceptance suites, security scans and documentation run as parallel tasks; the person reviews the exit checklist.

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ P0: Foundations](01-p0-foundations.md) · 📄 **Page 108 / 120** · [P2: Inspection product ▶️](03-p2-inspection-product.md)
<!-- /spec:nav-bottom -->
