# 🎤 Functional specification interview

**Date:** 2026-11-18. **Interviewee:** the product owner. **Input:** [landscape](landscape.md).
These answers are the source of the functional specification in [docs/specs/](../specs/README.md).

| # | Topic | Decision |
| --- | --- | --- |
| 1 | Purpose | A software suite that pilots small drone swarms for commercial uses |
| 2 | Activities | Light shows, agriculture, security and patrol, mapping and inspection: all four, specified together |
| 3 | Drones | Hardware-agnostic core with one adapter per drone family: MAVLink (PX4, ArduPilot) and vendor SDKs (DJI, Skydio, Parrot) |
| 4 | Squad size | Set per mission and per activity |
| 5 | Regulation | EU (EASA: Specific category, SORA 2.5, U-space) and US (FAA: Part 107, exemptions, waivers), per jurisdiction |
| 6 | Personas | Pilot, Mission planner, Fleet maintainer, Client, Site agent |
| 7 | Autonomy | Per activity: light shows pre-planned; inspection and patrol supervised autonomy; agriculture pre-planned routes with supervised re-planning for refills and failures |
| 8 | Suite | Mission studio, Ground control, Back office, Simulator, plus a Client portal |
| 9 | Client | Web portal by default (order, follow live, download); other modes configurable on demand |
| 10 | Fail-safes | Per activity: light shows stop everything; other activities degrade gracefully |
| 11 | AI | Mission assistant, live Co-pilot, Report writer |
| 12 | Deployment | Cloud, multi-Operator, and on-premise for one company |
| 13 | Data | Full processing: orthomosaics, 3D models, defect detection |
| 14 | Ground kit | Field kits and docks |
| 15 | Links | Radio per drone, 4G/5G, mesh between drones, vendor links |
| 16 | Blockchain | Not for flight coordination. Optional anchoring of evidence fingerprints: none, timestamping authority, or blockchain, per Operator |
| 17 | Approval | Swarm verifies every rule automatically, the Pilot signs the pre-flight checklist and launches |
| 18 | Safety rules | Geofence and altitude ceiling, separation, weather limits, maximum drones per Pilot |
| 19 | Languages | English, French, German, Spanish |
| 20 | Light shows | Built-in designer and import (Blender, Skybrush Studio), music by time code |
| 21 | Agriculture | Uniform rate by default, prescription maps (Shapefile, ISOXML) when provided |
| 22 | Patrol triggers | Schedule, site alarm, on demand |
| 23 | Inspection targets | Solar farms, wind turbines, power lines, buildings and bridges |
| 24 | Names | "Squad" for the drones of one mission (the product is Swarm); "Site agent" for site staff who request flights |
| 25 | Feature map | 19 features: 12 core, 4 activities, 3 AI |
| 26 | Visual identity | Light and dark mode for every screen, screenshots included |
| 27 | Squad configuration | Each Drone of a Squad may have its own Drone model, Payload (kit) and role |
| 28 | Ground control platforms | Desktop with several screens, laptop in the field, tablet, web browser |
| 29 | Manual control | Gamepad or joystick, vendor remote, on-screen commands, keyboard shortcuts |
| 30 | Always visible in flight | Map and Squad, live video, Alerts and Co-pilot, progress against plan |
| 31 | Assessment | Replay, plan against actual, Quality checks, Scorecard against the Client's request |
| 32 | Pilot settings | Workspace per platform, Alert thresholds within Operator limits, units, language, light or dark mode, Control mapping |
| 33 | On-site changes | The Pilot may swap a Drone, Payload or Battery; the Mission is checked again and the Pre-flight check signed again |
| 34 | Who sees the assessment | Pilot, Mission planner, Client (published Scorecard), Fleet maintainer (Drone and Battery behaviour) |

## 🎤 Second round: every open point settled (2026-11-18)

