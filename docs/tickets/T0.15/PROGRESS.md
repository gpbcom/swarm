# T0.15: Progress

**Status:** 🟡 Planned

<!-- ticket:specs -->
## 📚 Specifications

The technical pages, features, use cases and business rules of [TICKET.md](TICKET.md), copied by `python3 .claude/scripts/tickets/ticket_refs.py sync`.

- [🖥️ GUI and WebUI: apps and shared packages](../../specs/technical/10-frontends.md#apps)
- [🔩 Engine and services](../../specs/technical/04-engine.md)
- [📏 BR-017: Every screen in four languages](../../specs/functional/business-rules/BR-017-every-screen-in-four-languages.md)
- [📘 FS-012: Operators, deployment and languages](../../specs/functional/features/FS-012-operators-deployment-and-languages.md)
- [🏗️ Architecture](../../specs/technical/01-architecture.md)
- [🎬 UC-023](../../specs/functional/use-cases/UC-023-configure-the-workspace-of-ground-control.md)
- [🎬 UC-015](../../specs/functional/use-cases/UC-015-invite-a-client-to-the-client-portal.md)
<!-- /ticket:specs -->

## 📝 Events

| Time | Event | By | Result |
| --- | --- | --- | --- |
| 2026-11-20 13:55 | Plan written: 19 tasks, 6 waves | planner, scribe | ⏳ Awaiting approval |
| 2026-11-20 14:10 | Plan approved by the person (group approval) | 👤 person | 🟢 Approved |

<!-- timings -->
## ⏱️ Timings

Measured from the agents' transcripts by `python3 .claude/scripts/reports/progress.py timings --ticket T0.15` (TKT-10).

| Measure | Value |
| --- | --- |
| 🕒 Ticket started | 2026-11-20 13:43:42 |
| 🕒 Last activity | 2026-11-20 13:55:39 |
| ⏱️ **Overall ticket time** (first start to last activity) | **11m56s** |
| 🤖 Time with agents working (sum of runs) | 11m56s |
| ⏸️ Time between runs (approvals, fixes) | 0m00s |
| 🔁 Workflow runs | 1 |
| 🪙 **Tokens consumed** (input, output, cache write, cache read) | **11.83M** |

#### 🪙 Tokens by model

| Model | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- |
| 🟢 haiku | 0k | 50k | 361k | 781k | **1.19M** |
| 🔵 sonnet | 0k | 17k | 177k | 998k | **1.19M** |
| 🟣 opus | 0k | 152k | 389k | 8.90M | **9.44M** |
| **All models** | 0k | 220k | 929k | 10.68M | **11.83M** |

### 1. ticket-plan · 2026-11-20 13:43:42 to 13:55:39 · ⏱️ 11m56s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Ticket | 13:43:42 | 13:44:32 | 0m49s | 2 |
| Check | 13:44:33 | 13:44:36 | 0m03s | 1 |
| Plan | 13:44:37 | 13:54:23 | 9m46s | 1 |
| Write | 13:54:24 | 13:55:39 | 1m14s | 1 |

Tokens of this run: 0k · 220k · 929k · 10.68M · **11.83M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ done check T0.15 | 🟢 haiku | 13:43:42 | 13:43:55 | 0m12s | 0k | 0k | 96k | 102k | **200k** |
| ✅ ticket-writer T0.15 | 🔵 sonnet | 13:43:57 | 13:44:32 | 0m34s | 0k | 17k | 177k | 998k | **1.19M** |
| ✅ check TICKET.md T0.15 | 🟢 haiku | 13:44:33 | 13:44:36 | 0m03s | 0k | 0k | 51k | 99k | **151k** |
| ✅ planner T0.15 | 🟣 opus | 13:44:37 | 13:54:23 | 9m46s | 0k | 152k | 389k | 8.90M | **9.44M** |
| 🔄 scribe T0.15 | 🟢 haiku | 13:54:24 | 13:55:39 | 1m14s | 0k | 49k | 214k | 578k | **842k** |
<!-- /timings -->
