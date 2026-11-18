# 🔭 Commercial drone and swarm landscape

**Researched:** 2026-11-18. **Purpose:** know what already exists before writing the functional specification of
Swarm. Most sources are vendor pages and trade press; figures marked *unverified* conflict between sources.

## 🏭 Drone makers

| Maker | Position | Notes |
| --- | --- | --- |
| DJI (China) | Dominant, about 70 to 74 % of the market (*unverified*) | Enterprise line (Matrice), docks (Dock 3), fleet software FlightHub 2. Closed ecosystem, SDKs. Restricted in some public markets in the US. |
| Skydio (US) | Main US alternative, enterprise, public safety, defence | X10 and Skydio Dock, remote operations software with coordinated docks. |
| Parrot (France) | Main European maker, government and defence | Positions itself on secure and open platforms. |
| Autel Robotics (China) | Consumer, prosumer and enterprise | |
| Hylio (US) | Heavy agricultural spray drones | First FAA exemption (2024) for one crew flying up to 3 drones above 55 lb, without visual observer per some sources. Expiry 31 March 2026, renewal not confirmed. |
| Verge Aero (US) | Light show drones and software, sold together | Design Studio, Console, web portal. Locked to its own drones. |
| Bitcraze Crazyflie (Sweden) | Nano drones for research | Crazyswarm2 (ROS 2) has flown 49+ drones indoors. |

## 🧩 Multi-drone software

| Product | Kind | What it does |
| --- | --- | --- |
| DJI FlightHub 2 | Fleet management, DJI only | Remote missions from docks, live view, recharge in dock. |
| FlytBase | Hardware-agnostic dock orchestration | Many docks from one operations centre, per-dock yearly licence (about $4,500 per Dock 3 per year). |
| Skydio remote operations | Fleet, Skydio only | Coordinated groups of docks. |
| Skybrush (open source, GPL-3.0) | Light show design and swarm ground control | Skybrush Live (ground station), Studio for Blender (choreography), server. Works with ArduCopter. Paid Pro tier. |
| Verge Aero | Light show suite, closed | Design, flight console, licensing per organisation. |
| Drone Show Software | Light shows | Timed cue scripting. |
| DroneDeploy, Pix4D, DroneSense | Mapping, inspection, public safety | Mostly one pilot, one drone. |
| Shield AI Hivemind, Palladyne SwarmOS | Defence swarm autonomy | Autonomy that keeps working when links degrade. Out of scope for commercial use. |

## ⚙️ Open foundations

- **PX4** and **ArduPilot**: open-source autopilots. Both speak **MAVLink**, whose system and component IDs let one
  ground station address many vehicles.
- **QGroundControl**: ground station for PX4 and ArduPilot, multi-vehicle capable. Mission Planner has a basic
  leader and follower swarm mode. Neither has a built-in commercial swarm mode.
- **Gazebo** simulation runs several PX4 vehicles at once, which allows a swarm to be tested without hardware.

## ⚖️ Regulation

- **EU (EASA):** no specific rule for swarms. Flights beyond the Open category, BVLOS in particular, need a
  Specific category authorisation, usually through **SORA 2.5** or a standard scenario. U-space treats airspace with
  traffic services; a lighter "U-space light" is proposed in NPA 2026-103 (proposal, not law).
- **US (FAA):** Part 107 by default; one pilot for several drones needs an exemption (Hylio precedent, Part 137 for
  spraying). Large light shows fly under waivers.

## 🎯 What this means for Swarm

- Fleet tools (FlightHub 2, FlytBase, Skydio) manage **many drones, each on its own mission**. Show tools (Skybrush,
  Verge Aero) fly **many drones as one choreography**, scripted in advance. Little exists in between: a commercial
  swarm that **shares one task** (cover an area, inspect a structure, spray a field) and **re-plans** live when a
  drone fails.
- Open autopilots (PX4, ArduPilot over MAVLink) avoid lock-in to one maker; vendor SDKs give access to the dominant
  hardware.
- Regulation is the main barrier: one pilot for several drones needs an authorisation, so the software must produce
  the evidence an authorisation asks for (geofences, logs, fail-safes, pilot oversight).

## ⛓️ Blockchain: is it relevant?

**Not for flying.** Consensus between drones or with the ground through a ledger adds latency, radio traffic and
on-board computing for no safety gain; no deployment or figure supports it, and research designs (UTM-Chain) have to
shrink the ledger to fit on drones. Coordination stays on MAVLink, mesh and cellular links.

**Relevant for evidence, where several parties do not trust each other:**

