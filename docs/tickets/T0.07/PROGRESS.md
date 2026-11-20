# T0.07: Progress

**Status:** 🟡 Planned · **Ticket:** [TICKET.md](TICKET.md)

<!-- ticket:specs -->
## 📚 Specifications

The technical pages, features, use cases and business rules of [TICKET.md](TICKET.md), copied by `python3 .claude/scripts/tickets/ticket_refs.py sync`.

- [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo)
- [🔩 Engine and services: flight engine](../../specs/technical/04-engine.md#flight-engine)
- [🏋️ Scalability and performance: load tests](../../specs/technical/07-scalability.md#load-tests)
<!-- /ticket:specs -->

## 📝 Events

| Time | Event | By | Result |
| --- | --- | --- | --- |
| 2026-11-19 11:23 | Plan written: 13 tasks, 3 waves | ticket-plan | ⏳ Awaiting approval |
| 2026-11-19 11:25 | Plan approved | the person | ✅ Approved |
| 2026-11-19 12:01 | Wave 1: 8 of 8 tasks done | workers | ✅ |
| 2026-11-19 12:01 | Integrate (Waves) | integrator | ✅ 8 integrated, 0 blocked, not committed |
| 2026-11-19 12:01 | Wave 2: 3 of 3 tasks done | workers | ✅ |
| 2026-11-19 12:01 | Integrate (Waves) | integrator | ✅ 3 integrated, 0 blocked, not committed |
| 2026-11-19 12:01 | Wave 3: 2 of 2 tasks done | workers | ✅ |
| 2026-11-19 12:01 | Integrate (Waves) | integrator | ✅ 2 integrated, 0 blocked, not committed |
| 2026-11-19 12:01 | Verify 1 (2 not applicable) | verifier | ✅ passed |
| 2026-11-19 12:01 | Review 1 (full) | reviewer | ⚠️ 1 blocking, 5 follow-ups |
| 2026-11-19 12:01 | Review 2 (confirm fixes) | reviewer | ⚠️ 1 blocking, 1 follow-ups |
| 2026-11-19 12:01 | Integrate (Review) | integrator | ✅ 1 integrated, 0 blocked, not committed |
| 2026-11-19 12:01 | Review 3 (confirm fixes) | reviewer | ✅ 0 blocking, 2 follow-ups |

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| `packages/rust/swarm-core/python/pyproject.toml` | Remove `skip-auditwheel = true`, added only to make the xdist race happen less often, once the race is fixed, so the wheel is checked for manylinux compliance again. Or write down in Notes why it stays. |
| `.github/scripts/bench_gate.py` | Fail only when the lower bound of `mean.confidence_interval` is above the threshold, or when a regression also shows on a rerun. A +12.15 % failure on identical code (K13 evidence) shows that the gate compares only `mean.point_estimate`. Keep the "> 5 % fails" contract and its tests. |
| `tests/rust/swarm_core/test_swarm_core_wheel.py` | Make `built` a `@classmethod` under `@pytest.fixture(scope="class")`, or move it to a `conftest.py` in `tests/rust/swarm_core/` (lines 15-20). pytest warns `PytestRemovedIn10Warning` because the class-scoped fixture is an instance method. |
| `docs/tickets/T0.07/tests-evidences/ruff-check.txt` | Add `.github/scripts/bench_gate.py` to the ruff check and ruff format commands and their evidence, because CI's repository job lints `.github/scripts`. |
| `tests/ci/workflows/test_rust_workflow.py` | Find the comparison step by `--baseline-lenient pr-base` instead of the exact flag order `cargo bench --workspace --locked`, so the test does not depend on flag order. |
| `docs/tickets/T0.07/tests-evidences/pytest-n2-run1.txt` | Refresh the three `-n 2` runs (`pytest-n2-run1.txt` to `pytest-n2-run3.txt`) so that each file starts with the command `uv run pytest tests/rust/swarm_core -n 2`, and without the uv VIRTUAL_ENV warning, since they were made in the worker worktree. Owner: K05. |

<!-- timings -->
## ⏱️ Timings

Measured from the agents' transcripts by `python3 .claude/scripts/reports/progress.py timings --ticket T0.07` (TKT-10).

| Measure | Value |
| --- | --- |
| 🕒 Ticket started | 2026-11-19 11:14:18 |
| 🕒 Last activity | 2026-11-19 12:02:46 |
| ⏱️ **Overall ticket time** (first start to last activity) | **48m28s** |
| 🤖 Time with agents working (sum of runs) | 23m56s |
| ⏸️ Time between runs (approvals, fixes) | 24m31s |
| 🔁 Workflow runs | 3 |
| 🪙 **Tokens consumed** (input, output, cache write, cache read) | **18.49M** |

#### 🪙 Tokens by model

| Model | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- |
| 🔵 sonnet | 0k | 167k | 1.09M | 7.73M | **8.99M** |
| 🟢 haiku | 0k | 108k | 733k | 2.04M | **2.88M** |
| 🟣 opus | 0k | 164k | 779k | 5.67M | **6.62M** |
| **All models** | 0k | 440k | 2.61M | 15.44M | **18.49M** |

### 1. ticket-plan · 2026-11-19 11:14:18 to 11:24:12 · ⏱️ 9m53s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Ticket | 11:14:18 | 11:14:47 | 0m29s | 1 |
| Check | 11:14:48 | 11:14:50 | 0m02s | 1 |
| Plan | 11:14:51 | 11:22:57 | 8m06s | 1 |
| Write | 11:22:57 | 11:24:12 | 1m14s | 2 |

Tokens of this run: 0k · 209k · 803k · 5.94M · **6.96M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ ticket-writer T0.07 | 🔵 sonnet | 11:14:18 | 11:14:47 | 0m29s | 0k | 14k | 153k | 777k | **945k** |
| ✅ check TICKET.md T0.07 | 🟢 haiku | 11:14:48 | 11:14:50 | 0m02s | 0k | 0k | 35k | 56k | **92k** |
| ✅ planner T0.07 | 🟣 opus | 11:14:51 | 11:22:57 | 8m06s | 0k | 127k | 394k | 4.47M | **4.99M** |
| ✅ scribe T0.07 | 🟢 haiku | 11:22:57 | 11:24:08 | 1m10s | 0k | 66k | 185k | 586k | **838k** |
| ✅ check PLAN.md T0.07 | 🟢 haiku | 11:24:08 | 11:24:12 | 0m03s | 0k | 0k | 35k | 57k | **92k** |

### 2. ticket-run · 2026-11-19 11:48:09 to 11:48:25 · ⏱️ 0m16s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 11:48:09 | 11:48:25 | 0m16s | 3 |
| Waves | | | not run | 0 |
| Verify | | | not run | 0 |
| Review | | | not run | 0 |
| Finish | | | not run | 0 |

Tokens of this run: 0k · 4k · 111k · 146k · **262k** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.07 | 🟢 haiku | 11:48:09 | 11:48:17 | 0m08s | 0k | 4k | 42k | 59k | **106k** |
| ✅ plan check T0.07 | 🟢 haiku | 11:48:17 | 11:48:21 | 0m03s | 0k | 0k | 35k | 57k | **92k** |
| ✅ integrator prepare T0.07 | 🔵 sonnet | 11:48:21 | 11:48:25 | 0m03s | 0k | 0k | 32k | 29k | **62k** |

### 3. ticket-run · 2026-11-19 11:49:00 to 12:02:46 · ⏱️ 13m45s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 11:49:00 | 11:49:20 | 0m19s | 3 |
| Waves | 11:49:20 | 11:55:42 | 6m22s | 16 |
| Verify | 11:55:43 | 11:56:27 | 0m44s | 1 |
| Review | 11:56:27 | 12:01:22 | 4m54s | 8 |
| Finish | 12:01:22 | 12:02:46 | 1m23s | 4 |

Tokens of this run: 0k · 226k · 1.69M · 9.35M · **11.27M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.07 | 🟢 haiku | 11:49:00 | 11:49:10 | 0m10s | 0k | 4k | 94k | 67k | **167k** |
| ✅ plan check T0.07 | 🟢 haiku | 11:49:10 | 11:49:14 | 0m03s | 0k | 0k | 31k | 59k | **91k** |
| ✅ integrator prepare T0.07 | 🔵 sonnet | 11:49:15 | 11:49:20 | 0m04s | 0k | 0k | 28k | 32k | **61k** |
| ✅ K01 test-writer | 🔵 sonnet | 11:49:20 | 11:49:35 | 0m14s | 0k | 2k | 37k | 203k | **243k** |
| ✅ K02 test-writer | 🔵 sonnet | 11:49:20 | 11:49:34 | 0m13s | 0k | 2k | 36k | 168k | **207k** |
| ✅ K03 test-writer | 🔵 sonnet | 11:49:20 | 11:49:34 | 0m14s | 0k | 2k | 41k | 198k | **242k** |
| ✅ K04 test-writer | 🔵 sonnet | 11:49:20 | 11:50:04 | 0m43s | 0k | 15k | 44k | 374k | **435k** |
| ✅ K05 test-writer | 🔵 sonnet | 11:49:21 | 11:49:43 | 0m22s | 0k | 5k | 35k | 179k | **220k** |
| ✅ K06 test-writer | 🔵 sonnet | 11:49:21 | 11:50:06 | 0m45s | 0k | 13k | 45k | 430k | **489k** |
| ✅ K07 test-writer | 🔵 sonnet | 11:49:21 | 11:49:46 | 0m24s | 0k | 6k | 42k | 216k | **265k** |
| ✅ K08 doc-writer | 🟢 haiku | 11:49:21 | 11:49:42 | 0m20s | 0k | 11k | 50k | 445k | **508k** |
| ✅ integrator Waves | 🔵 sonnet | 11:50:07 | 11:50:15 | 0m08s | 0k | 0k | 32k | 159k | **193k** |
| ✅ K09 rust-implementer | 🔵 sonnet | 11:50:16 | 11:51:31 | 1m15s | 0k | 6k | 51k | 465k | **524k** |
| ✅ K10 implementer | 🔵 sonnet | 11:50:16 | 11:50:41 | 0m25s | 0k | 6k | 41k | 173k | **222k** |
| ✅ K11 implementer | 🔵 sonnet | 11:50:16 | 11:50:38 | 0m22s | 0k | 2k | 35k | 214k | **253k** |
| ✅ integrator Waves | 🔵 sonnet | 11:51:31 | 11:51:38 | 0m07s | 0k | 0k | 32k | 94k | **127k** |
| ✅ K12 rust-implementer | 🔵 sonnet | 11:51:39 | 11:54:06 | 2m27s | 0k | 33k | 89k | 1.71M | **1.83M** |
| ✅ K13 rust-implementer | 🔵 sonnet | 11:51:39 | 11:55:30 | 3m51s | 0k | 20k | 58k | 1.44M | **1.52M** |
| ✅ integrator Waves | 🔵 sonnet | 11:55:30 | 11:55:42 | 0m12s | 0k | 0k | 28k | 65k | **94k** |
| ✅ verifier round 1 | 🟢 haiku | 11:55:43 | 11:56:27 | 0m44s | 0k | 0k | 32k | 91k | **124k** |
| ✅ reviewer round 1 | 🟣 opus | 11:56:27 | 11:58:44 | 2m17s | 0k | 28k | 252k | 719k | **1.00M** |
| ❌ K12 rust-implementer (fix) | 🔵 sonnet | 11:58:45 | 11:59:03 | 0m17s | 0k | 5k | 40k | 172k | **218k** |
| ✅ verifier after review 1 | 🟢 haiku | 11:59:04 | 11:59:30 | 0m25s | 0k | 0k | 28k | 64k | **93k** |
| ✅ reviewer round 2 | 🟣 opus | 11:59:30 | 11:59:54 | 0m23s | 0k | 4k | 94k | 309k | **407k** |
| ✅ K05 test-writer (fix) | 🔵 sonnet | 11:59:55 | 12:00:17 | 0m22s | 0k | 1k | 34k | 140k | **176k** |
| ✅ integrator Review | 🔵 sonnet | 12:00:17 | 12:00:24 | 0m06s | 0k | 0k | 29k | 66k | **96k** |
| ✅ verifier after review 2 | 🟢 haiku | 12:00:24 | 12:00:56 | 0m32s | 0k | 0k | 28k | 96k | **126k** |
| ✅ reviewer round 3 | 🟣 opus | 12:00:57 | 12:01:22 | 0m25s | 0k | 4k | 38k | 180k | **223k** |
| ✅ scribe T0.07 | 🟢 haiku | 12:01:22 | 12:01:50 | 0m27s | 0k | 17k | 97k | 337k | **451k** |
| ✅ explainer T0.07 | 🔵 sonnet | 12:01:22 | 12:02:40 | 1m17s | 0k | 24k | 94k | 405k | **523k** |
| ✅ docs check T0.07 1 | 🟢 haiku | 12:02:40 | 12:02:44 | 0m04s | 0k | 0k | 35k | 57k | **93k** |
| 🔄 integrator finish T0.07 | 🔵 sonnet | 12:02:45 | 12:02:46 | 0m01s | 0k | 0k | 25k | 4k | **29k** |
<!-- /timings -->
