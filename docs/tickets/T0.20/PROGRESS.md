# T0.20: Progress

**Status:** 🟡 Planned

<!-- ticket:specs -->
## 📚 Specifications

The technical pages, features, use cases and business rules of [TICKET.md](TICKET.md), copied by `python3 .claude/scripts/tickets/ticket_refs.py sync`.

- [🖥️ GUI and WebUI: design system](../../specs/technical/10-frontends.md#design-system)
- [🎬 UC-029: Create an Operator](../../specs/functional/use-cases/UC-029-create-an-operator.md)
- [📏 BR-008: Operator isolation](../../specs/functional/business-rules/BR-008-operator-isolation.md)
- [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci)
- [🖼️ UC-029 A1](../../specs/functional/use-cases/UC-029-create-an-operator.md#screen-a1)
- [🖼️ UC-029 KO](../../specs/functional/use-cases/UC-029-create-an-operator.md#screen-ko)
- [🖼️ UC-029 A2](../../specs/functional/use-cases/UC-029-create-an-operator.md#screen-a2)
- [🖼️ UC-029 OK](../../specs/functional/use-cases/UC-029-create-an-operator.md#screen-ok)
<!-- /ticket:specs -->

## 📝 Events

| Time | Event | By | Result |
| --- | --- | --- | --- |
| 2026-11-20 13:50 | Plan written: 8 tasks, 4 waves | scribe | ⏳ Awaiting approval |
| 2026-11-20 14:10 | Plan approved by the person (group approval) | 👤 person | 🟢 Approved |

<!-- timings -->
## ⏱️ Timings

Measured from the agents' transcripts by `python3 .claude/scripts/reports/progress.py timings --ticket T0.20` (TKT-10).

| Measure | Value |
| --- | --- |
| 🕒 Ticket started | 2026-11-20 13:43:42 |
| 🕒 Last activity | 2026-11-20 13:50:26 |
| ⏱️ **Overall ticket time** (first start to last activity) | **6m43s** |
| 🤖 Time with agents working (sum of runs) | 6m43s |
| ⏸️ Time between runs (approvals, fixes) | 0m00s |
| 🔁 Workflow runs | 1 |
| 🪙 **Tokens consumed** (input, output, cache write, cache read) | **6.82M** |

#### 🪙 Tokens by model

| Model | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- |
| 🟢 haiku | 0k | 40k | 308k | 747k | **1.10M** |
| 🔵 sonnet | 0k | 14k | 220k | 1.12M | **1.36M** |
| 🟣 opus | 0k | 66k | 305k | 3.99M | **4.36M** |
| **All models** | 0k | 120k | 834k | 5.86M | **6.82M** |

### 1. ticket-plan · 2026-11-20 13:43:42 to 13:50:26 · ⏱️ 6m43s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Ticket | 13:43:42 | 13:44:33 | 0m50s | 2 |
| Check | 13:44:34 | 13:44:37 | 0m03s | 1 |
| Plan | 13:44:38 | 13:49:40 | 5m02s | 1 |
| Write | 13:49:40 | 13:50:26 | 0m45s | 1 |

Tokens of this run: 0k · 120k · 834k · 5.86M · **6.82M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ done check T0.20 | 🟢 haiku | 13:43:42 | 13:43:55 | 0m12s | 0k | 0k | 96k | 102k | **199k** |
| ✅ ticket-writer T0.20 | 🔵 sonnet | 13:43:57 | 13:44:33 | 0m35s | 0k | 14k | 220k | 1.12M | **1.36M** |
| ✅ check TICKET.md T0.20 | 🟢 haiku | 13:44:34 | 13:44:37 | 0m03s | 0k | 0k | 51k | 99k | **151k** |
| ✅ planner T0.20 | 🟣 opus | 13:44:38 | 13:49:40 | 5m02s | 0k | 66k | 305k | 3.99M | **4.36M** |
| 🔄 scribe T0.20 | 🟢 haiku | 13:49:40 | 13:50:26 | 0m45s | 0k | 38k | 160k | 545k | **744k** |
<!-- /timings -->
