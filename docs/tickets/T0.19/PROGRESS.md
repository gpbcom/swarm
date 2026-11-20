# T0.19: Progress

**Status:** 🟡 Planned

<!-- ticket:specs -->
## 📚 Specifications

The technical pages, features, use cases and business rules of [TICKET.md](TICKET.md), copied by `python3 .claude/scripts/tickets/ticket_refs.py sync`.

- [📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md)
- [🖥️ GUI and WebUI: apps and shared packages](../../specs/technical/10-frontends.md#apps)
- [🗺️ GUI and WebUI: maps and 3D](../../specs/technical/10-frontends.md#maps)
- [📨 GUI and WebUI: live data in the browser](../../specs/technical/10-frontends.md#live-data)
- [📨 API layer: live data over WebSocket](../../specs/technical/05-api.md#live)
- [🎨 GUI and WebUI: design system](../../specs/technical/10-frontends.md#design-system)
- [📏 BR-023](../../specs/functional/business-rules/BR-023-fixed-safety-controls.md)
- [🩺 Observability: signals](../../specs/technical/08-observability.md#signals)
- [🎬 UC-025: Monitor a Mission in Ground control](../../specs/functional/use-cases/UC-025-monitor-a-mission-in-ground-control.md)
- [⏱️ GUI and WebUI: front-end budgets](../../specs/technical/10-frontends.md#performance)
- [🖼️ UC-025 A1](../../specs/functional/use-cases/UC-025-monitor-a-mission-in-ground-control.md#screen-a1)
- [⏱️ Telemetry, Drone to Pilot's screen](../../specs/technical/07-scalability.md#budgets)
<!-- /ticket:specs -->

## 📝 Events

| Time | Event | By | Result |
| --- | --- | --- | --- |
| 2026-11-20 13:53 | Plan written: 19 tasks, 6 waves | planner | ⏳ Awaiting approval |
| 2026-11-20 14:10 | Plan approved by the person (group approval) | 👤 person | 🟢 Approved |

<!-- timings -->
## ⏱️ Timings

Measured from the agents' transcripts by `python3 .claude/scripts/reports/progress.py timings --ticket T0.19` (TKT-10).

| Measure | Value |
| --- | --- |
| 🕒 Ticket started | 2026-11-20 13:43:42 |
| 🕒 Last activity | 2026-11-20 13:53:57 |
| ⏱️ **Overall ticket time** (first start to last activity) | **10m15s** |
| 🤖 Time with agents working (sum of runs) | 10m15s |
| ⏸️ Time between runs (approvals, fixes) | 0m00s |
| 🔁 Workflow runs | 1 |
| 🪙 **Tokens consumed** (input, output, cache write, cache read) | **8.17M** |

#### 🪙 Tokens by model

| Model | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- |
| 🟢 haiku | 0k | 78k | 358k | 1.36M | **1.80M** |
| 🔵 sonnet | 0k | 24k | 247k | 1.75M | **2.02M** |
| 🟣 opus | 0k | 123k | 259k | 3.97M | **4.35M** |
| **All models** | 0k | 226k | 866k | 7.08M | **8.17M** |

### 1. ticket-plan · 2026-11-20 13:43:42 to 13:53:57 · ⏱️ 10m15s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Ticket | 13:43:42 | 13:44:45 | 1m02s | 2 |
| Check | 13:44:46 | 13:44:49 | 0m03s | 1 |
| Plan | 13:44:50 | 13:52:28 | 7m38s | 1 |
| Write | 13:52:28 | 13:53:57 | 1m28s | 1 |

Tokens of this run: 0k · 226k · 866k · 7.08M · **8.17M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ done check T0.19 | 🟢 haiku | 13:43:42 | 13:43:55 | 0m12s | 0k | 0k | 96k | 102k | **199k** |
| ✅ ticket-writer T0.19 | 🔵 sonnet | 13:43:57 | 13:44:45 | 0m47s | 0k | 24k | 247k | 1.75M | **2.02M** |
| ✅ check TICKET.md T0.19 | 🟢 haiku | 13:44:46 | 13:44:49 | 0m03s | 0k | 0k | 51k | 99k | **151k** |
| ✅ planner T0.19 | 🟣 opus | 13:44:50 | 13:52:28 | 7m38s | 0k | 123k | 259k | 3.97M | **4.35M** |
| 🔄 scribe T0.19 | 🟢 haiku | 13:52:28 | 13:53:57 | 1m28s | 0k | 77k | 211k | 1.16M | **1.45M** |
<!-- /timings -->
