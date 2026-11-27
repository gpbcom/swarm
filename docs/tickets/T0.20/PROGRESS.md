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
| 2026-11-27 09:57 | Plan written: 13 tasks, 4 waves | scribe | ⏳ Awaiting approval |
| 2026-11-27 10:11 | Plan approved by the person (group approval) | 👤 person | 🟢 Approved |
| 2026-11-27 12:57 | Wave 1: 6 of 6 tasks done | workers | ✅ |
| 2026-11-27 12:57 | Integrate (Waves) | integrator | ✅ 6 integrated, 0 blocked, not committed |
| 2026-11-27 12:57 | Wave 2: 3 of 3 tasks done | workers | ✅ |
| 2026-11-27 12:57 | Integrate (Waves) | integrator | ✅ 3 integrated, 0 blocked, not committed |
| 2026-11-27 12:57 | Wave 3: 2 of 2 tasks done | workers | ✅ |
| 2026-11-27 12:57 | Integrate (Waves) | integrator | ✅ 2 integrated, 0 blocked, not committed |
| 2026-11-27 12:57 | Wave 4: 1 of 2 tasks done | workers | ❌ |
| 2026-11-27 12:57 | Integrate (Waves) | integrator | ✅ 1 integrated, 0 blocked, not committed |
| 2026-11-27 12:57 | Stopped in wave 4: K13 not done | workers | ❌ |
| 2026-11-27 13:19 | Wave 4: 1 of 1 tasks done | workers | ✅ |
| 2026-11-27 13:19 | Integrate (Waves) | integrator | ✅ 1 integrated, 0 blocked, not committed |
| 2026-11-27 13:19 | Verify 1 (2 not applicable) | verifier | ❌ 5 failures |
| 2026-11-27 13:19 | Integrate (Verify) | integrator | ✅ 2 integrated, 0 blocked, not committed |
| 2026-11-27 13:19 | Verify 2 (2 not applicable) | verifier | ❌ 4 failures |
| 2026-11-27 13:19 | Integrate (Verify) | integrator | ✅ 1 integrated, 0 blocked, not committed |
| 2026-11-27 13:19 | Verify 3 (2 not applicable) | verifier | ❌ 1 failures |
| 2026-11-27 13:19 | Stopped: checks failing | verifier | ❌ Open failure: pytest, tests/conventions/mono_repo/frontend/test_frontend_e2e.py: tests/conventions/mono_repo/frontend/test_frontend_e2e.py:74 AssertionError; tests/conventions/mono_repo/frontend/test_frontend_e2e.py:93 AssertionError; FAILED TestFrontendE2e::test_the_capture_script_updates_every_snapshot_but_the_differences[frontend/apps/ground-control]; FAILED TestFrontendE2e::test_the_playwright_config_uses_the_shared_visual_config_and_no_web_server[frontend/apps/ground-control]. The verdict output was truncated after these lines. Environment: no. |
| 2026-11-27 13:19 | Work left uncommitted in /home/guillaume/Documents/Projects/PoC/swarm on feature/tickets; /ticket-run T0.20 continues it | scribe | ⚠️ |
| 2026-11-27 13:40 | Plan change approved (TKT-11): the Back office e2e publishes 127.0.0.1:8181, not 8180 (K05, K10, K11), because Ground control's e2e service holds 8180; `test_no_two_services_publish_the_same_host_port` keeps them apart | person | 🟢 Approved |
| 2026-11-27 13:40 | Decision: the visual checks of K06's `test_frontend_e2e.py` (the `capture` script, `defineVisualConfig`) apply only to the front ends whose e2e compares screens (`toHaveScreenshot`), today the Back office; every front end keeps the shared set-up and no `webServer`. Ground control moves to visual tests with the ticket that captures UC-025 | person | 🟢 Approved |
| 2026-11-27 13:40 | K06's test changed accordingly in the main checkout, at the person's word: 14 passed, ruff and mypy clean | main session | ✅ |
| 2026-11-27 13:43 | Verify 1 | verifier | ✅ passed |
| 2026-11-27 13:43 | Review 1 (full) | reviewer | ✅ 0 blocking, 6 follow-ups |
| 2026-11-27 13:43 | Waiting for the person's code review: nothing is committed or pushed until PLAN.md says **Push:** 🟢 Approved (TKT-18) | scribe | 👀 |
| 2026-11-27 14:06 | Push approved after the code review (TKT-18), in the conversation: the main session wrote `**Push:** 🟢 Approved` in PLAN.md at the person's word | person | 🟢 Approved |
| 2026-11-27 14:09 | Push approved after the code review | 👤 person | 🟢 |
| 2026-11-27 14:09 | Verify 1 (2 not applicable) | verifier | ✅ passed |

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| `.github/workflows/images.yml tests/ci/images/test_images_workflow.py` | Drop the duplicate upload-artifact step, or remove the front-end path from the first step, and update test_e2e_uploads_the_front_end_reports_on_failure to match. |
| `docs/specs/screens/UC-029/a1.png docs/specs/screens/UC-029/a1.dark.png docs/specs/screens/UC-029/ko.png docs/specs/screens/UC-029/ko.dark.png docs/specs/screens/UC-029/a2.png docs/specs/screens/UC-029/a2.dark.png docs/specs/screens/UC-029/ok.png docs/specs/screens/UC-029/ok.dark.png docs/tickets/T0.20/tests-evidences/` | Keep the output of one 'SWARM_IMAGE_TAG=local pnpm --filter @swarm/back-office run e2e' run in tests-evidences/. If the first CI run fails on rasterisation, recapture in CI's image (the plan's own fallback). |
| `qa/README.md AGENT.md` | Update both sentences to the delivered state. |
| `tests/conventions/mono_repo/frontend/test_frontend_e2e.py` | Use a plain comprehension, or a small classmethod that returns the specs that call toHaveScreenshot. |
| `frontend/apps/back-office/Dockerfile tests/infra/images/test_back_office_image.py` | Copy only the manifests, install, then copy the sources so the install layer is cached. Otherwise drop the redundant COPY, and keep the test's manifest assertion in line with the result. |
| `tests/harness/write_specs/test_palettise.py tests/harness/write_specs/helpers.py` | Move the constants and the two helper functions into helpers.py, or make them ClassVars and methods of TestPalettise. |

