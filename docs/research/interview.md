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

## 🤖 AI Assistant (2026-11-20)

The product owner asked for an AI Assistant able to use every feature, action and external connector of Swarm.

| # | Topic | Decision |
| --- | --- | --- |
| 73 | Assistant | One front door, the Assistant: every person talks to it; it answers itself or hands the work to the Mission assistant, the Co-pilot or the Report writer, which stay as its specialists |
| 74 | Who uses it | Every persona: Pilot, Mission planner, Fleet maintainer, Client, Site agent, Instructor and trainees, Swarm administrator |
| 75 | Where | A panel in every part of Swarm (Mission studio, Ground control, Back office, Client portal), aware of the screen the person is on; by voice; from a mobile phone; from outside chat tools (Slack, Microsoft Teams, e-mail) |
| 76 | Reach | Every action of Swarm can be opened to the Assistant, flight-critical ones included, through fine-grained permissions |
| 77 | Permission levels | Four levels per action or group of actions: Off, Read, Propose (a person accepts), Act (it acts and reports); an Act may require the person's confirmation for chosen actions |
| 78 | Who sets them | Layered: the Swarm administrator sets a ceiling per Operator; the Operator sets the levels per role inside it; each person may narrow them for themselves, never widen them |
| 79 | Default | A new Operator starts at Propose for every action the person may do |
| 80 | Flight-critical acts | At Act, the Assistant may sign, launch, abort, Hold or take manual control only while a named Pilot is on duty for that Squad and sees it in Ground control; the act is announced with a short countdown the Pilot can cancel; the Pilot stays the accountable person in the Flight log |
| 81 | Triggers | The Assistant starts when a person asks, on events (an Alarm, an Alert, a Mission request, a failed check, a weather change) and on schedules a person sets up, always within its permissions |
| 82 | Connectors | Swarm's own systems; MCP servers and A2A agents the Operator registers; generic REST APIs and webhooks; office tools (e-mail, calendar, documents of Microsoft 365 or Google Workspace) with the person's consent; Slack and Microsoft Teams; GIS and maps; invoicing and payments; asset registers and IoT platforms; each with its own permissions |
| 83 | ERP | Swarm defines one ERP port (Clients and Sites, quotes and invoices, Fleet assets and costs, staff time, manufacturing and purchase orders); Simple-ERP (gpbcom/simple-erp) is its first ERP, reached through the port and also through MCP and A2A |
| 84 | Squad sizing | The Mission planner plans how many Drones of which types a Mission needs, and the flight profile from that |
| 85 | Squad shortfall | When the Fleet lacks Drones, Payloads or Batteries for a planned Mission, Swarm may propose, through the ERP, a manufacturing order, a purchase of the missing spares and raw materials, the earliest date the Squad can be complete, or a smaller Squad with its trade-off |
| 86 | Who builds Drones | Both: some Drone models are built in-house by the Operator, others bought from makers; the ERP knows which for each model |
| 87 | Memory and knowledge | Each person's conversation history, kept with a retention the Operator sets; the Operator's own documents as a knowledge base the Assistant cites; Swarm's user guide and the regulations of each Jurisdiction; per-person learned preferences the person can see and erase |
| 88 | Offline | Online by default; it may also work offline with open-weight models |
| 89 | Cost | A monthly budget per Operator, optionally per person; usage and cost in the Back office; a warning at 80 %, read-only answers at 100 % until raised; help during a flight never stops |
| 90 | Oversight | An activity log of every act and proposal; undo for a set time where an act is reversible; a daily digest; on any act, the person can ask why |
| 91 | Languages | Swarm's four languages, by text and by voice, answering in the person's language |
| 92 | Roadmap | Grown in P5: M5 stays on 25 August 2028 for the three agents, MCP and A2A; a second part of P5, S44 to S49, ends with milestone M5b "Assistant in beta" on 17 November 2028 |
| 93 | Simple-ERP API | Simple-ERP has no API yet: it is an external prerequisite of the ERP tickets; its date is to be fixed by the Simple-ERP roadmap |
| 94 | Who sets the permissions of each role | The Mission planner, who already manages the Operator's people, within the ceiling the Swarm administrator set |
| 95 | Countdown and Undo | Operator settings; defaults: a 10-second countdown before a Flight-critical act, Undo offered for 5 minutes after a reversible act |
| 96 | Outside agents | Signing the Pre-flight check and launching always need the person's confirmation on their own device with their PIN, whatever the Assistant permission |
| 97 | Conversation retention | 12 months by default; each Operator sets it from 30 days to forever; a person may delete their own Conversations |
| 98 | Irreversible acts | Messages sent, orders received by the ERP or the supplier, Flight-critical acts and publications to the Client cannot be undone; the Assistant says so before acting |
| 99 | Master data | The ERP is the master of Clients (names, contacts, billing); Swarm is the master of Sites (boundaries, Geofence, access); each change flows to the other |
| 100 | Quotes | A Mission request creates a draft quote in the ERP; the Mission planner prices it there and the ERP sends it; Swarm shows its state on the Mission |
| 101 | Staff time | Flight time and time on the Site per Pilot, design time of the Mission planner, and hours each person enters per Mission |
| 102 | Simple-ERP API | Committed: ready by 25 September 2028 (S46) |
| 103 | Interview | Closed by the product owner on 2026-11-20 |
| 104 | Roadmap load | Correction: with P6 counted, S44 to S48 would have carried 9 to 11 tickets per sprint. The Assistant is split: its core (front door, permissions, oversight, budgets, 9 tickets) by M5b on 17 November 2028 (S44 to S48); its channels, Connectors, ERP and beta (14 tickets) in S53 to S56, in 2029, milestone M5c on 23 February 2029 |
