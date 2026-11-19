# 🎫 Tickets

The 262 tickets of the [roadmap](../specs/roadmap/README.md), generated from its phase pages, under the rules of
[`.claude/rules/tickets.md`](../../.claude/rules/tickets.md). A ticket gets its folder `docs/tickets/<ID>/` when it is planned.

## How to work a ticket

| Step | Command | Result |
| --- | --- | --- |
| 1. Plan | `/ticket-plan T1.07` | `TICKET.md`, `PROGRESS.md`, and `PLAN.md` with the task graph (waves, dependency graph and task details rendered by `.claude/scripts/plan.py`), awaiting approval |
| 2. Approve | Edit `PLAN.md`: `**Plan:** 🟢 Approved` | The only human gate |
| 3. Run | `/ticket-run T1.07` | Waves of agents in parallel worktrees, integration, verification, review, local merge into `develop` |

Status: ⬜ To do · 🟡 Planned (folder and plan exist) · 🔵 In progress · ✅ Done.

## Summary

| Phase | Sprints | Tickets |
| --- | --- | --- |
| [P0: Foundations](#p0) | S01 to S04 | 20 |
| [P1: First flight](#p1) | S05 to S13 | 45 |
| [P2: Inspection product](#p2) | S14 to S24 | 50 |
| [P3: Patrol](#p3) | S25 to S33 | 35 |
| [P4: Agriculture](#p4) | S32 to S38 | 26 |
| [P5: AI agents, MCP and A2A](#p5) | S36 to S43 | 31 |
| [P6: Light shows](#p6) | S41 to S48 | 25 |
| [P7: Scale and reach](#p7) | S45 to S52 | 30 |
| **Total** | S01 to S52 | **262** |

## <a id="p0"></a>P0: Foundations

Phase page: [🛣️ P0: Foundations](../specs/roadmap/01-p0-foundations.md).

| Ticket | Title | Sprint | Epic | Status |
| --- | --- | --- | --- | --- |
| [T0.01](../specs/roadmap/01-p0-foundations.md#s01) | Mono-repo layout and Terraform base | S01 | E0.1 Mono-repo, Terraform base and ticket harness | ⬜ To do |
| [T0.02](../specs/roadmap/01-p0-foundations.md#s01) | Claude Code ticket harness | S01 | E0.1 Mono-repo, Terraform base and ticket harness | ⬜ To do |
| [T0.03](../specs/roadmap/01-p0-foundations.md#s01) | Convention tests and linters | S01 | E0.1 Mono-repo, Terraform base and ticket harness | ⬜ To do |
| [T0.04](../specs/roadmap/01-p0-foundations.md#s01) | CI checks for every language | S01 | E0.2 CI/CD | ⬜ To do |
| [T0.05](../specs/roadmap/01-p0-foundations.md#s01) | Lifecycle and logging packages | S01 | E0.3 Shared packages | ⬜ To do |
| [T0.06](../specs/roadmap/01-p0-foundations.md#s02) | Shared models and generated types | S02 | E0.3 Shared packages | ⬜ To do |
| [T0.07](../specs/roadmap/01-p0-foundations.md#s02) | Rust core and benchmark gate | S02 | E0.3 Shared packages | ⬜ To do |
| [T0.08](../specs/roadmap/01-p0-foundations.md#s02) | Dev cell on k3s | S02 | E0.4 Dev cell and data platform | ⬜ To do |
| [T0.09](../specs/roadmap/01-p0-foundations.md#s02) | NATS JetStream and Operator accounts | S02 | E0.4 Dev cell and data platform | ⬜ To do |
| [T0.10](../specs/roadmap/01-p0-foundations.md#s02) | Images, scans, signatures and Playwright | S02 | E0.2 CI/CD | ⬜ To do |
| [T0.11](../specs/roadmap/01-p0-foundations.md#s03) | Keycloak and gateway authentication | S03 | E0.5 Identity and Operators | ⬜ To do |
| [T0.12](../specs/roadmap/01-p0-foundations.md#s03) | Service skeletons with row-level security | S03 | E0.5 Identity and Operators | ⬜ To do |
| [T0.13](../specs/roadmap/01-p0-foundations.md#s03) | Simulator base | S03 | E0.6 Simulator and live path | ⬜ To do |
| [T0.14](../specs/roadmap/01-p0-foundations.md#s03) | Design tokens, components and app shells | S03 | E0.7 Front-end foundation | ⬜ To do |
| [T0.15](../specs/roadmap/01-p0-foundations.md#s03) | Four languages | S03 | E0.7 Front-end foundation | ⬜ To do |
| [T0.16](../specs/roadmap/01-p0-foundations.md#s04) | Create an Operator (UC-029) | S04 | E0.5 Identity and Operators | ⬜ To do |
| [T0.17](../specs/roadmap/01-p0-foundations.md#s04) | Observability base | S04 | E0.4 Dev cell and data platform | ⬜ To do |
| [T0.18](../specs/roadmap/01-p0-foundations.md#s04) | Flight engine skeleton and live WebSocket | S04 | E0.6 Simulator and live path | ⬜ To do |
| [T0.19](../specs/roadmap/01-p0-foundations.md#s04) | Simulated Squad on the Ground control map | S04 | E0.6 Simulator and live path | ⬜ To do |
| [T0.20](../specs/roadmap/01-p0-foundations.md#s04) | Visual tests and UC-029 screenshots | S04 | E0.7 Front-end foundation | ⬜ To do |

## <a id="p1"></a>P1: First flight

Phase page: [🛣️ P1: First flight](../specs/roadmap/02-p1-first-flight.md).

| Ticket | Title | Sprint | Epic | Status |
| --- | --- | --- | --- | --- |
| [T1.01](../specs/roadmap/02-p1-first-flight.md#s05) | Safety tick in Rust | S05 | E1.1 Flight engine and safety loop | ⬜ To do |
| [T1.02](../specs/roadmap/02-p1-first-flight.md#s05) | MAVLink 2 adapter | S05 | E1.2 MAVLink adapter and Drone model approval | ⬜ To do |
| [T1.03](../specs/roadmap/02-p1-first-flight.md#s05) | Mission actor and command lanes | S05 | E1.1 Flight engine and safety loop | ⬜ To do |
| [T1.04](../specs/roadmap/02-p1-first-flight.md#s05) | Edge store and Flight log | S05 | E1.1 Flight engine and safety loop | ⬜ To do |
| [T1.05](../specs/roadmap/02-p1-first-flight.md#s05) | Fleet service | S05 | E1.3 Fleet and Authorisations | ⬜ To do |
| [T1.06](../specs/roadmap/02-p1-first-flight.md#s06) | Fleet screens (UC-007) | S06 | E1.3 Fleet and Authorisations | ⬜ To do |
| [T1.07](../specs/roadmap/02-p1-first-flight.md#s06) | Authorisations (UC-008) | S06 | E1.3 Fleet and Authorisations | ⬜ To do |
| [T1.08](../specs/roadmap/02-p1-first-flight.md#s06) | Mission studio map and Geofence | S06 | E1.4 Mission studio for Inspection | ⬜ To do |
| [T1.09](../specs/roadmap/02-p1-first-flight.md#s06) | Coverage planner | S06 | E1.4 Mission studio for Inspection | ⬜ To do |
| [T1.10](../specs/roadmap/02-p1-first-flight.md#s06) | Ground control frame and local live data | S06 | E1.7 Ground control monitoring | ⬜ To do |
| [T1.11](../specs/roadmap/02-p1-first-flight.md#s07) | Squad, tasks, routes and save (UC-001) | S07 | E1.4 Mission studio for Inspection | ⬜ To do |
| [T1.12](../specs/roadmap/02-p1-first-flight.md#s07) | Compatibility test in the Simulator (UC-014) | S07 | E1.2 MAVLink adapter and Drone model approval | ⬜ To do |
| [T1.13](../specs/roadmap/02-p1-first-flight.md#s07) | Automatic checks of the Pre-flight check | S07 | E1.5 Pre-flight check and launch | ⬜ To do |
| [T1.14](../specs/roadmap/02-p1-first-flight.md#s07) | Checklist, PIN signature and launch | S07 | E1.5 Pre-flight check and launch | ⬜ To do |
| [T1.15](../specs/roadmap/02-p1-first-flight.md#s07) | Two-layer safety loop in flight | S07 | E1.1 Flight engine and safety loop | ⬜ To do |
| [T1.16](../specs/roadmap/02-p1-first-flight.md#s08) | Lose a Drone (UC-005) | S08 | E1.6 Fail-safes, Re-plans and Pilot override | ⬜ To do |
| [T1.17](../specs/roadmap/02-p1-first-flight.md#s08) | Re-plans proposed by the Squad (UC-004) | S08 | E1.6 Fail-safes, Re-plans and Pilot override | ⬜ To do |
| [T1.18](../specs/roadmap/02-p1-first-flight.md#s08) | Hold the Squad and abort | S08 | E1.6 Fail-safes, Re-plans and Pilot override | ⬜ To do |
| [T1.19](../specs/roadmap/02-p1-first-flight.md#s08) | Manual control and Return to Squad (UC-006) | S08 | E1.6 Fail-safes, Re-plans and Pilot override | ⬜ To do |
| [T1.20](../specs/roadmap/02-p1-first-flight.md#s08) | Squad panel and progress (UC-025) | S08 | E1.7 Ground control monitoring | ⬜ To do |
| [T1.21](../specs/roadmap/02-p1-first-flight.md#s09) | Alerts and Alert thresholds (UC-026) | S09 | E1.7 Ground control monitoring | ⬜ To do |
| [T1.22](../specs/roadmap/02-p1-first-flight.md#s09) | Live video and Mosaic | S09 | E1.7 Ground control monitoring | ⬜ To do |
| [T1.23](../specs/roadmap/02-p1-first-flight.md#s09) | Focus view (UC-030) | S09 | E1.7 Ground control monitoring | ⬜ To do |
| [T1.24](../specs/roadmap/02-p1-first-flight.md#s09) | Workspace configuration (UC-023) | S09 | E1.8 Workspace, platforms and edge | ⬜ To do |
| [T1.25](../specs/roadmap/02-p1-first-flight.md#s09) | Simulate a Mission (UC-002) | S09 | E1.4 Mission studio for Inspection | ⬜ To do |
| [T1.26](../specs/roadmap/02-p1-first-flight.md#s10) | On-site changes (UC-024) | S10 | E1.5 Pre-flight check and launch | ⬜ To do |
| [T1.27](../specs/roadmap/02-p1-first-flight.md#s10) | Field edge on the Pilot's laptop | S10 | E1.8 Workspace, platforms and edge | ⬜ To do |
| [T1.28](../specs/roadmap/02-p1-first-flight.md#s10) | X500 real compatibility flight | S10 | E1.2 MAVLink adapter and Drone model approval | ⬜ To do |
| [T1.29](../specs/roadmap/02-p1-first-flight.md#s10) | Staging cell and nightly load run | S10 | E1.10 Flight tests, quality and exit | ⬜ To do |
| [T1.30](../specs/roadmap/02-p1-first-flight.md#s10) | Chaos at the edge | S10 | E1.1 Flight engine and safety loop | ⬜ To do |
| [T1.31](../specs/roadmap/02-p1-first-flight.md#s11) | Training sessions (UC-013) | S11 | E1.9 Training and the design partner | ⬜ To do |
| [T1.32](../specs/roadmap/02-p1-first-flight.md#s11) | Telemetry writer and Flight log upload | S11 | E1.10 Flight tests, quality and exit | ⬜ To do |
| [T1.33](../specs/roadmap/02-p1-first-flight.md#s11) | Fixes from the first C-01 flight days | S11 | E1.10 Flight tests, quality and exit | ⬜ To do |
| [T1.34](../specs/roadmap/02-p1-first-flight.md#s11) | Laptop and tablet layouts | S11 | E1.8 Workspace, platforms and edge | ⬜ To do |
| [T1.35](../specs/roadmap/02-p1-first-flight.md#s11) | Four languages and safety-control accessibility | S11 | E1.10 Flight tests, quality and exit | ⬜ To do |
| [T1.36](../specs/roadmap/02-p1-first-flight.md#s12) | Fail-safe test pack for M1 | S12 | E1.10 Flight tests, quality and exit | ⬜ To do |
| [T1.37](../specs/roadmap/02-p1-first-flight.md#s12) | Rugged edge box | S12 | E1.8 Workspace, platforms and edge | ⬜ To do |
| [T1.38](../specs/roadmap/02-p1-first-flight.md#s12) | Simulation environment and the design partner's Operator | S12 | E1.9 Training and the design partner | ⬜ To do |
| [T1.39](../specs/roadmap/02-p1-first-flight.md#s12) | Fixes from the later C-01 flight days | S12 | E1.10 Flight tests, quality and exit | ⬜ To do |
| [T1.40](../specs/roadmap/02-p1-first-flight.md#s12) | Front-end budgets | S12 | E1.10 Flight tests, quality and exit | ⬜ To do |
| [T1.41](../specs/roadmap/02-p1-first-flight.md#s13) | Screens to 📸 Screenshot | S13 | E1.10 Flight tests, quality and exit | ⬜ To do |
| [T1.42](../specs/roadmap/02-p1-first-flight.md#s13) | Acceptance suites | S13 | E1.10 Flight tests, quality and exit | ⬜ To do |
| [T1.43](../specs/roadmap/02-p1-first-flight.md#s13) | Security hardening | S13 | E1.10 Flight tests, quality and exit | ⬜ To do |
| [T1.44](../specs/roadmap/02-p1-first-flight.md#s13) | Design partner's first requests | S13 | E1.10 Flight tests, quality and exit | ⬜ To do |
| [T1.45](../specs/roadmap/02-p1-first-flight.md#s13) | Phase close and hand-over to P2 | S13 | E1.10 Flight tests, quality and exit | ⬜ To do |

## <a id="p2"></a>P2: Inspection product

Phase page: [🛣️ P2: Inspection product](../specs/roadmap/03-p2-inspection-product.md).

| Ticket | Title | Sprint | Epic | Status |
| --- | --- | --- | --- | --- |
| [T2.01](../specs/roadmap/03-p2-inspection-product.md#t2-01) | Upload from the edge | S14 | E2.1 Data from the edge | ⬜ To do |
| [T2.02](../specs/roadmap/03-p2-inspection-product.md#t2-02) | Tag every file | S14 | E2.1 Data from the edge | ⬜ To do |
| [T2.03](../specs/roadmap/03-p2-inspection-product.md#t2-03) | Processing queue | S14 | E2.2 Processing and Quality checks | ⬜ To do |
| [T2.04](../specs/roadmap/03-p2-inspection-product.md#t2-04) | Evidence chain | S14 | E2.5 Evidence ledger | ⬜ To do |
| [T2.05](../specs/roadmap/03-p2-inspection-product.md#t2-05) | Deliverable and Defect models | S14 | E2.4 Deliverables and Defects in the Back office | ⬜ To do |
| [T2.06](../specs/roadmap/03-p2-inspection-product.md#t2-06) | Photogrammetry worker | S15 | E2.2 Processing and Quality checks | ⬜ To do |
| [T2.07](../specs/roadmap/03-p2-inspection-product.md#t2-07) | Quality checks | S15 | E2.2 Processing and Quality checks | ⬜ To do |
| [T2.08](../specs/roadmap/03-p2-inspection-product.md#t2-08) | Flight log records | S15 | E2.5 Evidence ledger | ⬜ To do |
| [T2.09](../specs/roadmap/03-p2-inspection-product.md#t2-09) | Client portal frame | S15 | E2.6 Client portal | ⬜ To do |
| [T2.10](../specs/roadmap/03-p2-inspection-product.md#t2-10) | 📦 Deliverables list | S15 | E2.4 Deliverables and Defects in the Back office | ⬜ To do |
| [T2.11](../specs/roadmap/03-p2-inspection-product.md#t2-11) | Tiling | S16 | E2.2 Processing and Quality checks | ⬜ To do |
| [T2.12](../specs/roadmap/03-p2-inspection-product.md#t2-12) | Large Sites | S16 | E2.2 Processing and Quality checks | ⬜ To do |
| [T2.13](../specs/roadmap/03-p2-inspection-product.md#t2-13) | Hourly Anchoring | S16 | E2.5 Evidence ledger | ⬜ To do |
| [T2.14](../specs/roadmap/03-p2-inspection-product.md#t2-14) | Invitations | S16 | E2.6 Client portal | ⬜ To do |
| [T2.15](../specs/roadmap/03-p2-inspection-product.md#t2-15) | Client scopes | S16 | E2.6 Client portal | ⬜ To do |
| [T2.16](../specs/roadmap/03-p2-inspection-product.md#t2-16) | Solar model training | S17 | E2.3 Solar detection | ⬜ To do |
| [T2.17](../specs/roadmap/03-p2-inspection-product.md#t2-17) | Detection worker | S17 | E2.3 Solar detection | ⬜ To do |
| [T2.18](../specs/roadmap/03-p2-inspection-product.md#t2-18) | Defect review | S17 | E2.4 Deliverables and Defects in the Back office | ⬜ To do |
| [T2.19](../specs/roadmap/03-p2-inspection-product.md#t2-19) | Dismissal reasons | S17 | E2.4 Deliverables and Defects in the Back office | ⬜ To do |
| [T2.20](../specs/roadmap/03-p2-inspection-product.md#t2-20) | Ordering | S17 | E2.6 Client portal | ⬜ To do |
| [T2.21](../specs/roadmap/03-p2-inspection-product.md#t2-21) | Publication | S18 | E2.4 Deliverables and Defects in the Back office | ⬜ To do |
| [T2.22](../specs/roadmap/03-p2-inspection-product.md#t2-22) | Live follow-up | S18 | E2.6 Client portal | ⬜ To do |
| [T2.23](../specs/roadmap/03-p2-inspection-product.md#t2-23) | Downloads | S18 | E2.6 Client portal | ⬜ To do |
| [T2.24](../specs/roadmap/03-p2-inspection-product.md#t2-24) | Map and 3D viewer | S18 | E2.4 Deliverables and Defects in the Back office | ⬜ To do |
| [T2.25](../specs/roadmap/03-p2-inspection-product.md#t2-25) | Verification API | S18 | E2.5 Evidence ledger | ⬜ To do |
| [T2.26](../specs/roadmap/03-p2-inspection-product.md#t2-26) | 🔏 Evidence tab | S19 | E2.6 Client portal | ⬜ To do |
| [T2.27](../specs/roadmap/03-p2-inspection-product.md#t2-27) | Replay | S19 | E2.7 Debrief and Scorecard | ⬜ To do |
| [T2.28](../specs/roadmap/03-p2-inspection-product.md#t2-28) | Plan against actual | S19 | E2.7 Debrief and Scorecard | ⬜ To do |
| [T2.29](../specs/roadmap/03-p2-inspection-product.md#t2-29) | Quality checks view | S19 | E2.7 Debrief and Scorecard | ⬜ To do |
| [T2.30](../specs/roadmap/03-p2-inspection-product.md#t2-30) | Self-hosted beta cell | S19 | E2.9 Beta cells and operations | ⬜ To do |
| [T2.31](../specs/roadmap/03-p2-inspection-product.md#t2-31) | Scorecard computation | S20 | E2.7 Debrief and Scorecard | ⬜ To do |
| [T2.32](../specs/roadmap/03-p2-inspection-product.md#t2-32) | Scorecard review | S20 | E2.7 Debrief and Scorecard | ⬜ To do |
| [T2.33](../specs/roadmap/03-p2-inspection-product.md#t2-33) | Linked re-fly | S20 | E2.7 Debrief and Scorecard | ⬜ To do |
| [T2.34](../specs/roadmap/03-p2-inspection-product.md#t2-34) | Qualified timestamping authority | S20 | E2.5 Evidence ledger | ⬜ To do |
| [T2.35](../specs/roadmap/03-p2-inspection-product.md#t2-35) | Altered Flight log in the Debrief | S21 | E2.7 Debrief and Scorecard | ⬜ To do |
| [T2.36](../specs/roadmap/03-p2-inspection-product.md#t2-36) | 🧾 Scorecards for Clients | S21 | E2.6 Client portal | ⬜ To do |
| [T2.37](../specs/roadmap/03-p2-inspection-product.md#t2-37) | Report template | S21 | E2.8 Mission report from a template | ⬜ To do |
| [T2.38](../specs/roadmap/03-p2-inspection-product.md#t2-38) | Report review | S21 | E2.8 Mission report from a template | ⬜ To do |
| [T2.39](../specs/roadmap/03-p2-inspection-product.md#t2-39) | Orthomosaic budget | S22 | E2.2 Processing and Quality checks | ⬜ To do |
| [T2.40](../specs/roadmap/03-p2-inspection-product.md#t2-40) | Retention and object lock | S22 | E2.5 Evidence ledger | ⬜ To do |
| [T2.41](../specs/roadmap/03-p2-inspection-product.md#t2-41) | Upload on weak links | S22 | E2.1 Data from the edge | ⬜ To do |
| [T2.42](../specs/roadmap/03-p2-inspection-product.md#t2-42) | Dashboards and SLO alerts | S22 | E2.9 Beta cells and operations | ⬜ To do |
| [T2.43](../specs/roadmap/03-p2-inspection-product.md#t2-43) | Screenshots of processing and Defects | S23 | E2.10 Screens and exit | ⬜ To do |
| [T2.44](../specs/roadmap/03-p2-inspection-product.md#t2-44) | Screenshots of the Client portal | S23 | E2.10 Screens and exit | ⬜ To do |
| [T2.45](../specs/roadmap/03-p2-inspection-product.md#t2-45) | Screenshots of the Debrief | S23 | E2.10 Screens and exit | ⬜ To do |
| [T2.46](../specs/roadmap/03-p2-inspection-product.md#t2-46) | Load test | S23 | E2.9 Beta cells and operations | ⬜ To do |
| [T2.47](../specs/roadmap/03-p2-inspection-product.md#t2-47) | Penetration test fixes | S24 | E2.9 Beta cells and operations | ⬜ To do |
| [T2.48](../specs/roadmap/03-p2-inspection-product.md#t2-48) | Isolation suite | S24 | E2.9 Beta cells and operations | ⬜ To do |
| [T2.49](../specs/roadmap/03-p2-inspection-product.md#t2-49) | OVHcloud cell and beta release | S24 | E2.9 Beta cells and operations | ⬜ To do |
| [T2.50](../specs/roadmap/03-p2-inspection-product.md#t2-50) | Exit check | S24 | E2.10 Screens and exit | ⬜ To do |

## <a id="p3"></a>P3: Patrol

Phase page: [🛣️ P3: Patrol](../specs/roadmap/04-p3-patrol.md).

| Ticket | Title | Sprint | Epic | Status |
| --- | --- | --- | --- | --- |
| [T3.01](../specs/roadmap/04-p3-patrol.md#t3-01) | Notifier | S25 | E3.7 Notifications and webhooks out | ⬜ To do |
| [T3.02](../specs/roadmap/04-p3-patrol.md#t3-02) | Notification rules | S25 | E3.7 Notifications and webhooks out | ⬜ To do |
| [T3.03](../specs/roadmap/04-p3-patrol.md#t3-03) | Alarms in | S25 | E3.4 Alarms | ⬜ To do |
| [T3.04](../specs/roadmap/04-p3-patrol.md#t3-04) | Patrol routes | S25 | E3.3 Patrol routes and scheduled patrols | ⬜ To do |
| [T3.05](../specs/roadmap/04-p3-patrol.md#t3-05) | Docks in the Fleet | S26 | E3.1 Docks | ⬜ To do |
| [T3.06](../specs/roadmap/04-p3-patrol.md#t3-06) | Dock interface and simulated Dock | S26 | E3.1 Docks | ⬜ To do |
| [T3.07](../specs/roadmap/04-p3-patrol.md#t3-07) | Parrot sidecar | S26 | E3.2 Parrot adapter | ⬜ To do |
| [T3.08](../specs/roadmap/04-p3-patrol.md#t3-08) | Parrot commands | S27 | E3.2 Parrot adapter | ⬜ To do |
| [T3.09](../specs/roadmap/04-p3-patrol.md#t3-09) | Parrot Payload and video | S27 | E3.2 Parrot adapter | ⬜ To do |
| [T3.10](../specs/roadmap/04-p3-patrol.md#t3-10) | Alarm panel | S27 | E3.4 Alarms | ⬜ To do |
| [T3.11](../specs/roadmap/04-p3-patrol.md#t3-11) | Web Push and Pilots on duty | S27 | E3.7 Notifications and webhooks out | ⬜ To do |
| [T3.12](../specs/roadmap/04-p3-patrol.md#t3-12) | Real Dock | S28 | E3.1 Docks | ⬜ To do |
| [T3.13](../specs/roadmap/04-p3-patrol.md#t3-13) | Dock launch and Return home | S28 | E3.1 Docks | ⬜ To do |
| [T3.14](../specs/roadmap/04-p3-patrol.md#t3-14) | Launch on Alarm | S28 | E3.4 Alarms | ⬜ To do |
| [T3.15](../specs/roadmap/04-p3-patrol.md#t3-15) | Close an Alarm | S28 | E3.4 Alarms | ⬜ To do |
| [T3.16](../specs/roadmap/04-p3-patrol.md#t3-16) | ANAFI USA compatibility test | S28 | E3.2 Parrot adapter | ⬜ To do |
| [T3.17](../specs/roadmap/04-p3-patrol.md#t3-17) | Scheduled patrols | S29 | E3.3 Patrol routes and scheduled patrols | ⬜ To do |
| [T3.18](../specs/roadmap/04-p3-patrol.md#t3-18) | 🔔 Alarms for Site agents | S29 | E3.5 Site agents | ⬜ To do |
| [T3.19](../specs/roadmap/04-p3-patrol.md#t3-19) | Requests on demand | S29 | E3.5 Site agents | ⬜ To do |
| [T3.20](../specs/roadmap/04-p3-patrol.md#t3-20) | Accept or decline | S29 | E3.5 Site agents | ⬜ To do |
| [T3.21](../specs/roadmap/04-p3-patrol.md#t3-21) | No command for Site agents | S29 | E3.5 Site agents | ⬜ To do |
| [T3.22](../specs/roadmap/04-p3-patrol.md#t3-22) | SFU and simulcast | S30 | E3.6 Video at scale | ⬜ To do |
| [T3.23](../specs/roadmap/04-p3-patrol.md#t3-23) | Recording | S30 | E3.6 Video at scale | ⬜ To do |
| [T3.24](../specs/roadmap/04-p3-patrol.md#t3-24) | SIA DC-09 | S30 | E3.4 Alarms | ⬜ To do |
| [T3.25](../specs/roadmap/04-p3-patrol.md#t3-25) | Dock PC edge | S30 | E3.1 Docks | ⬜ To do |
| [T3.26](../specs/roadmap/04-p3-patrol.md#t3-26) | LL-HLS for Clients | S31 | E3.6 Video at scale | ⬜ To do |
| [T3.27](../specs/roadmap/04-p3-patrol.md#t3-27) | Face blurring | S31 | E3.6 Video at scale | ⬜ To do |
| [T3.28](../specs/roadmap/04-p3-patrol.md#t3-28) | Webhooks out | S31 | E3.7 Notifications and webhooks out | ⬜ To do |
| [T3.29](../specs/roadmap/04-p3-patrol.md#t3-29) | Patrol Debrief and Scorecard | S31 | E3.3 Patrol routes and scheduled patrols | ⬜ To do |
| [T3.30](../specs/roadmap/04-p3-patrol.md#t3-30) | Firmware watch | S31 | E3.2 Parrot adapter | ⬜ To do |
| [T3.31](../specs/roadmap/04-p3-patrol.md#t3-31) | Video load test | S32 | E3.6 Video at scale | ⬜ To do |
| [T3.32](../specs/roadmap/04-p3-patrol.md#t3-32) | C-03 field fixes | S32 | E3.8 Patrol beta readiness | ⬜ To do |
| [T3.33](../specs/roadmap/04-p3-patrol.md#t3-33) | Screenshots | S32 | E3.8 Patrol beta readiness | ⬜ To do |
| [T3.34](../specs/roadmap/04-p3-patrol.md#t3-34) | Penetration test fixes | S33 | E3.8 Patrol beta readiness | ⬜ To do |
| [T3.35](../specs/roadmap/04-p3-patrol.md#t3-35) | Beta readiness | S33 | E3.8 Patrol beta readiness | ⬜ To do |

## <a id="p4"></a>P4: Agriculture

Phase page: [🛣️ P4: Agriculture](../specs/roadmap/05-p4-agriculture.md).

| Ticket | Title | Sprint | Epic | Status |
| --- | --- | --- | --- | --- |
| [T4.01](../specs/roadmap/05-p4-agriculture.md#sprints) | Field and Prescription map models and storage | S32 | E4.1 Fields and Prescription maps | ⬜ To do |
| [T4.02](../specs/roadmap/05-p4-agriculture.md#sprints) | Shapefile import of Field boundaries and Prescription maps | S32 | E4.1 Fields and Prescription maps | ⬜ To do |
| [T4.03](../specs/roadmap/05-p4-agriculture.md#sprints) | ISOXML import | S33 | E4.1 Fields and Prescription maps | ⬜ To do |
| [T4.04](../specs/roadmap/05-p4-agriculture.md#sprints) | Coverage of a Field with the swath of each Payload | S33 | E4.2 Coverage and dose | ⬜ To do |
| [T4.05](../specs/roadmap/05-p4-agriculture.md#sprints) | Simulated sprayer | S33 | E4.3 Spraying at the edge | ⬜ To do |
| [T4.06](../specs/roadmap/05-p4-agriculture.md#sprints) | Mission studio for Agriculture | S34 | E4.1 Fields and Prescription maps | ⬜ To do |
| [T4.07](../specs/roadmap/05-p4-agriculture.md#sprints) | Field sets the Geofence | S34 | E4.1 Fields and Prescription maps | ⬜ To do |
| [T4.08](../specs/roadmap/05-p4-agriculture.md#sprints) | Dose computation per leg | S34 | E4.2 Coverage and dose | ⬜ To do |
| [T4.09](../specs/roadmap/05-p4-agriculture.md#sprints) | Sprayer and spreader Payloads in the Fleet | S34 | E4.3 Spraying at the edge | ⬜ To do |
| [T4.10](../specs/roadmap/05-p4-agriculture.md#sprints) | Pump control and tank level in the MAVLink adapter | S34 | E4.3 Spraying at the edge | ⬜ To do |
| [T4.11](../specs/roadmap/05-p4-agriculture.md#sprints) | Pump cut at the Field boundary in the safety loop | S35 | E4.3 Spraying at the edge | ⬜ To do |
| [T4.12](../specs/roadmap/05-p4-agriculture.md#sprints) | Spray Drone model connected and Approved | S35 | E4.7 Spray Drones, campaign and beta readiness | ⬜ To do |
| [T4.13](../specs/roadmap/05-p4-agriculture.md#sprints) | Refill level setting and trigger | S35 | E4.4 Refills and supervised Re-plans | ⬜ To do |
| [T4.14](../specs/roadmap/05-p4-agriculture.md#sprints) | Refill Re-plan in the planner library | S35 | E4.4 Refills and supervised Re-plans | ⬜ To do |
| [T4.15](../specs/roadmap/05-p4-agriculture.md#sprints) | Licences of the Pilot and the Operator | S35 | E4.6 Records, evidence and licences | ⬜ To do |
| [T4.16](../specs/roadmap/05-p4-agriculture.md#sprints) | Resume where stopped and gaps | S36 | E4.4 Refills and supervised Re-plans | ⬜ To do |
| [T4.17](../specs/roadmap/05-p4-agriculture.md#sprints) | Ground control Agriculture panels | S36 | E4.5 Ground control for Agriculture | ⬜ To do |
| [T4.18](../specs/roadmap/05-p4-agriculture.md#sprints) | Live spray coverage layer | S36 | E4.5 Ground control for Agriculture | ⬜ To do |
| [T4.19](../specs/roadmap/05-p4-agriculture.md#sprints) | Planned refills and battery swaps at design time | S37 | E4.2 Coverage and dose | ⬜ To do |
| [T4.20](../specs/roadmap/05-p4-agriculture.md#sprints) | Dose applied per zone | S37 | E4.6 Records, evidence and licences | ⬜ To do |
| [T4.21](../specs/roadmap/05-p4-agriculture.md#sprints) | Spray map Deliverable with its Evidence record | S37 | E4.6 Records, evidence and licences | ⬜ To do |
| [T4.22](../specs/roadmap/05-p4-agriculture.md#sprints) | Debrief and Scorecard for Agriculture | S38 | E4.6 Records, evidence and licences | ⬜ To do |
| [T4.23](../specs/roadmap/05-p4-agriculture.md#sprints) | Four languages and screenshots of UC-017 | S38 | E4.7 Spray Drones, campaign and beta readiness | ⬜ To do |
| [T4.24](../specs/roadmap/05-p4-agriculture.md#sprints) | Agriculture load test | S38 | E4.7 Spray Drones, campaign and beta readiness | ⬜ To do |
| [T4.25](../specs/roadmap/05-p4-agriculture.md#sprints) | Spreader for the autumn seeding beta | S38 | E4.7 Spray Drones, campaign and beta readiness | ⬜ To do |
| [T4.26](../specs/roadmap/05-p4-agriculture.md#sprints) | Patrol beta fixes (reserved slot) | S38 | E4.8 Patrol beta support (reserved) | ⬜ To do |

## <a id="p5"></a>P5: AI agents, MCP and A2A

Phase page: [🛣️ P5: AI agents, MCP and A2A](../specs/roadmap/06-p5-ai-agents.md).

| Ticket | Title | Sprint | Epic | Status |
| --- | --- | --- | --- | --- |
| [T5.01](../specs/roadmap/06-p5-ai-agents.md#sprints) | Agents service skeleton | S36 | E5.1 Agents service, LLM providers, proposals and evaluations | ⬜ To do |
| [T5.02](../specs/roadmap/06-p5-ai-agents.md#sprints) | LLM provider per Operator | S36 | E5.1 Agents service, LLM providers, proposals and evaluations | ⬜ To do |
| [T5.03](../specs/roadmap/06-p5-ai-agents.md#sprints) | Proposal flow | S37 | E5.1 Agents service, LLM providers, proposals and evaluations | ⬜ To do |
| [T5.04](../specs/roadmap/06-p5-ai-agents.md#sprints) | Agent tools | S37 | E5.1 Agents service, LLM providers, proposals and evaluations | ⬜ To do |
| [T5.05](../specs/roadmap/06-p5-ai-agents.md#sprints) | Evaluations and AI telemetry | S39 | E5.1 Agents service, LLM providers, proposals and evaluations | ⬜ To do |
| [T5.06](../specs/roadmap/06-p5-ai-agents.md#sprints) | Mission assistant graph | S39 | E5.2 Mission assistant | ⬜ To do |
| [T5.07](../specs/roadmap/06-p5-ai-agents.md#sprints) | Rule checks in proposals | S39 | E5.2 Mission assistant | ⬜ To do |
| [T5.08](../specs/roadmap/06-p5-ai-agents.md#sprints) | Mission studio Assistant | S39 | E5.2 Mission assistant | ⬜ To do |
| [T5.09](../specs/roadmap/06-p5-ai-agents.md#sprints) | Mission assistant evaluation set | S40 | E5.2 Mission assistant | ⬜ To do |
| [T5.10](../specs/roadmap/06-p5-ai-agents.md#sprints) | `agents-worker` Deployment | S40 | E5.6 A2A on `agents-a2a` and long runs on `agents-worker` | ⬜ To do |
| [T5.11](../specs/roadmap/06-p5-ai-agents.md#sprints) | Report writer graph | S40 | E5.3 Report writer | ⬜ To do |
| [T5.12](../specs/roadmap/06-p5-ai-agents.md#sprints) | Draft review conversation | S40 | E5.3 Report writer | ⬜ To do |
| [T5.13](../specs/roadmap/06-p5-ai-agents.md#sprints) | Publication with its Evidence record | S40 | E5.3 Report writer | ⬜ To do |
| [T5.14](../specs/roadmap/06-p5-ai-agents.md#sprints) | Report evaluation set | S41 | E5.3 Report writer | ⬜ To do |
| [T5.15](../specs/roadmap/06-p5-ai-agents.md#sprints) | Co-pilot graph on aggregates | S41 | E5.4 Co-pilot | ⬜ To do |
| [T5.16](../specs/roadmap/06-p5-ai-agents.md#sprints) | Co-pilot Re-plan proposals | S41 | E5.4 Co-pilot | ⬜ To do |
| [T5.17](../specs/roadmap/06-p5-ai-agents.md#sprints) | Explanations in Ground control | S41 | E5.4 Co-pilot | ⬜ To do |
| [T5.18](../specs/roadmap/06-p5-ai-agents.md#sprints) | Spoken Alerts | S41 | E5.4 Co-pilot | ⬜ To do |
| [T5.19](../specs/roadmap/06-p5-ai-agents.md#sprints) | Co-pilot evaluation on Replays | S41 | E5.4 Co-pilot | ⬜ To do |
| [T5.20](../specs/roadmap/06-p5-ai-agents.md#sprints) | MCP server tools | S42 | E5.5 MCP server on `agents-mcp` | ⬜ To do |
| [T5.21](../specs/roadmap/06-p5-ai-agents.md#sprints) | OAuth 2.1 delegation | S42 | E5.5 MCP server on `agents-mcp` | ⬜ To do |
| [T5.22](../specs/roadmap/06-p5-ai-agents.md#sprints) | `agents-mcp` Deployment | S42 | E5.5 MCP server on `agents-mcp` | ⬜ To do |
| [T5.23](../specs/roadmap/06-p5-ai-agents.md#sprints) | Human gate in the gateway and the missions service | S42 | E5.7 Human gate for Outside agents | ⬜ To do |
| [T5.24](../specs/roadmap/06-p5-ai-agents.md#sprints) | Confirmation on the person's own device | S42 | E5.7 Human gate for Outside agents | ⬜ To do |
| [T5.25](../specs/roadmap/06-p5-ai-agents.md#sprints) | A2A Agent Cards and tasks | S42 | E5.6 A2A on `agents-a2a` and long runs on `agents-worker` | ⬜ To do |
| [T5.26](../specs/roadmap/06-p5-ai-agents.md#sprints) | `agents-a2a` Deployment | S43 | E5.6 A2A on `agents-a2a` and long runs on `agents-worker` | ⬜ To do |
| [T5.27](../specs/roadmap/06-p5-ai-agents.md#sprints) | Agent rate limits and ledger | S43 | E5.5 MCP server on `agents-mcp` | ⬜ To do |
| [T5.28](../specs/roadmap/06-p5-ai-agents.md#sprints) | Registered outside agents | S43 | E5.6 A2A on `agents-a2a` and long runs on `agents-worker` | ⬜ To do |
| [T5.29](../specs/roadmap/06-p5-ai-agents.md#sprints) | Abuse and injection tests | S43 | E5.7 Human gate for Outside agents | ⬜ To do |
| [T5.30](../specs/roadmap/06-p5-ai-agents.md#sprints) | KEDA load test and beta enablement | S43 | E5.8 Scale proof and beta | ⬜ To do |
| [T5.31](../specs/roadmap/06-p5-ai-agents.md#sprints) | Patrol beta fixes (reserved slot) | S39 | E5.9 Patrol beta support (reserved) | ⬜ To do |

## <a id="p6"></a>P6: Light shows

Phase page: [🛣️ P6: Light shows](../specs/roadmap/07-p6-light-shows.md).

| Ticket | Title | Sprint | Epic | Status |
| --- | --- | --- | --- | --- |
| [T6.01](../specs/roadmap/07-p6-light-shows.md#sprints) | Choreography model and Skybrush Studio import | S41 | E6.1 Choreography model and import | ⬜ To do |
| [T6.02](../specs/roadmap/07-p6-light-shows.md#sprints) | Blender import | S42 | E6.1 Choreography model and import | ⬜ To do |
| [T6.03](../specs/roadmap/07-p6-light-shows.md#sprints) | Separation check per frame (spatial hash grid) | S43 | E6.2 Choreography checks in Rust | ⬜ To do |
| [T6.04](../specs/roadmap/07-p6-light-shows.md#sprints) | Audience, Site obstacles, Geofence, speed and acceleration checks | S44 | E6.2 Choreography checks in Rust | ⬜ To do |
| [T6.05](../specs/roadmap/07-p6-light-shows.md#sprints) | Battery to the end of the show | S44 | E6.2 Choreography checks in Rust | ⬜ To do |
| [T6.06](../specs/roadmap/07-p6-light-shows.md#sprints) | Import and check screens (A1, A2, KO1) | S44 | E6.3 Import screens and built-in designer | ⬜ To do |
| [T6.07](../specs/roadmap/07-p6-light-shows.md#sprints) | Check benchmark: 1,000 Drones over 10 minutes under 30 s | S44 | E6.2 Choreography checks in Rust | ⬜ To do |
| [T6.08](../specs/roadmap/07-p6-light-shows.md#sprints) | Timeline designer, first version | S44 | E6.3 Import screens and built-in designer | ⬜ To do |
| [T6.09](../specs/roadmap/07-p6-light-shows.md#sprints) | Designer 3D preview | S44 | E6.3 Import screens and built-in designer | ⬜ To do |
| [T6.10](../specs/roadmap/07-p6-light-shows.md#sprints) | Show mode of the flight engine: 50 Hz tick, deviation from the Choreography | S45 | E6.4 Flying the show at the edge | ⬜ To do |
| [T6.11](../specs/roadmap/07-p6-light-shows.md#sprints) | Whole-Squad Fail-safe: Hold, land, Held then Aborted | S45 | E6.4 Flying the show at the edge | ⬜ To do |
| [T6.12](../specs/roadmap/07-p6-light-shows.md#sprints) | Time code out and music playing | S45 | E6.4 Flying the show at the edge | ⬜ To do |
| [T6.13](../specs/roadmap/07-p6-light-shows.md#sprints) | Show view of Ground control (A3, OK, KO2) | S45 | E6.4 Flying the show at the edge | ⬜ To do |
| [T6.14](../specs/roadmap/07-p6-light-shows.md#sprints) | Sector split in the planner | S46 | E6.5 Partitioned edge and show coordinator | ⬜ To do |
| [T6.15](../specs/roadmap/07-p6-light-shows.md#sprints) | Sector node: separation across the overlap | S46 | E6.5 Partitioned edge and show coordinator | ⬜ To do |
| [T6.16](../specs/roadmap/07-p6-light-shows.md#sprints) | Show coordinator: time code to every sector, Hold the Squad and land within 100 ms | S46 | E6.5 Partitioned edge and show coordinator | ⬜ To do |
| [T6.17](../specs/roadmap/07-p6-light-shows.md#sprints) | Telemetry to the core at 5 Hz, full-rate log uploaded after landing | S46 | E6.5 Partitioned edge and show coordinator | ⬜ To do |
| [T6.18](../specs/roadmap/07-p6-light-shows.md#sprints) | Synthetic Drones in show mode at 50 Hz | S47 | E6.6 5,000-Drone load test and chaos | ⬜ To do |
| [T6.19](../specs/roadmap/07-p6-light-shows.md#sprints) | Nightly 5,000-Drone show in staging, budgets as assertions | S47 | E6.6 5,000-Drone load test and chaos | ⬜ To do |
| [T6.20](../specs/roadmap/07-p6-light-shows.md#sprints) | Chaos runs on the partitioned edge | S48 | E6.6 5,000-Drone load test and chaos | ⬜ To do |
| [T6.21](../specs/roadmap/07-p6-light-shows.md#sprints) | Show Drone model connected and approved (UC-014), show-light Payload control | S47 | E6.7 Real show | ⬜ To do |
| [T6.22](../specs/roadmap/07-p6-light-shows.md#sprints) | Pre-flight check and landing positions for about 50 Drones | S47 | E6.7 Real show | ⬜ To do |
| [T6.23](../specs/roadmap/07-p6-light-shows.md#sprints) | UC-016 screens to 📸 Screenshot | S48 | E6.7 Real show | ⬜ To do |
| [T6.24](../specs/roadmap/07-p6-light-shows.md#sprints) | Fixes from the rehearsals, Flight log of the show in the evidence ledger | S48 | E6.7 Real show | ⬜ To do |
| [T6.25](../specs/roadmap/07-p6-light-shows.md#sprints) | M6 release: documentation, exit checks | S48 | E6.7 Real show | ⬜ To do |

## <a id="p7"></a>P7: Scale and reach

Phase page: [🛣️ P7: Scale and reach](../specs/roadmap/08-p7-scale-and-reach.md).

| Ticket | Title | Sprint | Epic | Status |
| --- | --- | --- | --- | --- |
| [T7.01](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Staging cell at target: 200 Missions, k6 for 5,000 WebSocket clients, 500 video viewers, budgets as assertions | S45 | E7.1 Cell at target load | ⬜ To do |
| [T7.02](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Operator isolation suite at scale | S45 | E7.3 Operators at scale | ⬜ To do |
| [T7.03](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | OVHcloud cell hardened to target size for production, canary | S46 | E7.2 EU production cells and global layer | ⬜ To do |
| [T7.04](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Global layer in two EU regions, active and standby | S46 | E7.2 EU production cells and global layer | ⬜ To do |
| [T7.05](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Scaleway production cell, created with Terraform | S47 | E7.2 EU production cells and global layer | ⬜ To do |
| [T7.06](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Release waves across cells, stopped and rolled back on an SLO burn | S47 | E7.2 EU production cells and global layer | ⬜ To do |
| [T7.07](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Move an Operator between cells in a planned window | S48 | E7.2 EU production cells and global layer | ⬜ To do |
| [T7.08](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | DJI Drone adapter sidecar | S48 | E7.7 DJI and Skydio Drone adapters | ⬜ To do |
| [T7.09](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Skydio Drone adapter sidecar | S49 | E7.7 DJI and Skydio Drone adapters | ⬜ To do |
| [T7.10](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Compatibility suites for the vendor adapters, firmware re-approval | S49 | E7.7 DJI and Skydio Drone adapters | ⬜ To do |
| [T7.11](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | US self-hosted cell on k3s and MinIO | S49 | E7.4 US self-hosted cell | ⬜ To do |
| [T7.12](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Residency: US Operators in US cells | S49 | E7.4 US self-hosted cell | ⬜ To do |
| [T7.13](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | US Jurisdiction in Authorisations, from [🏛️ G-09](../specs/roadmap/09-regulatory-track.md#g-09) | S49 | E7.4 US self-hosted cell | ⬜ To do |
| [T7.14](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Edge appliance rings | S49 | E7.6 Edge appliance rings | ⬜ To do |
| [T7.15](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Signed offline bundle | S50 | E7.5 On-premises bundle | ⬜ To do |
| [T7.16](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Bundle installer, verification and updates | S50 | E7.5 On-premises bundle | ⬜ To do |
| [T7.17](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | On-premises install on [🤝 H-08](../specs/roadmap/11-hardware-and-partners.md#h-08) | S50 | E7.5 On-premises bundle | ⬜ To do |
| [T7.18](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Blockchain Anchoring through an aggregator | S50 | E7.8 Blockchain Anchoring | ⬜ To do |
| [T7.19](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Anchoring choice per Operator, verification with a blockchain receipt | S50 | E7.8 Blockchain Anchoring | ⬜ To do |
| [T7.20](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Cell rebuild and restore drill at target | S50 | E7.1 Cell at target load | ⬜ To do |
| [T7.21](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Chaos at target load | S51 | E7.1 Cell at target load | ⬜ To do |
| [T7.22](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Four-language audit of every screen and Notification | S51 | E7.3 Operators at scale | ⬜ To do |
| [T7.23](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Operator onboarding in the production cells | S51 | E7.3 Operators at scale | ⬜ To do |
| [T7.24](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Cross-cell SLO dashboards, on-call alerting | S51 | E7.1 Cell at target load | ⬜ To do |
| [T7.25](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Real compatibility flights of Matrice 4TD and X10 | S51 | E7.7 DJI and Skydio Drone adapters | ⬜ To do |
| [T7.26](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | C-07 fixes, Inspection and Patrol | S52 | E7.9 General availability | ⬜ To do |
| [T7.27](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | C-07 fixes, Agriculture and Light show | S52 | E7.9 General availability | ⬜ To do |
| [T7.28](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Release candidate: Trivy, OSV-Scanner, SBOM, cosign signatures | S52 | E7.9 General availability | ⬜ To do |
| [T7.29](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | General availability release, cells in waves, edges in rings | S52 | E7.9 General availability | ⬜ To do |
| [T7.30](../specs/roadmap/08-p7-scale-and-reach.md#sprints) | Last screens to 📸 Screenshot, `specs.py check` | S52 | E7.9 General availability | ⬜ To do |