<!-- timings -->
## ⏱️ Timings

Measured from the agents' transcripts by `python3 .claude/scripts/reports/progress.py timings --ticket T0.20` (TKT-10).

| Measure | Value |
| --- | --- |
| 🕒 Ticket started | 2026-11-20 13:43:42 |
| 🕒 Last activity | 2026-11-27 14:10:04 |
| ⏱️ **Overall ticket time** (first start to last activity) | **168h26m21s** |
| 🤖 Time with agents working (sum of runs) | 50m11s |
| ⏸️ Time between runs (approvals, fixes) | 167h36m10s |
| 🔁 Workflow runs | 6 |
| 🪙 **Tokens consumed** (input, output, cache write, cache read) | **52.65M** |

#### 🪙 Tokens by model

| Model | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- |
| 🟢 haiku | 0k | 200k | 3.23M | 12.55M | **15.99M** |
| 🔵 sonnet | 0k | 201k | 2.68M | 16.28M | **19.17M** |
| 🟣 opus | 0k | 211k | 940k | 16.34M | **17.49M** |
| **All models** | 1k | 612k | 6.85M | 45.18M | **52.65M** |

### 1. ticket-plan · 2026-11-20 13:43:42 to 13:50:37 · ⏱️ 6m54s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Ticket | 13:43:42 | 13:44:33 | 0m50s | 2 |
| Check | 13:44:34 | 13:44:37 | 0m03s | 1 |
| Plan | 13:44:38 | 13:49:40 | 5m02s | 1 |
| Write | 13:49:40 | 13:50:37 | 0m56s | 2 |

Tokens of this run: 0k · 122k · 894k · 6.11M · **7.13M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ done check T0.20 | 🟢 haiku | 13:43:42 | 13:43:55 | 0m12s | 0k | 0k | 96k | 102k | **199k** |
| ✅ ticket-writer T0.20 | 🔵 sonnet | 13:43:57 | 13:44:33 | 0m35s | 0k | 14k | 220k | 1.12M | **1.36M** |
| ✅ check TICKET.md T0.20 | 🟢 haiku | 13:44:34 | 13:44:37 | 0m03s | 0k | 0k | 51k | 99k | **151k** |
| ✅ planner T0.20 | 🟣 opus | 13:44:38 | 13:49:40 | 5m02s | 0k | 66k | 305k | 3.99M | **4.36M** |
| ✅ scribe T0.20 | 🟢 haiku | 13:49:40 | 13:50:33 | 0m52s | 0k | 39k | 165k | 702k | **907k** |
| ✅ check PLAN.md T0.20 | 🟢 haiku | 13:50:33 | 13:50:37 | 0m03s | 0k | 0k | 55k | 96k | **151k** |