| # | Topic | Decision |
| --- | --- | --- |
| 35 | Map background | Open map data by default, licensed satellite imagery, cached for use without network |
| 36 | Pre-flight check | Valid 30 minutes; signed with a personal PIN; Operator checklist per Activity, every item ticked |
| 37 | Telemetry | Always visible: state, battery, Link, altitude, Payload; the rest on demand |
| 38 | Re-plan answer | 60 seconds; no answer means Rejected |
| 39 | Fail-safes | Lost after 5 s; abort by press and hold 1 s, no dialog; Return to Squad; Resume from Held; new state Drone: Landed |
| 40 | Fleet | Maintenance intervals from the maker, shorter only; Drone model: Approved or Not approved |
| 41 | Authorisations | Warnings at 30 and 7 days; PDF required; on expiry Planned Missions go back to Draft |
| 42 | Data | Processing in the cloud and on premises; new state Deliverable: In review |
| 43 | Client live view | Positions; video only when the Operator enables it for the Mission |
| 44 | Evidence | Timestamping authority by default; public blockchain through an aggregator; Operator told at once of an Altered record |
| 45 | Training | An Instructor persona injects failures from a second Ground control |
| 46 | Adapters | MAVLink first, then Parrot; test in the Simulator then one real flight; new firmware means a new test |
| 47 | Operators | A Swarm administrator persona creates Operators (use case UC-029) |
| 48 | Light shows | SMPTE LTC or MIDI time code, or Swarm plays the music; after a fault the Mission ends Aborted |
| 49 | Agriculture | Pilot and Operator licences recorded; refill at 10 % tank |
| 50 | Patrol | Auto-launch from Docks only if enabled and a Pilot is on duty; fixed outcome list; webhook then SIA DC-09; requests wait 10 minutes, then Mission: Declined |
| 51 | Inspection | Swarm ships detection models, Operators may train their own; dismissing a Defect needs a reason, reviewer recorded |
| 52 | AI agents | LLM provider-agnostic, chosen per Operator (Claude by default in the cloud, open-weight on premises); the Co-pilot speaks critical Alerts |
| 53 | Reports | Common skeleton plus a section per Activity |
| 54 | Ground control configuration | Tablet without manual control; XInput gamepads first; default Operator limits; fixed inputs H and Ctrl+Shift+A held 1 s |
| 55 | Attention | Configurable streams within Operator limits; Focus view opened by a Drone event, a map click or a Mosaic click; one at a time, events queue (BR-027, UC-030) |
| 56 | Debrief | Criteria per Activity; a re-fly is a new linked Mission; Operator may tighten quality levels; an Altered Flight log cannot pass |
| 57 | Status | Every specification page approved |
| 58 | Housekeeping | No Git work for now; CLAUDE.md cleaned; AGENT.md renamed to Swarm; sample values kept, marked fictional |
| 59 | Event severity | Same scale as Alerts: Information, Warning, Critical; default Warning and above opens the Focus view; critical Alerts never muted |
| 60 | Notifications | In-app (🔔), e-mail, and mobile push for Site agents and Pilots on duty |
| 61 | Reviews and orders | Fixed dismissal reasons; reviewer recorded for confirmations and dismissals; an order needs at least one acceptance criterion; the Mission planner may converse with the Report writer about a draft |
| 62 | Flight details | Return to Squad refused: manual control kept, Alert, safe path proposed as a Re-plan; Abort released early sends nothing; landing reserve 20 % battery |
| 63 | Creating an Operator | Required: name, deployment, at least one Jurisdiction, first Mission planner's e-mail; LLM provider (Claude in the cloud) and Anchoring have defaults |

## 🎤 Final confirmations (2026-11-18)

| # | Topic | Decision |
| --- | --- | --- |
| 64 | Screen size on disk | Every screen PNG is a 256-colour palette PNG: 31 MB down to 13 MB; `render` writes them, `check` enforces it |
| 65 | Abort and Return to Squad | Confirmed on the UC-006 screens |
| 66 | Focus view | Confirmed on the UC-030 screens |
| 67 | Per-Drone configuration | Confirmed on the UC-024 screens |
| 68 | Flight log | Runs from the Pre-flight check to the last landing, so on-site changes and signed checks are in it |
| 69 | Sample cast | Instructor and Swarm administrator appear by role only, without a personal name |
| 70 | Swarm administration frame | Back office · Swarm administration; side bar Operators, People, Settings; applied to the UC-029 screens |
| 71 | Landing reserve in UC-002 | Confirmed: 20 % battery by default, an Operator setting |
| 72 | Aggregated map | Confirmed present: Ground control always shows every Drone's position on one map (FS-021, UC-025, BR-027); the list of open points is closed |
