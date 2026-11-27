# 🛣️ P6: Light shows

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ P5: AI agents, MCP and A2A](06-p5-ai-agents.md) · 📄 **Page 113 / 120** · [P7: Scale and reach ▶️](08-p7-scale-and-reach.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Sprints:** S41 to S48 · **Dates:** 17 Jul to 3 Nov 2028 · **Tickets:** about 25

> [!NOTE]
> P6 lets a [👤 Mission planner](../glossary.md#per-mission-planner) import or design a [🗃️ Choreography](../glossary.md#ent-choreography) that Swarm checks frame by frame, and lets a [👤 Pilot](../glossary.md#per-pilot) fly it as a [🔤 Light show](../glossary.md#term-light-show) on the music time code, from about 50 real Drones up to 5,000 simulated Drones on a partitioned edge; it comes now because the flight engine, the safety loop, the Simulator and the evidence ledger it relies on are proven by Inspection, Patrol and Agriculture, and the show is the hardest test of the safety budgets before general availability.

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

Deliver [📘 FS-013](../functional/features/FS-013-light-shows.md) end to end, and prove the scale limits of the edge that every other [🔤 Activity](../glossary.md#term-activity) only approaches:

- **Design and import.** The Mission planner imports a Choreography from Blender or Skybrush Studio, or builds a simple show on a timeline in the [⚙️ Mission studio](../glossary.md#sys-mission-studio). Swarm checks every frame for the [🔤 Separation distance](../glossary.md#term-separation-distance) between Drones and from the audience, speed, acceleration and battery, and names the frame and the Drones at fault ([📏 BR-002](../functional/business-rules/BR-002-separation-distance.md)).
- **Fly on the time code.** [⚙️ Ground control](../glossary.md#sys-ground-control) sends SMPTE LTC or MIDI time code to the audio desk of the show, or plays the music itself, and the [🗃️ Squad](../glossary.md#ent-squad) flies the Choreography frame by frame. The show is Pre-planned: only [🔤 Fail-safes](../glossary.md#term-fail-safe) act in flight ([📏 BR-005](../functional/business-rules/BR-005-autonomy-level-per-activity.md)).
- **Stop everything on a fault.** When one [🗃️ Drone](../glossary.md#ent-drone) fails or is lost, the whole Squad [🔤 Holds](../glossary.md#term-hold) and lands at its landing positions, the time code and the music stop, and the [🗃️ Mission](../glossary.md#ent-mission) ends [🔄 Mission: Aborted](../glossary.md#st-mission-aborted) once every Drone has landed ([📏 BR-006](../functional/business-rules/BR-006-fail-safe-per-activity.md)).
- **Scale to 5,000 Drones.** A show of more than 1,000 Drones is split into sectors of up to 1,000 Drones, each run by its own edge node, under a show coordinator that keeps the time code for every sector and sends Hold the Squad or land to all sectors within 100 ms ([🚀 Scalability and performance](../technical/07-scalability.md#big-shows)).
- **Milestone M6, 3 November 2028 (S48).** A real show of about 50 Drones above an audience, and 5,000 simulated Drones on a partitioned edge within budget in the nightly load test of staging.

## <a id="scope"></a>🧺 Scope

**📘 Features**

| Feature | Delivered in P6 | Acceptance criteria closed |
| --- | --- | --- |
| [📘 FS-013: Light shows](../functional/features/FS-013-light-shows.md) | All of it: import, built-in designer, frame checks, time code, whole-Squad Fail-safe, partitioned edge | AC-1, AC-2 |
| [📘 FS-011: Drone adapters](../functional/features/FS-011-drone-adapters.md) | The compatibility test of the rented show Drone model and its show-light [🗃️ Payload](../glossary.md#ent-payload) control, through the Drone adapter of its family | AC-1, run again for the show Drone model |
| [📘 FS-010: Simulator and training](../functional/features/FS-010-simulator-and-training.md) | Synthetic Drones flying Choreographies at 50 Hz, thousands per node, for the 5,000-Drone load test | None new: used as the test bench |

**🎬 Use cases**

| Use case | In P6 | Screens moved to 📸 Screenshot |
| --- | --- | --- |
| [🎬 UC-016: Import and fly a Light show](../functional/use-cases/UC-016-import-and-fly-a-light-show.md) | Delivered: every step, every alternative flow (A1 to A6) | A1, A2, KO1, A3, OK, KO2 |
| [🎬 UC-014: Connect a new Drone model](../functional/use-cases/UC-014-connect-a-new-drone-model.md) | Applied to the show Drone model of [🤝 H-07](11-hardware-and-partners.md#h-07) | None: its screens were captured in P1 and P3 |
| [🎬 UC-003: Run the Pre-flight check and launch](../functional/use-cases/UC-003-run-the-pre-flight-check-and-launch.md) | Applied to a Squad of about 50 Drones, with the Light show checklist of the [🗃️ Operator](../glossary.md#ent-operator) | None: captured in P1 |

**📏 Business rules**

| Rule | In P6 |
| --- | --- |
| [📏 BR-002: Separation distance](../functional/business-rules/BR-002-separation-distance.md) | Delivered for Choreographies: every frame, between every two Drones and from the audience; at the edge, across the overlap of two sectors |
| [📏 BR-006: Fail-safe per Activity](../functional/business-rules/BR-006-fail-safe-per-activity.md) | Delivered for Light shows: the whole Squad Holds, then lands; Mission Held, then Aborted |
| [📏 BR-005: Autonomy level per Activity](../functional/business-rules/BR-005-autonomy-level-per-activity.md) | Applied: Light shows are Pre-planned, no Re-plan in flight (UC-016 A6) |
| [📏 BR-015: Approved Drone models only](../functional/business-rules/BR-015-approved-drone-models-only.md) | Applied: the rented show Drones fly only once their Drone model is Approved |
| [📏 BR-014: Simulation isolation](../functional/business-rules/BR-014-simulation-isolation.md) | Applied: the 5,000 synthetic Drones use separate credentials and cannot address a real Drone |
| [📏 BR-007: Launch only after a passed Pre-flight check](../functional/business-rules/BR-007-launch-only-after-a-passed-pre-flight-check.md) | Applied: the Pre-flight check covers every Drone of the show |

**🛠️ Technical pages**

| Page | What P6 builds from it |
| --- | --- |
| [🚀 Scalability and performance: partitioned edge](../technical/07-scalability.md#big-shows) | Sectors of up to 1,000 Drones, overlap checks, show coordinator, Telemetry to the core at 5 Hz, full-rate log uploaded after landing |
| [🚀 Scalability and performance: budgets](../technical/07-scalability.md#budgets) | Hold the Squad under 100 ms, safety tick under 10 ms per sector of 1,000, Choreography check under 30 s |
| [🚀 Scalability and performance: load tests](../technical/07-scalability.md#load-tests) | The nightly 5,000-Drone show in staging, chaos runs |
| [🔩 Engine and services: safety loop](../technical/04-engine.md#safety-loop) | The 50 Hz tick for Light shows, deviation from the Choreography position at the current time code |
| [🔩 Engine and services: planner](../technical/04-engine.md#planner) | Choreography checks in Rust, every frame in parallel (rayon) |
| [🔩 Engine and services: simulator](../technical/04-engine.md#simulator) | Synthetic Rust Drones for volume |
| [🔩 Engine and services: Drone adapters](../technical/04-engine.md#adapters) | The adapter interface for the show Drone model, Payload control for the show light |
| [🧱 Data models](../technical/02-data-models.md#models) | The `Choreography` model of the `missions` service |
| [🧱 Data models: Telemetry frames](../technical/02-data-models.md#telemetry) | `SquadFrame` at 50 Hz, delta-encoded |
| [🗄️ Storage: the edge store](../technical/03-storage.md#edge-store) | The Choreography copied to SQLite at the Pre-flight check |
| [🏗️ Architecture: edge and core](../technical/01-architecture.md#edge-and-core) | Several edges for one Mission (sectors) |
| [🖥️ GUI and WebUI: maps and 3D](../technical/10-frontends.md#maps) | Choreographies drawn in 3D with deck.gl in the Mission studio and Ground control |
| [🩺 Observability: the edge](../technical/08-observability.md#edge) | Tick duration and Link quality per sector, shown to the Pilot |

## <a id="epics"></a>🪜 Epics

| ID | Epic | Delivers | Where | Tickets | Parallel tasks for the agents |
| --- | --- | --- | --- | --- | --- |
| E6.1 | Choreography model and import | [🎬 UC-016](../functional/use-cases/UC-016-import-and-fly-a-light-show.md) steps 1 and 3 | `backend/apps/missions` (`Choreography` model and storage), `backend/apps/planner` (import parsers), object storage for the frames | 2: T6.01, T6.02 | Pydantic model and its tests; Skybrush Studio parser; Blender parser; sample Choreographies of 50, 200 and 5,000 Drones as test fixtures; migration (expand step) |
| E6.2 | Choreography checks in Rust | UC-016 step 2, A1 to A3; [📏 BR-002](../functional/business-rules/BR-002-separation-distance.md); FS-013 AC-1 | `rust` (`swarm-core` planner crate, PyO3), `backend/apps/planner` | 4: T6.03 to T6.05, T6.07 | Spatial hash grid per frame; audience and Site obstacle distances; speed and acceleration against the [🗃️ Drone model](../glossary.md#ent-drone-model); battery to the end of the show with the landing reserve; criterion benchmarks; refusal messages that name the frame, the Drones and the limit |
| E6.3 | Import screens and built-in designer | UC-016 A1, A2, KO1 screens; the timeline designer of FS-013 | `frontend/apps/mission-studio`, `frontend/packages` (`maps`, `ui`, `i18n`) | 3: T6.06, T6.08, T6.09 | Import screen and progress of the check; refusal panel with a jump to the frame; timeline of formations, transitions and colours; 3D preview in deck.gl; texts in English, French, German and Spanish |
| E6.4 | Flying the show at the edge | UC-016 steps 4 to 6, A5, A6; [📏 BR-006](../functional/business-rules/BR-006-fail-safe-per-activity.md); FS-013 AC-2 | `backend/apps/flight-engine` (show mode of the Mission actor), `rust` (`swarm-core` safety crate), `frontend/apps/ground-control`, `frontend/apps/desktop` | 4: T6.10 to T6.13 | 50 Hz tick with deviation from the Choreography; whole-Squad Hold then land; Mission Held then Aborted; time code out (SMPTE LTC, MIDI time code) and music playing; show view in Ground control (A3, OK, KO2) |
| E6.5 | Partitioned edge and show coordinator | Shows of more than 1,000 Drones | `backend/apps/flight-engine` (sector node, show coordinator), `backend/apps/planner` (sector split), `infra/` (edge appliance with several nodes) | 4: T6.14 to T6.17 | Sector split with overlap; separation across the overlap; coordinator time code and broadcast of Hold the Squad and land; Telemetry to the core at 5 Hz and upload of the full-rate log after landing |
| E6.6 | 5,000-Drone load test and chaos | Milestone M6, simulated part | `backend/apps/simulator` (synthetic Drones in show mode), `tests/` (load, chaos), staging cell | 3: T6.18 to T6.20 | Synthetic Drones at 50 Hz; nightly run with every budget as an assertion; chaos: sector node killed, Link cut, coordinator restarted mid-show |
| E6.7 | Real show | Milestone M6, real part; [🛫 C-06](10-flight-test-campaigns.md#c-06) | `backend/apps/fleet` (show Drone model), `backend/apps/flight-engine` (adapter of the show Drones), the [🗃️ Field kit](../glossary.md#ent-field-kit) | 5: T6.21 to T6.25 | Compatibility test of the show Drone model ([🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md)); show-light Payload control; Pre-flight check for about 50 Drones; screens to 📸 Screenshot; fixes from the rehearsals |

## <a id="sprints"></a>🗓️ Sprint plan

P6 shares S41 to S48 with [🛣️ P5: AI agents, MCP and A2A](06-p5-ai-agents.md), which plans 5 or 6 tickets in each of S41 to S43 and 1 or 2 in each of S44 to S48 for the core of the Assistant, and S45 to S48 with [🛣️ P7: Scale and reach](08-p7-scale-and-reach.md). P6 therefore takes one ticket per sprint until P5 reaches milestone M5, then most of the capacity. The counts below are P6's share; with the other phases each sprint carries about 7 or 8 merged tickets (see the note on capacity in [🎲 Risks](#risks)).

| Sprint | Dates | Tickets | Sprint goal | What can be shown |
| --- | --- | --- | --- | --- |
| S41 | 17 to 28 Jul 2028 | T6.01 Choreography model and Skybrush Studio import | A Choreography of the sample cast, imported and stored with its Mission | M-2026-0415 Riverside Festival show holds a Choreography of 200 Drones imported from Skybrush Studio |
| S42 | 31 Jul to 11 Aug 2028 | T6.02 Blender import | Both tools import the same show the same way | The same show from Blender and from Skybrush Studio gives the same frames |
| S43 | 14 to 25 Aug 2028 | T6.03 Separation check per frame (spatial hash grid) | The first rule of step 2 of UC-016 runs in Rust and names what fails | The check refuses the Choreography with AW-147 and AW-148 1.5 m apart at 02:14, under the Separation distance of 3 m |
| S44 | 28 Aug to 8 Sep 2028 | T6.04 Audience, Site obstacles, Geofence, speed and acceleration checks · T6.05 Battery to the end of the show · T6.06 Import and check screens (A1, A2, KO1) · T6.07 Check benchmark: 1,000 Drones over 10 minutes under 30 s · T6.08 Timeline designer, first version · T6.09 Designer 3D preview | The Mission planner imports, sees every check run, corrects the show, or builds a simple one | Léa Martin imports a show, sees the refused frame in 3D, corrects it in Skybrush Studio, imports it again and gets Mission: Planned |
| S45 | 11 to 22 Sep 2028 | T6.10 Show mode of the flight engine: 50 Hz tick, deviation from the Choreography · T6.11 Whole-Squad Fail-safe: Hold, land, Held then Aborted · T6.12 Time code out and music playing · T6.13 Show view of Ground control (A3, OK, KO2) | A show of 200 simulated Drones flown end to end in the Simulator, on the time code | Sam Carter flies the show in the Simulator; a motor fault injected on AW-063 Holds and lands the whole Squad |
| S46 | 25 Sep to 6 Oct 2028 | T6.14 Sector split in the planner · T6.15 Sector node: separation across the overlap · T6.16 Show coordinator: time code to every sector, Hold the Squad and land within 100 ms · T6.17 Telemetry to the core at 5 Hz, full-rate log uploaded after landing | Several edges fly one Mission as one Squad | A 2,000-Drone simulated show split into two sectors, Held by one press of the Pilot |
| S47 | 9 to 20 Oct 2028 | T6.18 Synthetic Drones in show mode at 50 Hz · T6.19 Nightly 5,000-Drone show in staging, budgets as assertions · T6.21 Show Drone model connected and approved (UC-014), show-light Payload control · T6.22 Pre-flight check and landing positions for about 50 Drones | The 5,000-Drone show runs every night; the rented show Drones are Approved and fly a rehearsal | The staging dashboard of a nightly run (five sectors, tick durations, Hold latency to every Drone); the first rehearsal of [🛫 C-06](10-flight-test-campaigns.md#c-06) with about 50 real Drones, without an audience |
| S48 | 23 Oct to 3 Nov 2028 | T6.20 Chaos runs on the partitioned edge · T6.23 UC-016 screens to 📸 Screenshot · T6.24 Fixes from the rehearsals, Flight log of the show in the evidence ledger · T6.25 M6 release: documentation, exit checks | The real show and the M6 demonstration | The show above an audience at the event of [🤝 P-05](11-hardware-and-partners.md#p-05), and the nightly 5,000-Drone run |

**Total: 25 tickets** (S41 1, S42 1, S43 1, S44 6, S45 4, S46 4, S47 4, S48 4).

**Tickets in detail**

| Ticket | Sprint | Epic | What it does | Done when |
| --- | --- | --- | --- | --- |
| T6.01 | S41 | E6.1 | `Choreography` as a Pydantic model in `backend/apps/missions`: the Drones, the frames (time, position and colour of each Drone), the landing positions; frames in object storage, the reference in PostgreSQL; Skybrush Studio import in `backend/apps/planner` | A show of 200 Drones from Skybrush Studio round-trips; a malformed export is refused with a message that names the problem |
| T6.02 | S42 | E6.1 | Blender import behind the same interface as T6.01 | The same show exported from Blender and from Skybrush Studio gives the same frames |
| T6.03 | S43 | E6.2 | Separation between every two Drones in every frame, in the `swarm-core` planner crate: a spatial hash grid with a cell the size of the Separation distance, frames checked in parallel with rayon | The Choreography with AW-147 and AW-148 1.5 m apart at 02:14 is refused, naming the frame and the two Drones ([📏 BR-002](../functional/business-rules/BR-002-separation-distance.md) example 2) |
| T6.04 | S44 | E6.2 | Distance from the audience and the obstacles declared on the Site, the Geofence and the Altitude ceiling, speed and acceleration against the limits of the Drone model | UC-016 A2 and A3 are refused, naming the frame, the Drone and the limit |
| T6.05 | S44 | E6.2 | Battery each Drone needs to the end of the show, with the landing reserve of the Operator (20 % by default) | A Drone short of battery is refused (UC-016 A2) |
| T6.06 | S44 | E6.3 | Import and check screens in the Mission studio (A1, A2, KO1); the refusal panel jumps to the frame at fault; texts in four languages | The screens match their mock-ups in light and dark mode; a Playwright test covers the import, the refusal and the corrected import (A4) |
| T6.07 | S44 | E6.2 | Criterion benchmark of the whole check, 1,000 Drones over 10 minutes; a regression of more than 5 % fails the build | The check stays under 30 s |
| T6.08 | S44 | E6.3 | Timeline designer, first version: formations, transitions, colours and the music track; the checks of E6.2 run on every save | A two-minute opening for 50 Drones is built on the timeline and accepted |
| T6.09 | S44 | E6.3 | 3D preview in deck.gl, moved along the time code, with the Drones at fault highlighted | A Choreography of 5,000 Drones previews within the [front-end budgets](../technical/10-frontends.md#performance) |
| T6.10 | S45 | E6.4 | Show mode of the Mission actor in `backend/apps/flight-engine`: the Choreography copied to SQLite at the Pre-flight check, a 50 Hz tick, the deviation of each Drone from its Choreography position at the current time code | The tick benchmark stays under 5 ms for 500 Drones at 50 Hz |
| T6.11 | S45 | E6.4 | Whole-Squad Fail-safe: every Drone Holds, then lands at its landing position; Mission Held, then Aborted after the last landing; a Drone that proposes a new path is refused (UC-016 A6) | FS-013 AC-2 passes in the Simulator with 200 Drones; Hold reaches every Drone in under 100 ms |
| T6.12 | S45 | E6.4 | Time code out from Ground control (SMPTE LTC as an audio signal, MIDI time code), or the music played by Ground control; both stop on a Fail-safe | The time code read back by a test receiver matches the show clock frame by frame over a 10-minute show |
| T6.13 | S45 | E6.4 | Show view of Ground control: the Squad in 3D on the map, the time code, the deviation per Drone, the Drone at fault (A3, OK, KO2) | The screens match their mock-ups; Playwright runs against the real images |
| T6.14 | S46 | E6.5 | Sector split in the planner: sectors of up to 1,000 Drones with overlapping borders, one sector per edge node | A 5,000-Drone show splits into five sectors; every Drone belongs to one sector, and the Drones of an overlap are known to both neighbours |
| T6.15 | S46 | E6.5 | Sector node: the flight engine runs one sector and checks separation across the overlap with its neighbour's frames | Two Drones made to converge across a border Hold the whole Squad |
| T6.16 | S46 | E6.5 | Show coordinator at the edge: one time code for every sector, Hold the Squad and land sent to every sector | Hold reaches every Drone of a 2,000-Drone show in under 100 ms |
| T6.17 | S46 | E6.5 | Telemetry to the core at 5 Hz during a show; the full-rate log kept at the edge and uploaded after landing | The ingest of the cell stays flat during a show; the full Flight log arrives after landing |
| T6.18 | S47 | E6.6 | Synthetic Rust Drones in show mode: they follow a Choreography at 50 Hz, speak MAVLink and accept injected faults | 1,000 synthetic Drones per node in staging, every Flight log marked simulated ([📏 BR-014](../functional/business-rules/BR-014-simulation-isolation.md)) |
| T6.19 | S47 | E6.6 | Nightly 5,000-Drone show in staging, every budget an assertion | A missed budget fails the run and blocks the release |
| T6.20 | S48 | E6.6 | Chaos on the partitioned edge: a sector node killed, the Link to the core cut, the show coordinator restarted | The Fail-safe holds in each scenario, reported in the nightly run |
| T6.21 | S47 | E6.7 | The Drone model of [🤝 H-07](11-hardware-and-partners.md#h-07) added and tested through [🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md) with the Drone adapter of its family; show-light Payload control (colour, on, off) | Drone model: Approved, after the Simulator where the Drone model allows it and one real flight |
| T6.22 | S47 | E6.7 | Pre-flight check for about 50 Drones: the grid of landing positions, the Light show checklist of the Operator, the Field kit | Sam Carter signs one Pre-flight check for the whole Squad and the Mission is Verified |
| T6.23 | S48 | E6.7 | The six screens of UC-016 captured from the application in light and dark mode | Mock-ups deleted; `specs.py check` prints nothing |
| T6.24 | S48 | E6.7 | Fixes from the rehearsals; the Flight log of the show signed and anchored; Debrief of the show | The Flight log of the show shows Evidence record: Verified ([🎬 UC-012](../functional/use-cases/UC-012-verify-the-evidence-record-of-a-flight.md)) |
| T6.25 | S48 | E6.7 | M6 release: technical pages brought up to date, demo script, exit checklist | Every exit criterion below is ticked |

## <a id="demo"></a>🎤 Demo

The M6 demonstration, on 3 November 2028, uses the sample cast of the [🎨 Visual identity](../visual-identity.md): the Operator Aerowing Services, the Mission planner Léa Martin, the Pilot Sam Carter (the person who builds Swarm), the Client Riverside Festival and the [🗃️ Site](../glossary.md#ent-site) Riverside park, which stand for the real event of [🤝 P-05](11-hardware-and-partners.md#p-05).

1. **Import and refusal.** Léa Martin opens 🖊️ Design in the Mission studio, on M-2026-0415 Riverside Festival show, [🔄 Mission: Draft](../glossary.md#st-mission-draft), Separation distance 3 m. She imports a Choreography of 200 Drones from Skybrush Studio. The check refuses it: at 02:14, AW-147 and AW-148 are 1.5 m apart. The frame is named and the 3D preview jumps to it (UC-016 KO1, FS-013 AC-1).
2. **Correction and acceptance.** She imports the corrected show; every frame passes, the check of 200 Drones takes a few seconds, and the Mission becomes [🔄 Mission: Planned](../glossary.md#st-mission-planned).
3. **Built-in designer.** She builds a short opening on the timeline (a grid that turns into a ring, colours changing on the beat) and the same checks run on it.
4. **Simulated show and fault.** Sam Carter runs the [🗃️ Pre-flight check](../glossary.md#ent-pre-flight-check) in Ground control on the simulated Squad of 200 Drones, the Mission becomes [🔄 Mission: Verified](../glossary.md#st-mission-verified), and he launches. Ground control sends SMPTE LTC to the audio desk. At 03:40 a motor fault is injected on AW-063: every Drone Holds within 100 ms, the time code and the music stop, the Mission is [🔄 Mission: Held](../glossary.md#st-mission-held) while the Drones land, then Aborted (UC-016 KO2, FS-013 AC-2).
5. **5,000 Drones.** The staging dashboard replays last night's run: a Choreography of 5,000 synthetic Drones over five sectors of 1,000, the show coordinator keeping one time code, the safety tick under 10 ms per sector, Hold the Squad reaching every Drone under 100 ms, Telemetry to the core at 5 Hz.
6. **The real show.** The video of the show of about 50 rented Drones above the audience of the P-05 event, flown by Sam Carter on the time code of the event's audio desk, from Pre-flight check to [🔄 Drone: Landed](../glossary.md#st-drone-landed) for every Drone and [🔄 Mission: Completed](../glossary.md#st-mission-completed). The [🗃️ Flight log](../glossary.md#ent-flight-log) of the show, with its [🗃️ Evidence record](../glossary.md#ent-evidence-record), is opened in the Back office.

If the event authorisation of [🏛️ G-08](09-regulatory-track.md#g-08) is refused or late, step 6 shows the fallback of [🎲 R-16](12-risks.md#r-16): the same show without spectators, filmed.

## <a id="exit"></a>🚪 Exit criteria

**Acceptance criteria**

- [ ] [📘 FS-013](../functional/features/FS-013-light-shows.md) AC-1: a Choreography with two Drones too close at one frame is refused and the frame is named ([📏 BR-002](../functional/business-rules/BR-002-separation-distance.md), [🎬 UC-016](../functional/use-cases/UC-016-import-and-fly-a-light-show.md)). Automated on the sample Choreographies, and shown in the demo.
- [ ] [📘 FS-013](../functional/features/FS-013-light-shows.md) AC-2: a show in flight where one Drone fails Holds every Drone, then lands ([📏 BR-006](../functional/business-rules/BR-006-fail-safe-per-activity.md), [🎬 UC-016](../functional/use-cases/UC-016-import-and-fly-a-light-show.md)). Automated in the Simulator for 200 and 5,000 Drones, and drilled once with the real Squad of [🛫 C-06](10-flight-test-campaigns.md#c-06) before the show.
- [ ] [📘 FS-011](../functional/features/FS-011-drone-adapters.md) AC-1 run for the show Drone model: a failed compatibility step keeps its Drones [🔄 Drone: Grounded](../glossary.md#st-drone-grounded).
- [ ] Every alternative flow of UC-016 (A1 to A6) has an automated test.

**Budgets** ([🚀 Scalability and performance](../technical/07-scalability.md#budgets))

- [ ] Hold the Squad or abort, to every Drone: under 100 ms, for 200 Drones on one edge and for 5,000 Drones over five sectors.
- [ ] Safety tick: under 10 ms per sector of 1,000 Drones at 50 Hz, and under 5 ms for 500 Drones; 99.99 % of ticks within budget ([🩺 Observability](../technical/08-observability.md#slos)).
- [ ] Choreography check, 1,000 Drones over 10 minutes: under 30 s, as a criterion benchmark on every pull request.
- [ ] Pilot command to Drone, at the edge on a local link: p99 under 50 ms during a show.
- [ ] Telemetry, Drone to the Pilot's screen: p95 under 150 ms at the edge.

**Load tests** ([🚀 Scalability and performance](../technical/07-scalability.md#load-tests))

- [ ] The nightly 5,000-Drone show on a partitioned edge has passed every night for the last two weeks of the phase.
- [ ] The chaos runs pass: a sector node killed mid-show, the Link to the core cut, the show coordinator restarted; the Fail-safe holds every time.

**Screens and specifications**

- [ ] The six screens of UC-016 (A1, A2, KO1, A3, OK, KO2) moved from ✏️ Mock-up to 📸 Screenshot, in light and dark mode, and their mock-ups deleted.
- [ ] `python3 .claude/skills/write-specs/scripts/specs.py check` prints nothing.

**Milestone M6**

- [ ] A real show of about 50 Drones flown at the event of [🤝 P-05](11-hardware-and-partners.md#p-05), or its fallback without spectators, filmed ([🎲 R-16](12-risks.md#r-16)).

## <a id="dependencies"></a>⛓️ Dependencies

**Previous phases**

| Phase | What P6 needs from it |
| --- | --- |
| [🛣️ P0: Foundations](01-p0-foundations.md) | The synthetic Rust Drones of the Simulator, NATS, TimescaleDB, the OpenTelemetry base, the i18n framework |
| [🛣️ P1: First flight](02-p1-first-flight.md) | The flight engine and its Rust safety loop, the MAVLink Drone adapter, Ground control (web and Tauri), the Pre-flight check, Fail-safes, the Mission studio, the compatibility test of [🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md) |
| [🛣️ P2: Inspection product](03-p2-inspection-product.md) | The first real Squad flights, in [🛫 C-02](10-flight-test-campaigns.md#c-02) (P1 flies one real Drone at a time); the evidence ledger, so the Flight log of the show is signed and anchored; Debrief of the show |
| [🛣️ P3: Patrol](04-p3-patrol.md) | Several edges per cell and Telemetry at scale through the gateway, reused by the sector nodes |
| [🛣️ P5: AI agents, MCP and A2A](06-p5-ai-agents.md) | Nothing in the flight path: the Co-pilot is never in the safety loop and stays off during a show |

**Regulatory, hardware, partners and campaigns**

| Item | Due | Why P6 needs it |
| --- | --- | --- |
| [🏛️ G-05](09-regulatory-track.md#g-05) | S20 | The Specific category Authorisation under which the show is flown |
| [🏛️ G-06](09-regulatory-track.md#g-06) | 2 sprints before C-06 | Airspace and U-space checks for the event Site |
| [🏛️ G-08](09-regulatory-track.md#g-08) | S44 | Event authorisation, safety perimeter with the event organiser and the prefecture, insurance above an audience |
| [🤝 H-03](11-hardware-and-partners.md#h-03) | S12 | The rugged edge box that runs the flight engine at the show |
| [🤝 H-07](11-hardware-and-partners.md#h-07) | S45 | About 50 rented show Drones with lights and their radios, flown as a Squad above an audience only under the event authorisation of G-08 |
| [🤝 P-05](11-hardware-and-partners.md#p-05) | S44 | The event hosting the show: an audience and a show slot |
| [🛫 C-06](10-flight-test-campaigns.md#c-06) | S46 to S48 | The rehearsals and the real show |

## <a id="risks"></a>🎲 Risks

| Risk | Why it matters in P6 | Response in P6 |
| --- | --- | --- |
| [🎲 R-16](12-risks.md#r-16) Show permissions refused or late | The real show is the proof of M6 | Start [🏛️ G-08](09-regulatory-track.md#g-08) with P-05 in S41; if there is no answer 8 weeks before the event, book the fallback: the same show without spectators, filmed |
| [🎲 R-03](12-risks.md#r-03) Safety tick budget missed | The Light show tick runs at 50 Hz, with deviation from the Choreography added | Benchmarks of the show tick from T6.10 (S45) on; the sector size can drop below 1,000 Drones if the tick misses 10 ms; no real flight with a missed budget |
| [🎲 R-07](12-risks.md#r-07) Weather and seasons | C-06 falls in October, in the evening, outdoors | Two rehearsal dates and a reserve show date with P-05; the weather limits of the Pre-flight check apply unchanged |
| [🎲 R-11](12-risks.md#r-11) Crash or hardware loss in tests | About 50 rented Drones fly close together | Every rehearsal starts with a Fail-safe drill (one Drone faulted, whole Squad lands); the rental terms of H-07 and the insurance of G-08 are checked before the first rehearsal |
| [🎲 R-01](12-risks.md#r-01) Review bottleneck | P6 overlaps P5 (S41 to S48) and P7 (S45 to S48), and the person flies [🛫 C-05](10-flight-test-campaigns.md#c-05) (S44 to S46) and C-06 (S46 to S48) | P6 takes one ticket per sprint while P5 finishes; from S44 the safety-path tickets (E6.2, E6.4, E6.5) are reviewed first, and agents prepare the screenshots and the documentation while the person flies; across P5, P6 and P7, S41 to S50 carry about 6 tickets each, one more than the usual capacity |
| [🎲 R-08](12-risks.md#r-08) Scope too large | The designer could grow without limit | The designer stays a timeline of formations, transitions and colours; complex shows come from Blender or Skybrush Studio |

## <a id="work-split"></a>🧑‍💻 Work split

**The person**

- **Decisions:** the sector size and overlap width once the first benchmarks are in (S46); the tolerance of deviation from the Choreography; which time code the P-05 audio desk takes (SMPTE LTC or MIDI time code); go or no-go for each rehearsal and for the show.
- **Reviews:** every ticket of E6.2, E6.4 and E6.5 line by line, because they are in the safety path; the other epics on their tests and screens.
- **Partners and paperwork:** the show slot and safety perimeter with P-05, the event authorisation and insurance of [🏛️ G-08](09-regulatory-track.md#g-08), the rental of [🤝 H-07](11-hardware-and-partners.md#h-07).
- **Flights:** the compatibility flight of the show Drone model, the rehearsals and the show of C-06, as the Pilot.

**The agents, in parallel**

- One agent per parser (Skybrush Studio, Blender) in S41 and S42, with shared fixtures.
- In S43 and S44, the separation, distance and battery checks are independent modules of the `swarm-core` planner crate, each with its benchmark, while other agents build the import screens and the designer.
- In S45, the flight engine show mode, the time code output and the Ground control screens run as separate tasks behind one interface agreed in the ticket.
- Load-test scripts, chaos scenarios, mock-up updates, screenshots in light and dark mode, translations in four languages and the technical page updates run alongside every ticket.

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ P5: AI agents, MCP and A2A](06-p5-ai-agents.md) · 📄 **Page 113 / 120** · [P7: Scale and reach ▶️](08-p7-scale-and-reach.md)
<!-- /spec:nav-bottom -->