| Use case | Who needs proof | What is anchored |
| --- | --- | --- |
| Tamper-evident flight logs | Aviation authority, insurer, Client | The fingerprint (Merkle root) of each flight's telemetry, commands and Pilot decisions |
| Proof of service | Client, certification body | Agriculture: what was sprayed, where, when, how much. Inspection: which areas were covered |
| Patrol evidence | Client, police, court | Fingerprint of each video clip and event, so it can be shown to be unaltered |
| Shared registry between Operators | Several Operators on one site | Airspace reservations and drone identities, when no U-space service provides them |

**How:** Swarm chains and signs its records itself (hash chain, Merkle tree) and **anchors** the fingerprint
periodically. Anchoring is a choice per Operator: none, a qualified timestamping authority (RFC 3161, eIDAS), or a
public or consortium blockchain. Only fingerprints leave Swarm, never the data. This matches what exists today:
blockchain timestamping of flight data (OriginStamp for Unisphere) and blockchain-protected UTM records (Unifly,
Certiflight demonstration). Payments by smart contract are left out: low value, heavy regulation.

## 🔗 Sources

- [Commercial drone software platforms (2026), National Drone Centre](https://nationaldronecentre.com/commercial-drone-software-platforms/)
- [Drone swarm market 2026, Drone Intelligence](https://droneintelligence.ai/intelligence/drone-swarm-market)
- [Palladyne AI and Draganfly swarm milestone, The Robot Report](https://www.therobotreport.com/palladyne-ai-draganfly-reach-integration-milestone-autonomous-drone-swarms/)
- [Top 36 drone companies in 2026, The Drone U](https://www.thedroneu.com/blog/top-drone-companies/)
- [DJI market in 2025, The Drone Girl](https://www.thedronegirl.com/2025/11/06/2025-drone-market-dji/)
- [Skybrush Live features](https://docs.skybrush.io/public/skybrush-live-doc/latest/features.html)
- [Skybrush on GitHub](https://github.com/skybrush-io/live)
- [Verge Aero Composer, The Drone Girl](https://www.thedronegirl.com/2024/01/25/verge-aero-composer/)
- [Verge Aero documentation](https://docs.verge.aero/llms-full.txt)
- [Drone-in-a-box systems, UAV Coach](https://uavcoach.com/drone-in-a-box/)
- [Drone-in-the-box systems in 2026, The Drone U](https://www.thedroneu.com/blog/drone-in-the-box-systems/)
- [FlytBase for DJI Dock 3](https://www.flytbase.com/dji-dock-3)
- [Drone-in-a-box market, Drone Intelligence](https://droneintelligence.ai/intelligence/drone-in-a-box-market)
- [Hylio FAA swarm exemption, Flying Magazine](https://www.flyingmag.com/faa-approves-hylio-commercial-agricultural-drone-swarm-exemption/)
- [Hylio approval, Agriculture Dive](https://www.agriculturedive.com/news/hylio-scores-federal-approval-for-crop-spraying-drones-in-large-scale-farms/711392/)
- [ArduPilot Mission Planner swarming](https://ardupilot.org/planner/docs/swarming.html)
- [PX4 Crazyflie 2.1](https://docs.px4.io/v1.16/ko/complete_vehicles_mc/crazyflie21.html)
- [Regulatory-compliant integration of drone swarms, Drones Magazin](https://www.drones-magazin.de/en/articles/regulatory-compliant-integration-of-drone-swarms/)
- [EASA U-space light proposal, Unmanned Airspace](https://www.unmannedairspace.info/uncategorized/easa-issues-its-proposals-to-introduce-a-u-space-light-category-of-drone-traffic-management-systems/)
- [EASA adopts SORA 2.5, Bureau Veritas](https://aero.bureauveritas.com/newsroom/easa-adopts-sora-25-new-simplifications-specific-category-drones)
- [BVLOS UAS operations white paper, Mobility Alliance](https://mobilityalliance.eu/wp-content/uploads/2025/10/20250528-White-Paper-BVLOS-UAS-Operations.pdf)
- [US DoT report on blockchain for UTM, Unmanned Airspace](https://www.unmannedairspace.info/uncategorized/us-dot-report-highlights-blockchain-potential-for-utm-and-organ-delivery-by-drone/)
- [Transparency in drone flight secured by blockchain, OriginStamp](https://originstamp.com/en/clients/unisphere)
- [Unifly blockchain-backed UTM in Certiflight, DroneLife](https://dronelife.com/2025/02/14/unifly-demonstrates-blockchain-backed-utm-for-port-surveillance-in-certiflight-project/)
- [Blockchain for UAV applications, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8123815)
- [Merkle-tree flight data verification, arXiv](https://www.arxiv.org/pdf/2409.06507)
