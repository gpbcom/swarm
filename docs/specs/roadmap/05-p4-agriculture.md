# 🛣️ P4: Agriculture

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ P3: Patrol](04-p3-patrol.md) · 📄 **Page 100 / 108** · [P5: AI agents, MCP and A2A ▶️](06-p5-ai-agents.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Sprints:** S32 to S38 · **Dates:** 13 Mar 2028 to 16 Jun 2028 · **Tickets:** about 25, plus one slot reserved for the Patrol beta

> [!NOTE]
> P4 teaches Swarm to spray a [🗃️ Field](../glossary.md#ent-field) with a [🗃️ Squad](../glossary.md#ent-squad) at the doses of its [🗃️ Prescription map](../glossary.md#ent-prescription-map), with supervised refills and nothing sprayed outside the Field, and it comes now because the spring window (campaign [🛫 C-04](10-flight-test-campaigns.md#c-04)) is the only time before the autumn beta (M4) to fly it on a real farm.

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

At the end of P4, on 16 June 2028, the [👤 Pilot](../glossary.md#per-pilot) of the [🗃️ Operator](../glossary.md#ent-operator) Aerowing Services supervises a Squad of rented spray [🗃️ Drones](../glossary.md#ent-drone) over a partner Field, as written in [🎬 UC-017: Spray a Field with refills](../functional/use-cases/UC-017-spray-a-field-with-refills.md):

- The [👤 Mission planner](../glossary.md#per-mission-planner) imports the Field boundary and its Prescription map from a Shapefile or an ISOXML file, or sets a uniform dose, in the [⚙️ Mission studio](../glossary.md#sys-mission-studio). The Field sets the [🗃️ Geofence](../glossary.md#ent-geofence) of the [🗃️ Mission](../glossary.md#ent-mission) ([📏 BR-001](../functional/business-rules/BR-001-geofence-and-altitude-ceiling.md)).
- The planner splits the Field between the Drones of the Squad, on Pre-planned routes ([📏 BR-005](../functional/business-rules/BR-005-autonomy-level-per-activity.md)), and computes for each leg the pump flow that gives the dose of the zone below it ([📏 BR-018](../functional/business-rules/BR-018-dose-follows-the-prescription-map.md)).
- At the edge, the safety loop stops the pump of any Drone that reaches the Field boundary, every tick, even if the core is out of reach: nothing is sprayed outside the Field.
- When a tank reaches the refill level the Operator set (10 % by default), the Squad proposes a refill [🗃️ Re-plan](../glossary.md#ent-re-plan) that waits for the Pilot ([📏 BR-013](../functional/business-rules/BR-013-re-plan-approval.md)); the Drone flies to the refill point at the [🗃️ Field kit](../glossary.md#ent-field-kit) and resumes where it stopped.
- [⚙️ Ground control](../glossary.md#sys-ground-control) shows the dose of each zone, the tank of each Drone, the area sprayed, the points where a pump stopped and the gaps left.
- After landing, Swarm records the dose applied in each zone as a spray map [🗃️ Deliverable](../glossary.md#ent-deliverable) with its [🗃️ Evidence record](../glossary.md#ent-evidence-record) ([📏 BR-009](../functional/business-rules/BR-009-evidence-integrity.md)), and keeps the licences of the Pilot and of the Operator that [📘 FS-014](../functional/features/FS-014-agriculture.md#details) lists.

P4 also leaves Swarm ready for the autumn seeding beta (campaign [🛫 C-05](10-flight-test-campaigns.md#c-05), milestone M4 on 6 October 2028) on the partner farm [🤝 P-04](11-hardware-and-partners.md#p-04).

## <a id="scope"></a>🧺 Scope

**Features**

| Feature | What P4 delivers of it |
| --- | --- |
| [📘 FS-014: Agriculture](../functional/features/FS-014-agriculture.md) | All of it: Field and Prescription map import, uniform dose, Field split between the Squad, dose per zone, pump stopped at the Field boundary, refills, spray map, licences per Pilot and per Operator |
| [📘 FS-001: Mission design](../functional/features/FS-001-mission-design.md) | The Agriculture part of the Mission studio: a Field instead of a drawn area, the Prescription map layer, the swath and the refill point |
| [📘 FS-005: Fleet and readiness](../functional/features/FS-005-fleet-and-readiness.md) | The sprayer tank and the spreader as [🗃️ Payloads](../glossary.md#ent-payload), with their capacity and compatibility |
| [📘 FS-006: Authorisations and compliance](../functional/features/FS-006-authorisations-and-compliance.md) | The licences of [📘 FS-014](../functional/features/FS-014-agriculture.md#details): drone qualification and pesticide applicator licence per Pilot, Part 137 certificate per Operator in the US |
| [📘 FS-011: Drone adapters](../functional/features/FS-011-drone-adapters.md) | Payload control for a sprayer (pump on, off and flow) and tank level in the MAVLink adapter; the rented spray Drone model approved |
| [📘 FS-021: Ground control monitoring](../functional/features/FS-021-ground-control-monitoring.md) | The Agriculture panels: doses, tanks, area sprayed, pump stops, gaps |
| [📘 FS-022: Debrief and assessment](../functional/features/FS-022-debrief-and-assessment.md) | The Agriculture part of the Debrief and of the [🗃️ Scorecard](../glossary.md#ent-scorecard): area treated against the Field, gaps, refills |

**Use cases**

| Use case | What P4 delivers of it |
| --- | --- |
| [🎬 UC-017: Spray a Field with refills](../functional/use-cases/UC-017-spray-a-field-with-refills.md) | All of it, main flow and alternatives A1 and A2, with its six screens moved to 📸 Screenshot |
| [🎬 UC-001: Design a Mission](../functional/use-cases/UC-001-design-a-mission.md) | Designing an Agriculture Mission from an imported Field and Prescription map |
| [🎬 UC-004: Supervise a Squad and approve a Re-plan](../functional/use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md) | The refill Re-plan, reusing the approval flow and its 60-second countdown |
| [🎬 UC-014: Connect a new Drone model](../functional/use-cases/UC-014-connect-a-new-drone-model.md) | The rented spray Drone model of [🤝 H-06](11-hardware-and-partners.md#h-06), through the compatibility test suite, then one real flight |

**Business rules**

| Rule | Where P4 enforces it |
| --- | --- |
| [📏 BR-018: Dose follows the Prescription map](../functional/business-rules/BR-018-dose-follows-the-prescription-map.md) | Planner (flow per leg), Drone adapter (pump flow), edge safety loop (pump stopped at the Field boundary), spray map (dose applied per zone) |
| [📏 BR-001: Geofence and Altitude ceiling](../functional/business-rules/BR-001-geofence-and-altitude-ceiling.md) | The Field boundary sets the Geofence of the Mission |
| [📏 BR-005: Autonomy level per Activity](../functional/business-rules/BR-005-autonomy-level-per-activity.md) | Pre-planned routes, refills and failures re-planned under supervision |
| [📏 BR-013: Re-plan approval](../functional/business-rules/BR-013-re-plan-approval.md) | Every refill Re-plan waits for the Pilot |
| [📏 BR-022: Payload compatibility](../functional/business-rules/BR-022-payload-compatibility.md) | A sprayer tank or a spreader only on a Drone model that carries it, within its weight limit |
| [📏 BR-015: Approved Drone models only](../functional/business-rules/BR-015-approved-drone-models-only.md) | The rented spray Drones fly only once their model is Approved |
| [📏 BR-007: Launch only after a passed Pre-flight check](../functional/business-rules/BR-007-launch-only-after-a-passed-pre-flight-check.md) | A missing or expired licence of the Pilot or of the Operator fails the Pre-flight check of an Agriculture Mission |
| [📏 BR-009: Evidence integrity](../functional/business-rules/BR-009-evidence-integrity.md) | The spray map gets its Evidence record |
| [📏 BR-017: Every screen in four languages](../functional/business-rules/BR-017-every-screen-in-four-languages.md) | Every new Agriculture screen in English, French, German and Spanish |

**Technical pages**

| Page | What P4 builds on |
| --- | --- |
| [🧮 Planner](../technical/04-engine.md#planner) | Coverage paths with boustrophedon decomposition, refills in the Re-plans, Shapefile and ISOXML parsed into zones with a dose each |
| [🛡️ Safety loop](../technical/04-engine.md#safety-loop) | The Geofence step of the tick, extended with the pump cut at the Field boundary, within the safety tick budget |
| [🧷 Drone adapters](../technical/04-engine.md#adapters) | The Payload control method of the adapter interface, used for the pump |
| [🕹️ Simulator](../technical/04-engine.md#simulator) | A simulated sprayer (tank, flow, pump state) on synthetic Rust Drones and PX4 SITL |
| [🧱 Main models](../technical/02-data-models.md#models) | `Field` and `PrescriptionMap` in the missions service, the sprayer and spreader `Payload` in the fleet service; units in names: `dose_l_ha` for spraying and `dose_kg_ha` for seeding |
| [🗄️ PostgreSQL and PostGIS](../technical/03-storage.md#postgresql) | GiST indexes on Fields and Prescription map zones |
| [🕰️ TimescaleDB for Telemetry](../technical/03-storage.md#timescaledb) | Pump state and flow per tick, from which the dose applied is computed |
| [🗺️ Maps and 3D](../technical/10-frontends.md#maps) | deck.gl layers for Prescription map zones and the live spray coverage |
| [⏱️ Budgets](../technical/07-scalability.md#budgets) | Every budget holds with Agriculture Missions in the nightly load test |

## <a id="epics"></a>🪜 Epics

| # | Epic | Delivers (UC/BR links) | Where (services, apps, packages) | Tickets | Parallel tasks for the agents |
| --- | --- | --- | --- | --- | --- |
| E4.1 | Fields and Prescription maps | [🎬 UC-017](../functional/use-cases/UC-017-spray-a-field-with-refills.md) preconditions 2 and 3, [🎬 UC-001](../functional/use-cases/UC-001-design-a-mission.md), [📏 BR-018](../functional/business-rules/BR-018-dose-follows-the-prescription-map.md), [📏 BR-001](../functional/business-rules/BR-001-geofence-and-altitude-ceiling.md) | `services/missions` (models, storage, REST), `packages/rust` planner crate (parsers), `frontends/mission-studio`, `packages/ts/maps` | T4.01, T4.02, T4.03, T4.06, T4.07 (5) | Rust parser and fixtures; Python models with their validators and exceptions; PostGIS migration; REST endpoints and the generated `api-client`; deck.gl layer; mock-up update of UC-001 |
| E4.2 | Coverage and dose | [🎬 UC-017](../functional/use-cases/UC-017-spray-a-field-with-refills.md) steps 1 and 2, [📏 BR-018](../functional/business-rules/BR-018-dose-follows-the-prescription-map.md), [📏 BR-005](../functional/business-rules/BR-005-autonomy-level-per-activity.md) | `packages/rust` planner crate, `services/planner` | T4.04, T4.08, T4.19 (3) | Rust algorithm and criterion benchmark; property tests on the dose (every point of a zone gets its dose); Python service wrapper; planner documentation |
| E4.3 | Spraying at the edge | [🎬 UC-017](../functional/use-cases/UC-017-spray-a-field-with-refills.md) steps 2 and 3, alternative A2, [📏 BR-018](../functional/business-rules/BR-018-dose-follows-the-prescription-map.md), [📏 BR-022](../functional/business-rules/BR-022-payload-compatibility.md) | `services/flight-engine` (MAVLink adapter, safety loop), `packages/rust` safety crate, `services/fleet`, `services/simulator` | T4.05, T4.09, T4.10, T4.11 (4) | Rust safety step and its benchmark; adapter command and Telemetry fields; simulated sprayer; fleet Payload kinds; simulator scenario tests of the pump cut |
| E4.4 | Refills and supervised Re-plans | [🎬 UC-017](../functional/use-cases/UC-017-spray-a-field-with-refills.md) steps 4 and 5, alternative A1, [🎬 UC-004](../functional/use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md), [📏 BR-013](../functional/business-rules/BR-013-re-plan-approval.md), [📏 BR-005](../functional/business-rules/BR-005-autonomy-level-per-activity.md) | `packages/rust` planner crate (edge library), `services/flight-engine`, `services/missions`, `frontends/back-office` | T4.13, T4.14, T4.16 (3) | Refill trigger in the edge tick; Re-plan in the planner library, offline; Operator setting in the Back office; simulator scenarios (approved, rejected, no answer in 60 seconds) |
| E4.5 | Ground control for Agriculture | [🎬 UC-017](../functional/use-cases/UC-017-spray-a-field-with-refills.md) screens A1 to A4, OK and KO, [📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md) | `frontends/ground-control`, `packages/ts/maps`, `packages/ts/live`, `packages/ts/i18n` | T4.17, T4.18 (2) | React panels on the design tokens; deck.gl coverage layer fed from the Web Worker; messages in four languages; Playwright tests against the images |
| E4.6 | Records, evidence and licences | [🎬 UC-017](../functional/use-cases/UC-017-spray-a-field-with-refills.md) step 6 and precondition 5, [📏 BR-007](../functional/business-rules/BR-007-launch-only-after-a-passed-pre-flight-check.md), [📏 BR-009](../functional/business-rules/BR-009-evidence-integrity.md), [📏 BR-018](../functional/business-rules/BR-018-dose-follows-the-prescription-map.md) | `services/missions`, `services/processing` (spray map), `services/evidence`, `frontends/back-office`, `frontends/client-portal`, `frontends/ground-control` (Debrief) | T4.15, T4.20, T4.21, T4.22 (4) | TimescaleDB query of pump state per zone; spray map tiles; Evidence record hook; Back office licence forms; Debrief and Scorecard criteria for Agriculture |
| E4.7 | Spray Drones, campaign and beta readiness | [🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md), [📏 BR-015](../functional/business-rules/BR-015-approved-drone-models-only.md), [📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md) | `services/flight-engine`, `services/fleet`, `services/simulator`, `tests/load`, `docs/specs/screens` | T4.12, T4.23, T4.24, T4.25 (4) | Compatibility suite run in the simulator; field checklist; k6 and simulated fleet scenarios; screenshots of UC-017 in light and dark mode replacing the mock-ups |
| E4.8 | Patrol beta support (reserved) | [🎬 UC-018](../functional/use-cases/UC-018-respond-to-a-site-alarm.md), [🎬 UC-019](../functional/use-cases/UC-019-request-a-patrol-on-demand.md) | Whichever services and apps the Patrol beta needs fixed | T4.26 (1) | The fix, its regression test and its screenshot update, as for any ticket |

## <a id="sprints"></a>🗓️ Sprint plan

P4 overlaps the last two sprints of [🛣️ P3: Patrol](04-p3-patrol.md) and the first three of [🛣️ P5: AI agents, MCP and A2A](06-p5-ai-agents.md). Its tickets are spread so that about 5 tickets are merged per sprint across the phases running at the same time: 2 and 3 in S32 and S33 while P3 closes, 5 in S34 and S35, then 3, 3 and 4 while P5 starts. **One slot of S38 is reserved for fixes of the Patrol beta** (milestone M3, 30 June 2028, [🛣️ P3: Patrol](04-p3-patrol.md)): ticket T4.26, filled with whatever the beta raises, so S38 merges 5 tickets and P5 merges none that sprint.

| Sprint | Dates | Tickets | Sprint goal | What can be shown |
| --- | --- | --- | --- | --- |
| S32 | 13 to 24 Mar 2028 | T4.01 Field and Prescription map models and storage; T4.02 Shapefile import of Field boundaries and Prescription maps | A Field and its zones, each with a dose, are stored per Operator and read back through REST | A Shapefile from the partner farm ([🤝 P-04](11-hardware-and-partners.md#p-04)) imported in the dev cell, its zones and doses listed |
| S33 | 27 Mar to 7 Apr 2028 | T4.03 ISOXML import; T4.04 Coverage of a Field with the swath of each Payload; T4.05 Simulated sprayer | Both formats import; the planner covers a Field with the swath of each Drone; simulated Drones carry a tank that empties as they spray | North field imported from ISOXML and split between Alpha, Bravo and Charlie in the [⚙️ Simulator](../glossary.md#sys-simulator), tanks emptying |
| S34 | 10 to 21 Apr 2028 | T4.06 Mission studio for Agriculture; T4.07 Field sets the Geofence; T4.08 Dose computation per leg; T4.09 Sprayer and spreader Payloads in the Fleet; T4.10 Pump control and tank level in the MAVLink adapter | The Mission planner designs M-2026-0413 from the imported Field; each leg carries its pump flow; the rented spray Drones arrive ([🤝 H-06](11-hardware-and-partners.md#h-06)) | A Mission designed end to end in the Mission studio and simulated; on the ground at the farm, the pump of one rented Drone driven by Swarm with clear water |
| S35 | 24 Apr to 5 May 2028 | T4.11 Pump cut at the Field boundary in the safety loop; T4.12 Spray Drone model connected and Approved; T4.13 Refill level setting and trigger; T4.14 Refill Re-plan in the planner library; T4.15 Licences of the Pilot and the Operator | Nothing can be sprayed outside the Field; the spray Drone model passes its compatibility suite then one real flight; a tank at 10 % produces a refill Re-plan | First real flight of one spray Drone over the partner Field with water, the pump stopping at the boundary; a refill Re-plan approved in the Simulator |
| S36 | 8 to 19 May 2028 | T4.16 Resume where stopped and gaps; T4.17 Ground control Agriculture panels; T4.18 Live spray coverage layer | The Pilot sees doses, tanks, area sprayed and gaps live; a refilled Drone resumes exactly where it stopped | The first Squad of rented spray Drones sprays the partner Field with water, one refill approved by the Pilot, gaps shown live |
| S37 | 22 May to 2 Jun 2028 | T4.19 Planned refills and battery swaps at design time; T4.20 Dose applied per zone; T4.21 Spray map Deliverable with its Evidence record | The Mission planner sees the refills a Mission will need before it flies; after landing, the dose applied per zone becomes a spray map with its Evidence record | A spraying under the rules of [🏛️ G-07](09-regulatory-track.md#g-07), and the spray map of that flight verified with its Evidence record |
| S38 | 5 to 16 Jun 2028 | T4.22 Debrief and Scorecard for Agriculture; T4.23 Four languages and screenshots of UC-017; T4.24 Agriculture load test; T4.25 Spreader for the autumn seeding beta; T4.26 Patrol beta fixes (reserved slot) | Every exit criterion passes; the Patrol beta gets its fixes; Swarm is ready for the seeding campaign [🛫 C-05](10-flight-test-campaigns.md#c-05) | The [end-of-phase demonstration](#demo) to the design partner, and the 50-Drone Agriculture Mission in the nightly load test |

**Tickets in detail**

| Ticket | Sprint | Epic | What it does | Done when |
| --- | --- | --- | --- | --- |
| T4.01 | S32 | E4.1 | `Field` (boundary, Site, Client) and `PrescriptionMap` (zones, dose per zone in `dose_l_ha` for spraying or `dose_kg_ha` for seeding) as Pydantic models in `services/missions`, PostGIS tables with GiST indexes, REST resources with `ETag` and `Idempotency-Key` | A Field round-trips through REST; a zone outside its Field is refused with its own exception |
| T4.02 | S32 | E4.1 | Shapefile parser in the Rust planner crate (boundary and zones, the dose attribute chosen on import), exposed through PyO3 to the planner service | The partner farm's sample files import; a malformed file is refused with a message that names the problem |
| T4.03 | S33 | E4.1 | ISOXML parser for the same zones and doses, in the same crate, behind the same interface as T4.02 | The same Field imported from Shapefile and from ISOXML gives the same zones and doses |
| T4.04 | S33 | E4.2 | Coverage of a Field: boustrophedon decomposition with the swath of each Payload, legs assigned between the Drones by Payload, speed and battery | North field split between three simulated Drones with no strip left out; criterion benchmark added to the pull request run |
| T4.05 | S33 | E4.3 | Simulated sprayer on synthetic Rust Drones and PX4 SITL: tank capacity, flow, pump state, tank level in the Telemetry | A simulated Squad empties its tanks at the planned flows; scenario tests use it |
| T4.06 | S34 | E4.1 | Mission studio for Agriculture: choose the Field, show the Prescription map zones and doses, or set a uniform dose; refill point at the Field kit | [🎬 UC-001](../functional/use-cases/UC-001-design-a-mission.md) done for an Agriculture Mission in the browser and in the Tauri desktop app |
| T4.07 | S34 | E4.1 | The Field boundary sets the Geofence of the Mission; the Altitude ceiling of the [🗃️ Authorisation](../glossary.md#ent-authorisation) applies as for every Mission | A route leaving the Field is refused at design time ([📏 BR-001](../functional/business-rules/BR-001-geofence-and-altitude-ceiling.md)) |
| T4.08 | S34 | E4.2 | Dose computation: for each leg, the pump flow from the dose of the zone below it, the swath and the planned speed; legs crossing two zones change flow at the zone edge | Property test: every sampled point of a zone receives the dose of that zone, and the uniform dose when there is no Prescription map ([📏 BR-018](../functional/business-rules/BR-018-dose-follows-the-prescription-map.md) examples 1 and 2) |
| T4.09 | S34 | E4.3 | Sprayer tank and spreader as Payload kinds in `services/fleet`, with capacity, swath and weight; compatibility with the Drone model | A sprayer tank on a Drone model that cannot carry it is refused ([📏 BR-022](../functional/business-rules/BR-022-payload-compatibility.md)) |
| T4.10 | S34 | E4.3 | Payload control for a sprayer in the MAVLink adapter: pump on, off and flow; tank level read back in the Telemetry | Commands acknowledged per Drone on PX4 SITL, then on one rented Drone on the ground with clear water |
| T4.11 | S35 | E4.3 | Pump cut in the Rust safety tick: a Drone with its pump on that reaches the Field boundary has its pump stopped, at the edge, offline; the pump also stops outside the planned legs | [📏 BR-018](../functional/business-rules/BR-018-dose-follows-the-prescription-map.md) example 3 passes in simulation and in flight; the safety tick stays under 5 ms for 500 Drones |
| T4.12 | S35 | E4.7 | The rented spray Drone model of [🤝 H-06](11-hardware-and-partners.md#h-06) connected through [🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md): compatibility suite in the Simulator, then one real flight | The model is [🔄 Drone model: Approved](../glossary.md#st-drone-model-approved) ([📏 BR-015](../functional/business-rules/BR-015-approved-drone-models-only.md)) |
| T4.13 | S35 | E4.4 | Refill level as an Operator setting in the Back office (10 % by default, from [📘 FS-014](../functional/features/FS-014-agriculture.md#details)); the edge tick raises the refill trigger when a tank reaches it | The trigger fires at the setting in simulation, for each Drone separately |
| T4.14 | S35 | E4.4 | Refill Re-plan in the planner library at the edge: fly to the refill point, then back to the point where the pump stopped; proposed by the Squad and sent to Ground control for approval | [📘 FS-014](../functional/features/FS-014-agriculture.md) AC-2 passes in simulation, online and with the core cut |
| T4.15 | S35 | E4.6 | Licences in the Back office: per Pilot, the drone qualification of the [🔤 Jurisdiction](../glossary.md#term-jurisdiction) (EU A2 or STS, US Part 107) and the pesticide applicator licence; per Operator, the Part 137 certificate in the US ; the Pre-flight check of an Agriculture Mission fails when a licence of the Pilot or of the Operator is missing or expired ([📏 BR-007](../functional/business-rules/BR-007-launch-only-after-a-passed-pre-flight-check.md)) | Recorded with their expiry and listed with the Pilot and the Operator, as in [🎬 UC-017](../functional/use-cases/UC-017-spray-a-field-with-refills.md) precondition 5; a test Pilot with an expired pesticide applicator licence, and a US Operator without its Part 137 certificate, each fail the Pre-flight check with the licence named |
| T4.16 | S36 | E4.4 | Resume where stopped after a refill; a rejected or unanswered refill Re-plan leaves the strip unsprayed and marked as a gap | Alternative A1 of [🎬 UC-017](../functional/use-cases/UC-017-spray-a-field-with-refills.md) passes; the gap appears on the map and in the area sprayed |
| T4.17 | S36 | E4.5 | Ground control Agriculture panels: dose of each zone, tank of each Drone, area sprayed, refill Re-plan with its countdown | Screens A1, A2 and A3 of [🎬 UC-017](../functional/use-cases/UC-017-spray-a-field-with-refills.md#screens) match their mock-ups |
| T4.18 | S36 | E4.5 | Live spray coverage layer: the strips sprayed, the points where a pump stopped at the boundary, the gaps; decoded in the Web Worker, drawn by deck.gl | Screens A4, OK and KO match their mock-ups; the layer keeps the front-end budgets with 50 Drones |
| T4.19 | S37 | E4.2 | Planned refills and battery swaps at design time: the planner estimates when each tank and each [🗃️ Battery](../glossary.md#ent-battery) runs out and shows the expected refills in the Mission studio | The estimate is within one refill of what the simulated Squad does |
| T4.20 | S37 | E4.6 | Dose applied per zone, computed from the pump state and flow stored per tick in TimescaleDB, at the end of the Mission | In the Simulator, the dose applied matches the planned dose; on a real flight, a zone whose dose applied differs from the Prescription map by more than the pump's measured accuracy is marked on the spray map |
| T4.21 | S37 | E4.6 | Spray map as a Deliverable (processing worker, tiles for the Client portal), with its Evidence record signed and chained ([📏 BR-009](../functional/business-rules/BR-009-evidence-integrity.md)) | [📘 FS-014](../functional/features/FS-014-agriculture.md) AC-1 passes: each zone shows its dose on the spray map |
| T4.22 | S38 | E4.6 | Debrief and Scorecard for Agriculture: area treated against the Field, gaps, refills, pump stops at the boundary | The Debrief of a campaign flight shows them, and the Scorecard is assessed against the request |
| T4.23 | S38 | E4.7 | Every new screen in English, French, German and Spanish ([📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md)); screenshots of the six states of [🎬 UC-017](../functional/use-cases/UC-017-spray-a-field-with-refills.md#screens) in light and dark mode replace the mock-ups | `specs.py check` passes with the six rows in 📸 Screenshot |
| T4.24 | S38 | E4.7 | Agriculture load test: a 50-Drone Agriculture Mission (the per-Mission limit of [🎯 Targets](../technical/07-scalability.md#targets)) added to the nightly staging run, alongside the 200 Missions of the cell | Every budget of [⏱️ Budgets](../technical/07-scalability.md#budgets) holds; a miss fails the run |
| T4.25 | S38 | E4.7 | Spreader Payload for seeding: spreader control in the adapter and the simulator, the seeding dose per zone in kg/ha (`dose_kg_ha`) in the planner, as a fallback that needs no product ([🏛️ G-07](09-regulatory-track.md#g-07)) | A simulated seeding of North field passes the same checks as spraying; ready for [🛫 C-05](10-flight-test-campaigns.md#c-05) |
| T4.26 | S38 | E4.8 | Reserved slot for the Patrol beta (M3): the fixes its Dock site raises in its first weeks, chosen by the person at the start of S38 | Each fix merged with its test; the slot is not used for Agriculture work |

## <a id="demo"></a>🎤 Demo

Given on Friday 16 June 2028 to the design partner ([🤝 P-01](11-hardware-and-partners.md#p-01)), first on the screens with the sample cast, then with the recording of the last campaign flight on the partner farm. Sample cast: the Operator Aerowing Services, the Pilot Sam Carter, the Mission planner Léa Martin, the [👤 Client](../glossary.md#per-client) Domaine des Trois Chênes, the Field North field, the Mission M-2026-0413 Spraying of North field, the Drones Alpha, Bravo and Charlie.

1. **Import.** Léa Martin opens M-2026-0413 in the Mission studio, imports North field and its Prescription map from an ISOXML file: zone A at 2 L/ha, zone B at 1 L/ha. She shows the same Field imported from a Shapefile, with the same zones.
2. **Design.** The Field becomes the Geofence. The planner splits North field between Alpha, Bravo and Charlie, each with a sprayer tank, and shows the flow of each leg and the refills expected. Léa switches to a uniform dose of 1.5 L/ha to show [📏 BR-018](../functional/business-rules/BR-018-dose-follows-the-prescription-map.md) example 2, then back to the Prescription map.
3. **Licences.** In the Back office, the licences of Sam Carter are recorded: his drone qualification for the EU (EASA) Jurisdiction and his pesticide applicator licence. On a copy where that licence has expired, the Pre-flight check of M-2026-0413 fails and names the licence.
4. **Launch.** Sam Carter passes the Pre-flight check and launches the Squad in Ground control ([🎬 UC-017](../functional/use-cases/UC-017-spray-a-field-with-refills.md) steps 1 and 2). The map shows zone A and zone B, each Drone's tank and the area sprayed growing.
5. **Boundary.** Bravo reaches the edge of North field at the end of a pass: its pump stops, the point shows on the map (step 3, alternative A2).
6. **Refill.** Alpha's tank reaches 10 %. The Squad proposes a refill Re-plan, Ground control shows it with its 60-second countdown, and Sam approves it (steps 4 and 5). Alpha flies to the Field kit, the crew refills it, and Alpha resumes where it stopped while Bravo and Charlie keep spraying.
7. **Rejection.** On a second run in the Simulator, Sam rejects the refill Re-plan of Charlie: the strip Charlie could not spray shows as a gap (alternative A1).
8. **Spray map.** The Squad lands, M-2026-0413 is [🔄 Mission: Completed](../glossary.md#st-mission-completed), and the spray map shows the dose applied in each zone. Léa opens its Evidence record and verifies it.
9. **Real flight.** The same steps, replayed from the Flight log of the last flight of [🛫 C-04](10-flight-test-campaigns.md#c-04) on the partner farm, with the rented spray Drones.
10. **Scale.** The nightly load test report: a 50-Drone Agriculture Mission flown in staging with every budget held.

## <a id="exit"></a>🚪 Exit criteria

P4 closes when every box below is ticked. A box that cannot be ticked by 16 June 2028 moves, with a ticket, to the sprint where the autumn seeding beta needs it, and is reported in the [🎲 risks register](12-risks.md).

- [ ] [📘 FS-014](../functional/features/FS-014-agriculture.md#acceptance) AC-1: given a Prescription map with two zones, when the Squad sprays, then each zone receives its dose and the spray map shows it. Proved in the Simulator and on the partner farm.
- [ ] [📘 FS-014](../functional/features/FS-014-agriculture.md#acceptance) AC-2: given a Drone with an empty tank, when it needs a refill, then Swarm proposes a refill Re-plan to the Pilot. Proved online and with the core cut.
- [ ] [📏 BR-018](../functional/business-rules/BR-018-dose-follows-the-prescription-map.md#examples) examples 1, 2 and 3 pass as automated scenario tests in the Simulator.
- [ ] [🎬 UC-017](../functional/use-cases/UC-017-spray-a-field-with-refills.md) main flow and alternatives A1 and A2 pass end to end in Playwright, against the real images of `compose.e2e.yaml`.
- [ ] A missing or expired licence of the Pilot or of the Operator fails the Pre-flight check of an Agriculture Mission ([📏 BR-007](../functional/business-rules/BR-007-launch-only-after-a-passed-pre-flight-check.md)), proved by T4.15's tests.
- [ ] The rented spray Drone model is [🔄 Drone model: Approved](../glossary.md#st-drone-model-approved) ([📏 BR-015](../functional/business-rules/BR-015-approved-drone-models-only.md)).
- [ ] Budgets of [⏱️ Budgets](../technical/07-scalability.md#budgets) hold in the nightly load test with the Agriculture Mission added: safety tick under 5 ms for 500 Drones with the pump cut step, Pilot command to Drone p99 under 50 ms at the edge, Hold the Squad or abort to every Drone under 100 ms, Telemetry p95 under 150 ms at the edge and under 400 ms through the cell, REST inside a cell p95 under 100 ms for reads and under 250 ms for writes.
- [ ] The Rust benchmarks of the planner (coverage and dose) and of the safety tick show no regression above 5 % ([🏋️ Load tests](../technical/07-scalability.md#load-tests)).
- [ ] The six screens of [🎬 UC-017](../functional/use-cases/UC-017-spray-a-field-with-refills.md#screens) (A1, A2, A3, A4, OK, KO) are 📸 Screenshot in light and dark mode, and the Agriculture screens of [🎬 UC-001](../functional/use-cases/UC-001-design-a-mission.md#screens) match the application.
- [ ] Every new screen is in English, French, German and Spanish ([📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md)).
- [ ] `python3 .claude/skills/write-specs/scripts/specs.py check` prints nothing.
- [ ] CI is green on every changed service, front end and package, and the images are signed and published from `develop`.

## <a id="dependencies"></a>⛓️ Dependencies

**Previous phases**

| From | What P4 needs |
| --- | --- |
| [🛣️ P0: Foundations](01-p0-foundations.md) | The simulator base (PX4 SITL and synthetic Rust Drones), PostgreSQL with PostGIS and TimescaleDB, the i18n framework, the design tokens package |
| [🛣️ P1: First flight](02-p1-first-flight.md) | The flight engine and its Rust safety loop, the MAVLink adapter, the planner with its coverage paths, Re-plans and their approval in Ground control, the Pre-flight check, the Mission studio, the Fleet and the Authorisations |
| [🛣️ P2: Inspection product](03-p2-inspection-product.md) | Deliverables and processing workers, the evidence ledger with its timestamping authority, the Debrief and the Scorecard, the Client portal |
| [🛣️ P3: Patrol](04-p3-patrol.md) | Notifications (in-app, e-mail, Web Push), used to tell the Mission planner that a spray map Deliverable is ready for review, as for every other Deliverable |

**Cross-cutting items**

| Item | Sprint | Why P4 needs it |
| --- | --- | --- |
| [🏛️ G-07](09-regulatory-track.md#g-07) Agriculture rules, applicator licence, Prescription map formats agreed | S30 | No product is sprayed before it; the formats it agrees drive T4.02 and T4.03 |
| [🏛️ G-06](09-regulatory-track.md#g-06) Airspace and U-space checks for the partner farm | S32 | Two sprints before [🛫 C-04](10-flight-test-campaigns.md#c-04) starts |
| [🤝 P-04](11-hardware-and-partners.md#p-04) Partner farm | S30 | The Field, its Prescription maps and the place to fly |
| [🤝 H-06](11-hardware-and-partners.md#h-06) Rented spray Drones | S34 | T4.10, T4.12 and every real flight of the campaign |
| [🤝 P-01](11-hardware-and-partners.md#p-01) Design-partner Operator | S38 | Watches the demonstration and joins the beta |
| [🛫 C-04](10-flight-test-campaigns.md#c-04) Agriculture spring campaign | S34 to S38 | Proves UC-017 on a real Field |
| [🛫 C-05](10-flight-test-campaigns.md#c-05) Agriculture autumn seeding beta | S44 to S46 | Uses what P4 delivers, with T4.25, for milestone M4 on 6 October 2028 |

## <a id="risks"></a>🎲 Risks

| Risk | Why it matters in P4 | Response in P4 |
| --- | --- | --- |
| [🎲 R-07](12-risks.md#r-07) Weather and seasons | The spring window is short and rain or wind can ground every flight of a week | Everything is proved first in the Simulator; the campaign spans five sprints (S34 to S38) with its two spare weeks; flights lost to weather move to the autumn campaign [🛫 C-05](10-flight-test-campaigns.md#c-05) |
| [🎲 R-04](12-risks.md#r-04) Vendor SDK access restricted | The rented spray Drones may not speak MAVLink or may not expose their pump | [🤝 H-06](11-hardware-and-partners.md#h-06) is chosen among models whose pump can be driven through MAVLink; if none can be rented, the campaign flies Drones of [🤝 H-01](11-hardware-and-partners.md#h-01) with a small sprayer Payload |
| [🎲 R-11](12-risks.md#r-11) Crash or hardware loss in tests | Rented Drones and a partner's crop | One Drone alone first (S35), then the Squad (S36); clear water before any product; damage cover agreed with the rental before S34 |
| [🎲 R-03](12-risks.md#r-03) Safety tick budget missed | T4.11 adds a check to every tick | The pump cut reuses the prepared Geofence polygons of the tick; the criterion benchmark of the tick runs on every pull request of E4.3 |
| [🎲 R-15](12-risks.md#r-15) Regulation changes | Rules for applying products by Drone may change before or during the campaign | [🏛️ G-07](09-regulatory-track.md#g-07) is reviewed at S32; if spraying a product is not allowed, the campaign sprays clear water and the autumn beta seeds cover crops (T4.25) |
| [🎲 R-01](12-risks.md#r-01) Review bottleneck | P4 overlaps P3 (S32 and S33) and P5 (S36 to S38), and the person flies the campaign | Only 2 to 4 P4 tickets in overlapping sprints, and no P5 ticket in S38, which holds the Patrol beta slot; flying days have no review; agents prepare the campaign checklists |
| [🎲 R-08](12-risks.md#r-08) Scope too large for 24 months | Agriculture is the third Activity in the year | T4.19 (planned refills) and T4.22 (Agriculture Scorecard) are the first to move to the autumn if P4 slips |

## <a id="work-split"></a>🧑‍💻 Work split

**What the person does**

- **Reviews** the 25 tickets, about one a day in S34 and S35, fewer on flying days; reads every change to the safety loop (T4.11) and to the dose computation (T4.08) line by line.
- **Decides** the ISOXML subset to support with the partner farm (from [🏛️ G-07](09-regulatory-track.md#g-07)), the export format of the spray map, and which of the rented models to approve.
- **Flies** as the Pilot in [🛫 C-04](10-flight-test-campaigns.md#c-04): pump calibration with clear water in S34, one Drone in S35, the Squad from S36, the product sprayings in S37 if [🏛️ G-07](09-regulatory-track.md#g-07) allows them.
- **Partners:** checks the airspace of the partner farm ([🏛️ G-06](09-regulatory-track.md#g-06)), rents the spray Drones ([🤝 H-06](11-hardware-and-partners.md#h-06)), agrees the Prescription maps and the campaign days with the partner farm ([🤝 P-04](11-hardware-and-partners.md#p-04)), gives the demonstration to the design partner.

**What the agents do, in parallel**

- Split each ticket into tasks that run at the same time: the Rust code and its benchmark, the Python service code with its tests, the TypeScript screens with their Playwright tests, the mock-up or screenshot update, the technical documentation.
- Keep three tracks apart so that they never wait on each other: the planner track (E4.1, E4.2), the edge track (E4.3, E4.4) and the screens track (E4.5, E4.6).
- Run the simulated campaign every night before each flying day: the same Field, the same Squad, the same refills, so the person flies only what already passed in the Simulator.
- Prepare the campaign pack for each flying day: the Mission, the Pre-flight check list, the expected refills, and after landing the Debrief, the spray map and the list of issues as draft tickets.

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ P3: Patrol](04-p3-patrol.md) · 📄 **Page 100 / 108** · [P5: AI agents, MCP and A2A ▶️](06-p5-ai-agents.md)
<!-- /spec:nav-bottom -->
