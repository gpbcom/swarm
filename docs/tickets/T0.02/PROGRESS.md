# T0.02: Progress

**Status:** 🟡 Planned · **Ticket:** [TICKET.md](TICKET.md)

<!-- ticket:specs -->
## 📚 Specifications

The technical pages, features, use cases and business rules of [TICKET.md](TICKET.md), copied by `python3 .claude/scripts/tickets/ticket_refs.py sync`.

- [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo)
- [🧅 Architecture: layers inside each service](../../specs/technical/01-architecture.md#layers)
- [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci)
<!-- /ticket:specs -->

## 📝 Events

| Time | Event | By | Result |
| --- | --- | --- | --- |
| 2026-11-19 09:08 | Plan written: 19 tasks, 3 waves | ticket-plan | ⏳ Awaiting approval |
| 2026-11-19 09:10 | Plan approved | the person | ✅ Approved |
| 2026-11-19 09:15 | PLAN.md re-rendered by `plan.py render` into the readable format (waves, dependency graph, task details); the json task graph is unchanged and the plan stays approved | main session | ✅ Done |
| 2026-11-19 09:19 | TICKET.md links its technical pages (mono-repo, layers, CI/CD), copied into PLAN.md and PROGRESS.md by `ticket_refs.py sync` (TKT-2); task graph unchanged, plan stays approved | main session | ✅ Done |
| 2026-11-19 09:27 | Wave 1: 7 of 7 tasks done | workers | ✅ |
| 2026-11-19 09:27 | Merge (Waves) | integrator | ✅ 7 merged, 0 blocked |
| 2026-11-19 09:27 | Wave 2: 9 of 10 tasks done | workers | ❌ |
| 2026-11-19 09:27 | Merge (Waves) | integrator | ✅ 9 merged, 0 blocked |
| 2026-11-19 09:27 | Stopped in wave 2: K07 not done | ticket-run | ❌ |
| 2026-11-19 09:28 | K07 blocked by a defect in K01's helper (`tests/harness/check_ticket/helpers.py` built `specs/screens/screens/...`); the person chose to fix it and re-run | the person | ✅ Decided |
| 2026-11-19 09:28 | Gate defect: the gate agent returned placeholder briefs ("See PLAN.md json block") instead of copying them, so workers read PLAN.md themselves. Fixed: the gate returns `plan.py outline`, and each worker reads its exact brief with `plan.py task` | main session | ✅ Fixed |
| 2026-11-19 09:28 | K01 helper fixed; K07's script passes its 31 tests with it; `check_plan.py` passes on T0.01 and T0.02; wiring tests pass | main session | ✅ Done |
| 2026-11-19 09:34 | Wave 2: 1 of 1 tasks done | workers | ✅ |
| 2026-11-19 09:34 | Merge (Waves) | integrator | ✅ 1 merged, 0 blocked |
| 2026-11-19 09:34 | Wave 3: 2 of 2 tasks done | workers | ✅ |
| 2026-11-19 09:34 | Merge (Waves) | integrator | ✅ 2 merged, 0 blocked |
| 2026-11-19 09:34 | Verify 1 | verifier | ✅ passed |
| 2026-11-19 09:34 | Review 1 (full) | reviewer | ✅ 0 blocking, 5 follow-ups |
| 2026-11-19 09:34 | Merge into develop | integrator | ✅ merged locally, not pushed |

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| `.claude/workflows/ticket-run.js:239` (`ownerOf`) with `workerPrompt` at `:119-127` | Since commit 3a63742, a fix task that matches no plan task (id `FIX-<file>`, brief `''`) is told to run `plan.py task --id FIX-<file>`. That command can only print `Unknown task`, and the fixer never sees its `done_when`. Test the id against `K\d{2}` instead of testing for an empty brief, or give FIX tasks a non-empty brief so they keep the old `Brief` / `Done when` lines. Owner: main-session harness commit 3a63742, outside any K task. |
| `.claude/skills/ticket/SKILL.md` (Plan section) | SKILL.md says TICKET.md is "fixed at most twice". TKT-2 and `ticket-plan.js` send it back to the ticket-writer once and then stop. Change it to "once". Owner: K18. |
| `.claude/skills/ticket/SKILL.md` (intro and Hooks section) | The intro cites "TKT-1 to TKT-12". Make it TKT-1 to TKT-13. Also, "The hooks do nothing outside a linked worktree" is only true of `check_touched.py`: `format_edited.py` formats matching files in any checkout. Say that the SubagentStop hook is the one limited to worktrees. Owner: K18. |
| `docs/tickets/README.md` (line after the steps table) | SKILL.md is now on `ticket/T0.02`. Re-add the link to `.claude/skills/ticket/SKILL.md` that K19 dropped while it did not exist yet. Owner: K19. |
| `.claude/workflows/ticket-plan.js` (Check phase) | The ticket-writer's fix result is not kept, so `ticket.specs` and `ticket.assumptions` returned at the end still come from the first, failing TICKET.md. Assign the fix result to `ticket` when it is present. Owner: K16. |

<!-- timings -->
## ⏱️ Timings

Measured from the agents' transcripts by `python3 .claude/scripts/reports/progress.py timings --ticket T0.02` (TKT-10).

| Measure | Value |
| --- | --- |
| 🕒 Ticket started | 2026-11-19 08:54:42 |
| 🕒 Last activity | 2026-11-19 09:34:55 |
| ⏱️ **Overall ticket time** (first start to last activity) | **40m13s** |
| 🤖 Time with agents working (sum of runs) | 25m17s |
| ⏸️ Time between runs (approvals, fixes) | 14m56s |
| 🔁 Workflow runs | 3 |
| 🪙 **Tokens consumed** (input, output, cache write, cache read) | **25.19M** |

#### 🪙 Tokens by model

| Model | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- |
| 🔵 sonnet | 0k | 283k | 1.28M | 8.84M | **10.40M** |
| 🟣 opus | 0k | 199k | 706k | 6.55M | **7.45M** |
| 🟢 haiku | 0k | 187k | 1.23M | 5.92M | **7.34M** |
| **All models** | 0k | 670k | 3.21M | 21.31M | **25.19M** |

### 1. ticket-plan · 2026-11-19 08:54:42 to 09:08:41 · ⏱️ 13m58s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Ticket | 08:54:42 | 08:55:01 | 0m19s | 1 |
| Plan | 08:55:02 | 09:07:08 | 12m06s | 1 |
| Write | 09:07:08 | 09:08:41 | 1m32s | 1 |

Tokens of this run: 0k · 248k · 832k · 6.07M · **7.15M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ ticket-writer T0.02 | 🔵 sonnet | 08:54:42 | 08:55:01 | 0m19s | 0k | 10k | 147k | 268k | **425k** |
| ✅ planner T0.02 | 🟣 opus | 08:55:02 | 09:07:08 | 12m06s | 0k | 176k | 478k | 4.99M | **5.64M** |
| ✅ scribe T0.02 | 🟢 haiku | 09:07:08 | 09:08:41 | 1m32s | 0k | 61k | 206k | 815k | **1.08M** |

### 2. ticket-run · 2026-11-19 09:21:51 to 09:27:08 · ⏱️ 5m16s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 09:21:51 | 09:22:19 | 0m28s | 2 |
| Waves | 09:22:20 | 09:27:08 | 4m47s | 21 |
| Verify | | | not run | 0 |
| Review | | | not run | 0 |
| Finish | | | not run | 0 |

Tokens of this run: 0k · 318k · 1.49M · 10.26M · **12.07M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.02 | 🟢 haiku | 09:21:51 | 09:22:14 | 0m22s | 0k | 10k | 110k | 329k | **450k** |
| ✅ integrator prepare T0.02 | 🔵 sonnet | 09:22:14 | 09:22:19 | 0m05s | 0k | 0k | 32k | 60k | **93k** |
| ✅ K01 test-writer | 🔵 sonnet | 09:22:20 | 09:23:46 | 1m26s | 0k | 26k | 75k | 677k | **779k** |
| ✅ K02 test-writer | 🔵 sonnet | 09:22:20 | 09:23:23 | 1m03s | 0k | 19k | 58k | 592k | **671k** |
| ✅ K03 test-writer | 🔵 sonnet | 09:22:20 | 09:23:15 | 0m55s | 0k | 19k | 65k | 524k | **610k** |
| ✅ K04 test-writer | 🔵 sonnet | 09:22:20 | 09:23:40 | 1m19s | 0k | 32k | 80k | 797k | **910k** |
| ✅ K05 test-writer | 🔵 sonnet | 09:22:20 | 09:23:20 | 0m59s | 0k | 29k | 74k | 774k | **878k** |
| ✅ K06 doc-writer | 🟢 haiku | 09:22:20 | 09:22:40 | 0m19s | 0k | 13k | 95k | 334k | **442k** |
| ✅ K14 doc-writer | 🟢 haiku | 09:22:20 | 09:22:46 | 0m26s | 0k | 25k | 133k | 742k | **902k** |
| ✅ integrator Waves | 🔵 sonnet | 09:23:47 | 09:23:56 | 0m09s | 0k | 0k | 31k | 132k | **165k** |
| ❌ K07 implementer | 🔵 sonnet | 09:23:57 | 09:25:21 | 1m24s | 0k | 30k | 84k | 725k | **841k** |
| ✅ K08 implementer | 🔵 sonnet | 09:23:57 | 09:24:37 | 0m40s | 0k | 10k | 53k | 361k | **426k** |
| ✅ K09 implementer | 🔵 sonnet | 09:23:57 | 09:24:39 | 0m42s | 0k | 10k | 52k | 511k | **574k** |
| ✅ K10 implementer | 🔵 sonnet | 09:23:57 | 09:25:17 | 1m20s | 0k | 28k | 84k | 710k | **823k** |
| ✅ K11 implementer | 🔵 sonnet | 09:23:57 | 09:24:19 | 0m21s | 0k | 3k | 37k | 251k | **292k** |
| ✅ K12 doc-writer | 🟢 haiku | 09:23:57 | 09:24:15 | 0m18s | 0k | 5k | 63k | 265k | **334k** |
| ✅ K13 doc-writer | 🟢 haiku | 09:23:57 | 09:24:15 | 0m17s | 0k | 6k | 71k | 417k | **495k** |
| ✅ K15 doc-writer | 🟢 haiku | 09:23:57 | 09:24:17 | 0m19s | 0k | 6k | 49k | 451k | **507k** |
| ✅ K16 implementer | 🔵 sonnet | 09:24:15 | 09:24:35 | 0m20s | 0k | 3k | 38k | 181k | **222k** |
| ✅ K17 implementer | 🔵 sonnet | 09:24:16 | 09:24:37 | 0m20s | 0k | 2k | 39k | 229k | **270k** |
| ❌ K07 implementer | 🔵 sonnet | 09:25:22 | 09:26:46 | 1m24s | 0k | 29k | 75k | 826k | **931k** |
| ✅ integrator Waves | 🔵 sonnet | 09:26:47 | 09:26:59 | 0m11s | 0k | 2k | 39k | 161k | **203k** |
| ✅ scribe T0.02 | 🟢 haiku | 09:27:00 | 09:27:08 | 0m07s | 0k | 2k | 41k | 195k | **239k** |

### 3. ticket-run · 2026-11-19 09:28:54 to 09:34:55 · ⏱️ 6m01s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 09:28:54 | 09:29:28 | 0m34s | 3 |
| Waves | 09:29:29 | 09:32:14 | 2m44s | 6 |
| Verify | 09:32:15 | 09:32:25 | 0m09s | 1 |
| Review | 09:32:26 | 09:34:11 | 1m45s | 1 |
| Finish | 09:34:12 | 09:34:55 | 0m43s | 2 |

Tokens of this run: 0k · 103k · 892k · 4.98M · **5.97M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.02 | 🟢 haiku | 09:28:54 | 09:29:20 | 0m26s | 0k | 12k | 123k | 460k | **596k** |
| ✅ plan check T0.02 | 🟢 haiku | 09:29:20 | 09:29:23 | 0m03s | 0k | 0k | 34k | 55k | **90k** |
| ✅ integrator prepare T0.02 | 🔵 sonnet | 09:29:24 | 09:29:28 | 0m04s | 0k | 0k | 28k | 32k | **60k** |
| ✅ K07 implementer | 🔵 sonnet | 09:29:29 | 09:30:55 | 1m26s | 0k | 20k | 71k | 639k | **731k** |
| ✅ integrator Waves | 🔵 sonnet | 09:30:57 | 09:31:06 | 0m09s | 0k | 1k | 32k | 124k | **158k** |
| ✅ K18 doc-writer | 🟢 haiku | 09:31:08 | 09:31:36 | 0m28s | 0k | 14k | 64k | 447k | **525k** |
| ❌ K19 doc-writer | 🟢 haiku | 09:31:08 | 09:31:29 | 0m21s | 0k | 6k | 48k | 444k | **499k** |
| ✅ K19 doc-writer | 🟢 haiku | 09:31:37 | 09:32:01 | 0m23s | 0k | 8k | 57k | 603k | **669k** |
| ✅ integrator Waves | 🔵 sonnet | 09:32:01 | 09:32:14 | 0m12s | 0k | 1k | 34k | 125k | **161k** |
| ✅ verifier round 1 | 🟢 haiku | 09:32:15 | 09:32:25 | 0m09s | 0k | 0k | 31k | 59k | **91k** |
| ✅ reviewer round 1 | 🟣 opus | 09:32:26 | 09:34:11 | 1m45s | 0k | 22k | 228k | 1.56M | **1.81M** |
| ✅ integrator finish T0.02 | 🔵 sonnet | 09:34:12 | 09:34:23 | 0m11s | 0k | 1k | 36k | 127k | **166k** |
| 🔄 scribe T0.02 | 🟢 haiku | 09:34:24 | 09:34:55 | 0m31s | 0k | 14k | 100k | 296k | **411k** |
<!-- /timings -->
