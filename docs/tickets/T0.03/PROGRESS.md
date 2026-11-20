# T0.03: Progress

**Status:** 🟡 Planned · **Ticket:** [TICKET.md](TICKET.md)

<!-- ticket:specs -->
## 📚 Specifications

The technical pages, features, use cases and business rules of [TICKET.md](TICKET.md), copied by `python3 .claude/scripts/tickets/ticket_refs.py sync`.

- [🧅 Architecture: layers inside each service](../../specs/technical/01-architecture.md#layers)
- [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo)
- [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci)
<!-- /ticket:specs -->

## 📝 Events

| Time | Event | By | Result |
| --- | --- | --- | --- |
| 2026-11-19 09:51 | Plan written: 21 tasks, 4 waves | scribe | ⏳ Awaiting approval |
| 2026-11-19 10:03 | Plan approved | the person | ✅ Approved |
| 2026-11-19 10:09 | Wave 1: 10 of 10 tasks done | workers | ✅ |
| 2026-11-19 10:09 | Merge (Waves) | integrator | ✅ 10 merged, 1 blocked |
| 2026-11-19 10:09 | Wave 2: 3 of 3 tasks done | workers | ✅ |
| 2026-11-19 10:09 | Merge (Waves) | integrator | ✅ 3 merged, 1 blocked |
| 2026-11-19 10:09 | Wave 3: 7 of 7 tasks done | workers | ✅ |
| 2026-11-19 10:09 | Merge (Waves) | integrator | ✅ 7 merged, 1 blocked |
| 2026-11-19 10:09 | Wave 4: 0 of 1 tasks done | workers | ❌ |
| 2026-11-19 10:09 | Stopped in wave 4: K21 not done | workers | ❌ |
| 2026-11-19 10:13 | K21 blocked only by `ruff check tests/conventions`: 11 import-order errors (I001) in other tasks' test files, written before the modules they import existed, so ruff saw `tests` as third-party | main session | ⚠️ Found |
| 2026-11-19 10:13 | Fixed: `known-first-party = ["tests"]` in pyproject.toml (stable order for tests written first, TKT-4) and `ruff check --fix` on the test files; with K21's registry the suite gives 268 passed and ruff passes | main session | ✅ Fixed |
| 2026-11-19 10:16 | Wave 4: 1 of 1 tasks done | workers | ✅ |
| 2026-11-19 10:16 | Merge (Waves) | integrator | ✅ 1 merged, 0 blocked |
| 2026-11-19 10:16 | Verify 1 (4 not applicable) | verifier | ✅ passed |
| 2026-11-19 10:16 | Review 1 (full) | reviewer | ✅ 0 blocking, 6 follow-ups |
| 2026-11-19 10:16 | Merge into develop | integrator | ✅ merged locally, not pushed |

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| `AGENT.md` | K10, lines 112-121: the new 'Since T0.03, ...' paragraph sits between 'tests/conventions/ fails on any of these, in src/ and tests/ unless stated:' and the bullet list that colon introduces. Move it after the list, and mark in the list which bullets are enforced. In the same way, the new Rust and TypeScript block (lines 17-28) separates the uv commands from the bullets about them. Move it below those bullets. |
| `tests/conventions/rules/code/no_any.py` | K16, lines 41-48: the rule misses 'import typing as t' followed by 't.Any', and 'from typing import *'. Resolve module aliases from the Import nodes, and report a star import from typing or typing_extensions. |
| `tests/conventions/linters/test_typescript_settings.py` | K09, line 14: declare PACKAGE as ClassVar[str], as test_rust_settings.py and test_layer_imports.py already do. |
| `tests/conventions/helpers.py` | K01: AGENT.md says that tests/conventions/helpers.py holds the third-party protocol names that are exempt from the underscore-attribute rule. The new helpers.py holds no such list, because that rule is out of scope. When the rule is added, put the list here, or update the AGENT.md sentence. |
| `tests/conventions/samples/test_empty_service.py` | K06, lines 99-103: the assertion '14 passed' depends on the real gateway passing all seven rules and on the number of rules. Derive the count from len(ConventionRules.all()) times the number of services, so that adding a rule does not break this test. |
| `packages/rust/Cargo.toml` | K12: no crate exists yet, so cargo fmt and clippy have not been run against these settings (tests-evidences only holds cargo-metadata.txt). Run them on the first real crate in T0.07, and check that the crate has '[lints] workspace = true'. |

<!-- timings -->
## ⏱️ Timings

Measured from the agents' transcripts by `python3 .claude/scripts/reports/progress.py timings --ticket T0.03` (TKT-10).

| Measure | Value |
| --- | --- |
| 🕒 Ticket started | 2026-11-19 09:40:47 |
| 🕒 Last activity | 2026-11-19 10:17:08 |
| ⏱️ **Overall ticket time** (first start to last activity) | **36m20s** |
| 🤖 Time with agents working (sum of runs) | 19m21s |
| ⏸️ Time between runs (approvals, fixes) | 16m59s |
| 🔁 Workflow runs | 3 |
| 🪙 **Tokens consumed** (input, output, cache write, cache read) | **19.00M** |

#### 🪙 Tokens by model

| Model | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- |
| 🔵 sonnet | 0k | 198k | 1.42M | 10.88M | **12.49M** |
| 🟢 haiku | 0k | 104k | 768k | 2.42M | **3.29M** |
| 🟣 opus | 0k | 156k | 454k | 2.60M | **3.21M** |
| **All models** | 0k | 459k | 2.64M | 15.90M | **19.00M** |

### 1. ticket-plan · 2026-11-19 09:40:47 to 09:51:24 · ⏱️ 10m36s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Ticket | 09:40:47 | 09:41:16 | 0m28s | 1 |
| Check | 09:41:17 | 09:41:20 | 0m03s | 1 |
| Plan | 09:41:20 | 09:49:57 | 8m36s | 1 |
| Write | 09:49:57 | 09:51:24 | 1m26s | 2 |

Tokens of this run: 0k · 200k · 661k · 3.37M · **4.23M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ ticket-writer T0.03 | 🔵 sonnet | 09:40:47 | 09:41:16 | 0m28s | 0k | 10k | 149k | 642k | **802k** |
| ✅ check TICKET.md T0.03 | 🟢 haiku | 09:41:17 | 09:41:20 | 0m03s | 0k | 0k | 61k | 29k | **91k** |
| ✅ planner T0.03 | 🟣 opus | 09:41:20 | 09:49:57 | 8m36s | 0k | 135k | 262k | 1.96M | **2.35M** |
| ✅ scribe T0.03 | 🟢 haiku | 09:49:57 | 09:51:21 | 1m23s | 0k | 53k | 151k | 684k | **890k** |
| ✅ check PLAN.md T0.03 | 🟢 haiku | 09:51:21 | 09:51:24 | 0m02s | 0k | 0k | 35k | 58k | **94k** |

### 2. ticket-run · 2026-11-19 10:04:30 to 10:09:29 · ⏱️ 4m59s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 10:04:30 | 10:04:49 | 0m19s | 3 |
| Waves | 10:04:49 | 10:09:29 | 4m39s | 26 |
| Verify | | | not run | 0 |
| Review | | | not run | 0 |
| Finish | | | not run | 0 |

Tokens of this run: 0k · 196k · 1.38M · 10.23M · **11.81M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.03 | 🟢 haiku | 10:04:30 | 10:04:39 | 0m08s | 0k | 5k | 70k | 59k | **135k** |
| ✅ plan check T0.03 | 🟢 haiku | 10:04:39 | 10:04:42 | 0m03s | 0k | 0k | 35k | 56k | **92k** |
| ✅ integrator prepare T0.03 | 🔵 sonnet | 10:04:43 | 10:04:49 | 0m06s | 0k | 0k | 35k | 89k | **126k** |
| ✅ K01 test-writer | 🔵 sonnet | 10:04:49 | 10:05:33 | 0m43s | 0k | 13k | 60k | 536k | **610k** |
| ✅ K02 test-writer | 🔵 sonnet | 10:04:50 | 10:05:31 | 0m41s | 0k | 13k | 47k | 487k | **548k** |
| ✅ K03 test-writer | 🔵 sonnet | 10:04:50 | 10:05:39 | 0m49s | 0k | 15k | 64k | 749k | **829k** |
| ✅ K04 test-writer | 🔵 sonnet | 10:04:50 | 10:05:35 | 0m45s | 0k | 12k | 61k | 432k | **507k** |
| ✅ K05 test-writer | 🔵 sonnet | 10:04:50 | 10:05:30 | 0m40s | 0k | 13k | 50k | 410k | **473k** |
| ✅ K06 test-writer | 🔵 sonnet | 10:04:50 | 10:05:30 | 0m40s | 0k | 7k | 52k | 720k | **780k** |
| ✅ K07 test-writer | 🔵 sonnet | 10:04:50 | 10:05:33 | 0m42s | 0k | 13k | 57k | 405k | **476k** |
| ✅ K08 test-writer | 🔵 sonnet | 10:04:50 | 10:05:25 | 0m35s | 0k | 8k | 44k | 433k | **486k** |
| ✅ K09 test-writer | 🔵 sonnet | 10:05:26 | 10:06:05 | 0m39s | 0k | 11k | 42k | 525k | **578k** |
| ✅ K10 doc-writer | 🟢 haiku | 10:05:31 | 10:05:47 | 0m15s | 0k | 5k | 69k | 243k | **318k** |
| ✅ integrator Waves | 🔵 sonnet | 10:06:06 | 10:06:19 | 0m13s | 0k | 1k | 33k | 170k | **205k** |
| ✅ K11 implementer | 🔵 sonnet | 10:06:20 | 10:06:46 | 0m26s | 0k | 6k | 39k | 219k | **265k** |
| ✅ K12 rust-implementer | 🔵 sonnet | 10:06:20 | 10:06:51 | 0m31s | 0k | 4k | 38k | 654k | **698k** |
| ✅ K13 frontend-implementer | 🔵 sonnet | 10:06:20 | 10:07:20 | 1m00s | 0k | 11k | 48k | 928k | **989k** |
| ✅ integrator Waves | 🔵 sonnet | 10:07:23 | 10:07:36 | 0m12s | 0k | 1k | 35k | 193k | **231k** |
| ✅ K14 implementer | 🔵 sonnet | 10:07:36 | 10:07:53 | 0m16s | 0k | 3k | 40k | 211k | **255k** |
| ✅ K15 implementer | 🔵 sonnet | 10:07:36 | 10:07:51 | 0m14s | 0k | 2k | 40k | 178k | **221k** |
| ✅ K16 implementer | 🔵 sonnet | 10:07:36 | 10:07:59 | 0m22s | 0k | 3k | 39k | 259k | **302k** |
| ✅ K17 implementer | 🔵 sonnet | 10:07:37 | 10:07:55 | 0m18s | 0k | 2k | 38k | 218k | **260k** |
| ✅ K18 implementer | 🔵 sonnet | 10:07:37 | 10:08:19 | 0m42s | 0k | 16k | 51k | 475k | **543k** |
| ✅ K19 implementer | 🔵 sonnet | 10:07:37 | 10:08:15 | 0m37s | 0k | 7k | 47k | 476k | **531k** |
| ✅ K20 implementer | 🔵 sonnet | 10:07:37 | 10:07:58 | 0m21s | 0k | 4k | 40k | 218k | **262k** |
| ✅ integrator Waves | 🔵 sonnet | 10:08:20 | 10:08:37 | 0m16s | 0k | 2k | 34k | 235k | **272k** |
| ❌ K21 implementer | 🔵 sonnet | 10:08:37 | 10:08:58 | 0m21s | 0k | 2k | 49k | 218k | **270k** |
| ❌ K21 implementer | 🔵 sonnet | 10:08:59 | 10:09:21 | 0m21s | 0k | 2k | 43k | 356k | **402k** |
| ✅ scribe T0.03 | 🟢 haiku | 10:09:22 | 10:09:29 | 0m07s | 0k | 1k | 65k | 65k | **132k** |

### 3. ticket-run · 2026-11-19 10:13:22 to 10:17:08 · ⏱️ 3m45s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 10:13:22 | 10:13:42 | 0m19s | 3 |
| Waves | 10:13:42 | 10:14:10 | 0m27s | 2 |
| Verify | 10:14:11 | 10:14:25 | 0m14s | 1 |
| Review | 10:14:26 | 10:16:10 | 1m44s | 1 |
| Finish | 10:16:11 | 10:17:08 | 0m57s | 2 |

Tokens of this run: 0k · 62k · 598k · 2.29M · **2.96M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.03 | 🟢 haiku | 10:13:22 | 10:13:33 | 0m10s | 0k | 5k | 50k | 58k | **114k** |
| ✅ plan check T0.03 | 🟢 haiku | 10:13:33 | 10:13:37 | 0m03s | 0k | 0k | 34k | 56k | **91k** |
| ✅ integrator prepare T0.03 | 🔵 sonnet | 10:13:37 | 10:13:42 | 0m04s | 0k | 0k | 31k | 60k | **92k** |
| ✅ K21 implementer | 🔵 sonnet | 10:13:42 | 10:14:01 | 0m18s | 0k | 1k | 33k | 177k | **212k** |
| ✅ integrator Waves | 🔵 sonnet | 10:14:01 | 10:14:10 | 0m08s | 0k | 0k | 28k | 96k | **125k** |
| ✅ verifier round 1 | 🟢 haiku | 10:14:11 | 10:14:25 | 0m14s | 0k | 0k | 32k | 90k | **123k** |
| ✅ reviewer round 1 | 🟣 opus | 10:14:26 | 10:16:10 | 1m44s | 0k | 20k | 191k | 646k | **859k** |
| ✅ integrator finish T0.03 | 🔵 sonnet | 10:16:11 | 10:16:21 | 0m10s | 0k | 1k | 34k | 94k | **130k** |
| 🔄 scribe T0.03 | 🟢 haiku | 10:16:22 | 10:17:08 | 0m46s | 0k | 31k | 160k | 1.01M | **1.20M** |
<!-- /timings -->
