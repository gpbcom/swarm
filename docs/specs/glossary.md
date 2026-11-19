# 📖 Glossary

<!-- spec:nav-top -->
> [🏠 Index](README.md) · [◀️ Swarm specifications](README.md) · 📄 **Page 2 / 109** · [Visual identity ▶️](visual-identity.md)
<!-- /spec:nav-top -->

> [!IMPORTANT]
> This page is the only source of names. Every persona, entity, system, term and state in the specifications uses the name written here, spelt the same way, and links to its row the first time it appears on a page. The words under **Do not say** are refused by the check.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [👤 Personas](#personas)
2. [🗃️ Entities](#entities)
3. [⚙️ Systems](#systems)
4. [🔤 Terms](#terms)
5. [🔄 States](#states)
<!-- /spec:summary -->

## <a id="personas"></a>👤 Personas

The people, or roles, who interact with Swarm.

<!-- Row format: | <a id="per-<slug>"></a>👤 **<Name>** | <Definition, one or two sentences> | <alias>, <alias> | -->

| Name | Definition | Do not say |
| --- | --- | --- |
| <a id="per-pilot"></a>👤 **Pilot** | The remote pilot in command of a Squad. Signs the Pre-flight check, launches, supervises the Squad in flight, approves Re-plans, takes manual control or aborts. Holds the qualifications the Jurisdiction requires. | RPIC, drone pilot |
| <a id="per-mission-planner"></a>👤 **Mission planner** | Designs Missions in the Mission studio before they fly: Activity, area, routes, Choreography, Squad, rules. Records the Authorisations of the Operator and invites Clients. Never flies. | mission designer |
| <a id="per-fleet-maintainer"></a>👤 **Fleet maintainer** | Keeps the Fleet ready: registers Drones, Batteries and Docks, tracks flight hours and maintenance, grounds a Drone that is not airworthy, connects new Drone models. | technician, mechanic |
| <a id="per-client"></a>👤 **Client** | The customer of an Operator. Orders Missions, follows them live and downloads their Deliverables in the Client portal. Sees only its own Missions. | customer |
| <a id="per-site-agent"></a>👤 **Site agent** | A person working at a Site of a Client, such as a security guard or a farm manager. Requests a Mission on demand and receives Alarms and their outcome, but never pilots. | guard, site staff |
| <a id="per-instructor"></a>👤 **Instructor** | A senior Pilot who runs a training session in the Simulator from a second Ground control and injects failures for the trainee Pilot. | trainer |
| <a id="per-swarm-administrator"></a>👤 **Swarm administrator** | Creates Operators and their first accounts. In the cloud, a member of the Swarm team; on premises, the IT administrator of the company. | superuser |

## <a id="entities"></a>🗃️ Entities

The things Swarm stores, receives or produces.

<!-- Row format: | <a id="ent-<slug>"></a>🗃️ **<Name>** | <Definition> | <alias>, <alias> | -->

| Name | Definition | Do not say |
| --- | --- | --- |
| <a id="ent-operator"></a>🗃️ **Operator** | The organisation that uses Swarm to fly Missions for its Clients, such as a drone service company. Owns a Fleet, employs Pilots, Mission planners and Fleet maintainers, and holds Authorisations. Its data is isolated from other Operators. | tenant |
| <a id="ent-mission"></a>🗃️ **Mission** | One job flown for a Client at a Site: its Activity, area, routes or Choreography, Squad, time slot and rules. | job, flight plan |
| <a id="ent-squad"></a>🗃️ **Squad** | The Drones assigned to one Mission, flown together under one Pilot. Its Drones may differ: each has its own Drone model, Payload and role in the Mission. | drone group |
| <a id="ent-drone"></a>🗃️ **Drone** | One aircraft of the Fleet, of a given Drone model, identified by its registration. | UAV, UAS, aircraft |
| <a id="ent-drone-model"></a>🗃️ **Drone model** | A make and model of Drone with its limits (weight, speed, wind, range, payload) and the Drone adapter that flies it. | airframe |
| <a id="ent-fleet"></a>🗃️ **Fleet** | All the Drones, Payloads, Batteries, Docks and Field kits of an Operator. | inventory |
| <a id="ent-payload"></a>🗃️ **Payload** | The kit a Drone carries for its part of a Mission: RGB, zoom or thermal camera, LiDAR, sprayer tank, spreader, spotlight, loudspeaker, show light. Mounted on the Drone models it fits, within their weight limit. | - |
| <a id="ent-battery"></a>🗃️ **Battery** | A flight battery, tracked by charge cycles and health. | - |
| <a id="ent-dock"></a>🗃️ **Dock** | A weatherproof box at a Site where a Drone lands, recharges and takes off without a person present. | drone-in-a-box, nest, hangar |
| <a id="ent-field-kit"></a>🗃️ **Field kit** | The equipment a crew brings to a Site to launch Drones by hand: Drones, Batteries, radios, landing pads. | ground kit |
| <a id="ent-site"></a>🗃️ **Site** | A place where Missions fly for a Client: a solar farm, a field, a stadium, a warehouse. Has a boundary, Docks if any, and Site agents. | location |
| <a id="ent-authorisation"></a>🗃️ **Authorisation** | The permission an aviation authority gives an Operator to fly a kind of Mission in a Jurisdiction: its area, Altitude ceiling, Pilot ratio, validity dates and conditions. | permit |
| <a id="ent-geofence"></a>🗃️ **Geofence** | The volume a Mission may fly in: an area and an Altitude ceiling, inside the Authorisation. | fence, no-fly box |
| <a id="ent-pre-flight-check"></a>🗃️ **Pre-flight check** | The list of verifications made before a Mission launches: the automatic checks of Swarm and the checklist the Pilot signs. | - |
| <a id="ent-re-plan"></a>🗃️ **Re-plan** | A change to a Mission in flight, such as sharing the work of a lost Drone between the others or sending a Drone to refill. | replanning, re-route |
| <a id="ent-flight-log"></a>🗃️ **Flight log** | The record of a Mission from its Pre-flight check to the last landing: checks, on-site changes, Telemetry, commands, Alerts and Pilot decisions, with time stamps. | black box |
| <a id="ent-deliverable"></a>🗃️ **Deliverable** | A product of a Mission for the Client: an orthomosaic, a 3D model, a defect list, a spray map, a patrol clip, a Mission report. | output file |
| <a id="ent-defect"></a>🗃️ **Defect** | A fault found on an inspected structure, such as a hot spot on a solar panel or a crack in a blade, with its position and pictures. | finding |
| <a id="ent-evidence-record"></a>🗃️ **Evidence record** | The signed fingerprint of a Flight log or a Deliverable, chained to the previous ones, that shows they were not altered. | audit trail |
| <a id="ent-choreography"></a>🗃️ **Choreography** | The timed positions and light colours of every Drone of a Light show, with its music time code. | show file |
| <a id="ent-field"></a>🗃️ **Field** | An agricultural parcel to spray or seed, with its boundary. | parcel |
| <a id="ent-prescription-map"></a>🗃️ **Prescription map** | A map that gives the dose to apply in each zone of a Field, imported from a Shapefile or ISOXML file. | rate map |
| <a id="ent-patrol-route"></a>🗃️ **Patrol route** | The path and the points to watch on a Site, flown on a schedule or on demand. | - |
| <a id="ent-alarm"></a>🗃️ **Alarm** | An event raised by the Site security system, such as an intrusion or a fire, with its position on the Site. | - |
| <a id="ent-workspace"></a>🗃️ **Workspace** | The arrangement of the panels of Ground control (map, Squad, video, Alerts, progress) over the screens of one platform, saved per Pilot: desktop with several screens, laptop, tablet or web browser. | - |
| <a id="ent-debrief"></a>🗃️ **Debrief** | The review of a Mission after landing: Replay, plan against actual, quality checks of the data and Scorecard. | post-mortem |
| <a id="ent-scorecard"></a>🗃️ **Scorecard** | The result of a Mission against each acceptance criterion of the Client's request, passed or failed, with its evidence. | - |

## <a id="systems"></a>⚙️ Systems

Swarm itself, and the external systems it talks to.

<!-- Row format: | <a id="sys-<slug>"></a>⚙️ **<Name>** | <Definition> | <alias>, <alias> | -->

| Name | Definition | Do not say |
| --- | --- | --- |
| <a id="sys-swarm"></a>⚙️ **Swarm** | The software suite these pages specify: Mission studio, Ground control, Back office, Client portal and Simulator. | - |
| <a id="sys-mission-studio"></a>⚙️ **Mission studio** | The desktop part of Swarm where the Mission planner designs and simulates Missions. | planner app |
| <a id="sys-ground-control"></a>⚙️ **Ground control** | The desktop part of Swarm where the Pilot runs the Pre-flight check, launches and supervises a Squad. | GCS |
| <a id="sys-back-office"></a>⚙️ **Back office** | The web part of Swarm for the Fleet, Authorisations, Operators, Flight logs and Evidence records. | admin console |
| <a id="sys-client-portal"></a>⚙️ **Client portal** | The web part of Swarm for Clients and Site agents. | customer portal |
| <a id="sys-simulator"></a>⚙️ **Simulator** | Flies a virtual Squad with the real flight software of each Drone model, to test Missions and train Pilots. | digital twin |
| <a id="sys-drone-adapter"></a>⚙️ **Drone adapter** | The part of Swarm that talks to one family of Drones: MAVLink (PX4, ArduPilot), DJI, Skydio or Parrot. | driver |
| <a id="sys-mission-assistant"></a>⚙️ **Mission assistant** | The AI agent that proposes a Mission from the Mission planner's description and checks it against the rules. Runs on the LLM provider the Operator chose. | chatbot |
| <a id="sys-co-pilot"></a>⚙️ **Co-pilot** | The AI agent that watches the Telemetry in flight, explains Alerts and proposes Re-plans to the Pilot. Runs on the LLM provider the Operator chose. | autopilot assistant |
| <a id="sys-report-writer"></a>⚙️ **Report writer** | The AI agent that drafts the Mission report and the compliance evidence after a Mission. Runs on the LLM provider the Operator chose. | - |
| <a id="sys-site-security-system"></a>⚙️ **Site security system** | The intrusion and fire detection system of a Site, which sends Alarms to Swarm. | - |
| <a id="sys-anchoring-service"></a>⚙️ **Anchoring service** | Where Evidence records are anchored, as the Operator chooses: a timestamping authority (eIDAS, RFC 3161) or a blockchain. | - |
| <a id="sys-weather-service"></a>⚙️ **Weather service** | Gives the forecast and the current wind, rain, temperature and visibility at a Site. | - |
| <a id="sys-u-space-service"></a>⚙️ **U-space service** | The airspace service of a Jurisdiction (U-space in the EU, LAANC in the US) that receives flight intentions and grants airspace. | UTM |

## <a id="terms"></a>🔤 Terms

The other words that have a precise meaning in the specifications.

<!-- Row format: | <a id="term-<slug>"></a>🔤 **<Name>** | <Definition> | <alias>, <alias> | -->

| Name | Definition | Do not say |
| --- | --- | --- |
| <a id="term-activity"></a>🔤 **Activity** | The commercial use a Mission serves: Light show, Agriculture, Patrol or Inspection. It sets the Autonomy level and the Fail-safe. | vertical |
| <a id="term-light-show"></a>🔤 **Light show** | The Activity of drawing shapes in the night sky with lit Drones, following a Choreography. | drone show |
| <a id="term-agriculture"></a>🔤 **Agriculture** | The Activity of spraying or seeding a Field. | crop spraying |
| <a id="term-patrol"></a>🔤 **Patrol** | The Activity of watching a Site along a Patrol route, on a schedule, on an Alarm or on demand. | surveillance |
| <a id="term-inspection"></a>🔤 **Inspection** | The Activity of mapping a Site or inspecting a structure (solar farm, wind turbine, power line, building, bridge) to find Defects. | survey |
| <a id="term-autonomy-level"></a>🔤 **Autonomy level** | How much the Squad decides by itself in flight: **Pre-planned** (everything computed before take-off, only Fail-safes in flight) or **Supervised autonomy** (the Squad re-plans, the Pilot approves major Re-plans). | - |
| <a id="term-fail-safe"></a>🔤 **Fail-safe** | What a Drone or the Squad does by itself when something goes wrong: Hold, Return home or land. | failsafe |
| <a id="term-hold"></a>🔤 **Hold** | A Drone stops and hovers where it is, waiting for a command. | hover, loiter |
| <a id="term-return-home"></a>🔤 **Return home** | A Drone flies back to its take-off point or its Dock and lands. | RTH, RTL |
| <a id="term-altitude-ceiling"></a>🔤 **Altitude ceiling** | The highest altitude a Drone may fly at, set by the Authorisation and the Geofence. | max height |
| <a id="term-separation-distance"></a>🔤 **Separation distance** | The smallest distance allowed between two Drones, and between a Drone and people or obstacles. | safety gap |
| <a id="term-pilot-ratio"></a>🔤 **Pilot ratio** | The largest number of Drones one Pilot may supervise at once, set by the Authorisation. | - |
| <a id="term-jurisdiction"></a>🔤 **Jurisdiction** | The set of aviation rules a Mission flies under: EU (EASA) or US (FAA). | - |
| <a id="term-bvlos"></a>🔤 **BVLOS** | Beyond visual line of sight: a Drone flies where the Pilot cannot see it directly. | - |
| <a id="term-telemetry"></a>🔤 **Telemetry** | What each Drone reports in flight: position, altitude, speed, battery, link quality, payload. | - |
| <a id="term-link"></a>🔤 **Link** | The connection between a Drone and Ground control: radio, 4G or 5G, mesh through other Drones, or the vendor's own link. | - |
| <a id="term-alert"></a>🔤 **Alert** | A message Swarm shows the Pilot about a risk or a fault in flight, with a severity: Information, Warning or Critical. Events a Drone detects use the same severities. | - |
| <a id="term-notification"></a>🔤 **Notification** | A message Swarm sends a person about something that needs their attention outside a flight: in the part of Swarm they use (🔔), by e-mail, and by push on a mobile for Site agents and Pilots on duty. | - |
| <a id="term-anchoring"></a>🔤 **Anchoring** | Publishing the fingerprint of Evidence records to the Anchoring service, so that their date and content can be proven later. | notarisation |
| <a id="term-replay"></a>🔤 **Replay** | Playing a Flight log back on the map with a timeline, the Telemetry, the Alerts and the Pilot's decisions. | playback |
| <a id="term-alert-threshold"></a>🔤 **Alert threshold** | The value of battery, Link quality or wind at which Ground control warns the Pilot. The Pilot sets it within the limits the Operator sets. | - |
| <a id="term-control-mapping"></a>🔤 **Control mapping** | Which gamepad, joystick or keyboard input gives which command in Ground control. Hold the Squad and abort keep fixed inputs. | key binding |
| <a id="term-quality-check"></a>🔤 **Quality check** | An automatic check that the data of a Mission is good enough for its Deliverables: image overlap, sharpness, thermal calibration, spray uniformity, gaps. | - |
| <a id="term-focus-view"></a>🔤 **Focus view** | One Drone shown large in Ground control: its video and Telemetry, with the map and the Squad kept visible but smaller. Opened by an event the Drone detects, a click on the Drone on the map, or a click on its tile in the Mosaic. | zoom view |
| <a id="term-mosaic"></a>🔤 **Mosaic** | The grid of live video tiles in Ground control, one per Drone, up to the number of streams the Pilot chose. | video wall |
| <a id="term-llm-provider"></a>🔤 **LLM provider** | The supplier of the language models behind the AI agents. Swarm is provider-agnostic: each Operator chooses its LLM provider and models; on premises, an open-weight model on its own servers. | - |
| <a id="term-outside-agent"></a>🔤 **Outside agent** | An AI agent outside Swarm that connects through MCP or A2A on behalf of a person, as that person's delegate, with that person's rights. | external bot |

## <a id="states"></a>🔄 States

The states a persona or an entity can be in, named `<Persona or entity>: <State>`. Every state is shown on at least one screen of a use case ([🖼️ Screens](../../.claude/rules/specs.md#spec-12)).

<!-- Row format: | <a id="st-<owner-slug>-<state-slug>"></a>🔄 **<Owner>: <State>** | <What is true in this state> | <alias>, <alias> | -->

| Name | Definition | Do not say |
| --- | --- | --- |
| <a id="st-pilot-supervising"></a>🔄 **Pilot: Supervising** | The Pilot watches a Squad flying by itself and can intervene at any time. | - |
| <a id="st-pilot-in-manual-control"></a>🔄 **Pilot: In manual control** | The Pilot flies one Drone, or commands the whole Squad, directly. The Squad no longer decides by itself. | - |
| <a id="st-mission-requested"></a>🔄 **Mission: Requested** | A Client or a Site agent has asked for the Mission; no Mission planner has planned it yet. | - |
| <a id="st-mission-declined"></a>🔄 **Mission: Declined** | A Pilot refused the request, or no Pilot answered it in time. It will not fly. | - |
| <a id="st-mission-draft"></a>🔄 **Mission: Draft** | The Mission planner is designing the Mission. | - |
| <a id="st-mission-planned"></a>🔄 **Mission: Planned** | The Mission is complete and breaks no rule. It can be simulated or prepared for flight. | - |
| <a id="st-mission-verified"></a>🔄 **Mission: Verified** | The Pre-flight check has passed and the Pilot has signed it. The Mission can launch. | - |
| <a id="st-mission-flying"></a>🔄 **Mission: Flying** | The Squad is in the air executing the Mission. | - |
| <a id="st-mission-held"></a>🔄 **Mission: Held** | The whole Squad is in Hold, waiting for the Pilot. | - |
| <a id="st-mission-completed"></a>🔄 **Mission: Completed** | Every Drone has landed and the Mission's work is done. | - |
| <a id="st-mission-aborted"></a>🔄 **Mission: Aborted** | The Mission was stopped before its work was done. Its Drones Return home or land. | - |
| <a id="st-drone-ready"></a>🔄 **Drone: Ready** | The Drone is airworthy, charged and available for a Squad. | - |
| <a id="st-drone-grounded"></a>🔄 **Drone: Grounded** | The Drone may not fly: maintenance due, fault, or failed check. | - |
| <a id="st-drone-airborne"></a>🔄 **Drone: Airborne** | The Drone is flying its part of a Mission. | - |
| <a id="st-drone-returning"></a>🔄 **Drone: Returning** | The Drone is flying back to its take-off point or its Dock. | - |
| <a id="st-drone-landed"></a>🔄 **Drone: Landed** | The Drone is on the ground after a flight, at its take-off point, its Dock or a landing position. | - |
| <a id="st-drone-lost"></a>🔄 **Drone: Lost** | Ground control has no Link to the Drone, through any path. | - |
| <a id="st-drone-model-approved"></a>🔄 **Drone model: Approved** | Its Drone adapter passed the compatibility test for its current firmware. Its Drones may fly. | - |
| <a id="st-drone-model-not-approved"></a>🔄 **Drone model: Not approved** | Its compatibility test has not passed, or its firmware changed since. Its Drones stay Grounded. | - |
| <a id="st-re-plan-proposed"></a>🔄 **Re-plan: Proposed** | The Squad or the Co-pilot proposes a Re-plan that needs the Pilot's approval. | - |
| <a id="st-re-plan-applied"></a>🔄 **Re-plan: Applied** | The Re-plan is approved and the Squad flies it. | - |
| <a id="st-re-plan-rejected"></a>🔄 **Re-plan: Rejected** | The Pilot has refused the Re-plan. The Squad keeps its plan. | - |
| <a id="st-authorisation-valid"></a>🔄 **Authorisation: Valid** | The Authorisation is in force for today and covers the Mission. | - |
| <a id="st-authorisation-expired"></a>🔄 **Authorisation: Expired** | The Authorisation is past its end date. No Mission may fly under it. | - |
| <a id="st-deliverable-processing"></a>🔄 **Deliverable: Processing** | Swarm is building the Deliverable from the Mission's data. | - |
| <a id="st-deliverable-in-review"></a>🔄 **Deliverable: In review** | The Deliverable is built and waits for a person to review it before it is published. | - |
| <a id="st-deliverable-published"></a>🔄 **Deliverable: Published** | The Deliverable is ready and visible to the Client. | - |
| <a id="st-defect-suspected"></a>🔄 **Defect: Suspected** | Detection found a possible Defect. A person has not confirmed it yet. | - |
| <a id="st-defect-confirmed"></a>🔄 **Defect: Confirmed** | A person confirmed the Defect. It is reported to the Client. | - |
| <a id="st-defect-dismissed"></a>🔄 **Defect: Dismissed** | A person decided it is not a Defect. It is not reported. | - |
| <a id="st-alarm-raised"></a>🔄 **Alarm: Raised** | The Site security system has raised the Alarm and a Squad is responding. | - |
| <a id="st-alarm-closed"></a>🔄 **Alarm: Closed** | The Pilot has closed the Alarm with its outcome. | - |
| <a id="st-evidence-record-verified"></a>🔄 **Evidence record: Verified** | The Flight log or Deliverable matches its Evidence record and its Anchoring. | - |
| <a id="st-evidence-record-altered"></a>🔄 **Evidence record: Altered** | The Flight log or Deliverable no longer matches its Evidence record. | - |
| <a id="st-scorecard-passed"></a>🔄 **Scorecard: Passed** | Every acceptance criterion of the request is met. | - |
| <a id="st-scorecard-failed"></a>🔄 **Scorecard: Failed** | At least one acceptance criterion is not met; a re-fly or an explanation to the Client is needed. | - |

<!-- spec:nav-bottom -->
---

> [🏠 Index](README.md) · [◀️ Swarm specifications](README.md) · 📄 **Page 2 / 109** · [Visual identity ▶️](visual-identity.md)
<!-- /spec:nav-bottom -->