### 2. ticket-plan · 2026-11-27 09:48:43 to 09:57:59 · ⏱️ 9m15s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Ticket | 09:48:43 | 09:49:16 | 0m32s | 2 |
| Check | 09:49:16 | 09:49:22 | 0m06s | 1 |
| Plan | 09:49:23 | 09:56:53 | 7m30s | 1 |
| Write | 09:56:53 | 09:57:59 | 1m05s | 2 |

Tokens of this run: 0k · 170k · 925k · 10.09M · **11.19M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ done check T0.20 | 🟢 haiku | 09:48:43 | 09:48:55 | 0m12s | 0k | 0k | 60k | 118k | **179k** |
| ✅ ticket-writer T0.20 | 🔵 sonnet | 09:48:57 | 09:49:16 | 0m18s | 0k | 3k | 194k | 598k | **796k** |
| ✅ check TICKET.md T0.20 | 🟢 haiku | 09:49:16 | 09:49:22 | 0m06s | 0k | 0k | 60k | 118k | **179k** |
| ✅ planner T0.20 | 🟣 opus | 09:49:23 | 09:56:53 | 7m30s | 0k | 115k | 354k | 8.44M | **8.91M** |
| ✅ scribe T0.20 | 🟢 haiku | 09:56:53 | 09:57:55 | 1m01s | 0k | 49k | 196k | 760k | **1.01M** |
| ✅ check PLAN.md T0.20 | 🟢 haiku | 09:57:56 | 09:57:59 | 0m03s | 0k | 0k | 60k | 58k | **118k** |

### 3. ticket-run · 2026-11-27 12:50:14 to 12:57:41 · ⏱️ 7m26s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 12:50:14 | 12:50:56 | 0m41s | 4 |
| Waves | 12:50:57 | 12:57:41 | 6m44s | 19 |
| Verify | | | not run | 0 |
| Review | | | not run | 0 |
| Finish | | | not run | 0 |

Tokens of this run: 0k · 177k · 1.89M · 14.57M · **16.64M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.20 | 🟢 haiku | 12:50:14 | 12:50:27 | 0m12s | 0k | 3k | 129k | 309k | **443k** |
| ✅ plan check T0.20 | 🟢 haiku | 12:50:27 | 12:50:31 | 0m03s | 0k | 0k | 57k | 59k | **117k** |
| ✅ start rule T0.20 | 🟢 haiku | 12:50:32 | 12:50:42 | 0m10s | 0k | 0k | 57k | 59k | **117k** |
| ✅ integrator prepare T0.20 | 🔵 sonnet | 12:50:42 | 12:50:56 | 0m13s | 0k | 0k | 57k | 125k | **184k** |
| ✅ K01 test-writer | 🔵 sonnet | 12:50:57 | 12:51:46 | 0m49s | 0k | 12k | 80k | 738k | **831k** |
| ✅ K02 test-writer | 🔵 sonnet | 12:50:57 | 12:52:03 | 1m06s | 0k | 8k | 84k | 751k | **844k** |
| ✅ K03 test-writer | 🔵 sonnet | 12:50:57 | 12:52:33 | 1m36s | 0k | 33k | 145k | 1.51M | **1.69M** |
| ✅ K04 test-writer | 🔵 sonnet | 12:50:57 | 12:51:22 | 0m24s | 0k | 5k | 72k | 252k | **330k** |
| ✅ K05 test-writer | 🔵 sonnet | 12:50:57 | 12:51:27 | 0m29s | 0k | 5k | 88k | 545k | **639k** |
| ✅ K06 test-writer | 🔵 sonnet | 12:50:57 | 12:51:34 | 0m36s | 0k | 8k | 86k | 745k | **839k** |
| ✅ integrator Waves | 🔵 sonnet | 12:52:37 | 12:52:46 | 0m09s | 0k | 1k | 62k | 310k | **373k** |
| ✅ K07 frontend-implementer | 🔵 sonnet | 12:52:47 | 12:53:46 | 0m58s | 0k | 25k | 96k | 985k | **1.11M** |
| ✅ K08 implementer | 🔵 sonnet | 12:52:47 | 12:53:44 | 0m57s | 0k | 15k | 78k | 1.19M | **1.28M** |
| ✅ K10 frontend-implementer | 🔵 sonnet | 12:52:47 | 12:53:35 | 0m48s | 0k | 7k | 76k | 1.02M | **1.10M** |
| ✅ integrator Waves | 🔵 sonnet | 12:53:48 | 12:53:56 | 0m07s | 0k | 0k | 61k | 186k | **248k** |
| ✅ K09 frontend-implementer | 🔵 sonnet | 12:53:56 | 12:54:48 | 0m51s | 0k | 11k | 75k | 1.28M | **1.37M** |
| ✅ K11 implementer | 🔵 sonnet | 12:53:56 | 12:54:28 | 0m31s | 0k | 4k | 70k | 723k | **798k** |
| ✅ integrator Waves | 🔵 sonnet | 12:54:55 | 12:55:07 | 0m11s | 0k | 0k | 62k | 251k | **314k** |
| ✅ K12 doc-writer | 🟢 haiku | 12:55:07 | 12:55:54 | 0m46s | 0k | 18k | 98k | 1.56M | **1.68M** |
| ❌ K13 mockup-writer | 🟢 haiku | 12:55:08 | 12:56:27 | 1m19s | 0k | 4k | 84k | 672k | **761k** |
| ❌ K13 mockup-writer | 🟢 haiku | 12:56:27 | 12:57:16 | 0m48s | 0k | 3k | 72k | 590k | **667k** |
| ✅ integrator Waves | 🔵 sonnet | 12:57:16 | 12:57:28 | 0m12s | 0k | 0k | 61k | 253k | **315k** |
| ✅ scribe T0.20 | 🟢 haiku | 12:57:29 | 12:57:41 | 0m12s | 0k | 3k | 131k | 442k | **577k** |

