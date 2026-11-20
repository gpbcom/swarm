# T0.17: Progress

**Status:** 🟡 Planned · **Ticket:** [TICKET.md](TICKET.md)

<!-- ticket:specs -->
## 📚 Specifications

The technical pages, features, use cases and business rules of [TICKET.md](TICKET.md), copied by `python3 .claude/scripts/tickets/ticket_refs.py sync`.

- [🩺 Observability: signals](../../specs/technical/08-observability.md#signals)
<!-- /ticket:specs -->

## 📝 Events

| Time | Event | By | Result |
| --- | --- | --- | --- |
| 2026-11-20 13:58 | Plan written: 30 tasks, 4 waves | scribe | ⏳ Awaiting approval |
| 2026-11-20 14:10 | Plan approved by the person (group approval) | 👤 person | 🟢 Approved |

<!-- timings -->
## ⏱️ Timings

Measured from the agents' transcripts by `python3 .claude/scripts/reports/progress.py timings --ticket T0.17` (TKT-10).

| Measure | Value |
| --- | --- |
| 🕒 Ticket started | 2026-11-20 13:43:42 |
| 🕒 Last activity | 2026-11-20 14:00:28 |
| ⏱️ **Overall ticket time** (first start to last activity) | **16m46s** |
| 🤖 Time with agents working (sum of runs) | 16m46s |
| ⏸️ Time between runs (approvals, fixes) | 0m00s |
| 🔁 Workflow runs | 1 |
| 🪙 **Tokens consumed** (input, output, cache write, cache read) | **13.37M** |

#### 🪙 Tokens by model

| Model | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- |
| 🟢 haiku | 0k | 128k | 453k | 753k | **1.34M** |
| 🔵 sonnet | 0k | 12k | 184k | 1.22M | **1.42M** |
| 🟣 opus | 0k | 220k | 371k | 10.02M | **10.61M** |
| **All models** | 0k | 361k | 1.01M | 12.00M | **13.37M** |

### 1. ticket-plan · 2026-11-20 13:43:42 to 14:00:28 · ⏱️ 16m46s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Ticket | 13:43:42 | 13:44:30 | 0m48s | 2 |
| Check | 13:44:31 | 13:44:35 | 0m03s | 1 |
| Plan | 13:44:36 | 13:58:24 | 13m48s | 1 |
| Write | 13:58:24 | 14:00:28 | 2m04s | 1 |

Tokens of this run: 0k · 361k · 1.01M · 12.00M · **13.37M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ done check T0.17 | 🟢 haiku | 13:43:42 | 13:43:55 | 0m13s | 0k | 1k | 96k | 102k | **200k** |
| ✅ ticket-writer T0.17 | 🔵 sonnet | 13:43:57 | 13:44:30 | 0m33s | 0k | 12k | 184k | 1.22M | **1.42M** |
| ✅ check TICKET.md T0.17 | 🟢 haiku | 13:44:31 | 13:44:35 | 0m03s | 0k | 0k | 51k | 99k | **151k** |
| ✅ planner T0.17 | 🟣 opus | 13:44:36 | 13:58:24 | 13m48s | 0k | 220k | 371k | 10.02M | **10.61M** |
| 🔄 scribe T0.17 | 🟢 haiku | 13:58:24 | 14:00:28 | 2m04s | 0k | 127k | 305k | 551k | **983k** |
<!-- /timings -->
