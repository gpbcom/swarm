# 🛣️ P3: Patrol

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ P2: Inspection product](03-p2-inspection-product.md) · 📄 **Page 99 / 108** · [P4: Agriculture ▶️](05-p4-agriculture.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Sprints:** S25 to S33 · **Dates:** 6 Dec 2027 to 7 Apr 2028 · **Tickets:** about 35

> [!NOTE]
> P3 adds the second Activity, Patrol, with Docks, the Parrot adapter, Alarms from the Site security system, Site agents, video at scale and Notifications, because it reuses the Squads, the Client portal and the evidence ledger of P1 and P2 and needs a winter of Dock flights before the Patrol beta of M3 on 30 Jun 2028.

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

After P2, Swarm sells [🔤 Inspection](../glossary.md#term-inspection): a crew brings a [🗃️ Field kit](../glossary.md#ent-field-kit), flies, and leaves. [🔤 Patrol](../glossary.md#term-patrol) is different: [🗃️ Drones](../glossary.md#ent-drone) live in [🗃️ Docks](../glossary.md#ent-dock) at the [🗃️ Site](../glossary.md#ent-site), fly a [🗃️ Patrol route](../glossary.md#ent-patrol-route) on a schedule, and answer an [🗃️ Alarm](../glossary.md#ent-alarm) at night with nobody on the Site. At the end of P3:

- A [👤 Mission planner](../glossary.md#per-mission-planner) designs a Patrol route with its points to watch, and scheduled patrols fly it from the Docks of the Site, under Supervised autonomy.
- The [⚙️ Site security system](../glossary.md#sys-site-security-system) sends Alarms through a webhook, then through SIA DC-09 alarm panels; the nearest Drones Ready in a Dock fly to the Alarm, by themselves when the Operator enabled it and a [👤 Pilot](../glossary.md#per-pilot) is on duty.
- The Pilot watches the video in [⚙️ Ground control](../glossary.md#sys-ground-control), closes each Alarm with its outcome, and every clip has its [🗃️ Evidence record](../glossary.md#ent-evidence-record).
- A [👤 Site agent](../glossary.md#per-site-agent) receives Alarms and their outcome in the [⚙️ Client portal](../glossary.md#sys-client-portal), and requests a Patrol on demand, but never pilots.
- The Parrot [⚙️ Drone adapter](../glossary.md#sys-drone-adapter) flies the ANAFI USA, approved by its compatibility test.
- Video scales: an SFU in each cell and at the edge, simulcast for the Mosaic and the [🔤 Focus view](../glossary.md#term-focus-view), LL-HLS for Clients when the Operator enables it, recordings fingerprinted.
- Every [🔤 Notification](../glossary.md#term-notification) appears in the part of Swarm the person uses (🔔), by e-mail, and by push on a mobile for Site agents and Pilots on duty.
- Campaign [🛫 C-03](10-flight-test-campaigns.md#c-03) proves it at a partner's Dock site, so that the Site can then patrol for one month and reach milestone M3.

## <a id="scope"></a>🧺 Scope

**Features**

| Feature | Delivered in P3 | Left for later |
| --- | --- | --- |
| [📘 FS-015: Patrol](../functional/features/FS-015-patrol.md) | All of it: Patrol routes, scheduled patrols, Alarms by webhook then SIA DC-09, launch on Alarm, closing an Alarm, requests on demand, clip evidence | None |
| [📘 FS-011: Drone adapters](../functional/features/FS-011-drone-adapters.md) | The Parrot adapter, the second family after MAVLink, with its compatibility test and the firmware rule | DJI and Skydio, in [🛣️ P7](08-p7-scale-and-reach.md) |
| [📘 FS-012: Operators, deployment and languages](../functional/features/FS-012-operators-deployment-and-languages.md) | Notifications: in-app (🔔), e-mail, Web Push, in the person's language | Production cells, the US cell and the on-premises bundle, in [🛣️ P7](08-p7-scale-and-reach.md) |

**Features extended in P3**

| Feature | Extension |
| --- | --- |
| [📘 FS-001: Mission design](../functional/features/FS-001-mission-design.md) | Patrol routes and their schedule in the [⚙️ Mission studio](../glossary.md#sys-mission-studio) |
| [📘 FS-005: Fleet and readiness](../functional/features/FS-005-fleet-and-readiness.md) | Docks registered by the [👤 Fleet maintainer](../glossary.md#per-fleet-maintainer), their state in each Drone's readiness |
| [📘 FS-008: Client portal](../functional/features/FS-008-client-portal.md) | Live video for the [👤 Client](../glossary.md#per-client) when the Operator enables it; 🔔 Alarms and requests for Site agents |
| [📘 FS-021: Ground control monitoring](../functional/features/FS-021-ground-control-monitoring.md) | The Mosaic and the Focus view served by the SFU, with simulcast layers |
| [📘 FS-022: Debrief and assessment](../functional/features/FS-022-debrief-and-assessment.md) | The Patrol criteria of the [🗃️ Scorecard](../glossary.md#ent-scorecard): route completed, points checked, time to reach an Alarm |

**Use cases**

| Use case | Delivered in P3 | Left for later |
| --- | --- | --- |
| [🎬 UC-018: Respond to a Site Alarm](../functional/use-cases/UC-018-respond-to-a-site-alarm.md) | Every step and alternative flow | None |
| [🎬 UC-019: Request a Patrol on demand](../functional/use-cases/UC-019-request-a-patrol-on-demand.md) | Every step and alternative flow | None |
| [🎬 UC-014: Connect a new Drone model](../functional/use-cases/UC-014-connect-a-new-drone-model.md) | Every step and alternative flow, for the ANAFI USA by Parrot | DJI and Skydio Drone models (P7) |
| [🎬 UC-011: Follow a Mission and download its Deliverables](../functional/use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md) | A1, the live video for the Client, left open by P2 | None |

**Business rules**

| Rule | How P3 applies it |
| --- | --- |
| [📏 BR-019: Site agents request, never pilot](../functional/business-rules/BR-019-site-agents-request-never-pilot.md) | Delivered: the Site agent role reaches no command, no Squad subject and no MCP tool; a request waits for a Pilot |
| [📏 BR-005: Autonomy level per Activity](../functional/business-rules/BR-005-autonomy-level-per-activity.md) | Applied to Patrol: Supervised autonomy, the Squad reroutes to an Alarm, the Pilot approves major Re-plans |
| [📏 BR-015: Approved Drone models only](../functional/business-rules/BR-015-approved-drone-models-only.md) | Applied to the ANAFI USA and to each of its firmware versions |
| [📏 BR-009: Evidence integrity](../functional/business-rules/BR-009-evidence-integrity.md) | Applied to video recordings and Alarm clips |
| [📏 BR-007: Launch only after a passed Pre-flight check](../functional/business-rules/BR-007-launch-only-after-a-passed-pre-flight-check.md) | Applied to scheduled patrols and accepted requests; launch on Alarm concerns Drones of a Mission already Flying, whose check has passed |
| [📏 BR-011: Drone readiness](../functional/business-rules/BR-011-drone-readiness.md) | A Drone in a Dock is Ready only when the Dock reports it charged and available |
| [📏 BR-016: Clients see only their own Missions](../functional/business-rules/BR-016-clients-see-only-their-own-missions.md) | Applied to Site agents: only the Alarms and Missions of their Site |
| [📏 BR-017: Every screen in four languages](../functional/business-rules/BR-017-every-screen-in-four-languages.md) | Applied to every Notification text, translated in the person's language |

**Technical pages**

| Page | What P3 builds from it |
| --- | --- |
| [🔩 Engine and services: Drone adapters](../technical/04-engine.md#adapters) | The Parrot sidecar process using Parrot's SDK, bridged to the flight engine over a local socket, behind the common adapter interface |
| [🔩 Engine and services: Planner](../technical/04-engine.md#planner) | Re-plans that send patrolling Drones to an Alarm |
| [🔩 Engine and services: Notifier](../technical/04-engine.md#notifier) | The `notifier` service: in-app, e-mail and Web Push channels; deduplication, rate limits, quiet hours except safety; Babel translations |
| [🔩 Engine and services: Processing](../technical/04-engine.md#processing) | The video worker: clips and face blurring for Client-visible video |
| [🔌 API layer: Webhooks](../technical/05-api.md#webhooks) | Alarms in at `/v1/sites/{id}/alarms` with a secret per Site, the SIA DC-09 receiver, webhooks out signed with HMAC-SHA256 and retried for 24 hours |
| [🔌 API layer: Video](../technical/05-api.md#video) | LiveKit SFU in each cell and at the edge, three-layer simulcast, LL-HLS for Clients, recordings to object storage |
| [🖥️ GUI and WebUI: Video](../technical/10-frontends.md#video) | The Mosaic on the smallest layer, the Focus view on the full one, streams past the Operator's maximum not subscribed |
| [🔐 Security: Links](../technical/06-security.md#links) | WireGuard tunnels from Docks to the edge; the vendor's own encryption wrapped by the Parrot adapter |
| [🔐 Security: Privacy and compliance](../technical/06-security.md#privacy) | Face blurring in Client-visible video on request, raw video kept 90 days |
| [🚢 Deployment: Edge appliance](../technical/09-deployment.md#edge) | The minimal edge on the Dock PC, updated over the air, never during a Mission |
| [🚀 Scalability and performance: Cells](../technical/07-scalability.md#cells) | 500 video viewers and 5,000 WebSocket clients per cell |
| [🚀 Scalability and performance: Budgets](../technical/07-scalability.md#budgets) | WebRTC video under 300 ms glass to glass; Hold the Squad and abort under 100 ms for Drones launched from Docks too |

## <a id="epics"></a>🪜 Epics

| Epic | Name | Delivers (UC/BR links) | Where (services, apps, packages) | Tickets | Parallel tasks for the agents |
| --- | --- | --- | --- | --- | --- |
| <a id="e3-1"></a>E3.1 | Docks | [🎬 UC-018](../functional/use-cases/UC-018-respond-to-a-site-alarm.md) steps 2 and 5, [📏 BR-011](../functional/business-rules/BR-011-drone-readiness.md) | `fleet` (Dock entity), `flight-engine` (Dock interface), `simulator` (simulated Dock), `back-office` (🛸 Fleet), `deploy/` (Dock PC edge) | 5: [T3.05](#t3-05), [T3.06](#t3-06), [T3.12](#t3-12), [T3.13](#t3-13), [T3.25](#t3-25) | Dock model and migrations; interface and simulated Dock with tests; vendor integration behind the interface; WireGuard and update ring configuration; Back office screens |
| <a id="e3-2"></a>E3.2 | Parrot adapter | [🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md), [📏 BR-015](../functional/business-rules/BR-015-approved-drone-models-only.md) | Parrot sidecar beside `flight-engine`, `video-relay`, `simulator` (compatibility suite), `back-office` | 5: [T3.07](#t3-07), [T3.08](#t3-08), [T3.09](#t3-09), [T3.16](#t3-16), [T3.30](#t3-30) | Sidecar code and its socket protocol; Telemetry mapping tests; each command as a compatibility step; video bridge; firmware watch |
| <a id="e3-3"></a>E3.3 | Patrol routes and scheduled patrols | [📏 BR-005](../functional/business-rules/BR-005-autonomy-level-per-activity.md), [📏 BR-007](../functional/business-rules/BR-007-launch-only-after-a-passed-pre-flight-check.md), [📏 BR-026](../functional/business-rules/BR-026-scorecard-against-the-request.md) | `mission-studio`, `missions` (schedules), `planner`, `ground-control` (Debrief) | 3: [T3.04](#t3-04), [T3.17](#t3-17), [T3.29](#t3-29) | Route editor and its points to watch; schedule rules and tests; Patrol criteria of the Scorecard; screens |
| <a id="e3-4"></a>E3.4 | Alarms | [🎬 UC-018](../functional/use-cases/UC-018-respond-to-a-site-alarm.md), [📏 BR-005](../functional/business-rules/BR-005-autonomy-level-per-activity.md), [📏 BR-009](../functional/business-rules/BR-009-evidence-integrity.md) | `gateway` (webhook in), SIA DC-09 receiver, `missions` (Alarm), `planner` (reroute), `ground-control` (Alarm panel) | 5: [T3.03](#t3-03), [T3.10](#t3-10), [T3.14](#t3-14), [T3.15](#t3-15), [T3.24](#t3-24) | Alarm model and webhook with signed test posts; alarm panel simulator; Re-plan to the Alarm in Rust; Ground control panel against its mock-ups; outcome list in four languages |
| <a id="e3-5"></a>E3.5 | Site agents | [🎬 UC-019](../functional/use-cases/UC-019-request-a-patrol-on-demand.md), [🎬 UC-018](../functional/use-cases/UC-018-respond-to-a-site-alarm.md) step 6, [📏 BR-019](../functional/business-rules/BR-019-site-agents-request-never-pilot.md), [📏 BR-016](../functional/business-rules/BR-016-clients-see-only-their-own-missions.md) | `client-portal` (🔔 Alarms, requests), `ground-control` (requests), `missions` (request timer), `gateway` (role) | 4: [T3.18](#t3-18), [T3.19](#t3-19), [T3.20](#t3-20), [T3.21](#t3-21) | Request flow and its timer tests; Client portal and Ground control screens; role tests added to the isolation suite of P2 |
| <a id="e3-6"></a>E3.6 | Video at scale | [🎬 UC-018](../functional/use-cases/UC-018-respond-to-a-site-alarm.md) step 3, [🎬 UC-011](../functional/use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md) A1, [📏 BR-009](../functional/business-rules/BR-009-evidence-integrity.md) | LiveKit SFU (cell and edge), `video-relay`, `processing` (video worker), CDN, `packages/ts/live` | 5: [T3.22](#t3-22), [T3.23](#t3-23), [T3.26](#t3-26), [T3.27](#t3-27), [T3.31](#t3-31) | SFU charts; simulcast settings; WebRTC helpers; LL-HLS packaging; blurring worker and its test clips; k6 and WebRTC load scenarios |
| <a id="e3-7"></a>E3.7 | Notifications and webhooks out | [📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md), [🎬 UC-019](../functional/use-cases/UC-019-request-a-patrol-on-demand.md) A1 and A3 | `notifier` (new service), `gateway` (WebSocket push), Valkey (Pilots on duty), every app's 🔔 | 4: [T3.01](#t3-01), [T3.02](#t3-02), [T3.11](#t3-11), [T3.28](#t3-28) | Service and channels; rules with tests; Babel catalogues in four languages; service worker for Web Push in each installable app; webhook signer and retry tests |
| <a id="e3-8"></a>E3.8 | Patrol beta readiness | Every use case of P3 moves to 📸 Screenshot | `frontends/*/e2e`, `docs/specs/screens/`, `deploy/` (OVHcloud cell) | 4: [T3.32](#t3-32), [T3.33](#t3-33), [T3.34](#t3-34), [T3.35](#t3-35) | Field issues turned into tests; Playwright captures in both modes; penetration test fixes; runbook for the beta month |

## <a id="sprints"></a>🗓️ Sprint plan

P3 has 35 tickets. S25 also carries the support of milestone M2 (17 Dec 2027), S26 falls over the year-end holidays, and S32 and S33 share the capacity with [🛣️ P4: Agriculture](05-p4-agriculture.md), which starts in S32 with 2 and 3 tickets. Counting P4, every sprint stays at about 5 tickets merged: 4, 3, 4, 5, 5, 4, 5, then 3 + 2 and 2 + 3.

| Sprint | Dates | Tickets | Sprint goal | What can be shown |
| --- | --- | --- | --- | --- |
| S25 | 6 to 17 Dec 2027 | [T3.01](#t3-01) Notifier, [T3.02](#t3-02) Notification rules, [T3.03](#t3-03) Alarms in, [T3.04](#t3-04) Patrol routes | M2 is reached; Notifications and Alarms exist | The design partner's M2 Mission; a signed webhook raises an Alarm at gate 3 of Northgate warehouse; Léa Martin draws the Patrol route |
| S26 | 20 to 31 Dec 2027 | [T3.05](#t3-05) Docks in the Fleet, [T3.06](#t3-06) Dock interface and simulated Dock, [T3.07](#t3-07) Parrot sidecar | Docks exist, in the Fleet and in the Simulator; the ANAFI USA speaks to Swarm | A simulated Squad takes off from two simulated Docks; Echo's Telemetry in Ground control |
| S27 | 3 to 14 Jan 2028 | [T3.08](#t3-08) Parrot commands, [T3.09](#t3-09) Parrot Payload and video, [T3.10](#t3-10) Alarm panel, [T3.11](#t3-11) Web Push and Pilots on duty | The ANAFI USA obeys every command; the Pilot sees Alarms | Echo on a bench obeys Hold and Return home; an Alarm on the map with the nearest Ready Drones; a push on Inès Garcia's phone |
| S28 | 17 to 28 Jan 2028 | [T3.12](#t3-12) Real Dock, [T3.13](#t3-13) Dock launch and Return home, [T3.14](#t3-14) Launch on Alarm, [T3.15](#t3-15) Close an Alarm, [T3.16](#t3-16) ANAFI USA compatibility test | Drones answer Alarms from Docks | ANAFI USA Approved; in the Simulator, Delta and Echo leave Dock 1 and Dock 2 for gate 3, the Alarm is closed and the clip chained |
| S29 | 31 Jan to 11 Feb 2028 | [T3.17](#t3-17) Scheduled patrols, [T3.18](#t3-18) 🔔 Alarms for Site agents, [T3.19](#t3-19) Requests on demand, [T3.20](#t3-20) Accept or decline, [T3.21](#t3-21) No command for Site agents | Site agents are part of Patrol | Inès Garcia requests a look at the car park, Sam Carter accepts; a second request with no answer becomes Declined |
| S30 | 14 to 25 Feb 2028 | [T3.22](#t3-22) SFU and simulcast, [T3.23](#t3-23) Recording, [T3.24](#t3-24) SIA DC-09, [T3.25](#t3-25) Dock PC edge | C-03 opens at the Dock site; video at scale | The first scheduled patrol from the real Dock; Mosaic and Focus view from the SFU; an alarm panel raises an Alarm through SIA DC-09 |
| S31 | 28 Feb to 10 Mar 2028 | [T3.26](#t3-26) LL-HLS for Clients, [T3.27](#t3-27) Face blurring, [T3.28](#t3-28) Webhooks out, [T3.29](#t3-29) Patrol Debrief and Scorecard, [T3.30](#t3-30) Firmware watch | Clients see what the Operator allows, privately; a firmware change grounds its Drones | Northgate Logistics follows a patrol in LL-HLS with faces blurred; a Patrol Scorecard with the time to reach an Alarm; a new ANAFI USA firmware grounds its Drones until the test passes |
| S32 | 13 to 24 Mar 2028 | [T3.31](#t3-31) Video load test, [T3.32](#t3-32) C-03 field fixes, [T3.33](#t3-33) Screenshots | The Patrol chain holds at the Site and at cell scale, and its screens are the real application | The nightly run with 500 video viewers; Playwright captures replacing the mock-ups of three use cases |
| S33 | 27 Mar to 7 Apr 2028 | [T3.34](#t3-34) Penetration test fixes, [T3.35](#t3-35) Beta readiness | Patrol is ready for its beta | The [phase demonstration](#demo), on the last day of C-03 |

### 🎫 Tickets

| Ticket | Sprint | Epic | Delivers | Done when |
| --- | --- | --- | --- | --- |
| <a id="t3-01"></a>T3.01 | S25 | [E3.7](#e3-7) | The `notifier` service: in-app Notifications stored and pushed over WebSocket to the 🔔 of every app, e-mail through the SMTP relay | Léa Martin gets a 🔔 and an e-mail when Priya Shah orders a Mission |
| <a id="t3-02"></a>T3.02 | S25 | [E3.7](#e3-7) | Rules: deduplication per event, rate limits per person, quiet hours except safety, texts translated with Babel; the messages P2 showed in its apps (Mission requested, Evidence record: Altered, Deliverables and Scorecards published) move to the notifier | Three verifications of one Altered record send one Notification; a Client who chose German gets it in German |
| <a id="t3-03"></a>T3.03 | S25 | [E3.4](#e3-4) | Alarm entity, Alarm: Raised and Alarm: Closed, and the webhook in at `/v1/sites/{id}/alarms` with a secret per Site | A signed post raises an intrusion Alarm at gate 3; a wrong secret is refused and logged |
| <a id="t3-04"></a>T3.04 | S25 | [E3.3](#e3-3) | Patrol routes in the Mission studio: path, points to watch, Docks of the Site as take-off points, Supervised autonomy | The Patrol route of Northgate warehouse passes the rules of Mission design and is Mission: Planned |
| <a id="t3-05"></a>T3.05 | S26 | [E3.1](#e3-1) | Docks in the Fleet: registered by the Fleet maintainer in the Back office with their Site and Drones; Dock state in each Drone's readiness | Noah Weber registers Dock 1 and Dock 2 at Northgate warehouse; Delta is Ready only once Dock 1 reports it charged |
| <a id="t3-06"></a>T3.06 | S26 | [E3.1](#e3-1) | Dock interface in the flight engine (open, close, charge state, Drone inside) and a simulated Dock in the Simulator, isolated like every simulated Squad | A simulated Squad leaves and returns to two simulated Docks; the Flight log is marked simulated |
| <a id="t3-07"></a>T3.07 | S26 | [E3.2](#e3-2) | Parrot sidecar using Parrot's SDK, bridged to the flight engine over a local socket: connect and stream Telemetry into the ring buffer | Echo ([🤝 H-04](11-hardware-and-partners.md#h-04)) on a bench shows its Telemetry in Ground control |
| <a id="t3-08"></a>T3.08 | S27 | [E3.2](#e3-2) | Parrot commands: upload Geofence, Fail-safes and route; arm and take off; go to; Hold; Return home; land; acknowledged per Drone on the safety lane | Each command passes on the bench and is a step of the compatibility suite |
| <a id="t3-09"></a>T3.09 | S27 | [E3.2](#e3-2) | Parrot Payload control and video into `video-relay`, the vendor's encryption wrapped by the adapter | Echo's camera shows in the Mosaic and in its Focus view |
| <a id="t3-10"></a>T3.10 | S27 | [E3.4](#e3-4) | Ground control Alarm panel: the Alarm on the map, the nearest Drones Ready in a Dock proposed, the Pilot sends them; with no Drone Ready, the Alarm stays Raised and the Pilot and the Site agent are told | [🎬 UC-018](../functional/use-cases/UC-018-respond-to-a-site-alarm.md) step 1, A1 and A2 pass in the Simulator |
| <a id="t3-11"></a>T3.11 | S27 | [E3.7](#e3-7) | Web Push from the installable web apps, and the presence of Pilots on duty in Valkey | Inès Garcia's phone and Sam Carter's tablet receive a push; going off duty stops Sam's pushes except safety |
| <a id="t3-12"></a>T3.12 | S28 | [E3.1](#e3-1) | The Dock chosen in S22 ([🤝 H-05](11-hardware-and-partners.md#h-05)) behind the Dock interface, linked to the edge through WireGuard | The real Dock opens, Echo takes off and lands on the test Site, the Dock reports charging |
| <a id="t3-13"></a>T3.13 | S28 | [E3.1](#e3-1) | Launch from a Dock and Return home to the Dock: the Dock is each Drone's home, Drone: Landed at its Dock, charging after landing | Simulator and one real flight end with the Drone inside its Dock |
| <a id="t3-14"></a>T3.14 | S28 | [E3.4](#e3-4) | Launch on Alarm: an Operator setting per Site; with a Pilot on duty, the Drones of the Flying Mission waiting in Docks take off by themselves; the planner sends them to the Alarm; the Pilot is Supervising | [🎬 UC-018](../functional/use-cases/UC-018-respond-to-a-site-alarm.md) step 2 passes; with no Pilot on duty or the setting off, nothing takes off by itself |
| <a id="t3-15"></a>T3.15 | S28 | [E3.4](#e3-4) | Close an Alarm: outcome from the fixed list (false alarm, intrusion confirmed, fire confirmed, other), optional comment; the clip gets its Evidence record; the Drones Return home to their Docks | [🎬 UC-018](../functional/use-cases/UC-018-respond-to-a-site-alarm.md) steps 4 and 5 pass |
| <a id="t3-16"></a>T3.16 | S28 | [E3.2](#e3-2) | Compatibility test of the ANAFI USA: in the Simulator if it can fly this Drone model, otherwise straight to the real flight; then one real flight of Echo by Sam Carter in a test area; Approved for its current firmware | [🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md) main flow, A1, A2, A3 and A5 pass; [📘 FS-011](../functional/features/FS-011-drone-adapters.md#acceptance) AC-1 passes with a Return home fault injected |
| <a id="t3-17"></a>T3.17 | S29 | [E3.3](#e3-3) | Scheduled patrols: a schedule on a Patrol route creates its Missions; each waits for the Pre-flight check of the Pilot on duty before it launches | The night patrol of Northgate is created each night and launches only after Sam Carter signs its Pre-flight check |
| <a id="t3-18"></a>T3.18 | S29 | [E3.5](#e3-5) | Client portal 🔔 Alarms for Site agents: the Alarms of their Site, their outcome, and the warning that no Drone can fly; read only | [🎬 UC-018](../functional/use-cases/UC-018-respond-to-a-site-alarm.md) step 6 and A4 pass |
| <a id="t3-19"></a>T3.19 | S29 | [E3.5](#e3-5) | Client portal requests: point to watch and a note; Mission: Requested sent to the Pilots on duty; waits 10 minutes, an Operator setting; then Mission: Declined, and the Site agent and every Pilot on duty are told | [🎬 UC-019](../functional/use-cases/UC-019-request-a-patrol-on-demand.md) steps 1 to 3 and A3 pass |
| <a id="t3-20"></a>T3.20 | S29 | [E3.5](#e3-5) | Ground control requests: point, note, Drones Ready in the Docks of the Site; accepting makes the Mission Planned on its Patrol route and opens the Pre-flight check; declining makes it Declined | [🎬 UC-019](../functional/use-cases/UC-019-request-a-patrol-on-demand.md) steps 4 to 6 and A1 pass |
| <a id="t3-21"></a>T3.21 | S29 | [E3.5](#e3-5) | The Site agent role reaches no command endpoint, no Squad subject and no MCP tool; added to the isolation suite of P2 | [🎬 UC-019](../functional/use-cases/UC-019-request-a-patrol-on-demand.md) A2 passes; every command called as a Site agent is refused and logged |
| <a id="t3-22"></a>T3.22 | S30 | [E3.6](#e3-6) | LiveKit SFU in the cell and at the edge, three-layer simulcast; the Mosaic takes the smallest layer, the Focus view the full one; streams past the Operator's maximum are not subscribed | Video of the Squad under 300 ms glass to glass at the edge; switching to the Focus view under 200 ms |
| <a id="t3-23"></a>T3.23 | S30 | [E3.6](#e3-6) | Recording: video segments to object storage, fingerprinted; the Alarm clip cut from the segments and chained | The clip of an Alarm verifies like a Flight log in the 🔏 Evidence tab |
| <a id="t3-24"></a>T3.24 | S30 | [E3.4](#e3-4) | SIA DC-09 receiver that turns an alarm panel's message into the same call as the webhook | An alarm panel simulator raises the intrusion Alarm at gate 3 through SIA DC-09 |
| <a id="t3-25"></a>T3.25 | S30 | [E3.1](#e3-1) | Minimal edge on the Dock PC (flight engine, `video-relay`, leaf node), signed updates over the air in rings, never during a Mission | The Dock site keeps patrolling with the cell link cut, and replays its Flight log in order when it returns; an update waits for the landing |
| <a id="t3-26"></a>T3.26 | S31 | [E3.6](#e3-6) | LL-HLS for the Client portal, produced from the SFU and served by the CDN, only when the Operator enabled it for the Mission | [🎬 UC-011](../functional/use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md) A1 passes with 2 to 5 s of delay; off by default |
| <a id="t3-27"></a>T3.27 | S31 | [E3.6](#e3-6) | Face blurring in Client-visible video, on request, by the video worker of `processing` | Faces in the test clips are blurred in every Client-visible copy; the Pilot's video is unchanged |
| <a id="t3-28"></a>T3.28 | S31 | [E3.7](#e3-7) | Webhooks out: Mission events, Deliverables and Scorecards published, Alarm outcomes; HMAC-SHA256, exponential back-off for 24 hours, visible in the Back office | A receiver stopped for an hour gets every event, in order, once it restarts |
| <a id="t3-29"></a>T3.29 | S31 | [E3.3](#e3-3) | Patrol in the Debrief and the Scorecard: route completed, points checked, time to reach an Alarm, with the timeline of events and Alarms | The night patrol with one Alarm gets its Scorecard, each criterion with its evidence |
| <a id="t3-30"></a>T3.30 | S31 | [E3.2](#e3-2) | Firmware watch: a firmware version that differs from the approved one makes the Drone model Not approved and its Drones Grounded until the test passes again | [🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md) A4 passes |
| <a id="t3-31"></a>T3.31 | S32 | [E3.6](#e3-6) | Nightly load test extended: 500 video viewers and 5,000 WebSocket clients per cell, Patrol Missions with Alarms among the 200 Missions in flight | Every budget holds for 5 nights in a row |
| <a id="t3-32"></a>T3.32 | S32 | [E3.8](#e3-8) | Fixes from C-03: Dock behaviour in cold and wet weather, Parrot Link at night, 4G uploads from the Dock site | Each field issue has its test, and the test passes |
| <a id="t3-33"></a>T3.33 | S32 | [E3.8](#e3-8) | Playwright captures of [🎬 UC-018](../functional/use-cases/UC-018-respond-to-a-site-alarm.md), [🎬 UC-019](../functional/use-cases/UC-019-request-a-patrol-on-demand.md) and [🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md) in both modes, rows moved to 📸 Screenshot | Visual comparison passes; the mock-ups are deleted |
| <a id="t3-34"></a>T3.34 | S33 | [E3.8](#e3-8) | Penetration test before Patrol goes live: webhook in, SIA DC-09 receiver, Web Push, Site agent role, Dock links; and its fixes | No high or critical issue left open |
| <a id="t3-35"></a>T3.35 | S33 | [E3.8](#e3-8) | Patrol beta readiness: the Dock site, its Client and Site agents in the OVHcloud cell of the design partner, the duty roster of Pilots, the runbook of the beta month | The Dock site is set up for the beta month, and the runbook is reviewed with the partner |

## <a id="demo"></a>🎤 Demo

Given on 7 Apr 2028, the last day of S33 and of C-03. It is played twice: first in the simulation environment, with the sample cast of the [🎨 visual identity](../visual-identity.md) exactly as the use cases tell it, then live at the Dock site with the real kit of C-03 (one Dock and 2 ANAFI USA).

| Cast | Plays |
| --- | --- |
| Aerowing Services | The [🗃️ Operator](../glossary.md#ent-operator) |
| Sam Carter | The [👤 Pilot](../glossary.md#per-pilot) on duty |
| Léa Martin | The [👤 Mission planner](../glossary.md#per-mission-planner) |
| Noah Weber | The [👤 Fleet maintainer](../glossary.md#per-fleet-maintainer) |
| Inès Garcia of Northgate Logistics | The [👤 Site agent](../glossary.md#per-site-agent) |
| Northgate warehouse, Dock 1, Dock 2 | The [🗃️ Site](../glossary.md#ent-site) and its [🗃️ Docks](../glossary.md#ent-dock) |
| Charlie on the Patrol route, Delta and Echo (ANAFI USA) in the Docks | The [🗃️ Squad](../glossary.md#ent-squad) of M-2026-0414 Night patrol of Northgate |

1. **Connect.** Noah Weber shows the compatibility test of the ANAFI USA: every step passed in the test area, the Drone model Approved for its firmware, Echo Ready ([🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md)).
2. **Plan.** Léa Martin shows the Patrol route of Northgate warehouse, its points to watch and its nightly schedule.
3. **Patrol.** Sam Carter, on duty, signs the Pre-flight check of M-2026-0414; Charlie flies the Patrol route, Delta and Echo wait in Dock 1 and Dock 2.
4. **Alarm.** At 22:41 the Site security system raises an intrusion Alarm at gate 3 through its webhook. Ground control shows Alarm: Raised; launch on Alarm is enabled and Sam is on duty, so Delta and Echo take off by themselves; Inès Garcia's phone receives the push ([🎬 UC-018](../functional/use-cases/UC-018-respond-to-a-site-alarm.md)).
5. **Watch and close.** Sam watches gate 3 in the Mosaic, then in Echo's Focus view, and closes the Alarm with its outcome. The clip gets its Evidence record; Delta and Echo Return home to their Docks.
6. **Site agent.** Inès reads the outcome in 🔔 Alarms. She looks for a command and finds none. She requests a look at the car park with a note; Sam accepts it and the Mission is Planned on its Patrol route. A second request, left unanswered, becomes Declined when the waiting time ends, set short for the demonstration ([🎬 UC-019](../functional/use-cases/UC-019-request-a-patrol-on-demand.md)).
7. **Alarm panel.** The same flow starts from an alarm panel through SIA DC-09, with no Drone Ready: the Alarm stays Raised and Sam and Inès are told at once that no Drone can fly.
8. **Client view.** Northgate Logistics follows the patrol in the Client portal through LL-HLS, enabled by Aerowing Services for this Mission, with faces blurred ([🎬 UC-011](../functional/use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md)).
9. **Morning after.** Sam opens the Debrief: the timeline of the night, the route completed, the points checked and the time to reach the Alarm in the Scorecard. The Operator's system has received each Alarm outcome by webhook.
10. **Live.** At the Dock site, the real Dock launches an ANAFI USA on an Alarm from the Site's security system, and lands it back inside.

Milestone M3 ([🏆 Milestones](README.md#milestones)) comes after P3: the Dock site patrols on a schedule and on Alarms for one month, from 1 to 30 Jun 2028 (S37 to S39), with a Pilot on duty, on the OVHcloud cell of the design partner. Meanwhile it keeps flying scheduled patrols from S34. P3 has no ticket after S33: as the product owner decided, the fixes of the Patrol beta are taken from the capacity of [🛣️ P4](05-p4-agriculture.md) and [🛣️ P5](06-p5-ai-agents.md), as the first tickets of their sprints, inside the 5 tickets merged per sprint.

## <a id="exit"></a>🚪 Exit criteria

**Acceptance criteria**, each run as a Playwright or API test, and once at the Dock site:

- [ ] [📘 FS-015](../functional/features/FS-015-patrol.md#acceptance) AC-1: an Alarm at gate 3 sent by the Site security system is shown to the Pilot, and the nearest Drones are proposed.
- [ ] [📘 FS-015](../functional/features/FS-015-patrol.md#acceptance) AC-2: a Site agent's request for a look at the car park waits for a Pilot to accept it.
- [ ] [📘 FS-011](../functional/features/FS-011-drone-adapters.md#acceptance) AC-1: a new Drone model whose compatibility test fails on Return home keeps its Drones Grounded, shown with the ANAFI USA.
- [ ] [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md#details) Notifications: every Notification appears in the 🔔 of the part of Swarm the person uses and by e-mail; Site agents and Pilots on duty also get it by push on a mobile.
- [ ] [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md#acceptance) AC-2 run again on Notifications: a Site agent who chose German gets every Notification in German.
- [ ] [📘 FS-008](../functional/features/FS-008-client-portal.md#acceptance) AC-2 run again with live video enabled: the Client sees the Squad and its video, and has no command.
- [ ] [📘 FS-022](../functional/features/FS-022-debrief-and-assessment.md#details) Patrol criteria: route completed, points checked and time to reach an Alarm are assessed in the Scorecard.

**Budgets** ([🚀 Budgets](../technical/07-scalability.md#budgets), [🚀 Cells](../technical/07-scalability.md#cells), [🖥️ Front-end budgets](../technical/10-frontends.md#performance)):

- [ ] WebRTC video under 300 ms glass to glass, measured at the Dock site and through the cell.
- [ ] Switching to the Focus view under 200 ms.
- [ ] Hold the Squad or abort reaches every Drone in under 100 ms, Drones launched from a Dock included; the Pilot command p99 under 50 ms at the edge on a local link, measured for the Parrot adapter and recorded.
- [ ] One cell serves 500 video viewers and 5,000 WebSocket clients in the nightly load test.
- [ ] Telemetry p95 under 150 ms at the edge and under 400 ms through the cell, with the Patrol Missions in the load.

**Screens, checks and tests**:

- [ ] Every screen row of [🎬 UC-018](../functional/use-cases/UC-018-respond-to-a-site-alarm.md), [🎬 UC-019](../functional/use-cases/UC-019-request-a-patrol-on-demand.md) and [🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md) reads 📸 Screenshot, in light and dark mode.
- [ ] `python3 .claude/skills/write-specs/scripts/specs.py check` prints nothing.
- [ ] The nightly load test, with video and Alarms, passes every assertion for 5 nights in a row.
- [ ] The chaos test cuts the Dock site's link to the cell mid-patrol: the patrol goes on, the Flight log and the clips arrive in order afterwards.
- [ ] The isolation suite, with the Site agent role, passes on every pull request.
- [ ] The penetration test has no high or critical issue open.
- [ ] Campaign [🛫 C-03](10-flight-test-campaigns.md#c-03) is closed with its report: scheduled patrols, Alarms by webhook and SIA DC-09, Dock launches, night video, Site agents.

## <a id="dependencies"></a>⛓️ Dependencies

| Needs | From | Why |
| --- | --- | --- |
| The Client portal, the evidence ledger, the Debrief, the Scorecard, the self-hosted and OVHcloud beta cells, and the isolation suite | [🛣️ P2: Inspection product](03-p2-inspection-product.md) | Site agents, clips and Patrol Scorecards build on them |
| The MAVLink adapter and its compatibility suite, Ground control with the Mosaic and the Focus view, the Pre-flight check, Re-plans, the Fleet | [🛣️ P1: First flight](02-p1-first-flight.md) | The Parrot adapter follows the same interface and test; Patrol flies under the same safety loop |
| The Simulator and its isolated credentials | [🛣️ P0: Foundations](01-p0-foundations.md) | Simulated Docks and the simulation half of the demonstration |
| 2 Parrot ANAFI USA | [🤝 H-04](11-hardware-and-partners.md#h-04), S24 | The Parrot adapter from S26, its compatibility test in S28 |
| One Dock | [🤝 H-05](11-hardware-and-partners.md#h-05), chosen S22, delivered by S26 | The real Dock in S28 |
| The Dock site | [🤝 P-03](11-hardware-and-partners.md#p-03), S28 | Its Site security system, its Site agents, C-03 and the beta month |
| Airspace and U-space checks of the Dock site | [🏛️ G-06](09-regulatory-track.md#g-06), by S28 | Two sprints before C-03 |
| Specific category Authorisation | [🏛️ G-05](09-regulatory-track.md#g-05), S20, extended to BVLOS on request if the Dock site needs it | Squad flights at a Site with nobody on it |
| Campaign at the Dock site | [🛫 C-03](10-flight-test-campaigns.md#c-03), S30 to S33 | Real Dock launches, Alarms, night video |
| Shared capacity in S32 and S33 | [🛣️ P4: Agriculture](05-p4-agriculture.md) | P3 takes 3 tickets in S32 and 2 in S33, P4 the other 2 and 3 |
| Capacity for the fixes of the Patrol beta, S34 to S39 | [🛣️ P4: Agriculture](05-p4-agriculture.md), [🛣️ P5: AI agents, MCP and A2A](06-p5-ai-agents.md) | The beta month of M3 comes after P3; its fixes come first in their sprints |

## <a id="risks"></a>🎲 Risks

| Risk | Why it matters in P3 | Response in P3 |
| --- | --- | --- |
| [🎲 R-04](12-risks.md#r-04) Vendor SDK access restricted | The Parrot adapter depends on Parrot's SDK and its terms | Ask for the SDK terms in S24 when H-04 arrives; MAVLink stays the core path, so Patrol can fly X500 Drones if the Parrot adapter slips and the chosen Dock takes them |
| [🎲 R-07](12-risks.md#r-07) Weather and seasons | C-03 runs from February to early April, with night flights | Two spare weeks inside C-03; Simulator rehearsals; the Dock's own weather limits respected; the demonstration has a simulated half |
| [🎲 R-14](12-risks.md#r-14) GDPR complaint about video | Patrol films a Site and sometimes people, at night | Face blurring in Client-visible video ([T3.27](#t3-27)); LL-HLS off by default; raw video kept 90 days; the data processing register updated for the Dock site |
| [🎲 R-02](12-risks.md#r-02) Specific category Authorisation late or too narrow | A Site with nobody on it may need BVLOS | Ask for the extension of G-05 as soon as the Dock site is known (S28); otherwise C-03 flies in visual line of sight from the Dock, with the person on the Site |
| [🎲 R-10](12-risks.md#r-10) Security incident | The webhook in and the SIA DC-09 receiver are open to the Internet; Docks hold links to Drones | A secret per Site, rate limits, WireGuard for Docks, penetration test [T3.34](#t3-34) |
| [🎲 R-13](12-risks.md#r-13) Browser API gaps | Web Push differs between mobile browsers | E-mail stays the fallback for every Notification; the supported browsers are listed for Site agents and Pilots on duty |
| [🎲 R-11](12-risks.md#r-11) Crash or hardware loss in tests | A Dock landing at night with nobody on the Site | Every Dock launch rehearsed in the Simulator first; the first real Dock flights in daylight with the person on the Site |
| [🎲 R-01](12-risks.md#r-01) Review bottleneck | M2 support in S25, holidays in S26, P4 overlap in S32 and S33 | Fewer P3 tickets in those sprints; agents prepare the next tickets complete with tests and screens |
| [🎲 R-08](12-risks.md#r-08) Scope too large for 24 months | P3 also extends five features of P1 and P2 | DJI and Skydio stay in P7; recognising people in the video stays out of scope ([📘 FS-015](../functional/features/FS-015-patrol.md#out-of-scope)) |

## <a id="work-split"></a>🧑‍💻 Work split

| The person | The Claude Code agents, in parallel |
| --- | --- |
| Reviews and merges 2 to 5 P3 tickets a sprint, the Site agent role and the webhook in first | Split each ticket into tasks that run at once: service code, Rust Re-plans, the Parrot sidecar, tests, Helm charts, screens against their mock-ups, translations, documentation |
| Supports the design partner through M2 in S25 | Turn every issue the partner reports into a test and a fix ticket |
| Gets the Parrot SDK terms, installs the Dock, flies C-03 as the Pilot, by day then at night | Keep the simulated Docks and the alarm panel simulator in step with the real ones, so every field issue is reproduced in the Simulator |
| Runs the partners and the regulator: [🤝 P-03](11-hardware-and-partners.md#p-03), [🤝 H-05](11-hardware-and-partners.md#h-05), [🏛️ G-05](09-regulatory-track.md#g-05) extension, [🏛️ G-06](09-regulatory-track.md#g-06) | Prepare the Site, its Geofence, the Patrol route and the Alarm webhook of the Dock site in the OVHcloud cell |
| Decides the Operator settings with the Dock site: launch on Alarm, the waiting time of requests, quiet hours | Write the settings into the OVHcloud cell and their tests |
| Gives the demonstration, runs the exit check, and plans the beta month with the Dock site | Run the load tests, the chaos test, the Playwright captures and `specs.py check` every night, and report what fails |

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ P2: Inspection product](03-p2-inspection-product.md) · 📄 **Page 99 / 108** · [P4: Agriculture ▶️](05-p4-agriculture.md)
<!-- /spec:nav-bottom -->