### 4. ticket-run · 2026-11-27 13:05:30 to 13:19:24 · ⏱️ 13m53s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 13:05:30 | 13:06:11 | 0m40s | 4 |
| Waves | 13:06:11 | 13:07:39 | 1m27s | 2 |
| Verify | 13:07:39 | 13:19:11 | 11m31s | 10 |
| Review | | | not run | 0 |
| Finish | 13:19:11 | 13:19:24 | 0m12s | 1 |

Tokens of this run: 0k · 56k · 1.15M · 7.34M · **8.55M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.20 | 🟢 haiku | 13:05:30 | 13:05:44 | 0m13s | 0k | 6k | 78k | 311k | **396k** |
| ✅ plan check T0.20 | 🟢 haiku | 13:05:44 | 13:05:48 | 0m03s | 0k | 0k | 60k | 58k | **119k** |
| ✅ start rule T0.20 | 🟢 haiku | 13:05:48 | 13:05:59 | 0m10s | 0k | 0k | 60k | 119k | **180k** |
| ✅ integrator prepare T0.20 | 🔵 sonnet | 13:05:59 | 13:06:11 | 0m11s | 0k | 0k | 63k | 60k | **124k** |
| ✅ K13 mockup-writer | 🟢 haiku | 13:06:11 | 13:07:27 | 1m15s | 0k | 25k | 140k | 3.13M | **3.30M** |
| ✅ integrator Waves | 🔵 sonnet | 13:07:27 | 13:07:39 | 0m12s | 0k | 0k | 66k | 316k | **384k** |
| ✅ verifier round 1 | 🟢 haiku | 13:07:39 | 13:11:07 | 3m27s | 0k | 2k | 67k | 183k | **253k** |
| ✅ K06 test-writer (fix) | 🔵 sonnet | 13:11:07 | 13:11:21 | 0m14s | 0k | 2k | 77k | 322k | **402k** |
| ❌ K07 frontend-implementer (fix) | 🔵 sonnet | 13:11:07 | 13:11:30 | 0m23s | 0k | 2k | 73k | 390k | **466k** |
| ✅ K01 test-writer (fix) | 🔵 sonnet | 13:11:07 | 13:11:31 | 0m23s | 0k | 2k | 69k | 325k | **397k** |
| ✅ integrator Verify | 🔵 sonnet | 13:11:32 | 13:11:45 | 0m13s | 0k | 1k | 63k | 386k | **451k** |
| ✅ verifier round 2 | 🟢 haiku | 13:11:45 | 13:15:11 | 3m25s | 0k | 2k | 62k | 187k | **251k** |
| ❌ K06 test-writer (fix) | 🔵 sonnet | 13:15:11 | 13:15:30 | 0m18s | 0k | 2k | 67k | 399k | **468k** |
| ✅ K07 frontend-implementer (fix) | 🔵 sonnet | 13:15:11 | 13:15:32 | 0m21s | 0k | 1k | 62k | 264k | **328k** |
| ✅ integrator Verify | 🔵 sonnet | 13:15:33 | 13:15:41 | 0m08s | 0k | 0k | 62k | 188k | **251k** |
| ✅ verifier round 3 | 🟢 haiku | 13:15:42 | 13:19:11 | 3m29s | 0k | 1k | 2k | 307k | **311k** |
| ✅ scribe T0.20 | 🟢 haiku | 13:19:11 | 13:19:24 | 0m12s | 0k | 4k | 74k | 387k | **466k** |

