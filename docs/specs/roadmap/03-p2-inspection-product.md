# 🛣️ P2: Inspection product

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ P1: First flight](02-p1-first-flight.md) · 📄 **Page 109 / 120** · [P3: Patrol ▶️](04-p3-patrol.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Sprints:** S14 to S24 · **Dates:** 5 Jul 2027 to 3 Dec 2027 · **Tickets:** about 50

> [!NOTE]
> P2 flies the first real Squad (4 X500, one Pilot) in campaign C-02 and turns its flights into an Inspection product a drone service company can sell (Deliverables, Defects confirmed by a person, the Client portal, the evidence ledger, the Debrief and the Scorecard), because the design partner signed at M1b needs it to fly a real Mission for a Client at M2 on 17 Dec 2027.

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

At the end of P1, a [👤 Pilot](../glossary.md#per-pilot) can design, check, launch and supervise an [🔤 Inspection](../glossary.md#term-inspection) [🗃️ Squad](../glossary.md#ent-squad) in the Simulator, but real Drones fly only one at a time, in the Open category, and the images stay on the Drones' cards. P2 flies the first real Squad and closes the loop from the landing to the [👤 Client](../glossary.md#per-client):

- **The first real Squad flight** of Swarm happens in campaign [🛫 C-02](10-flight-test-campaigns.md#c-02): 4 X500 under one Pilot, at the partner's solar farm, under the Specific category [🗃️ Authorisation](../glossary.md#ent-authorisation) [🏛️ G-05](09-regulatory-track.md#g-05). If G-05 is late, C-02 stays in the Open category with one Drone at a time, and the first Squad flight waits for G-05.

- The data of every [🗃️ Drone](../glossary.md#ent-drone) reaches the cell after landing, tagged with its Drone, [🗃️ Payload](../glossary.md#ent-payload), position and time, and passes the [🔤 Quality checks](../glossary.md#term-quality-check) before anything is built.
- `processing` builds the [🗃️ Deliverables](../glossary.md#ent-deliverable) of an Inspection (orthomosaic, 3D model, defect list) on GPU workers, and detection marks [🗃️ Defects](../glossary.md#ent-defect) on solar farms, the first structure Swarm ships a model for.
- The [👤 Mission planner](../glossary.md#per-mission-planner) reviews every Deliverable and every Defect in the [⚙️ Back office](../glossary.md#sys-back-office), and nothing reaches the Client before a person publishes it.
- The [⚙️ Client portal](../glossary.md#sys-client-portal) exists: the Client is invited, orders a [🗃️ Mission](../glossary.md#ent-mission), follows it on a map, reads its [🗃️ Scorecard](../glossary.md#ent-scorecard), downloads its Deliverables and verifies their [🗃️ Evidence records](../glossary.md#ent-evidence-record).
- Every closed [🗃️ Flight log](../glossary.md#ent-flight-log) and every published Deliverable has an Evidence record, signed, chained and anchored every hour with a qualified timestamping authority through the [⚙️ Anchoring service](../glossary.md#sys-anchoring-service).
- The Pilot debriefs each Mission in [⚙️ Ground control](../glossary.md#sys-ground-control) ([🗃️ Debrief](../glossary.md#ent-debrief): [🔤 Replay](../glossary.md#term-replay), plan against actual, Quality checks), and the Mission planner assesses it against the request in the [⚙️ Mission studio](../glossary.md#sys-mission-studio), with a re-fly of the gaps when needed.
- Two beta cells exist, both provisioned with Terraform, then Helm and Argo CD (decision T43): a self-hosted beta cell, where C-02 runs and which stays as the second cell (on-premises rehearsal and fallback), and an [OVHcloud](../technical/09-deployment.md#providers) cell opened early, in S24, where the design partner's [🗃️ Operator](../glossary.md#ent-operator) runs its beta from M2.
- Campaign C-02 proves the whole chain at the partner's solar farm, from the first real Squad flight to the published Scorecard.

## <a id="scope"></a>🧺 Scope

**Features**

| Feature | Delivered in P2 | Left for later |
| --- | --- | --- |
| [📘 FS-007: Data processing and Deliverables](../functional/features/FS-007-data-processing-and-deliverables.md) | Collection, tagging, Quality checks, orthomosaic, 3D model, defect list, review and publication, in the cloud cells | Processing on the Operator's own GPU server, with the on-premises bundle of [🛣️ P7](08-p7-scale-and-reach.md) |
| [📘 FS-008: Client portal](../functional/features/FS-008-client-portal.md) | The whole app: invitation, ordering, following the Squad at 2 Hz, Scorecards, downloads, evidence | Live video for Clients (LL-HLS), in [🛣️ P3](04-p3-patrol.md) |
| [📘 FS-009: Evidence ledger and Anchoring](../functional/features/FS-009-evidence-ledger-and-anchoring.md) | Chain per Operator, signatures, hourly Anchoring with a qualified timestamping authority, verification | The blockchain option, in [🛣️ P7](08-p7-scale-and-reach.md) |
| [📘 FS-016: Inspection](../functional/features/FS-016-inspection.md) | Mixed thermal and RGB Squads processed together, solar farm detection, Defect review | Detection models for other structures |
| [📘 FS-022: Debrief and assessment](../functional/features/FS-022-debrief-and-assessment.md) | Replay, plan against actual, Quality checks, Scorecard with the Inspection criteria, re-fly | Patrol criteria in [🛣️ P3](04-p3-patrol.md), Agriculture criteria in [🛣️ P4](05-p4-agriculture.md), Light show criteria in [🛣️ P6](07-p6-light-shows.md) |
| [📘 FS-019: Mission reports](../functional/features/FS-019-mission-reports.md) | The report template, filled from the Mission's data without AI, reviewed and published by a person | The [⚙️ Report writer](../glossary.md#sys-report-writer) and its conversation, in [🛣️ P5](06-p5-ai-agents.md) |

**Use cases**

| Use case | Delivered in P2 | Left for later |
| --- | --- | --- |
| [🎬 UC-009: Process flight data into Deliverables](../functional/use-cases/UC-009-process-flight-data-into-deliverables.md) | Every step and alternative flow, Anchoring with a timestamping authority | Step 3 on the Operator's own GPU server (P7) |
| [🎬 UC-010: Order a Mission in the Client portal](../functional/use-cases/UC-010-order-a-mission-in-the-client-portal.md) | Every step and alternative flow | None |
| [🎬 UC-011: Follow a Mission and download its Deliverables](../functional/use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md) | Every step, alternative flows A2 to A6 | A1, live video for the Client (P3) |
| [🎬 UC-012: Verify the Evidence record of a flight](../functional/use-cases/UC-012-verify-the-evidence-record-of-a-flight.md) | Every step, alternative flows A1 and A3 | A2, the blockchain option (P7) |
| [🎬 UC-015: Invite a Client to the Client portal](../functional/use-cases/UC-015-invite-a-client-to-the-client-portal.md) | Every step and alternative flow; the Site agent's access is created, and its 🔔 Alarms fill in P3 | None |
| [🎬 UC-020: Review the Defects of an Inspection](../functional/use-cases/UC-020-review-the-defects-of-an-inspection.md) | Every step and alternative flow | None |
| [🎬 UC-027: Debrief a Mission](../functional/use-cases/UC-027-debrief-a-mission.md) | Every step and alternative flow, for Inspection | Other Activities with their phases |
| [🎬 UC-028: Assess a Mission against the request](../functional/use-cases/UC-028-assess-a-mission-against-the-request.md) | Every step and alternative flow, for Inspection | Other Activities with their phases |
| [🎬 UC-022: Receive the Mission report](../functional/use-cases/UC-022-receive-the-mission-report.md) | Steps 2 to 5, with a report built from the template | Step 1 and the conversation of step 2, by the Report writer (P5) |

**Business rules**

| Rule | How P2 applies it |
| --- | --- |
| [📏 BR-009: Evidence integrity](../functional/business-rules/BR-009-evidence-integrity.md) | Delivered: chain, signature, Anchoring, verification, Altered warning |
| [📏 BR-016: Clients see only their own Missions](../functional/business-rules/BR-016-clients-see-only-their-own-missions.md) | Delivered: the Client's Sites in the token, checked in the gateway and by row-level security; another Client's Mission answers not found |
| [📏 BR-020: Defects confirmed by a person](../functional/business-rules/BR-020-defects-confirmed-by-a-person.md) | Delivered: only Confirmed Defects leave the Back office; dismissals need a reason from the fixed list |
| [📏 BR-026: Scorecard against the request](../functional/business-rules/BR-026-scorecard-against-the-request.md) | Delivered for the Inspection criteria: coverage, image overlap, ground resolution, thermal calibration |
| [📏 BR-008: Operator isolation](../functional/business-rules/BR-008-operator-isolation.md) | Applied again to every new table, bucket path and subject: Deliverables, Defects, Evidence records, Scorecards |
| [📏 BR-017: Every screen in four languages](../functional/business-rules/BR-017-every-screen-in-four-languages.md) | Applied to every new screen, and to the report template |
| [📏 BR-021: AI agents propose, people decide](../functional/business-rules/BR-021-ai-agents-propose-people-decide.md) | Its human half only: Deliverables, Defects, reports and Scorecards are published by a named person; the AI agents come in P5 |

**Technical pages**

| Page | What P2 builds from it |
| --- | --- |
| [🔩 Engine and services: Processing](../technical/04-engine.md#processing) | The `processing` service: JetStream work queue with priorities, NodeODM photogrammetry, ONNX Runtime detection, tiling, PyTorch training on the GPU pool |
| [🔩 Engine and services: Evidence](../technical/04-engine.md#evidence) | The `evidence` service: one chain per Operator, SHA-256, Ed25519 through the vault, hourly Merkle Anchoring with RFC 3161 |
| [🗄️ Storage: Object storage](../technical/03-storage.md#object-storage) | One bucket per Operator, resumable multipart uploads from the edge, signed URLs, object lock for evidence |
| [🗄️ Storage: Retention](../technical/03-storage.md#retention) | Raw images and video 90 days, Deliverables and evidence files 5 years under object lock |
| [🗄️ Storage: Backups and recovery](../technical/03-storage.md#backups) | pgBackRest for both beta cells, monthly restore drill |
| [🔌 API layer: REST](../technical/05-api.md#rest) | `/v1/deliverables`, `/v1/defects`, `/v1/scorecards`, `/v1/evidence/{id}/verify` |
| [🔌 API layer: Live data](../technical/05-api.md#live) | Client portal subscriptions at 2 Hz, positions only |
| [🔐 Security: Roles and Operator isolation](../technical/06-security.md#authorisation) | Client and Site agent roles, scoped to their Sites |
| [🔐 Security: Privacy and compliance](../technical/06-security.md#privacy) | Retention of raw images, data processing register per Operator |
| [🖥️ GUI and WebUI: Maps and 3D](../technical/10-frontends.md#maps) | Orthomosaics as Cloud Optimized GeoTIFF, 3D models as 3D Tiles, Defects as a deck.gl layer |
| [🖥️ GUI and WebUI: Front-end budgets](../technical/10-frontends.md#performance) | The Client portal, a new app, held to the first-load budget |
| [🚀 Scalability and performance: Budgets](../technical/07-scalability.md#budgets) | The orthomosaic budget: 1,000 images in under 30 minutes on one GPU worker |
| [🚢 Deployment: Environments](../technical/09-deployment.md#environments) | A self-hosted beta cell (C-02, then on-premises rehearsal and fallback) deployed from the same charts as staging |
| [🚢 Deployment: Where it runs](../technical/09-deployment.md#providers) | An OVHcloud cell opened early, in S24, for the design partner; every cell's infrastructure written in Terraform (decision T43), then Helm and Argo CD |

## <a id="epics"></a>🪜 Epics

| Epic | Name | Delivers (UC/BR links) | Where (services, apps, packages) | Tickets | Parallel tasks for the agents |
| --- | --- | --- | --- | --- | --- |
| <a id="e2-1"></a>E2.1 | Data from the edge | [🎬 UC-009](../functional/use-cases/UC-009-process-flight-data-into-deliverables.md) step 1, [📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md) | `flight-engine` (upload after landing), `gateway`, object storage bucket per Operator, `packages/python` (file tags) | 3: [T2.01](#t2-01), [T2.02](#t2-02), [T2.41](#t2-41) | Upload client with resume and its tests against MinIO; tag model and its validators; chaos test cutting the link mid-upload |
| <a id="e2-2"></a>E2.2 | Processing and Quality checks | [🎬 UC-009](../functional/use-cases/UC-009-process-flight-data-into-deliverables.md) steps 2 and 3, A1 | `processing` (workers: photogrammetry, tiling), KEDA `ScaledObject`, GPU node pool | 6: [T2.03](#t2-03), [T2.06](#t2-06), [T2.07](#t2-07), [T2.11](#t2-11), [T2.12](#t2-12), [T2.39](#t2-39) | Worker code; sample data sets of 100 and 1,000 images; Helm chart and scaler; benchmark in staging; Quality check rules from a catalogue |
| <a id="e2-3"></a>E2.3 | Solar detection | [🎬 UC-020](../functional/use-cases/UC-020-review-the-defects-of-an-inspection.md) precondition 2, [📏 BR-020](../functional/business-rules/BR-020-defects-confirmed-by-a-person.md) | `processing` (detection worker, training on the GPU pool), `models/<model_id>/` in object storage | 2: [T2.16](#t2-16), [T2.17](#t2-17) | Labelling tooling and pre-labels; training script and evaluation set; ONNX export; worker and its tests on a fixed image set |
| <a id="e2-4"></a>E2.4 | Deliverables and Defects in the Back office | [🎬 UC-009](../functional/use-cases/UC-009-process-flight-data-into-deliverables.md) steps 4 and 5, A2, [🎬 UC-020](../functional/use-cases/UC-020-review-the-defects-of-an-inspection.md), [📏 BR-020](../functional/business-rules/BR-020-defects-confirmed-by-a-person.md) | `missions` (Deliverable and Defect states), `back-office` (📦 Deliverables), `packages/ts/maps`, `packages/ts/api-client` | 6: [T2.05](#t2-05), [T2.10](#t2-10), [T2.18](#t2-18), [T2.19](#t2-19), [T2.21](#t2-21), [T2.24](#t2-24) | Models and migrations; REST endpoints and OpenAPI; React screens against the mock-ups; Playwright flows; i18n messages in four languages |
| <a id="e2-5"></a>E2.5 | Evidence ledger | [🎬 UC-009](../functional/use-cases/UC-009-process-flight-data-into-deliverables.md) step 6, A3, [🎬 UC-012](../functional/use-cases/UC-012-verify-the-evidence-record-of-a-flight.md), [📏 BR-009](../functional/business-rules/BR-009-evidence-integrity.md) | `evidence` (Python with Rust hashing in `packages/rust`), vault transit engine, object lock bucket path `evidence/` | 6: [T2.04](#t2-04), [T2.08](#t2-08), [T2.13](#t2-13), [T2.25](#t2-25), [T2.34](#t2-34), [T2.40](#t2-40) | Chain writer and its property tests (tamper, reorder, gap); Merkle tree in Rust with benchmarks; RFC 3161 client; verification API; retention tasks |
| <a id="e2-6"></a>E2.6 | Client portal | [🎬 UC-010](../functional/use-cases/UC-010-order-a-mission-in-the-client-portal.md), [🎬 UC-011](../functional/use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md), [🎬 UC-012](../functional/use-cases/UC-012-verify-the-evidence-record-of-a-flight.md), [🎬 UC-015](../functional/use-cases/UC-015-invite-a-client-to-the-client-portal.md), [📏 BR-016](../functional/business-rules/BR-016-clients-see-only-their-own-missions.md), [📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md) | `client-portal` (new app), `gateway` (roles, live rate), Keycloak (invitations), `packages/ts/ui`, `packages/ts/live`, `packages/ts/i18n` | 8: [T2.09](#t2-09), [T2.14](#t2-14), [T2.15](#t2-15), [T2.20](#t2-20), [T2.22](#t2-22), [T2.23](#t2-23), [T2.26](#t2-26), [T2.36](#t2-36) | App frame from the visual identity; each screen against its mock-up; isolation tests per role; translations; Web Worker hashing for the evidence page |
| <a id="e2-7"></a>E2.7 | Debrief and Scorecard | [🎬 UC-027](../functional/use-cases/UC-027-debrief-a-mission.md), [🎬 UC-028](../functional/use-cases/UC-028-assess-a-mission-against-the-request.md), [📏 BR-026](../functional/business-rules/BR-026-scorecard-against-the-request.md), [📏 BR-009](../functional/business-rules/BR-009-evidence-integrity.md) | `ground-control` (📼 Replay, 📊 Plan against actual, 🔬 Quality checks), `mission-studio` (🧾 Scorecard), `missions` (Scorecard, linked re-fly), TimescaleDB reads | 7: [T2.27](#t2-27), [T2.28](#t2-28), [T2.29](#t2-29), [T2.31](#t2-31), [T2.32](#t2-32), [T2.33](#t2-33), [T2.35](#t2-35) | Coverage computation in Rust; timeline component; Scorecard rules and their tests per criterion; screens; replay of a recorded C-01 Flight log as fixture |
| <a id="e2-8"></a>E2.8 | Mission report from a template | [🎬 UC-022](../functional/use-cases/UC-022-receive-the-mission-report.md) steps 2 to 5, [📏 BR-020](../functional/business-rules/BR-020-defects-confirmed-by-a-person.md), [📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md) | `processing` (report renderer), `back-office`, `client-portal` | 2: [T2.37](#t2-37), [T2.38](#t2-38) | Template in four languages; renderer and its golden files; review screen |
| <a id="e2-9"></a>E2.9 | Beta cells and operations | [📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md), [📏 BR-016](../functional/business-rules/BR-016-clients-see-only-their-own-missions.md) | `deploy/` (Terraform for the self-hosted and OVHcloud beta cells, Helm values, Argo CD apps), pgBackRest, OpenTelemetry dashboards, `tests/load` (k6) | 6: [T2.30](#t2-30), [T2.42](#t2-42), [T2.46](#t2-46), [T2.47](#t2-47), [T2.48](#t2-48), [T2.49](#t2-49) | Terraform modules per provider; charts and values; restore drill script; moving an Operator between cells; dashboards and SLO alerts; k6 scenarios; cross-Operator and cross-Client test suite; release notes |
| <a id="e2-10"></a>E2.10 | Screens and exit | Every use case of P2 moves to 📸 Screenshot | `frontends/*/e2e` (Playwright), `docs/specs/screens/` | 4: [T2.43](#t2-43), [T2.44](#t2-44), [T2.45](#t2-45), [T2.50](#t2-50) | Playwright captures in light and dark mode with the sample data; screen rows updated; `specs.py check` |

## <a id="sprints"></a>🗓️ Sprint plan

About 5 tickets merged per sprint until S19, then 4 during campaign [🛫 C-02](10-flight-test-campaigns.md#c-02), when the person also flies. P1 ends in S13 and P3 starts in S25, so P2 has the whole capacity: 50 tickets.

| Sprint | Dates | Tickets | Sprint goal | What can be shown |
| --- | --- | --- | --- | --- |
| S14 | 5 to 16 Jul 2027 | [T2.01](#t2-01) Upload from the edge, [T2.02](#t2-02) Tag every file, [T2.03](#t2-03) Processing queue, [T2.04](#t2-04) Evidence chain, [T2.05](#t2-05) Deliverable and Defect models | The data of a landed Squad reaches the cell, and the first Evidence records are chained | A simulated Inspection lands; its images appear in the Operator's bucket, tagged; a record chain verifies in a test |
| S15 | 19 to 30 Jul 2027 | [T2.06](#t2-06) Photogrammetry worker, [T2.07](#t2-07) Quality checks, [T2.08](#t2-08) Flight log records, [T2.09](#t2-09) Client portal frame, [T2.10](#t2-10) 📦 Deliverables list | The first orthomosaic is built after the Quality checks pass | An orthomosaic of a C-01 data set, Deliverable: Processing then In review; a failed overlap check names the Drone and the area |
| S16 | 2 to 13 Aug 2027 | [T2.11](#t2-11) Tiling, [T2.12](#t2-12) Large Sites, [T2.13](#t2-13) Hourly Anchoring, [T2.14](#t2-14) Invitations, [T2.15](#t2-15) Client scopes | Deliverables are viewable by tiles, and a Client can be invited and sees only its Sites | Priya Shah accepts her invitation, chooses her language, and sees only the Missions of Helio Energy |
| S17 | 16 to 27 Aug 2027 | [T2.16](#t2-16) Solar model training, [T2.17](#t2-17) Detection worker, [T2.18](#t2-18) Defect review, [T2.19](#t2-19) Dismissal reasons, [T2.20](#t2-20) Ordering | Detection marks Suspected Defects and the Mission planner reviews them; Clients can order | 12 Suspected Defects on a solar data set; Léa Martin confirms and dismisses them; Priya Shah orders an Inspection of Les Vignes |
| S18 | 30 Aug to 10 Sep 2027 | [T2.21](#t2-21) Publication, [T2.22](#t2-22) Live follow-up, [T2.23](#t2-23) Downloads, [T2.24](#t2-24) Map and 3D viewer, [T2.25](#t2-25) Verification API | A Client follows a Mission and downloads its published Deliverables | Priya Shah follows a simulated Squad at 2 Hz, then downloads the orthomosaic and the defect list with the 9 Confirmed Defects |
| S19 | 13 to 24 Sep 2027 | [T2.26](#t2-26) 🔏 Evidence tab, [T2.27](#t2-27) Replay, [T2.28](#t2-28) Plan against actual, [T2.29](#t2-29) Quality checks view, [T2.30](#t2-30) Self-hosted beta cell | The Debrief exists in Ground control, and the self-hosted beta cell is ready for C-02 | Sam Carter replays M-2026-0412 with the loss of Delta; Priya Shah verifies a Flight log, then an edited copy shows Altered |
| S20 | 27 Sep to 8 Oct 2027 | [T2.31](#t2-31) Scorecard computation, [T2.32](#t2-32) Scorecard review, [T2.33](#t2-33) Linked re-fly, [T2.34](#t2-34) Qualified timestamping authority | Missions are assessed against the request; C-02 opens at the solar farm with the first real Squad flight, 4 X500 under one Pilot, once G-05 is granted (8 Oct 2027 at the latest) | The Fail-safe drills of the Squad at the solar farm, then the first real Squad flight; a Failed Scorecard at 96 % coverage, a linked re-fly, then Passed; Anchoring receipts from the qualified timestamping authority |
| S21 | 11 to 22 Oct 2027 | [T2.35](#t2-35) Altered Flight log in the Debrief, [T2.36](#t2-36) 🧾 Scorecards for Clients, [T2.37](#t2-37) Report template, [T2.38](#t2-38) Report review | The Client reads the Scorecard and receives a report built from the template; C-02 flies the real Squad every flight day | The first real Squad Mission of C-02, from landing to a published report in English and French |
| S22 | 25 Oct to 5 Nov 2027 | [T2.39](#t2-39) Orthomosaic budget, [T2.40](#t2-40) Retention and object lock, [T2.41](#t2-41) Upload on weak links, [T2.42](#t2-42) Dashboards and SLO alerts | The chain holds at the speed and on the links of a real Site, with a real Squad of 4 X500 | 1,000 C-02 images to an orthomosaic in under 30 minutes on one GPU worker; an upload resumed after a cut 4G link |
| S23 | 8 to 19 Nov 2027 | [T2.43](#t2-43) Screenshots of processing and Defects, [T2.44](#t2-44) Screenshots of the Client portal, [T2.45](#t2-45) Screenshots of the Debrief, [T2.46](#t2-46) Load test | The screens of P2 are the real application | Playwright captures replacing the mock-ups of eight use cases, in light and dark mode; the nightly load test with Client portal viewers |
| S24 | 22 Nov to 3 Dec 2027 | [T2.47](#t2-47) Penetration test fixes, [T2.48](#t2-48) Isolation suite, [T2.49](#t2-49) OVHcloud cell and beta release, [T2.50](#t2-50) Exit check | Inspection is ready to go live for the design partner, on its OVHcloud cell | The [phase demonstration](#demo), given to the design partner on the last day of C-02, on the OVHcloud cell |

### 🎫 Tickets

| Ticket | Sprint | Epic | Delivers | Done when |
| --- | --- | --- | --- | --- |
| <a id="t2-01"></a>T2.01 | S14 | [E2.1](#e2-1) | After landing, `flight-engine` uploads the images, video and Flight log of each Drone to `op-<operator_id>/missions/<mission_id>/raw/<drone_id>/` with resumable multipart uploads and SHA-256 checksums | A simulated Squad of 4 Drones uploads 400 images; a restarted upload resumes at the last part; checksums are stored for the Evidence records |
| <a id="t2-02"></a>T2.02 | S14 | [E2.1](#e2-1) | Every file tagged with its Drone, Payload, position and time, matched from the Flight log | Each image of a mixed thermal and RGB Squad carries the four tags; an image with no matching Telemetry is reported, not dropped |
| <a id="t2-03"></a>T2.03 | S14 | [E2.2](#e2-2) | The `processing` service: JetStream work queue with priorities (detection before photogrammetry, interactive before batch), GPU workers scaled by KEDA on queue depth, to zero when idle | A queued task starts a GPU worker from zero; two queued tasks run in priority order |
| <a id="t2-04"></a>T2.04 | S14 | [E2.5](#e2-5) | The `evidence` service: one append-only chain per Operator, SHA-256 of the content, hash of the previous record, Ed25519 signature through the vault transit engine, one writer per Operator chain | Property tests: a changed, removed or reordered record breaks the chain; the signing key never leaves the vault |
| <a id="t2-05"></a>T2.05 | S14 | [E2.4](#e2-4) | Deliverable and Defect models with their states (Processing, In review, Published; Suspected, Confirmed, Dismissed) in the `missions` schema, with row-level security by Operator | Model tests of AGENT.md pass; a query without the Operator setting returns nothing |
| <a id="t2-06"></a>T2.06 | S15 | [E2.2](#e2-2) | Photogrammetry worker: OpenDroneMap through NodeODM on GPU, orthomosaic and 3D model of an Inspection | A data set of C-01 builds an orthomosaic and a 3D model; progress is shown on Deliverable: Processing |
| <a id="t2-07"></a>T2.07 | S15 | [E2.2](#e2-2) | Quality checks of an Inspection: image overlap, sharpness, thermal calibration, gaps; pass levels from a catalogue, Operator and Client levels when stricter | A data set with low overlap over one area is stopped before processing, naming the check, the Drone and the area ([🎬 UC-009](../functional/use-cases/UC-009-process-flight-data-into-deliverables.md) A1) |
| <a id="t2-08"></a>T2.08 | S15 | [E2.5](#e2-5) | Every closed Flight log gets its Evidence record, reusing the upload checksums; Telemetry archives in Parquet are fingerprinted too | A Flight log closed at the edge while offline gets its record once the leaf node reconnects, in order |
| <a id="t2-09"></a>T2.09 | S15 | [E2.6](#e2-6) | `frontends/client-portal`: frame of the visual identity, sign-in with Keycloak, four languages, installable web app, first-load budget | The empty portal loads in under 2.5 s on 4G with under 300 kB of JavaScript for the first route |
| <a id="t2-10"></a>T2.10 | S15 | [E2.4](#e2-4) | Back office 📦 Deliverables: list per Mission with states and progress | Léa Martin sees the Deliverables of M-2026-0412 move from Processing to In review |
| <a id="t2-11"></a>T2.11 | S16 | [E2.2](#e2-2) | Tiling worker: orthomosaics as Cloud Optimized GeoTIFF, 3D models as 3D Tiles, served by range through signed URLs | The orthomosaic opens in a browser by tiles, without downloading the whole file |
| <a id="t2-12"></a>T2.12 | S16 | [E2.2](#e2-2) | Large Sites split into sub-models and merged | A data set twice the size of one worker's memory builds in parts and merges without a visible seam |
| <a id="t2-13"></a>T2.13 | S16 | [E2.5](#e2-5) | Hourly Merkle tree of the records, its root anchored with an RFC 3161 timestamping authority (a test service until [🤝 P-07](11-hardware-and-partners.md#p-07)), receipts stored with the records; no Anchoring when the Operator chose none | One hour of records gets one receipt; each record proves its place in the tree ([🎬 UC-009](../functional/use-cases/UC-009-process-flight-data-into-deliverables.md) A3 covered) |
| <a id="t2-14"></a>T2.14 | S16 | [E2.6](#e2-6) | Back office 👥 People: the Mission planner invites a Client and a Site agent with their Sites; Keycloak sends the invitations; the invited person chooses a language | [🎬 UC-015](../functional/use-cases/UC-015-invite-a-client-to-the-client-portal.md) steps 1 to 4 and A2 pass in Playwright |
| <a id="t2-15"></a>T2.15 | S16 | [E2.6](#e2-6) | Client and Site agent roles: their Sites in the token, checked in the gateway, enforced by row-level security; a Mission of another Client or Operator answers not found and the attempt is logged | [🎬 UC-015](../functional/use-cases/UC-015-invite-a-client-to-the-client-portal.md) A1 and A3 pass |
| <a id="t2-16"></a>T2.16 | S17 | [E2.3](#e2-3) | Solar farm detection model (hot spots, broken panels) trained with PyTorch on the GPU pool, from data labelled with the design partner's consent, exported to ONNX and stored in the model registry | Recall of at least 90 % and precision of at least 80 % on the design partner's validation set, recorded with the model version; a model below either does not enter the Inspection beta |
| <a id="t2-17"></a>T2.17 | S17 | [E2.3](#e2-3) | Detection worker (ONNX Runtime on GPU): Suspected Defects with kind, position and their thermal and RGB pictures; an Operator's own model can be chosen from its registry | A solar data set gives Suspected Defects placed on the orthomosaic, each with both pictures |
| <a id="t2-18"></a>T2.18 | S17 | [E2.4](#e2-4) | Back office Defect review: list of Suspected Defects, thermal and RGB pictures side by side, confirm | [🎬 UC-020](../functional/use-cases/UC-020-review-the-defects-of-an-inspection.md) steps 1 to 3 pass; the reviewer's name and the time are recorded |
| <a id="t2-19"></a>T2.19 | S17 | [E2.4](#e2-4) | Dismissal with a required reason from the fixed list (not a Defect, duplicate, already known to the Client, image quality too low, other with a comment) | [🎬 UC-020](../functional/use-cases/UC-020-review-the-defects-of-an-inspection.md) A1 passes; "other" without a comment is refused |
| <a id="t2-20"></a>T2.20 | S17 | [E2.6](#e2-6) | Client portal ordering: Site among the Client's Sites, Activity, time slot, acceptance criteria of an Inspection; the Mission is created Requested for the Operator and appears in the Mission studio | [🎬 UC-010](../functional/use-cases/UC-010-order-a-mission-in-the-client-portal.md) and its A1 and A2 pass |
| <a id="t2-21"></a>T2.21 | S18 | [E2.4](#e2-4) | Publication of reviewed Deliverables: the defect list holds Confirmed Defects only; each published Deliverable gets its Evidence record | [🎬 UC-009](../functional/use-cases/UC-009-process-flight-data-into-deliverables.md) steps 4 to 6 and A2, [🎬 UC-020](../functional/use-cases/UC-020-review-the-defects-of-an-inspection.md) step 5 and A2 pass |
| <a id="t2-22"></a>T2.22 | S18 | [E2.6](#e2-6) | Client portal 🗺️ Missions and the Mission page: Squad positions live at 2 Hz, positions only, read only; the Operator can turn the live view off for a Client | [🎬 UC-011](../functional/use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md) steps 1 and 2, A2 and A3 pass; no command reaches the gateway from this role |
| <a id="t2-23"></a>T2.23 | S18 | [E2.6](#e2-6) | Client portal 📦 Deliverables: downloads of Published Deliverables through short-lived signed URLs; others listed without a download | [🎬 UC-011](../functional/use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md) steps 4 and 5 and A6 pass |
| <a id="t2-24"></a>T2.24 | S18 | [E2.4](#e2-4) | Map viewer shared by the Back office and the Client portal: orthomosaic tiles in MapLibre, Defects as a deck.gl layer, 3D model through 3D Tiles (`packages/ts/maps`) | The 9 Confirmed Defects of Les Vignes show on the orthomosaic; the 3D model turns in the browser |
| <a id="t2-25"></a>T2.25 | S18 | [E2.5](#e2-5) | `/v1/evidence/{id}/verify`: recompute the fingerprint, walk the chain, check the receipt; Evidence record: Altered tells the Operator at once in the Back office | An edited Flight log answers Altered and names the failed check |
| <a id="t2-26"></a>T2.26 | S19 | [E2.6](#e2-6) | Client portal 🔏 Evidence tab: choose a file or drop a copy; the fingerprint is computed in a Web Worker, only the fingerprint leaves the browser | [🎬 UC-012](../functional/use-cases/UC-012-verify-the-evidence-record-of-a-flight.md) steps 1 to 5, A1 and A3 pass |
| <a id="t2-27"></a>T2.27 | S19 | [E2.7](#e2-7) | Ground control 📼 Replay: map, timeline, Telemetry, Alerts and the Pilot's decisions, read from the full-rate table; the Flight log is checked against its Evidence record on opening | [🎬 UC-027](../functional/use-cases/UC-027-debrief-a-mission.md) steps 1 and 2 pass on a recorded Flight log |
| <a id="t2-28"></a>T2.28 | S19 | [E2.7](#e2-7) | 📊 Plan against actual: coverage from camera footprints (Rust), gaps, flight time, Drones lost, Re-plans applied | The loss of Delta gives 96 % coverage and two rows of panels as gaps ([🎬 UC-027](../functional/use-cases/UC-027-debrief-a-mission.md) step 3) |
| <a id="t2-29"></a>T2.29 | S19 | [E2.7](#e2-7) | 🔬 Quality checks in the Debrief, with the pass level used for each (Swarm default, Operator, Client) and the areas that fail | [🎬 UC-027](../functional/use-cases/UC-027-debrief-a-mission.md) step 4, step 5 and A2 pass |
| <a id="t2-30"></a>T2.30 | S19 | [E2.9](#e2-9) | Self-hosted beta cell, provisioned with Terraform (decision T43), then Helm and Argo CD from the same charts as staging: CloudNativePG with PostGIS and TimescaleDB, NATS, Valkey, MinIO, GPU node, pgBackRest. C-02 runs on it; after M2 it stays as the second cell, for on-premises rehearsal and as fallback | A restore drill rebuilds the cell in under 1 hour with under 5 minutes of data lost |
| <a id="t2-31"></a>T2.31 | S20 | [E2.7](#e2-7) | Scorecard computed in `missions` for the Inspection criteria (coverage, image overlap, ground resolution, thermal calibration), each with its evidence | Coverage of 96 % against 100 % gives Scorecard: Failed with the gaps proposed for a re-fly |
| <a id="t2-32"></a>T2.32 | S20 | [E2.7](#e2-7) | Mission studio 🧾 Scorecard: review and publish by a named person | [🎬 UC-028](../functional/use-cases/UC-028-assess-a-mission-against-the-request.md) steps 1, 2 and 5 and A1 pass; Swarm records that Léa Martin published it |
| <a id="t2-33"></a>T2.33 | S20 | [E2.7](#e2-7) | Re-fly of the gaps as a new Mission linked to the original; the original Scorecard assessed again with both; a Failed Scorecard sent with an explanation per failed criterion | [🎬 UC-028](../functional/use-cases/UC-028-assess-a-mission-against-the-request.md) steps 3 and 4 and A2 pass with M-2026-0416 |
| <a id="t2-34"></a>T2.34 | S20 | [E2.5](#e2-5) | Anchoring with the qualified timestamping authority of [🤝 P-07](11-hardware-and-partners.md#p-07) (eIDAS, RFC 3161), default for every Operator | Receipts of both beta cells come from the qualified authority; the verification page names it |
| <a id="t2-35"></a>T2.35 | S21 | [E2.7](#e2-7) | An Altered Flight log in the Debrief: the Operator is told at once, the Debrief stays readable and marked, and the Scorecard cannot pass | [🎬 UC-027](../functional/use-cases/UC-027-debrief-a-mission.md) A1 passes |
| <a id="t2-36"></a>T2.36 | S21 | [E2.6](#e2-6) | Client portal 🧾 Scorecards: each criterion, requested and actual, passed or failed; only published Scorecards are shown | [🎬 UC-011](../functional/use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md) step 3, A4 and A5 pass; [🎬 UC-028](../functional/use-cases/UC-028-assess-a-mission-against-the-request.md) step 6 passes |
| <a id="t2-37"></a>T2.37 | S21 | [E2.8](#e2-8) | Mission report template: summary, Mission, Squad, work done against the request, Scorecard, Deliverables, incidents, Evidence records, and the Confirmed Defects with their pictures; rendered to PDF in the Client's language | The report of M-2026-0412 renders in English, French, German and Spanish, with the 9 Confirmed Defects only |
| <a id="t2-38"></a>T2.38 | S21 | [E2.8](#e2-8) | The report as a Deliverable: In review in the Back office, published by a person, with its Evidence record, downloaded in the Client portal | [🎬 UC-022](../functional/use-cases/UC-022-receive-the-mission-report.md) steps 2 to 5 pass without the Report writer |
| <a id="t2-39"></a>T2.39 | S22 | [E2.2](#e2-2) | Photogrammetry tuned on C-02 data: GPU settings, split size, parallel sub-models | 1,000 images give an orthomosaic in under 30 minutes on one GPU worker, measured in the nightly run |
| <a id="t2-40"></a>T2.40 | S22 | [E2.5](#e2-5) | Retention: raw images and video deleted after 90 days (Operator setting), fingerprints kept; Deliverables, evidence files and Flight logs under object lock for 5 years | A raw file past its date is deleted and its record still verifies; a locked file cannot be deleted |
| <a id="t2-41"></a>T2.41 | S22 | [E2.1](#e2-1) | Upload on the weak links of a real Site: bandwidth limit, upload from the rugged edge box after the field laptop leaves, priority to the Flight log | A C-02 upload over a cut 4G link completes later without a duplicate file |
| <a id="t2-42"></a>T2.42 | S22 | [E2.9](#e2-9) | Dashboards and SLO alerts for the processing queue, the GPU pool, the evidence chain and Anchoring ([🩺 Observability](../technical/08-observability.md#dashboards)) | A stalled Anchoring hour raises an alert to the person |
| <a id="t2-43"></a>T2.43 | S23 | [E2.10](#e2-10) | Playwright captures of [🎬 UC-009](../functional/use-cases/UC-009-process-flight-data-into-deliverables.md) and [🎬 UC-020](../functional/use-cases/UC-020-review-the-defects-of-an-inspection.md) in both modes, rows moved to 📸 Screenshot | Visual comparison with the mock-ups passes; the mock-ups are deleted |
| <a id="t2-44"></a>T2.44 | S23 | [E2.10](#e2-10) | Captures of [🎬 UC-010](../functional/use-cases/UC-010-order-a-mission-in-the-client-portal.md), [🎬 UC-011](../functional/use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md), [🎬 UC-012](../functional/use-cases/UC-012-verify-the-evidence-record-of-a-flight.md) and [🎬 UC-015](../functional/use-cases/UC-015-invite-a-client-to-the-client-portal.md) | Same as T2.43 |
| <a id="t2-45"></a>T2.45 | S23 | [E2.10](#e2-10) | Captures of [🎬 UC-027](../functional/use-cases/UC-027-debrief-a-mission.md) and [🎬 UC-028](../functional/use-cases/UC-028-assess-a-mission-against-the-request.md) | Same as T2.43 |
| <a id="t2-46"></a>T2.46 | S23 | [E2.9](#e2-9) | Nightly load test extended with k6 Client portal viewers at 2 Hz and the REST lists of Deliverables, Defects and Scorecards | Reads p95 under 100 ms and writes under 250 ms inside the cell; Telemetry to a Client portal under 400 ms p95 |
| <a id="t2-47"></a>T2.47 | S24 | [E2.9](#e2-9) | Penetration test before Inspection goes live ([🔐 Supply chain and testing](../technical/06-security.md#supply-chain)), and its fixes | No high or critical issue left open |
| <a id="t2-48"></a>T2.48 | S24 | [E2.9](#e2-9) | Isolation suite in CI: every new endpoint called as another Operator, another Client and a Site agent | Every call answers not found or forbidden; the suite runs on every pull request |
| <a id="t2-49"></a>T2.49 | S24 | [E2.9](#e2-9) | [OVHcloud](../technical/09-deployment.md#providers) cell opened early for the design partner: infrastructure in Terraform (decision T43), Managed Kubernetes and Object Storage, then Helm and Argo CD; the design partner's Operator moved there from the self-hosted beta cell in a planned window; beta release with release notes in four languages, the C-02 Missions kept as reference data | The design partner signs in on the OVHcloud cell and finds its C-02 Missions with their Deliverables and Evidence records; both cells pass the restore drill |
| <a id="t2-50"></a>T2.50 | S24 | [E2.10](#e2-10) | Exit check: every criterion of [🚪 Exit criteria](#exit) run and recorded, fixes from the C-02 debrief | Every box below is ticked |

## <a id="demo"></a>🎤 Demo

Given to the design partner on 3 Dec 2027, the last day of S24 and of C-02, with the sample cast of the [🎨 visual identity](../visual-identity.md) on the OVHcloud cell opened in S24. The flight part replays the Flight log and data of one of the first real Squad Missions of C-02 (4 X500, one Pilot), so the demonstration does not depend on the weather.

| Cast | Plays |
| --- | --- |
| Aerowing Services | The [🗃️ Operator](../glossary.md#ent-operator) |
| Sam Carter | The [👤 Pilot](../glossary.md#per-pilot) |
| Léa Martin | The [👤 Mission planner](../glossary.md#per-mission-planner) |
| Priya Shah of Helio Energy | The [👤 Client](../glossary.md#per-client) |
| Les Vignes solar farm | The [🗃️ Site](../glossary.md#ent-site) |
| Alpha (thermal camera), Bravo (RGB camera), Charlie (zoom camera) and Delta, all X500 | The [🗃️ Squad](../glossary.md#ent-squad) of M-2026-0412 Inspection of Les Vignes |

1. **Invite.** Léa Martin invites Priya Shah from 👥 People. Priya opens the invitation, chooses English, and sees only the Missions of Helio Energy; a link to M-2026-0414 Night patrol of Northgate answers not found ([🎬 UC-015](../functional/use-cases/UC-015-invite-a-client-to-the-client-portal.md)).
2. **Order.** Priya orders an Inspection of Les Vignes for 3 December, 10:00 to 12:00, with 100 % coverage and image overlap of at least 75 %. The Mission is Requested and appears in Léa's Mission studio ([🎬 UC-010](../functional/use-cases/UC-010-order-a-mission-in-the-client-portal.md)).
3. **Fly.** Léa plans M-2026-0412 (P1); Sam Carter runs the Pre-flight check and launches the Squad of 4 Drones, as in the first real Squad flights of C-02. Priya follows the Squad on the map, positions only, with no command. Delta's Link is lost at 10:31, the Re-plan is approved at 10:33, the Squad lands at 10:52 ([🎬 UC-011](../functional/use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md)).
4. **Debrief.** Sam opens the Debrief: the Flight log matches its Evidence record, the Replay shows each event, the plan against actual shows 96 % coverage with rows 14 and 15 as gaps, and the gap check fails ([🎬 UC-027](../functional/use-cases/UC-027-debrief-a-mission.md)).
5. **Process.** The data reaches the OVHcloud cell and passes its Quality checks; the orthomosaic and the 3D model are built, then In review. The timer shows the budget for 1,000 images ([🎬 UC-009](../functional/use-cases/UC-009-process-flight-data-into-deliverables.md)).
6. **Review Defects.** Detection has marked 12 Suspected Defects. Léa compares thermal and RGB pictures, confirms 9 and dismisses 3, one of them a sun reflection, with a reason from the list ([🎬 UC-020](../functional/use-cases/UC-020-review-the-defects-of-an-inspection.md)).
7. **Assess.** The Scorecard is Failed at 96 %. Léa plans the re-fly M-2026-0416 for 14:00, linked to M-2026-0412; once it is flown and debriefed, the Scorecard is assessed again with both and is Passed. Léa publishes it ([🎬 UC-028](../functional/use-cases/UC-028-assess-a-mission-against-the-request.md)).
8. **Deliver.** Léa publishes the orthomosaic, the 3D model, the defect list with 9 Defects, and the report built from the template. Priya reads the Scorecard, then downloads the Deliverables and the report ([🎬 UC-011](../functional/use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md), [🎬 UC-022](../functional/use-cases/UC-022-receive-the-mission-report.md)).
9. **Verify.** Priya verifies the Flight log in the 🔏 Evidence tab: Evidence record: Verified, with its Anchoring date and the timestamping authority. She drops an edited copy: Evidence record: Altered, and Aerowing Services is told at once ([🎬 UC-012](../functional/use-cases/UC-012-verify-the-evidence-record-of-a-flight.md)).

After the demonstration, milestone M2 ([🏆 Milestones](README.md#milestones)) is reached when the design partner's own Pilots fly a real Mission for one of its Clients and deliver an orthomosaic, Defects and a Scorecard, by 17 Dec 2027 (S25, the first sprint of P3).

## <a id="exit"></a>🚪 Exit criteria

**Acceptance criteria** of the features ([📘 FS-007](../functional/features/FS-007-data-processing-and-deliverables.md#acceptance), [📘 FS-008](../functional/features/FS-008-client-portal.md#acceptance), [📘 FS-009](../functional/features/FS-009-evidence-ledger-and-anchoring.md#acceptance), [📘 FS-016](../functional/features/FS-016-inspection.md#acceptance), [📘 FS-022](../functional/features/FS-022-debrief-and-assessment.md#acceptance), [📘 FS-019](../functional/features/FS-019-mission-reports.md#acceptance)), each run as a Playwright or API test on the OVHcloud cell:

- [ ] [📘 FS-007](../functional/features/FS-007-data-processing-and-deliverables.md#acceptance) AC-1: a completed Inspection's orthomosaic goes Processing, then Published once the Mission planner publishes it.
- [ ] [📘 FS-008](../functional/features/FS-008-client-portal.md#acceptance) AC-1: a Client of Helio Energy orders an Inspection of Les Vignes and the Mission is Requested for the Operator.
- [ ] [📘 FS-008](../functional/features/FS-008-client-portal.md#acceptance) AC-2: the Client sees the Squad of a Mission Flying on the map, with no command.
- [ ] [📘 FS-009](../functional/features/FS-009-evidence-ledger-and-anchoring.md#acceptance) AC-1: an unchanged Flight log shows Evidence record: Verified with its Anchoring date.
- [ ] [📘 FS-009](../functional/features/FS-009-evidence-ledger-and-anchoring.md#acceptance) AC-2: a Flight log edited after closing shows Evidence record: Altered.
- [ ] [📘 FS-016](../functional/features/FS-016-inspection.md#acceptance) AC-1: of 12 Suspected Defects, the 9 confirmed are the only ones in the Client's defect list.
- [ ] [📘 FS-022](../functional/features/FS-022-debrief-and-assessment.md#acceptance) AC-1: the Debrief of a completed Inspection shows the Replay, the plan against actual and the Quality checks.
- [ ] [📘 FS-022](../functional/features/FS-022-debrief-and-assessment.md#acceptance) AC-2: 96 % coverage against 100 % gives a Failed Scorecard with the gaps proposed for a re-fly.
- [ ] [📘 FS-022](../functional/features/FS-022-debrief-and-assessment.md#acceptance) AC-3: a reviewed Scorecard published by the Mission planner is seen by the Client.
- [ ] [📘 FS-019](../functional/features/FS-019-mission-reports.md#acceptance) AC-1, without the AI part: a report built from the template and published by the Mission planner reaches the Client with its Evidence record. The drafting by the Report writer is checked in P5.
- [ ] The solar detection model reaches recall of at least 90 % and precision of at least 80 % on the design partner's validation set ([T2.16](#t2-16)).
- [ ] The first real Squad flight is flown in C-02: 4 X500 under one Pilot, under [🏛️ G-05](09-regulatory-track.md#g-05), with the Fail-safe drills of the Squad passed at the start of the campaign. If G-05 is late, this box moves to the first flight day after its grant.
- [ ] [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md#acceptance) AC-2 run again on the new app: an invited Client who chose German sees every screen of the Client portal in German.

**Budgets** ([🚀 Budgets](../technical/07-scalability.md#budgets), [🖥️ Front-end budgets](../technical/10-frontends.md#performance)):

- [ ] Orthomosaic of 1,000 images on one GPU worker in under 30 minutes, on C-02 data, in the nightly run.
- [ ] REST inside the OVHcloud cell: p95 under 100 ms for reads and under 250 ms for writes on the Deliverables, Defects, Scorecards and evidence endpoints.
- [ ] Telemetry from the Drone to the Client portal through the cell: p95 under 400 ms.
- [ ] Client portal first load: under 2.5 s to interactive on 4G, under 300 kB of JavaScript for the first route.
- [ ] Each beta cell, self-hosted and OVHcloud, rebuilt from Terraform, GitOps and backups in under 1 hour, with under 5 minutes of data lost, in a restore drill ([🗄️ Backups and recovery](../technical/03-storage.md#backups)).

**Screens, checks and tests**:

- [ ] Every screen row of [🎬 UC-009](../functional/use-cases/UC-009-process-flight-data-into-deliverables.md), [🎬 UC-010](../functional/use-cases/UC-010-order-a-mission-in-the-client-portal.md), [🎬 UC-011](../functional/use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md), [🎬 UC-012](../functional/use-cases/UC-012-verify-the-evidence-record-of-a-flight.md), [🎬 UC-015](../functional/use-cases/UC-015-invite-a-client-to-the-client-portal.md), [🎬 UC-020](../functional/use-cases/UC-020-review-the-defects-of-an-inspection.md), [🎬 UC-027](../functional/use-cases/UC-027-debrief-a-mission.md) and [🎬 UC-028](../functional/use-cases/UC-028-assess-a-mission-against-the-request.md) reads 📸 Screenshot, in light and dark mode.
- [ ] `python3 .claude/skills/write-specs/scripts/specs.py check` prints nothing.
- [ ] The nightly staging load test, extended with Client portal viewers, passes every assertion for 5 nights in a row.
- [ ] The isolation suite (other Operator, other Client, Site agent) passes on every pull request.
- [ ] The evidence chain of every Operator of both beta cells verifies end to end, and every hour since S20 has its Anchoring receipt.
- [ ] The penetration test has no high or critical issue open.
- [ ] Campaign [🛫 C-02](10-flight-test-campaigns.md#c-02) is closed with its report: every Mission processed, debriefed, assessed and published.

## <a id="dependencies"></a>⛓️ Dependencies

| Needs | From | Why |
| --- | --- | --- |
| Keycloak, NATS, PostgreSQL with PostGIS and TimescaleDB, Valkey, the dev cell, the design tokens and the i18n framework | [🛣️ P0: Foundations](01-p0-foundations.md) | Every new service and app of P2 is built on them |
| Flight log, Mission design for Inspection, Ground control, Pre-flight check, Re-plans, Fleet and Authorisations in the Back office | [🛣️ P1: First flight](02-p1-first-flight.md) | P2 starts where a Squad has landed |
| The design-partner Operator | [🤝 P-01](11-hardware-and-partners.md#p-01), signed S12 (M1b) | Labelled data with its consent, the first Operator of both beta cells, the demonstration audience |
| The solar farm Client Site | [🤝 P-02](11-hardware-and-partners.md#p-02), S18 | The Site of C-02 and of the M2 Mission |
| The timestamping authority | [🤝 P-07](11-hardware-and-partners.md#p-07), S20 | Qualified Anchoring from [T2.34](#t2-34) on |
| Thermal and RGB Payloads | [🤝 H-02](11-hardware-and-partners.md#h-02), S08 | Mixed Squads and the solar detection model |
| 4 X500 PX4 with RTK and the rugged edge box | [🤝 H-01](11-hardware-and-partners.md#h-01), S06; [🤝 H-03](11-hardware-and-partners.md#h-03), S12 | The Squad of C-02 and uploads from the Site |
| Specific category Authorisation | [🏛️ G-05](09-regulatory-track.md#g-05), S20 | The first real Squad flight (4 X500, one Pilot) and every Squad flight of C-02 |
| An OVHcloud account opened early | [🤝 P-06](11-hardware-and-partners.md#p-06), production cells from S46 | The OVHcloud cell of the design partner, opened in S24 ahead of the other production cells |
| Airspace and U-space checks of the solar farm | [🏛️ G-06](09-regulatory-track.md#g-06), by S18 | Two sprints before C-02 |
| The first campaign's data | [🛫 C-01](10-flight-test-campaigns.md#c-01), S10 to S12 | Single-Drone flights in the Open category: test data sets for processing and the Debrief before C-02 |
| Campaign at the solar farm | [🛫 C-02](10-flight-test-campaigns.md#c-02), S20 to S24 | Real data, real Site, real budget measurements |

P2 also prepares P3: the Dock vendor is chosen in S22 ([🤝 H-05](11-hardware-and-partners.md#h-05)) and the 2 Parrot ANAFI USA arrive in S24 ([🤝 H-04](11-hardware-and-partners.md#h-04)).

## <a id="risks"></a>🎲 Risks

| Risk | Why it matters in P2 | Response in P2 |
| --- | --- | --- |
| [🎲 R-02](12-risks.md#r-02) Specific category Authorisation late | C-02 needs [🏛️ G-05](09-regulatory-track.md#g-05) by 8 Oct 2027 | Fall back on the [regulatory track](09-regulatory-track.md#dependencies): C-02 flies in the Open category with one Drone at a time, in visual line of sight, and the first real Squad flight waits for G-05; the software scope of P2 does not change |
| [🎲 R-06](12-risks.md#r-06) Photogrammetry quality or speed | The orthomosaic budget and the Defects shown to the Client depend on it | Measure from S15 on C-01 data, not at the end; [T2.12](#t2-12) splits large Sites; [T2.39](#t2-39) is reserved for tuning; the processing interface stays open for another photogrammetry engine; detection is reviewed by a person anyway ([📏 BR-020](../functional/business-rules/BR-020-defects-confirmed-by-a-person.md)) |
| [🎲 R-05](12-risks.md#r-05) Design partner lost | The beta, the training data and M2 depend on it | Show progress to the partner every sprint from S16 (invitation, then ordering); if the partner leaves, the person flies the beta Missions with a partner Site directly, as the [risks register](12-risks.md#r-05) plans |
| [🎲 R-07](12-risks.md#r-07) Weather and seasons | C-02 runs from late September to early December | Two spare weeks inside C-02; Simulator rehearsals before each flight day; the demonstration replays recorded data |
| [🎲 R-01](12-risks.md#r-01) Review bottleneck | 50 tickets, and four sprints with flight days | Fewer tickets during C-02; agents prepare screens and tests in parallel so that a ticket arrives complete; review the riskiest tickets (evidence, isolation) first |
| [🎲 R-10](12-risks.md#r-10) Security incident or key compromise | A leaked signing key would make Evidence records worthless | Keys only in the vault transit engine; penetration test [T2.47](#t2-47); every verification checks the signature and the chain, not only the fingerprint |
| [🎲 R-14](12-risks.md#r-14) GDPR complaint about video | Inspection images can show people on the Site | Raw images deleted after 90 days ([T2.40](#t2-40)); a data processing register per Operator; Client-visible video waits for face blurring in P3 |
| [🎲 R-11](12-risks.md#r-11) Crash or hardware loss in tests | C-02 is the first campaign on a Client's Site and the first real Squad flight | Every Fail-safe tested again in the Simulator before each flight day; a Mission can fly with one Drone fewer, and the coverage planner shares its area |
| [🎲 R-08](12-risks.md#r-08) Scope too large for 24 months | P2 is the largest phase | AI drafting moved to P5, on-premises processing and blockchain Anchoring to P7, live video for Clients to P3 |

## <a id="work-split"></a>🧑‍💻 Work split

| The person | The Claude Code agents, in parallel |
| --- | --- |
| Reviews and merges about 5 tickets a sprint, 4 during C-02, the evidence and isolation tickets first | Split each ticket into tasks that run at once: service code, Rust parts, tests, migrations, OpenAPI and the generated client, screens against their mock-ups, translations, documentation |
| Checks the solar model against its threshold (recall of at least 90 % and precision of at least 80 % on the design partner's validation set), and labels or checks the training data with the agents' pre-labels | Prepare the labelling tools, the training and evaluation scripts, and the ONNX export |
| Decides the wording of the report template with the design partner, in four languages | Render the template and keep its golden files up to date |
| Flies C-02 as the Pilot: flight days, Fail-safe tests, the C-02 report | Turn every field issue of C-02 into a reproducible test before it is fixed |
| Runs the partners and the regulator: [🤝 P-01](11-hardware-and-partners.md#p-01), [🤝 P-02](11-hardware-and-partners.md#p-02), [🤝 P-07](11-hardware-and-partners.md#p-07), [🏛️ G-05](09-regulatory-track.md#g-05), [🏛️ G-06](09-regulatory-track.md#g-06) | Keep the C-02 checklists, Site data and Geofence ready in the Mission studio |
| Chooses the Dock vendor for P3 in S22 ([🤝 H-05](11-hardware-and-partners.md#h-05)) | Compare the vendors' interfaces against the Drone adapter interface and write the comparison |
| Gives the demonstration and runs the exit check | Run the load tests, the restore drill, the Playwright captures and `specs.py check` every night, and report what fails |

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ P1: First flight](02-p1-first-flight.md) · 📄 **Page 109 / 120** · [P3: Patrol ▶️](04-p3-patrol.md)
<!-- /spec:nav-bottom -->
