# 🛣️ P7: Scale and reach

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ P6: Light shows](07-p6-light-shows.md) · 📄 **Page 114 / 120** · [Regulatory track ▶️](09-regulatory-track.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Sprints:** S45 to S52 · **Dates:** 11 Sep to 29 Dec 2028 · **Tickets:** about 30

> [!NOTE]
> P7 takes Swarm from betas to general availability: cells proven at target load, the OVHcloud cell of the design partner hardened to target size and a Scaleway cell beside it, a US self-hosted cell, the on-premises bundle installed once, edge appliances updated in rings, DJI and Skydio Drone adapters and the blockchain Anchoring option; it comes last because it hardens and widens what P0 to P6 built, and every Activity must already fly before it can be validated for release.

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

Reach milestone **M7, general availability, on 29 December 2028 (S52)**: Inspection and Patrol sold in the EU cloud cells, a full cell at target load in staging, and the on-premises bundle installed once. On the way, P7 closes the parts of the features that only matter at scale or for more [🗃️ Operators](../glossary.md#ent-operator):

- **Cells at target load.** One cell holds 200 Missions in flight, 100,000 Telemetry frames per second, 5,000 live viewers and about 1,000 Operators, and every budget holds as an assertion of the nightly load test ([🚀 Scalability and performance](../technical/07-scalability.md#cells)).
- **Production in the EU.** The OVHcloud cell opened in S24 (P2) for the design partner, beside a self-hosted beta cell, is brought to target size for production, and a Scaleway cell is added. Every cell's infrastructure is provisioned with Terraform (decision T43), then deployed with Helm and Argo CD, released in waves after a canary cell, with the global layer (Keycloak, Operator directory, routing of each Operator to its cell) in two EU regions, active and standby ([🚢 Deployment](../technical/09-deployment.md#providers)).
- **Operator isolation at scale.** No person ever sees another Operator's data, across a cell of about 1,000 Operators, across cells and on premises ([📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md)).
- **Reach.** A US self-hosted cell for testing, with US Operators' data kept in US cells; the signed on-premises bundle for one company; the [⚙️ Drone adapters](../glossary.md#sys-drone-adapter) for DJI and Skydio Drones; the public blockchain option of [🔤 Anchoring](../glossary.md#term-anchoring).
- **Release.** The validation flights of [🛫 C-07](10-flight-test-campaigns.md#c-07) fly one Mission per [🔤 Activity](../glossary.md#term-activity) on the release candidate; Agriculture and Light shows stay in beta after M7.

## <a id="scope"></a>🧺 Scope

**📘 Features**

| Feature | Delivered in P7 | Acceptance criteria closed |
| --- | --- | --- |
| [📘 FS-012: Operators, deployment and languages](../functional/features/FS-012-operators-deployment-and-languages.md) | Operators placed in production cells, moved between cells, isolated at scale; the on-premises deployment; every screen in four languages checked before release | AC-1, AC-2, AC-3, in the production cells and on premises |
| [📘 FS-011: Drone adapters](../functional/features/FS-011-drone-adapters.md) | The DJI and Skydio Drone adapters, after MAVLink (P1) and Parrot (P3) | AC-1, for the Drone models Matrice 4TD and X10 |
| [📘 FS-009: Evidence ledger and Anchoring](../functional/features/FS-009-evidence-ledger-and-anchoring.md) | The public blockchain option, through an aggregator, chosen per Operator | AC-1, AC-2, with a blockchain receipt |

**🎬 Use cases**

| Use case | In P7 | Screens |
| --- | --- | --- |
| [🎬 UC-014: Connect a new Drone model](../functional/use-cases/UC-014-connect-a-new-drone-model.md) | Run for the Matrice 4TD (DJI) and the X10 (Skydio) | Kept as 📸 Screenshot; the steps of the vendor test are checked against them |
| [🎬 UC-029: Create an Operator](../functional/use-cases/UC-029-create-an-operator.md) | In the production cells, in the US cell, and on premises by the company's IT administrator | Kept as 📸 Screenshot; re-captured if the cell choice changes the screen |
| [🎬 UC-012: Verify the Evidence record of a flight](../functional/use-cases/UC-012-verify-the-evidence-record-of-a-flight.md) | With a blockchain receipt as well as a timestamping authority receipt | A2, OK and KO re-captured with a blockchain receipt |
| [🎬 UC-015: Invite a Client to the Client portal](../functional/use-cases/UC-015-invite-a-client-to-the-client-portal.md) | Run in every production cell for FS-012 AC-1 and AC-2 | Kept as 📸 Screenshot |

**📏 Business rules**

| Rule | In P7 |
| --- | --- |
| [📏 BR-008: Operator isolation](../functional/business-rules/BR-008-operator-isolation.md) | At scale: about 1,000 Operators per cell, several cells, the global layer, on premises |
| [📏 BR-015: Approved Drone models only](../functional/business-rules/BR-015-approved-drone-models-only.md) | For the DJI and Skydio Drone models, and again for each new firmware |
| [📏 BR-009: Evidence integrity](../functional/business-rules/BR-009-evidence-integrity.md) | With the blockchain Anchoring option |
| [📏 BR-010: Valid Authorisation for the Jurisdiction](../functional/business-rules/BR-010-valid-authorisation-for-the-jurisdiction.md) | US Authorisations recorded like EU ones, for the US cell |
| [📏 BR-017: Every screen in four languages](../functional/business-rules/BR-017-every-screen-in-four-languages.md) | Audited on every screen and every [🔤 Notification](../glossary.md#term-notification) before release |
| [📏 BR-014: Simulation isolation](../functional/business-rules/BR-014-simulation-isolation.md) | Load tests at target in staging, never against a production cell |

**🛠️ Technical pages**

| Page | What P7 builds from it |
| --- | --- |
| [🚀 Scalability and performance: targets](../technical/07-scalability.md#targets) | The platform targets the cells are sized for |
| [🚀 Scalability and performance: cells](../technical/07-scalability.md#cells) | The limits of one cell, placement of Operators, moving an Operator between cells |
| [🚀 Scalability and performance: budgets](../technical/07-scalability.md#budgets) | REST, Telemetry through the cell, video, cell rebuild |
| [🚀 Scalability and performance: load tests](../technical/07-scalability.md#load-tests) | The nightly full cell at target load, chaos |
| [🚀 Scalability and performance: techniques](../technical/07-scalability.md#techniques) | Batched `COPY`, PgBouncer, replicas, the hot paths to tune at target |
| [🏗️ Architecture: cells and the global layer](../technical/01-architecture.md#cells) | Global layer, cells, edges |
| [🚢 Deployment: where it runs](../technical/09-deployment.md#providers) | OVHcloud, Scaleway, self-hosted k3s with MinIO; each cell provisioned with Terraform (decision T43) |
| [🚢 Deployment: delivery](../technical/09-deployment.md#delivery) | Helm umbrella chart per cell, KEDA, Argo CD, waves, expand and contract migrations |
| [🚢 Deployment: edge appliance](../technical/09-deployment.md#edge) | Signed updates over the air, in rings, never during a Mission |
| [🚢 Deployment: on-premises bundle](../technical/09-deployment.md#on-premises) | Signed offline bundle, sizing guide |
| [🚢 Deployment: environments](../technical/09-deployment.md#environments) | Staging at target, production cells, simulation |
| [🔐 Security: roles and Operator isolation](../technical/06-security.md#authorisation) | Isolation tests at scale |
| [🔐 Security: privacy and compliance](../technical/06-security.md#privacy) | Residency: EU Operators in EU cells, US Operators in US cells |
| [🔐 Security: secrets and keys](../technical/06-security.md#secrets) | Signing keys of each new cell, on premises included |
| [🔐 Security: supply chain](../technical/06-security.md#supply-chain) | Signed images, bundle and edge appliance |
| [🔩 Engine and services: Drone adapters](../technical/04-engine.md#adapters) | DJI and Skydio sidecars on the adapter interface |
| [🔩 Engine and services: evidence](../technical/04-engine.md#evidence) | Hourly Merkle root anchored on a public blockchain through an aggregator |
| [🗄️ Storage: backups and recovery](../technical/03-storage.md#backups) | Restore drills at target size, RPO 5 minutes |
| [🩺 Observability: SLOs](../technical/08-observability.md#slos) and [dashboards](../technical/08-observability.md#dashboards) | Cross-cell views in Mimir, burn-rate alerts, on-call rota |

## <a id="epics"></a>🪜 Epics

| ID | Epic | Delivers | Where | Tickets | Parallel tasks for the agents |
| --- | --- | --- | --- | --- | --- |
| E7.1 | Cell at target load | Cell limits and budgets of [🚀 Scalability and performance](../technical/07-scalability.md#budgets); M7 proof "a full cell at target load in staging" | `tests/` (load: k6, simulated fleets; chaos), `backend/apps/simulator`, staging cell, `infra/` | 4: T7.01, T7.20, T7.21, T7.24 | Load harness for 200 Missions (synthetic Drones for volume, PX4 SITL for a sample); k6 scenarios for 5,000 WebSocket clients and REST; video viewers on the SFU; restore drill script; chaos scenarios; SLO dashboards |
| E7.2 | EU production cells and global layer | [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md) in the cloud | `infra/` (Terraform per provider, umbrella chart with values per provider), `infra/environments` (Argo CD), Keycloak, Operator directory | 5: T7.03 to T7.07 | Terraform sizing of the OVHcloud cell; Terraform for the Scaleway cell; Helm values per provider; CloudNativePG with PostGIS and TimescaleDB; global layer active and standby; waves and rollback; cell move procedure |
| E7.3 | Operators at scale | [📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md), [📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md); [🎬 UC-029](../functional/use-cases/UC-029-create-an-operator.md) and [🎬 UC-015](../functional/use-cases/UC-015-invite-a-client-to-the-client-portal.md) in production | `backend/apps/gateway`, `backend/apps/missions`, `frontend/apps/back-office`, `frontend/apps/client-portal`, `frontend/packages` (`i18n`) | 3: T7.02, T7.22, T7.23 | Isolation suite with 1,000 synthetic Operators; cross-cell probes; translation audit per front end and for the `notifier` texts; onboarding runbook |
| E7.4 | US self-hosted cell | Residency of [🔐 Security](../technical/06-security.md#privacy); [📏 BR-010](../functional/business-rules/BR-010-valid-authorisation-for-the-jurisdiction.md) for US Authorisations | `infra/` (k3s, MinIO), `backend/apps/missions` (US Jurisdiction), global layer routing | 3: T7.11 to T7.13 | k3s cell from the same charts; region check in routing; US Jurisdiction and Authorisation types from [🏛️ G-09](09-regulatory-track.md#g-09) |
| E7.5 | On-premises bundle | [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md) on premises; M7 proof "the on-premises bundle installed once" | `infra/` (k3s bundle), every image, base maps, detection models, the open-weight model | 3: T7.15 to T7.17 | Bundle builder; signature and verification; offline installer; sizing guide; install on [🤝 H-08](11-hardware-and-partners.md#h-08) |
| E7.6 | Edge appliance rings | Updates of every edge, in rings | `infra/` (edge appliance), `frontend/apps/desktop` (Tauri updater), `backend/apps/flight-engine` | 1: T7.14 | Signed update channel; no update during a Mission; rollback to the previous version; rings internal, early Operators, everyone |
| E7.7 | DJI and Skydio Drone adapters | [📘 FS-011](../functional/features/FS-011-drone-adapters.md) AC-1; [🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md); [📏 BR-015](../functional/business-rules/BR-015-approved-drone-models-only.md) | `backend/apps/flight-engine` (sidecars over a local socket, like Parrot), `backend/apps/fleet`, `backend/apps/simulator` | 4: T7.08 to T7.10, T7.25 | DJI sidecar; Skydio sidecar; compatibility suite per family; Drone model data for Matrice 4TD and X10; real test flights |
| E7.8 | Blockchain Anchoring | [📘 FS-009](../functional/features/FS-009-evidence-ledger-and-anchoring.md) AC-1 and AC-2 with the blockchain option; [📏 BR-009](../functional/business-rules/BR-009-evidence-integrity.md); [🎬 UC-012](../functional/use-cases/UC-012-verify-the-evidence-record-of-a-flight.md) | `backend/apps/evidence`, `frontend/apps/client-portal`, `frontend/apps/back-office` | 2: T7.18, T7.19 | Aggregator client; receipt storage and checking; Operator setting; verification page with a blockchain receipt |
| E7.9 | General availability | Milestone M7 | Every service and front end, `infra/`, `docs/specs` | 5: T7.26 to T7.30 | Fixes from C-07 per Activity; release candidate scans and signatures; release notes; last screenshots; `specs.py check` |

## <a id="sprints"></a>🗓️ Sprint plan

P7 shares S45 to S48 with [🛣️ P6: Light shows](07-p6-light-shows.md), which takes 4 tickets in each of them for the M6 show, and with the core of the Assistant of [🛣️ P5](06-p5-ai-agents.md), 2 tickets in each of S45 to S48, so P7 starts with 2 tickets per sprint and takes the whole capacity from S49. Across the three phases, S45 to S48 carry about 8 merged tickets each, S49 and S50 about 6, and S51 and S52 carry 5: one more than the usual capacity, see [🎲 R-01](12-risks.md#r-01) below.

| Sprint | Dates | Tickets | Sprint goal | What can be shown |
| --- | --- | --- | --- | --- |
| S45 | 11 to 22 Sep 2028 | T7.01 Staging cell at target: 200 Missions, k6 for 5,000 WebSocket clients, 500 video viewers, budgets as assertions · T7.02 Operator isolation suite at scale | The nightly run measures the whole cell, not only the edge, and probes it for leaks between Operators | The first nightly report at target, with the budgets it misses listed; 1,000 Operators probed for leaks, none found |
| S46 | 25 Sep to 6 Oct 2028 | T7.03 OVHcloud cell hardened to target size for production, canary · T7.04 Global layer in two EU regions, active and standby | The cell the design partner has flown from since S24 is ready for general availability, behind the global layer | The OVHcloud cell resized by Terraform without stopping the design partner; Aerowing Services routed by the Operator directory to it |
| S47 | 9 to 20 Oct 2028 | T7.05 Scaleway production cell, created with Terraform · T7.06 Release waves across cells, stopped and rolled back on an SLO burn | Two providers, one release process | A release that burns its SLO in the canary cell stops and rolls back before the second cell |
| S48 | 23 Oct to 3 Nov 2028 | T7.07 Move an Operator between cells in a planned window · T7.08 DJI Drone adapter sidecar | Operators can grow between cells; the first vendor sidecar after Parrot | An Operator moved from the OVHcloud cell to the Scaleway cell between two flights; the Matrice 4TD answering every command of the adapter interface in its contract tests |
| S49 | 6 to 17 Nov 2028 | T7.09 Skydio Drone adapter sidecar · T7.10 Compatibility suites for the vendor adapters, firmware re-approval · T7.11 US self-hosted cell on k3s and MinIO · T7.12 Residency: US Operators in US cells · T7.13 US Jurisdiction in Authorisations, from [🏛️ G-09](09-regulatory-track.md#g-09) · T7.14 Edge appliance rings | Reach: more Drone families, a second region, safe edge updates | Matrice 4TD and X10 pass the compatibility test in the Simulator where their Drone model allows it; a US test Operator created in the US cell |
| S50 | 20 Nov to 1 Dec 2028 | T7.15 Signed offline bundle · T7.16 Bundle installer, verification and updates · T7.17 On-premises install on [🤝 H-08](11-hardware-and-partners.md#h-08) · T7.18 Blockchain Anchoring through an aggregator · T7.19 Anchoring choice per Operator, verification with a blockchain receipt · T7.20 Cell rebuild and restore drill at target | The bundle installed once; evidence anchored either way; recovery proven | The company's IT administrator, as Swarm administrator, creates its Operator on the H-08 install; a Flight log verified against a blockchain receipt |
| S51 | 4 to 15 Dec 2028 | T7.21 Chaos at target load · T7.22 Four-language audit of every screen and Notification · T7.23 Operator onboarding in the production cells · T7.24 Cross-cell SLO dashboards, on-call alerting · T7.25 Real compatibility flights of Matrice 4TD and X10 | The release candidate is complete and hardened | C-07 flights of the release candidate; a pod killed, an edge Link cut and a database failover during the nightly run at target, all recovered |
| S52 | 18 to 29 Dec 2028 | T7.26 C-07 fixes, Inspection and Patrol · T7.27 C-07 fixes, Agriculture and Light show · T7.28 Release candidate: Trivy, OSV-Scanner, SBOM, cosign signatures · T7.29 General availability release, cells in waves, edges in rings · T7.30 Last screens to 📸 Screenshot, `specs.py check` | General availability | The M7 demonstration |

**Total: 30 tickets** (S45 2, S46 2, S47 2, S48 2, S49 6, S50 6, S51 5, S52 5).

**Tickets in detail**

| Ticket | Sprint | Epic | What it does | Done when |
| --- | --- | --- | --- | --- |
| T7.01 | S45 | E7.1 | Staging cell at target: 200 Missions of simulated Drones (synthetic Rust Drones for volume, PX4 SITL for a sample), k6 for REST and 5,000 WebSocket clients, 500 video viewers on the SFU; every budget an assertion | The first nightly report at target exists; each missed budget has its own ticket |
| T7.02 | S45 | E7.3 | Isolation suite at scale: 1,000 synthetic Operators in one cell; every REST resource, WebSocket stream and NATS subject probed with another Operator's identity, also across cells | Every probe answers Not found and the attempt is logged ([📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md) example 2) |
| T7.03 | S46 | E7.2 | Production hardening of the OVHcloud cell opened in S24: Terraform brings Managed Kubernetes, its node pools, the GPU pool and Object Storage to target size; CloudNativePG with PostGIS, TimescaleDB and 2 replicas, NATS, Valkey and KEDA through the umbrella chart; its Argo CD application marked as the canary | A simulated Mission flies end to end in the resized cell for a test Operator, and the design partner's data and flights are untouched |
| T7.04 | S46 | E7.2 | Global layer: Keycloak and the Operator directory in two EU regions, active and standby; the routing of each Operator to its cell | Sign-in survives a switch to the standby region; each Operator resolves to exactly one cell |
| T7.05 | S47 | E7.2 | Scaleway cell: Kapsule and Object Storage created with Terraform, then the same umbrella chart through Helm and Argo CD; only the Terraform variables and the Helm values differ | The end-to-end test of T7.03 passes unchanged |
| T7.06 | S47 | E7.2 | Release waves: the canary cell first, then the other cells; an SLO burn during a wave stops it and rolls back | A faulty build is stopped in the canary cell and never reaches the second cell |
| T7.07 | S48 | E7.2 | Move an Operator between cells during a planned window: data copied, edges re-pointed between flights | After the move, the Operator's Flight logs show Evidence record: Verified and its edges fly against the new cell |
| T7.08 | S48 | E7.7 | DJI Drone adapter: a sidecar using the vendor's SDK or cloud API, bridged to the flight engine over a local socket like the Parrot one; the Matrice 4TD as a Drone model | Every command of the adapter interface is covered by a contract test |
| T7.09 | S49 | E7.7 | Skydio Drone adapter on the same pattern; the X10 as a Drone model | Every command of the adapter interface is covered by a contract test |
| T7.10 | S49 | E7.7 | Compatibility suites for both families; the firmware version recorded with the approval; a new firmware sets the Drone model back to Not approved | UC-014 A2 and A4 are automated for both families |
| T7.11 | S49 | E7.4 | US self-hosted cell on k3s with MinIO, its servers provisioned with Terraform, then the same charts through Helm and Argo CD | A simulated Mission flies end to end in the US cell |
| T7.12 | S49 | E7.4 | Residency: an Operator under a US Jurisdiction is placed only in a US cell, an EU Operator only in an EU cell; only fingerprints leave a region, to the Anchoring service | A placement across regions is refused; no cell replicates data to another region |
| T7.13 | S49 | E7.4 | The US Jurisdiction and its Authorisations recorded like EU ones, from the study of [🏛️ G-09](09-regulatory-track.md#g-09) | A US Mission without a valid Authorisation cannot pass its Pre-flight check ([📏 BR-010](../functional/business-rules/BR-010-valid-authorisation-for-the-jurisdiction.md)) |
| T7.14 | S49 | E7.6 | Edge appliance rings: signed updates over the air, never during a Mission, the previous version kept for rollback; rings internal, early Operators, everyone | An update that arrives during a Mission waits for the last landing; a bad version rolls back |
| T7.15 | S50 | E7.5 | Signed offline bundle: images, charts, base maps (PMTiles), detection models, the open-weight model, with its SBOM | The bundle verifies without network; a modified bundle is refused |
| T7.16 | S50 | E7.5 | Installer on k3s or the company's Kubernetes, updates by new bundle, the sizing guide (3 nodes for up to 20 Missions in flight, one GPU server), the same observability stack as the cloud | Install and update succeed on a clean cluster without network |
| T7.17 | S50 | E7.5 | Test install on [🤝 H-08](11-hardware-and-partners.md#h-08): the company's IT administrator, as Swarm administrator, creates the Operator ([🎬 UC-029](../functional/use-cases/UC-029-create-an-operator.md)); processing and the open-weight model on its GPU server | The Operator is created; an orthomosaic of 1,000 images takes under 30 minutes; the Mission assistant answers with the open-weight model |
| T7.18 | S50 | E7.8 | Blockchain Anchoring: the hourly Merkle root sent to a public blockchain through the aggregator of [🤝 P-09](11-hardware-and-partners.md#p-09); the receipt stored with the records | Every hour of a week in staging has its receipt |
| T7.19 | S50 | E7.8 | The Anchoring choice per Operator in the Back office (timestamping authority by default, blockchain, none); verification checks either receipt; an Altered record tells the Operator at once | FS-009 AC-1 and AC-2 pass with both kinds of receipt |
| T7.20 | S50 | E7.1 | Cell rebuild and restore drill at target size: point-in-time recovery with pgBackRest, object storage from its replica | RTO under 1 hour, RPO under 5 minutes |
| T7.21 | S51 | E7.1 | Chaos at target load: pods killed, the edge Link cut mid-flight, a database failover | Fail-safes, buffering and recovery hold; the edges keep flying |
| T7.22 | S51 | E7.3 | Four-language audit: every screen and every Notification in English, French, German and Spanish; a missing text fails CI | No missing text in any front end or in the `notifier` |
| T7.23 | S51 | E7.3 | Onboarding in the production cells: runbook for UC-029 and UC-015 for new Operators; the design partner of [🤝 P-01](11-hardware-and-partners.md#p-01) stays in the OVHcloud cell it has used since S24, and is moved with T7.07 only if its placement requires it | A new Operator onboarded with the runbook flies from a production cell |
| T7.24 | S51 | E7.1 | SLO dashboards across cells in Mimir, burn-rate alerts to the on-call rota, weekly error budgets | A forced SLO burn reaches the on-call rota |
| T7.25 | S51 | E7.7 | Real compatibility flights in a test area, on the DJI Drone of [🤝 H-09](11-hardware-and-partners.md#h-09) and the Skydio Drone of [🤝 H-10](11-hardware-and-partners.md#h-10) | Each Drone model is Approved, or its vendor is left out of general availability ([🎲 R-04](12-risks.md#r-04)) |
| T7.26 | S52 | E7.9 | Fixes from C-07 for Inspection and Patrol | The failing step of each C-07 Mission passes again, in flight or in the Simulator |
| T7.27 | S52 | E7.9 | Fixes from C-07 for Agriculture and Light shows | The same, for the Missions of these two Activities |
| T7.28 | S52 | E7.9 | Release candidate: Trivy and OSV-Scanner scans, SBOM, cosign signatures; key and certificate expiry checked | No open critical vulnerability; every image, the bundle and the edge update signed |
| T7.29 | S52 | E7.9 | General availability release: image tags bumped by pull request, the canary cell then the waves; edges in rings | Every production cell and the internal ring run the release |
| T7.30 | S52 | E7.9 | Last screens to 📸 Screenshot, roadmap pages brought up to date, `specs.py check` | No ✏️ Mock-up left; the check prints nothing |

## <a id="demo"></a>🎤 Demo

The M7 demonstration, on 29 December 2028, uses the sample cast of the [🎨 Visual identity](../visual-identity.md).

1. **A new Operator in production.** The [👤 Swarm administrator](../glossary.md#per-swarm-administrator) opens ➕ Operators in the [⚙️ Back office](../glossary.md#sys-back-office) and creates Aerowing Services, deployment cloud, Jurisdiction EU (EASA), Anchoring by a qualified timestamping authority. The global layer places it in the OVHcloud cell and invites its first [👤 Mission planner](../glossary.md#per-mission-planner), Léa Martin ([🎬 UC-029](../functional/use-cases/UC-029-create-an-operator.md), FS-012 AC-3).
2. **Clients and languages.** Léa Martin invites the [👤 Client](../glossary.md#per-client) Helio Energy; its contact Priya Shah chooses German and every screen of the [⚙️ Client portal](../glossary.md#sys-client-portal) is in German (FS-012 AC-2). A search for Missions by another Operator in the same cell finds none of Aerowing Services' (FS-012 AC-1).
3. **Inspection and Patrol on the release.** M-2026-0412 Inspection of Les Vignes and M-2026-0414 Night patrol of Northgate, flown during [🛫 C-07](10-flight-test-campaigns.md#c-07) by the [👤 Pilot](../glossary.md#per-pilot) Sam Carter on the release candidate, with the Co-pilot on, are opened in the production cell with their Deliverables, Alarms and Scorecards.
4. **New Drone families.** The [👤 Fleet maintainer](../glossary.md#per-fleet-maintainer) Noah Weber shows the Matrice 4TD (DJI) and the X10 (Skydio) as [🔄 Drone model: Approved](../glossary.md#st-drone-model-approved) after their compatibility tests, and a Matrice 4TD whose new firmware made it [🔄 Drone model: Not approved](../glossary.md#st-drone-model-not-approved) again ([🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md), FS-011 AC-1).
5. **Blockchain Anchoring.** A second test Operator has chosen the blockchain option. Priya Shah verifies a Flight log of that Operator's Mission: [🔄 Evidence record: Verified](../glossary.md#st-evidence-record-verified) with its blockchain receipt; the same file edited after closing shows [🔄 Evidence record: Altered](../glossary.md#st-evidence-record-altered) ([🎬 UC-012](../functional/use-cases/UC-012-verify-the-evidence-record-of-a-flight.md), FS-009 AC-1 and AC-2).
6. **A full cell at target.** The staging dashboard of last night's run: 200 Missions in flight, 100,000 frames per second into TimescaleDB, 5,000 WebSocket clients and 500 video viewers, every budget green; then the last restore drill, the cell rebuilt in under one hour with under five minutes of data lost.
7. **Reach.** The US self-hosted cell with a US test Operator whose data stays in it; the on-premises install on [🤝 H-08](11-hardware-and-partners.md#h-08), with its own Swarm administrator, processing on its GPU server and the open-weight model; the edge appliance rings, with the general availability version reaching the internal ring first.

## <a id="exit"></a>🚪 Exit criteria

**Acceptance criteria**

- [ ] [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md) AC-1: two Operators in the cloud never see each other's Missions, in each production cell, across cells and after an Operator is moved ([📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md), [🎬 UC-015](../functional/use-cases/UC-015-invite-a-client-to-the-client-portal.md)).
- [ ] [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md) AC-2: an invited Client who chose German sees every screen in German ([📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md), [🎬 UC-015](../functional/use-cases/UC-015-invite-a-client-to-the-client-portal.md)); the same audit passes for English, French and Spanish.
- [ ] [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md) AC-3: a new Operator created by the Swarm administrator sees no other Operator's data, in the production cells, in the US cell and on premises ([📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md), [🎬 UC-029](../functional/use-cases/UC-029-create-an-operator.md)).
- [ ] [📘 FS-011](../functional/features/FS-011-drone-adapters.md) AC-1: for the Matrice 4TD and the X10, a compatibility test that fails on Return home keeps their Drones [🔄 Drone: Grounded](../glossary.md#st-drone-grounded) ([📏 BR-015](../functional/business-rules/BR-015-approved-drone-models-only.md), [🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md)).
- [ ] [📘 FS-009](../functional/features/FS-009-evidence-ledger-and-anchoring.md) AC-1 and AC-2 with the blockchain option: an unchanged Flight log shows Evidence record: Verified with its Anchoring date, an edited one shows Evidence record: Altered ([📏 BR-009](../functional/business-rules/BR-009-evidence-integrity.md), [🎬 UC-012](../functional/use-cases/UC-012-verify-the-evidence-record-of-a-flight.md)).
- [ ] Every acceptance criterion of every feature passes again on the release candidate, in the staging cell and in the C-07 flights.

**Budgets** ([🚀 Scalability and performance](../technical/07-scalability.md#budgets)), measured on one cell at target load

- [ ] REST inside a cell: p95 under 100 ms for reads, under 250 ms for writes.
- [ ] Telemetry, Drone to the Pilot's screen: p95 under 400 ms through the cell, under 150 ms at the edge.
- [ ] WebRTC video: under 300 ms glass to glass.
- [ ] Hold the Squad or abort, to every Drone: under 100 ms; Pilot command at the edge: p99 under 50 ms.
- [ ] Cell rebuild: RTO under 1 hour, RPO under 5 minutes, in the restore drill of [🗄️ Storage](../technical/03-storage.md#backups).
- [ ] Cell limits held together: 200 Missions in flight, 100,000 frames per second, 5,000 WebSocket clients, 500 video viewers, about 1,000 Operators ([🚀 Scalability and performance](../technical/07-scalability.md#cells)).
- [ ] On premises, on [🤝 H-08](11-hardware-and-partners.md#h-08): an orthomosaic of 1,000 images in under 30 minutes on its GPU server.
- [ ] The SLOs of [🩺 Observability](../technical/08-observability.md#slos) hold for the last two weeks of the phase in the production cells.

**Load tests** ([🚀 Scalability and performance](../technical/07-scalability.md#load-tests))

- [ ] The nightly full cell at target load, with the 5,000-Drone show of P6, has passed every night for the last two weeks of the phase.
- [ ] The chaos runs pass at target load: pods killed, the edge Link cut mid-flight, a database failover.

**Screens and specifications**

- [ ] The screens of UC-012 A2, OK and KO show a blockchain receipt as a 📸 Screenshot in light and dark mode, if the receipt changes them.
- [ ] No ✏️ Mock-up is left under `docs/specs/screens/`: every state of every use case is a 📸 Screenshot, in light and dark mode, or `➖ No screen`.
- [ ] `python3 .claude/skills/write-specs/scripts/specs.py check` prints nothing.

**Milestone M7**

- [ ] Inspection and Patrol sold in the EU cloud cells; a full cell at target load in staging; the on-premises bundle installed once.

## <a id="dependencies"></a>⛓️ Dependencies

**Previous phases**

| Phase | What P7 needs from it |
| --- | --- |
| [🛣️ P0: Foundations](01-p0-foundations.md) | The mono-repo, CI/CD, Keycloak, the self-hosted k3s cell, NATS, PostgreSQL with PostGIS and TimescaleDB, Valkey, OpenTelemetry, the i18n framework, [🎬 UC-029](../functional/use-cases/UC-029-create-an-operator.md) |
| [🛣️ P1: First flight](02-p1-first-flight.md) | The Drone adapter interface and the compatibility test of [🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md), the flight engine, the Simulator |
| [🛣️ P2: Inspection product](03-p2-inspection-product.md) | The OVHcloud cell and the self-hosted beta cell opened in S24, provisioned with Terraform; the first real Squad flights of [🛫 C-02](10-flight-test-campaigns.md#c-02); the evidence ledger with the timestamping authority, the Back office and the Client portal ([🎬 UC-015](../functional/use-cases/UC-015-invite-a-client-to-the-client-portal.md)), processing on GPU |
| [🛣️ P3: Patrol](04-p3-patrol.md) | The Parrot sidecar, the pattern for the DJI and Skydio sidecars; the SFU and LL-HLS; the `notifier` |
| [🛣️ P4: Agriculture](05-p4-agriculture.md) | Agriculture flown again in C-07 |
| [🛣️ P5: AI agents, MCP and A2A](06-p5-ai-agents.md) | KEDA in every cell; the open-weight model shipped in the on-premises bundle; the Co-pilot used in C-07 |
| [🛣️ P6: Light shows](07-p6-light-shows.md) | The 5,000-Drone show on a partitioned edge, part of the nightly load test at target |

**Regulatory, hardware, partners and campaigns**

| Item | Due | Why P7 needs it |
| --- | --- | --- |
| [🤝 P-06](11-hardware-and-partners.md#p-06) | S24, S46 | The OVHcloud cell, open since S24 and hardened in P7; the Scaleway production cell |
| [🤝 H-09](11-hardware-and-partners.md#h-09) and [🤝 H-10](11-hardware-and-partners.md#h-10) | S47 | A rented DJI Drone and a rented Skydio Drone for the real flights of the compatibility test (T7.25) |
| [🤝 P-09](11-hardware-and-partners.md#p-09) | S47 | The blockchain aggregator account of T7.18 |
| [🤝 H-08](11-hardware-and-partners.md#h-08) | S46 | The GPU server of the on-premises test install |
| [🏛️ G-09](09-regulatory-track.md#g-09) | S47 | The US rules study, before the US cell and the US Jurisdiction |
| [🤝 P-01](11-hardware-and-partners.md#p-01) | S12 | The design-partner Operator, in the OVHcloud cell since S24 |
| [🤝 P-07](11-hardware-and-partners.md#p-07) | S20 | The timestamping authority, still the default Anchoring |
| [🏛️ G-05](09-regulatory-track.md#g-05) and [🏛️ G-06](09-regulatory-track.md#g-06) | S20; 2 sprints before C-07 | The Authorisation and the Site checks of the C-07 flights |
| [🤝 H-01](11-hardware-and-partners.md#h-01), [🤝 H-04](11-hardware-and-partners.md#h-04), [🤝 H-05](11-hardware-and-partners.md#h-05) | S06, S24, S26 | The test fleet flown in C-07 |
| [🛫 C-07](10-flight-test-campaigns.md#c-07) | S50 to S52 | The validation flights for every Activity |

## <a id="risks"></a>🎲 Risks

| Risk | Why it matters in P7 | Response in P7 |
| --- | --- | --- |
| [🎲 R-12](12-risks.md#r-12) Cell ingest target not reached | The M7 proof needs a full cell at target load | T7.01 runs from S45, so a miss is known seven sprints before M7; larger batches, more partitions, an extra writer; if still short, smaller cells, more of them |
| [🎲 R-04](12-risks.md#r-04) Vendor SDK access restricted | DJI and Skydio adapters depend on the vendors' SDKs or cloud APIs | Ask for SDK access in S45, before T7.08; MAVLink and Parrot stay the supported path; a refused vendor is dropped from general availability and partners are told which Drone models are supported |
| [🎲 R-10](12-risks.md#r-10) Security incident or key compromise | New cells, a US cell and an on-premises bundle each hold signing keys and Operators' data | Keys of each cell in its vault; T7.02 isolation suite at scale; signed bundle and edge updates; supply chain checks of T7.28 block the release |
| [🎲 R-15](12-risks.md#r-15) Regulation changes | US rules for several Drones per Pilot may move | The US cell opens for testing only; US Operators fly under their own Authorisations, recorded like EU ones |
| [🎲 R-07](12-risks.md#r-07) Weather and seasons | C-07 flies in December, for every Activity | Fly each Activity on the first suitable day of S50; Agriculture and Light shows, which stay in beta, can be validated in the Simulator if the weather blocks them |
| [🎲 R-11](12-risks.md#r-11) Crash or hardware loss in tests | C-07 flies the whole test fleet on a release candidate | Fail-safe drill at the start of each C-07 flight day; no flight on a build that misses a budget |
| [🎲 R-01](12-risks.md#r-01) Review bottleneck | S45 to S48 carry about 8 tickets each across P5, P6 and P7, and S49 and S50 about 6, while the person flies C-06 (S46 to S48) and C-07 (S50 to S52) | Infrastructure tickets (charts, values, bundle) are reviewed on their test runs and plans; safety-path changes are frozen after S50 except fixes |
| [🎲 R-08](12-risks.md#r-08) Scope too large | P7 is the last phase; nothing can slip past M7 | Order of cuts if needed: the Skydio adapter, then the blockchain option, then the US cell; the M7 proof itself is never cut |

## <a id="work-split"></a>🧑‍💻 Work split

**The person**

- **Decisions:** which cell is the canary; the wave order; whether the design partner must move from the OVHcloud cell at all; which Drone models of DJI and Skydio are supported at general availability; the go for general availability on 29 December 2028.
- **Reviews:** the isolation suite (T7.02), the residency check (T7.12), the bundle and edge signatures (T7.15, T7.14), the Anchoring receipts (T7.18, T7.19) line by line; infrastructure tickets on their plans, test runs and dashboards.
- **Partners and accounts:** the production accounts with OVHcloud and Scaleway ([🤝 P-06](11-hardware-and-partners.md#p-06)), the DJI and Skydio SDK access and the rented Drones of [🤝 H-09](11-hardware-and-partners.md#h-09) and [🤝 H-10](11-hardware-and-partners.md#h-10), the blockchain aggregator account of [🤝 P-09](11-hardware-and-partners.md#p-09), the GPU server of [🤝 H-08](11-hardware-and-partners.md#h-08).
- **Regulatory:** the US rules study of [🏛️ G-09](09-regulatory-track.md#g-09) in S47.
- **Flights:** the real compatibility flights of the Matrice 4TD and the X10, and the C-07 validation flights for every Activity, as the Pilot.

**The agents, in parallel**

- The OVHcloud and Scaleway cells and the US k3s cell are provisioned with Terraform, and they and the on-premises bundle are deployed from the same umbrella chart, so agents work on each provider's Terraform variables and Helm values as separate tasks.
- The DJI and Skydio sidecars run as two independent tasks on the adapter interface, each with its compatibility suite.
- Load scenarios, chaos scenarios, dashboards, the translation audit per front end, release notes, screenshots in light and dark mode and the technical page updates run alongside every ticket.
- During C-07, agents turn each problem the person notes in the field into a fix ticket for S52, with its failing test first.

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ P6: Light shows](07-p6-light-shows.md) · 📄 **Page 114 / 120** · [Regulatory track ▶️](09-regulatory-track.md)
<!-- /spec:nav-bottom -->