### 5. ticket-run · 2026-11-27 13:36:34 to 13:44:46 · ⏱️ 8m11s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 13:36:34 | 13:37:14 | 0m39s | 4 |
| Waves | | | not run | 0 |
| Verify | 13:37:14 | 13:40:40 | 3m26s | 1 |
| Review | 13:40:41 | 13:43:25 | 2m44s | 1 |
| Finish | 13:43:25 | 13:44:46 | 1m20s | 4 |

Tokens of this run: 0k · 74k · 1.28M · 5.73M · **7.09M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.20 | 🟢 haiku | 13:36:34 | 13:36:45 | 0m11s | 0k | 5k | 135k | 259k | **400k** |
| ✅ plan check T0.20 | 🟢 haiku | 13:36:46 | 13:36:50 | 0m04s | 0k | 0k | 62k | 59k | **122k** |
| ✅ start rule T0.20 | 🟢 haiku | 13:36:50 | 13:37:01 | 0m10s | 0k | 0k | 59k | 62k | **122k** |
| ✅ integrator prepare T0.20 | 🔵 sonnet | 13:37:01 | 13:37:14 | 0m12s | 0k | 0k | 65k | 126k | **192k** |
| ✅ verifier round 1 | 🟢 haiku | 13:37:14 | 13:40:40 | 3m26s | 0k | 0k | 124k | 124k | **249k** |
| ✅ reviewer round 1 | 🟣 opus | 13:40:41 | 13:43:25 | 2m44s | 0k | 29k | 281k | 3.91M | **4.22M** |
| ✅ scribe T0.20 | 🟢 haiku | 13:43:25 | 13:43:52 | 0m26s | 0k | 13k | 163k | 281k | **459k** |
| ✅ explainer T0.20 | 🔵 sonnet | 13:43:25 | 13:44:37 | 1m11s | 0k | 24k | 208k | 777k | **1.01M** |
| ✅ docs check T0.20 1 | 🟢 haiku | 13:44:37 | 13:44:40 | 0m03s | 0k | 0k | 62k | 59k | **122k** |
| ✅ scribe T0.20 (timings) | 🟢 haiku | 13:44:41 | 13:44:46 | 0m04s | 0k | 0k | 117k | 71k | **189k** |

### 6. ticket-run · 2026-11-27 14:05:34 to 14:10:04 · ⏱️ 4m29s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 14:05:34 | 14:06:16 | 0m42s | 4 |
| Waves | | | not run | 0 |
| Verify | 14:06:17 | 14:09:44 | 3m27s | 1 |
| Review | | | not run | 0 |
| Finish | 14:09:44 | 14:10:04 | 0m19s | 3 |

Tokens of this run: 0k · 10k · 702k · 1.33M · **2.04M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.20 | 🟢 haiku | 14:05:34 | 14:05:46 | 0m12s | 0k | 5k | 135k | 253k | **394k** |
| ✅ plan check T0.20 | 🟢 haiku | 14:05:47 | 14:05:51 | 0m04s | 0k | 0k | 64k | 119k | **183k** |
| ✅ start rule T0.20 | 🟢 haiku | 14:05:52 | 14:06:03 | 0m11s | 0k | 0k | 61k | 121k | **184k** |
| ✅ integrator prepare T0.20 | 🔵 sonnet | 14:06:04 | 14:06:16 | 0m12s | 0k | 0k | 65k | 126k | **192k** |
| ✅ verifier round 1 | 🟢 haiku | 14:06:17 | 14:09:44 | 3m27s | 0k | 0k | 124k | 187k | **313k** |
| ✅ scribe T0.20 | 🟢 haiku | 14:09:44 | 14:09:56 | 0m12s | 0k | 2k | 131k | 394k | **528k** |
| ✅ docs check T0.20 1 | 🟢 haiku | 14:09:56 | 14:10:01 | 0m04s | 0k | 0k | 61k | 121k | **184k** |
| 🔄 integrator finish T0.20 | 🔵 sonnet | 14:10:02 | 14:10:04 | 0m02s | 0k | 0k | 57k | 4k | **61k** |
<!-- /timings -->
