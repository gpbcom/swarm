# T0.18: Progress

**Status:** 🟡 Planned · **Ticket:** [TICKET.md](TICKET.md)

<!-- ticket:specs -->
## 📚 Specifications

The technical pages, features, use cases and business rules of [TICKET.md](TICKET.md), copied by `python3 .claude/scripts/tickets/ticket_refs.py sync`.

- [📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md)
- [🔩 Engine and services: flight engine](../../specs/technical/04-engine.md#flight-engine)
- [📨 API layer: live data over WebSocket](../../specs/technical/05-api.md#live)
- [🚀 Scalability and performance: budgets](../../specs/technical/07-scalability.md#budgets)
<!-- /ticket:specs -->

## 📝 Events

| Time | Event | By | Result |
| --- | --- | --- | --- |
| 2026-11-20 14:03 | Plan written: 26 tasks, 6 waves | scribe | ⏳ Awaiting approval |
| 2026-11-20 | Gateway paths of the plan aligned with T0.12's plan (`api/rest/gateway_rest_app.py`, `models/config/gateway_config.py`) | person | ✅ plan re-rendered, checks pass |
| 2026-11-20 14:10 | Plan approved by the person (group approval) | 👤 person | 🟢 Approved |
| 2026-11-23 18:58 | Wave 1: 12 of 12 tasks done | workers | ✅ |
| 2026-11-23 18:58 | Integrate (Waves) | integrator | ✅ 11 integrated, 1 blocked, not committed |
| 2026-11-23 18:58 | Wave 2: 3 blocking file(s) sent to their owners: packages/rust/swarm-core/mavlink/tests/decode.rs, packages/rust/swarm-core/mavlink/tests/latest_frames.rs, packages/python/swarm-models/tests/service/schemas/test_schema_exporter.py | workers | 🔁 |
| 2026-11-23 18:58 | Integrate (Waves) | integrator | ✅ 2 integrated, 0 blocked, not committed |
| 2026-11-23 18:58 | Wave 2: 4 of 4 tasks done | workers | ✅ |
| 2026-11-23 18:58 | Integrate (Waves) | integrator | ✅ 4 integrated, 0 blocked, not committed |
| 2026-11-23 18:58 | Wave 3: 3 of 4 tasks done | workers | ❌ |
| 2026-11-23 18:58 | Integrate (Waves) | integrator | ✅ 3 integrated, 0 blocked, not committed |
| 2026-11-23 18:58 | Stopped in wave 3: K20 not done | workers | ❌ |
| 2026-11-23 19:00 | K09 integrated by hand: services/gateway/tests/conftest.py, created by T0.11's K01 too, now holds both the Keycloak stand-in and the NATS fixtures | main session | ✅ |
| 2026-11-23 19:00 | K20 integrated by hand: done as briefed, blocked only by code-rule failures in other tasks' test files, left to the checks | main session | ✅ |
| 2026-11-23 19:00 | T0.11, T0.15 and T0.18 share files: checked and shipped together, on the person's decision | 👤 person | 🟢 |
| 2026-11-23 19:17 | Started with --force despite: T0.11 is open in /home/guillaume/Documents/Projects/PoC/swarm and changes services/gateway: wait for it (area lock). | 👤 person | ⚠️ |
| 2026-11-23 19:17 | Wave 4: 3 of 3 tasks done | workers | ✅ |
| 2026-11-23 19:17 | Integrate (Waves) | integrator | ✅ 3 integrated, 0 blocked, not committed |
| 2026-11-23 19:17 | Wave 5: 4 blocking file(s) sent to their owners: services/flight-engine/tests/service/engine/test_flight_engine.py, services/gateway/tests/api/live/conftest.py, services/gateway/tests/api/live/test_gateway_live_router.py, services/gateway/tests/clients/nats/test_mission_feed_client.py | workers | 🔁 |
| 2026-11-23 19:17 | Integrate (Waves) | integrator | ✅ 3 integrated, 0 blocked, not committed |
| 2026-11-23 19:17 | Wave 5: 2 of 2 tasks done | workers | ✅ |
| 2026-11-23 19:17 | Integrate (Waves) | integrator | ✅ 2 integrated, 0 blocked, not committed |
| 2026-11-23 19:17 | Wave 6: 2 blocking file(s) sent to their owners: services/flight-engine/tests/clients/leaf/test_squad_frame_publisher.py, services/flight-engine/tests/service/engine/test_flight_engine.py | workers | 🔁 |
| 2026-11-23 19:17 | Integrate (Waves) | integrator | ✅ 2 integrated, 0 blocked, not committed |
| 2026-11-23 19:17 | Wave 6: 0 of 1 tasks done | workers | ❌ |
| 2026-11-23 19:17 | Stopped in wave 6: K26 not done | workers | ❌ |
| 2026-11-23 19:18 | K26 integrated by hand: its code passes mypy and the flight-engine tests; blocked only by code-rule failures in wave-1 test files, left to the checks | main session | ✅ |
| 2026-11-23 19:20 | Started with --force despite: T0.11 is open in /home/guillaume/Documents/Projects/PoC/swarm and changes services/gateway: wait for it (area lock). | 👤 person | ⚠️ |
| 2026-11-23 19:20 | Verify 1 (1 not applicable) | verifier | ❌ 2 failures |
| 2026-11-23 19:20 | Stopped: environment problem (missing tool or module), the person fixes the environment and re-runs. Open failures: pytest (environment): 4 collection errors in services/flight-engine/tests (api/cli/commands/test_serve_command.py, api/cli/test_flight_engine_main.py, api/factories/test_flight_engine_api_factories.py, clients/mavlink/test_mavlink_listener.py), run interrupted; cargo clippy (packages/rust): 4 errors in swarm-models/src/generated.rs (dead code: live_subscription_rate never used, LiveSubscription never constructed), could not compile swarm-models | verifier | ❌ |
| 2026-11-23 19:20 | Work left uncommitted in /home/guillaume/Documents/Projects/PoC/swarm on feature/tickets; /ticket-run T0.18 continues it | main session | ⚠️ |
| 2026-11-26 16:05 | packages/rust/swarm-models/src/lib.rs re-exports Language, LiveOperation, LiveRate and LiveSubscription, so clippy no longer finds them dead: a file no task owned, changed by hand and added to T0.18's own files | main session | ✅ |
| 2026-11-26 16:06 | Started with --force despite: T0.11 is open in /home/guillaume/Documents/Projects/PoC/swarm and changes services/gateway: wait for it (area lock). | 👤 person | ⚠️ |
| 2026-11-26 16:06 | Verify 1 (1 not applicable) | verifier | ❌ 3 failures |
| 2026-11-26 16:06 | Integrate (Verify) | integrator | ✅ 1 integrated, 0 blocked, not committed |
| 2026-11-26 16:06 | Verify 2 (1 not applicable) | verifier | ❌ 2 failures |
| 2026-11-26 16:06 | Integrate (Verify) | integrator | ✅ 1 integrated, 0 blocked, not committed |
| 2026-11-26 16:06 | Verify 3 (1 not applicable) | verifier | ❌ 1 failures |
| 2026-11-26 16:06 | Stopped: checks failing | verifier | ❌ pytest: services/flight-engine/tests/api/cli/commands/test_serve_command.py, ERROR collecting (not an environment failure). The checks ran in the clean worktree /tmp/swarm-checks-ifi51ecf and the detail is truncated by checks.py. |
| 2026-11-26 16:06 | Work left uncommitted in /home/guillaume/Documents/Projects/PoC/swarm on feature/tickets; /ticket-run T0.18 continues it | main session | ⚠️ |
| 2026-11-26 16:12 | services/flight-engine/tests/api/cli/commands/test_serve_command.py renamed test_flight_engine_serve_command.py: its basename clashed with the simulator's, so pytest could not collect it (AGENT.md, Tests) | main session | ✅ |
| 2026-11-26 16:17 | tests/deploy/images/test_service_images.py builds the home variable of a hyphenated service as SWARM_FLIGHT_ENGINE_HOME (it gave SWARM_FLIGHT-ENGINE_HOME): a file no task owned, fixed by hand and added to T0.18's own files | main session | ✅ |
| 2026-11-26 16:24 | By hand, after the fix rounds could not reach them: the flight-engine Dockerfile sets SWARM_FLIGHT_ENGINE_HOME=/app (K23's file, as the gateway does), and test_flight_engine.py imports its stand-in helper under Third-party imports, as the import rule requires (K07's file) | main session | ✅ |
| 2026-11-26 16:26 | Started with --force despite: T0.11 is open in /home/guillaume/Documents/Projects/PoC/swarm and changes services/gateway: wait for it (area lock). | 👤 person | ⚠️ |
| 2026-11-26 16:26 | Verify 1 (1 not applicable) | verifier | ❌ 3 failures |
| 2026-11-26 16:26 | Integrate (Verify) | integrator | ✅ 2 integrated, 0 blocked, not committed |
| 2026-11-26 16:26 | Verify 2 (1 not applicable) | verifier | ❌ 2 failures |
| 2026-11-26 16:26 | Integrate (Verify) | integrator | ✅ 1 integrated, 0 blocked, not committed |
| 2026-11-26 16:26 | Verify 3 (1 not applicable) | verifier | ❌ 3 failures |
| 2026-11-26 16:26 | Stopped: checks failing: pytest services/flight-engine/Dockerfile (test_every_rule_holds_for_every_service[flight-engine-import_sections] and test_the_runtime_stage_names_the_folder_its_conf_is_copied_to[flight-engine] failed, 2 failed, 4546 passed, 79 skipped); pytest tests/deploy/images/test_service_images.py (AssertionError at line 80, same test); pytest tests/rust/swarm_core/test_swarm_core_wheel.py (test_maturin_builds_exactly_one_wheel_named_after_the_module, with the same two failures; environment: no) | workflow | ❌ |
| 2026-11-26 16:26 | Work left uncommitted in /home/guillaume/Documents/Projects/PoC/swarm on feature/tickets; /ticket-run T0.18 continues it | scribe | ⚠️ |
| 2026-11-26 16:37 | Started with --force despite: T0.11 is open in /home/guillaume/Documents/Projects/PoC/swarm and changes services/gateway: wait for it (area lock). | 👤 person | ⚠️ |
| 2026-11-26 16:37 | Verify 1 (1 not applicable) | verifier | ✅ passed |
| 2026-11-26 16:37 | Review 1 (full) | reviewer | ✅ 0 blocking, 10 follow-ups |
| 2026-11-26 16:37 | Waiting for the person's code review: nothing is committed or pushed until PLAN.md says **Push:** 🟢 Approved (TKT-18) | 👀 | 🟡 Awaiting code review |
| 2026-11-26 17:04 | Found by T0.11's joint checks under load: MissionFeedClient.subscribe returned before NATS held the subscription, so the first frame after a join could be lost. Fixed by hand in services/gateway/src/gateway/clients/nats/mission_feed_client.py (flush after subscribe, handler registered first); the test-side flush a fix task of T0.11 had added to test_live_feed.py was removed. Gateway live tests pass, test_live_feed.py 5 times out of 5 | main session | ✅ |
| 2026-11-26 17:13 | Code reviewed and push approved by the person ("The T0.15 and T0.18 ticket is done. Go ahead with those."); pushed together with T0.11, which shares their files | 👤 person | 🟢 Approved |

## 🔜 Follow-ups

Non-blocking findings of the review (TKT-12). They do not hold the merge.

| File | What to change |
| --- | --- |
| packages/python/swarm-live/src/swarm_live/api/live/live_session.py:145 (close) | Owner K18. In close(), `await sender` only catches CancelledError. A sender that already ended with another exception makes close() raise before `source.leave` runs for that topic and every later one, and `self.joined` was already cleared. One example is Starlette's RuntimeError when a second sender writes after another sender saw the disconnect. In the gateway, those Missions then keep their mailbox and their NATS subscription for good. Fix: catch and log each sender's failure at WARNING with type(error).__name__, and call leave in a finally for each topic. |
| packages/python/swarm-live/src/swarm_live/api/live/live_session.py:100 (_subscribe) and services/gateway/src/gateway/api/live/live_router.py:57 (_serve) | Owners K18 and K25. Two errors escape after the socket is accepted: SEMissionFeedError from source.join, and SELiveFeedNotReadyError from source_for. The handler ends with an ASGI error instead of a clean close. Catch both, log them at WARNING or ERROR, and close the socket with 1011 or 1013. |
| packages/python/swarm-live/src/swarm_live/api/live/live_session.py:100 | Owner K18. One socket can subscribe to any number of Mission ids of its own Operator, and each new id opens a NATS subscription in the gateway. Cap the topics per session with a value in LiveSessionConfig, with its default written in conf/app.yaml. |
| services/flight-engine/src/flight_engine/api/live/live_endpoint.py:57 and services/flight-engine/src/flight_engine/models/missions/mission_catalog.py | Owners K26 and K19. The edge /v1/live has no Operator check, and its hub key is the topic without the Operator. This is safe only while it binds to 127.0.0.1 and an edge serves one Operator, and MissionCatalog accepts Missions of several Operators. Either refuse a catalogue with more than one operator_id, or key the edge hub by Operator. Record it for the Ground control edge ticket. |
| packages/rust/swarm-core/mavlink/src/frame.rs:152 (parse_v2) and services/flight-engine/src/flight_engine/clients/mavlink/mavlink_listener.py:73 | Owners K14 and K22. Signed frames are accepted without checking the signature, and message ids with no known CRC extra are accepted without a CRC check. Any UDP sender on the Mission port is trusted for any system id of the Mission. Plan MAVLink signing and a sender address check with the adapter work. |
| services/flight-engine/src/flight_engine/service/missions/squad_frame_builder.py:79-105 | Owner K24. An unknown battery or heading is sent as 0.0, which on screen reads the same as an empty battery. Consider an optional value in TelemetryFrame (a shared model change, so the generated types must be regenerated) or an explicit 'unknown' flag before T0.19 shows it. |
| tests/live/conftest.py:121 and tests/live/helpers.py:3 | Owner K11. Three changes: move the nested `consume` coroutine of the gateway_port fixture into a helper function; catch SELiveFeedNotReadyError instead of Exception in the readiness loop; and replace the file-level `# ruff: noqa: I001` with `# isort: skip` on the lines concerned. |
| docs/tickets/T0.18/tests-evidences/pytest.txt | Owner K11, through the verifier. The pytest report does not show whether tests/live/test_live_path.py ran or was skipped: it skips without nats-server or the swarm_core wheel, and 79 tests were skipped. Keep a dedicated evidence file for tests/live run with -rs, so that criterion 1 has evidence that it ran. |
| services/gateway/src/gateway/api/live/live_router.py:36 | Owner K25. `operator: ClassVar[LiveOperator]` is a lower-case class attribute. Name it OPERATOR, or make it an instance attribute, and keep the test's dependency override working. |
| packages/python/swarm-live/src/swarm_live/service/live_mailbox.py, live_hub.py, live_codec.py; services/flight-engine/src/flight_engine/clients/mavlink/mavlink_listener.py:81 | Owner T0.17, observability. Several DEBUG lines run per datagram, per frame and per watcher, and the root level is DEBUG with a file handler. That is hundreds of lines per second for 10 Drones. Measure their cost on the Telemetry path when the live path is instrumented. |

<!-- timings -->
## ⏱️ Timings

Measured from the agents' transcripts by `python3 .claude/scripts/reports/progress.py timings --ticket T0.18` (TKT-10).

| Measure | Value |
| --- | --- |
| 🕒 Ticket started | 2026-11-20 13:43:42 |
| 🕒 Last activity | 2026-11-26 16:38:51 |
| ⏱️ **Overall ticket time** (first start to last activity) | **146h55m08s** |
| 🤖 Time with agents working (sum of runs) | 1h38m35s |
| ⏸️ Time between runs (approvals, fixes) | 145h16m33s |
| 🔁 Workflow runs | 9 |
| 🪙 **Tokens consumed** (input, output, cache write, cache read) | **137.23M** |

#### 🪙 Tokens by model

| Model | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- |
| 🟢 haiku | 0k | 260k | 3.67M | 10.36M | **14.29M** |
| 🔵 sonnet | 2k | 1.88M | 7.46M | 87.51M | **96.86M** |
| 🟣 opus | 0k | 320k | 951k | 24.81M | **26.08M** |
| **All models** | 3k | 2.47M | 12.08M | 122.68M | **137.23M** |

### 1. ticket-plan · 2026-11-20 13:43:42 to 14:05:27 · ⏱️ 21m44s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Ticket | 13:43:42 | 13:44:36 | 0m53s | 2 |
| Check | 13:44:37 | 13:44:40 | 0m03s | 1 |
| Plan | 13:44:41 | 14:03:15 | 18m34s | 1 |
| Write | 14:03:15 | 14:05:27 | 2m11s | 2 |

Tokens of this run: 0k · 374k · 1.08M · 19.09M · **20.54M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ done check T0.18 | 🟢 haiku | 13:43:42 | 13:43:55 | 0m12s | 0k | 0k | 96k | 102k | **200k** |
| ✅ ticket-writer T0.18 | 🔵 sonnet | 13:43:57 | 13:44:36 | 0m39s | 0k | 16k | 116k | 1.55M | **1.68M** |
| ✅ check TICKET.md T0.18 | 🟢 haiku | 13:44:37 | 13:44:40 | 0m03s | 0k | 0k | 51k | 99k | **151k** |
| ✅ planner T0.18 | 🟣 opus | 13:44:41 | 14:03:15 | 18m34s | 0k | 278k | 547k | 16.07M | **16.90M** |
| ✅ scribe T0.18 | 🟢 haiku | 14:03:15 | 14:05:23 | 2m07s | 0k | 78k | 217k | 1.22M | **1.52M** |
| ✅ check PLAN.md T0.18 | 🟢 haiku | 14:05:24 | 14:05:27 | 0m02s | 0k | 0k | 48k | 51k | **99k** |

### 2. workflow · 2026-11-23 18:40:57 to 18:58:47 · ⏱️ 17m50s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 18:40:57 | 18:41:40 | 0m43s | 4 |
| Waves | 18:41:40 | 18:58:47 | 17m07s | 30 |

Tokens of this run: 1k · 1.21M · 3.94M · 47.34M · **52.49M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.18 | 🟢 haiku | 18:40:57 | 18:41:14 | 0m17s | 0k | 10k | 118k | 120k | **249k** |
| ✅ plan check T0.18 | 🟢 haiku | 18:41:15 | 18:41:18 | 0m03s | 0k | 0k | 60k | 105k | **166k** |
| ✅ start rule T0.18 | 🟢 haiku | 18:41:19 | 18:41:27 | 0m08s | 0k | 0k | 53k | 55k | **109k** |
| ✅ integrator prepare T0.18 | 🔵 sonnet | 18:41:28 | 18:41:40 | 0m12s | 0k | 0k | 58k | 113k | **173k** |
| ✅ K01 test-writer | 🔵 sonnet | 18:41:40 | 18:43:35 | 1m54s | 0k | 45k | 100k | 885k | **1.03M** |
| ✅ K02 test-writer | 🔵 sonnet | 18:41:40 | 18:42:11 | 0m30s | 0k | 8k | 81k | 380k | **470k** |
| ✅ K03 test-writer | 🔵 sonnet | 18:41:41 | 18:42:46 | 1m05s | 0k | 32k | 118k | 1.55M | **1.71M** |
| ✅ K04 test-writer | 🔵 sonnet | 18:41:41 | 18:45:10 | 3m29s | 0k | 109k | 187k | 3.67M | **3.96M** |
| ✅ K05 test-writer | 🔵 sonnet | 18:41:41 | 18:45:09 | 3m28s | 0k | 179k | 283k | 2.11M | **2.57M** |
| ✅ K06 test-writer | 🔵 sonnet | 18:41:41 | 18:43:04 | 1m23s | 0k | 41k | 114k | 1.42M | **1.58M** |
| ✅ K07 test-writer | 🔵 sonnet | 18:41:41 | 18:45:35 | 3m53s | 0k | 114k | 215k | 3.64M | **3.97M** |
| ✅ K08 test-writer | 🔵 sonnet | 18:41:41 | 18:43:33 | 1m51s | 0k | 61k | 168k | 1.99M | **2.22M** |
| ✅ K09 test-writer | 🔵 sonnet | 18:42:12 | 18:44:26 | 2m13s | 0k | 73k | 141k | 3.84M | **4.06M** |
| ✅ K10 test-writer | 🔵 sonnet | 18:42:46 | 18:44:14 | 1m28s | 0k | 31k | 114k | 1.85M | **2.00M** |
| ✅ K11 test-writer | 🔵 sonnet | 18:43:05 | 18:45:49 | 2m43s | 0k | 71k | 190k | 2.97M | **3.23M** |
| ✅ K12 test-writer | 🔵 sonnet | 18:43:34 | 18:44:02 | 0m28s | 0k | 5k | 73k | 726k | **804k** |
| ✅ integrator Waves | 🔵 sonnet | 18:45:49 | 18:46:09 | 0m20s | 0k | 3k | 70k | 617k | **691k** |
| ✅ K13 implementer | 🔵 sonnet | 18:46:09 | 18:46:36 | 0m26s | 0k | 5k | 67k | 507k | **581k** |
| ❌ K14 rust-implementer | 🔵 sonnet | 18:46:10 | 18:49:38 | 3m28s | 0k | 75k | 170k | 1.83M | **2.08M** |
| ❌ K15 implementer | 🔵 sonnet | 18:46:10 | 18:47:31 | 1m21s | 0k | 15k | 98k | 1.49M | **1.60M** |
| ✅ K16 implementer | 🔵 sonnet | 18:46:10 | 18:46:31 | 0m21s | 0k | 3k | 66k | 568k | **639k** |
| ✅ K01 test-writer (fix) | 🔵 sonnet | 18:49:39 | 18:49:56 | 0m17s | 0k | 1k | 57k | 182k | **242k** |
| ✅ K03 test-writer (fix) | 🔵 sonnet | 18:49:39 | 18:49:52 | 0m13s | 0k | 1k | 59k | 310k | **370k** |
| ✅ integrator Waves | 🔵 sonnet | 18:49:57 | 18:50:08 | 0m11s | 0k | 2k | 68k | 553k | **624k** |
| ✅ K14 rust-implementer | 🔵 sonnet | 18:50:09 | 18:52:47 | 2m37s | 0k | 72k | 123k | 1.56M | **1.76M** |
| ✅ K15 implementer | 🔵 sonnet | 18:50:09 | 18:51:25 | 1m16s | 0k | 15k | 96k | 1.68M | **1.80M** |
| ✅ integrator Waves | 🔵 sonnet | 18:52:47 | 18:53:23 | 0m35s | 0k | 5k | 85k | 1.46M | **1.55M** |
| ✅ K17 rust-implementer | 🔵 sonnet | 18:53:23 | 18:54:19 | 0m55s | 0k | 8k | 74k | 591k | **674k** |
| ✅ K18 implementer | 🔵 sonnet | 18:53:23 | 18:55:48 | 2m24s | 0k | 69k | 177k | 2.84M | **3.08M** |
| ✅ K19 implementer | 🔵 sonnet | 18:53:23 | 18:57:53 | 4m29s | 0k | 112k | 259k | 5.15M | **5.52M** |
| ❌ K20 doc-writer | 🟢 haiku | 18:53:23 | 18:54:07 | 0m43s | 0k | 11k | 78k | 1.18M | **1.27M** |
| ❌ K20 doc-writer | 🟢 haiku | 18:57:56 | 18:58:28 | 0m31s | 0k | 10k | 124k | 906k | **1.04M** |
| ✅ integrator Waves | 🔵 sonnet | 18:58:28 | 18:58:37 | 0m08s | 0k | 0k | 62k | 238k | **301k** |
| ✅ scribe T0.18 | 🟢 haiku | 18:58:37 | 18:58:47 | 0m10s | 0k | 4k | 122k | 241k | **368k** |

### 3. workflow · 2026-11-23 18:59:32 to 19:00:06 · ⏱️ 0m33s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 18:59:32 | 19:00:06 | 0m33s | 3 |

Tokens of this run: 0k · 11k · 191k · 368k · **571k** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.18 | 🟢 haiku | 18:59:32 | 18:59:53 | 0m20s | 0k | 11k | 82k | 257k | **351k** |
| ✅ plan check T0.18 | 🟢 haiku | 18:59:53 | 18:59:56 | 0m02s | 0k | 0k | 54k | 55k | **109k** |
| ✅ start rule T0.18 | 🟢 haiku | 18:59:56 | 19:00:06 | 0m10s | 0k | 0k | 54k | 55k | **109k** |

### 4. workflow · 2026-11-23 19:00:28 to 19:17:48 · ⏱️ 17m19s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 19:00:28 | 19:01:14 | 0m46s | 4 |
| Waves | 19:01:15 | 19:17:48 | 16m33s | 20 |

Tokens of this run: 0k · 630k · 2.41M · 30.55M · **33.60M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.18 | 🟢 haiku | 19:00:28 | 19:00:49 | 0m20s | 0k | 11k | 33k | 489k | **533k** |
| ✅ plan check T0.18 | 🟢 haiku | 19:00:49 | 19:00:52 | 0m02s | 0k | 0k | 7k | 159k | **166k** |
| ✅ start rule T0.18 | 🟢 haiku | 19:00:52 | 19:01:02 | 0m09s | 0k | 0k | 54k | 55k | **109k** |
| ✅ integrator prepare T0.18 | 🔵 sonnet | 19:01:03 | 19:01:14 | 0m11s | 0k | 0k | 61k | 125k | **187k** |
| ✅ K21 implementer | 🔵 sonnet | 19:01:15 | 19:04:07 | 2m52s | 0k | 71k | 188k | 3.30M | **3.56M** |
| ✅ K22 implementer | 🔵 sonnet | 19:01:15 | 19:03:04 | 1m48s | 0k | 79k | 186k | 2.59M | **2.86M** |
| ✅ K23 implementer | 🔵 sonnet | 19:01:15 | 19:01:46 | 0m31s | 0k | 6k | 66k | 745k | **817k** |
| ✅ integrator Waves | 🔵 sonnet | 19:04:13 | 19:04:22 | 0m09s | 0k | 0k | 74k | 299k | **375k** |
| ❌ K24 implementer | 🔵 sonnet | 19:04:22 | 19:07:25 | 3m02s | 0k | 109k | 206k | 3.40M | **3.71M** |
| ❌ K25 implementer | 🔵 sonnet | 19:04:22 | 19:07:41 | 3m18s | 0k | 39k | 165k | 3.26M | **3.47M** |
| ✅ K07 test-writer (fix) | 🔵 sonnet | 19:07:48 | 19:08:11 | 0m23s | 0k | 2k | 61k | 682k | **746k** |
| ❌ K04 test-writer (fix) | 🔵 sonnet | 19:07:48 | 19:08:14 | 0m25s | 0k | 3k | 75k | 750k | **829k** |
| ✅ K10 test-writer (fix) | 🔵 sonnet | 19:07:48 | 19:08:05 | 0m16s | 0k | 3k | 71k | 177k | **252k** |
| ✅ K09 test-writer (fix) | 🔵 sonnet | 19:07:48 | 19:08:08 | 0m19s | 0k | 3k | 64k | 359k | **427k** |
| ✅ integrator Waves | 🔵 sonnet | 19:08:14 | 19:08:25 | 0m10s | 0k | 0k | 62k | 237k | **300k** |
| ✅ K24 implementer | 🔵 sonnet | 19:08:25 | 19:11:40 | 3m14s | 0k | 113k | 198k | 3.55M | **3.86M** |
| ✅ K25 implementer | 🔵 sonnet | 19:08:26 | 19:11:02 | 2m36s | 0k | 26k | 153k | 2.22M | **2.40M** |
| ✅ integrator Waves | 🔵 sonnet | 19:11:48 | 19:11:56 | 0m08s | 0k | 0k | 80k | 302k | **383k** |
| ❌ K26 implementer | 🔵 sonnet | 19:11:57 | 19:16:02 | 4m04s | 0k | 143k | 222k | 6.13M | **6.50M** |
| ✅ K06 test-writer (fix) | 🔵 sonnet | 19:16:09 | 19:16:21 | 0m11s | 0k | 2k | 63k | 174k | **240k** |
| ✅ K07 test-writer (fix) | 🔵 sonnet | 19:16:09 | 19:16:18 | 0m08s | 0k | 0k | 57k | 118k | **176k** |
| ✅ integrator Waves | 🔵 sonnet | 19:16:22 | 19:16:30 | 0m08s | 0k | 0k | 61k | 235k | **298k** |
| ❌ K26 implementer | 🔵 sonnet | 19:16:30 | 19:17:30 | 0m59s | 0k | 4k | 76k | 952k | **1.03M** |
| ✅ scribe T0.18 | 🟢 haiku | 19:17:37 | 19:17:48 | 0m10s | 0k | 3k | 120k | 238k | **361k** |

### 5. workflow · 2026-11-23 19:19:07 to 19:21:03 · ⏱️ 1m56s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Finish | 19:20:50 | 19:21:03 | 0m12s | 1 |
| Gate | 19:19:07 | 19:19:53 | 0m46s | 4 |
| Verify | 19:19:53 | 19:20:50 | 0m57s | 1 |

Tokens of this run: 0k · 21k · 399k · 994k · **1.42M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.18 | 🟢 haiku | 19:19:07 | 19:19:27 | 0m20s | 0k | 11k | 75k | 231k | **319k** |
| ✅ plan check T0.18 | 🟢 haiku | 19:19:27 | 19:19:30 | 0m02s | 0k | 0k | 56k | 53k | **109k** |
| ✅ start rule T0.18 | 🟢 haiku | 19:19:30 | 19:19:42 | 0m11s | 0k | 0k | 57k | 108k | **166k** |
| ✅ integrator prepare T0.18 | 🔵 sonnet | 19:19:43 | 19:19:53 | 0m10s | 0k | 0k | 55k | 119k | **175k** |
| ✅ verifier round 1 | 🟢 haiku | 19:19:53 | 19:20:50 | 0m57s | 0k | 2k | 60k | 169k | **233k** |
| ✅ scribe T0.18 | 🟢 haiku | 19:20:50 | 19:21:03 | 0m12s | 0k | 6k | 93k | 311k | **411k** |

### 6. workflow · 2026-11-26 15:58:05 to 15:58:42 · ⏱️ 0m36s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 15:58:05 | 15:58:42 | 0m36s | 3 |

Tokens of this run: 0k · 13k · 258k · 653k · **925k** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.18 | 🟢 haiku | 15:58:05 | 15:58:29 | 0m23s | 0k | 12k | 137k | 431k | **580k** |
| ✅ plan check T0.18 | 🟢 haiku | 15:58:29 | 15:58:31 | 0m02s | 0k | 0k | 61k | 109k | **172k** |
| ✅ start rule T0.18 | 🟢 haiku | 15:58:32 | 15:58:42 | 0m10s | 0k | 0k | 59k | 112k | **172k** |

### 7. workflow · 2026-11-26 15:59:30 to 16:06:24 · ⏱️ 6m53s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Finish | 16:06:12 | 16:06:24 | 0m11s | 1 |
| Gate | 15:59:30 | 16:00:18 | 0m47s | 4 |
| Verify | 16:00:18 | 16:06:12 | 5m53s | 15 |

Tokens of this run: 0k · 66k · 1.34M · 8.36M · **9.77M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.18 | 🟢 haiku | 15:59:30 | 15:59:52 | 0m21s | 0k | 11k | 74k | 365k | **451k** |
| ✅ plan check T0.18 | 🟢 haiku | 15:59:52 | 15:59:56 | 0m03s | 0k | 0k | 58k | 110k | **169k** |
| ✅ start rule T0.18 | 🟢 haiku | 15:59:56 | 16:00:06 | 0m09s | 0k | 0k | 55k | 56k | **111k** |
| ✅ integrator prepare T0.18 | 🔵 sonnet | 16:00:07 | 16:00:18 | 0m10s | 0k | 0k | 60k | 116k | **177k** |
| ✅ verifier round 1 | 🟢 haiku | 16:00:18 | 16:01:24 | 1m05s | 0k | 1k | 62k | 172k | **236k** |
| ✅ FIX-pyproject.toml implementer (fix) | 🔵 sonnet | 16:01:24 | 16:02:10 | 0m46s | 0k | 2k | 75k | 555k | **633k** |
| ❌ K01 test-writer (fix) | 🔵 sonnet | 16:01:24 | 16:02:08 | 0m43s | 0k | 2k | 70k | 503k | **576k** |
| ❌ K14 rust-implementer (fix) | 🔵 sonnet | 16:01:24 | 16:02:37 | 1m12s | 0k | 5k | 83k | 674k | **763k** |
| ❌ K15 implementer (fix) | 🔵 sonnet | 16:01:24 | 16:01:57 | 0m33s | 0k | 2k | 69k | 362k | **434k** |
| ❌ K17 rust-implementer (fix) | 🔵 sonnet | 16:01:25 | 16:02:26 | 1m01s | 0k | 5k | 75k | 644k | **725k** |
| ✅ integrator Verify | 🔵 sonnet | 16:02:38 | 16:02:45 | 0m07s | 0k | 0k | 57k | 179k | **238k** |
| ✅ verifier round 2 | 🟢 haiku | 16:02:46 | 16:03:49 | 1m03s | 0k | 1k | 6k | 227k | **235k** |
| ✅ K08 test-writer (fix) | 🔵 sonnet | 16:03:50 | 16:04:41 | 0m50s | 0k | 7k | 95k | 1.06M | **1.16M** |
| ❌ K01 test-writer (fix) | 🔵 sonnet | 16:03:50 | 16:04:30 | 0m39s | 0k | 3k | 66k | 492k | **561k** |
| ❌ K14 rust-implementer (fix) | 🔵 sonnet | 16:03:50 | 16:04:54 | 1m04s | 0k | 6k | 71k | 680k | **758k** |
| ❌ K15 implementer (fix) | 🔵 sonnet | 16:03:50 | 16:04:21 | 0m30s | 0k | 2k | 67k | 426k | **496k** |
| ❌ K17 rust-implementer (fix) | 🔵 sonnet | 16:03:50 | 16:04:50 | 0m59s | 0k | 4k | 78k | 895k | **978k** |
| ✅ integrator Verify | 🔵 sonnet | 16:04:54 | 16:05:07 | 0m12s | 0k | 1k | 62k | 480k | **544k** |
| ✅ verifier round 3 | 🟢 haiku | 16:05:08 | 16:06:12 | 1m04s | 0k | 1k | 57k | 176k | **234k** |
| ✅ scribe T0.18 | 🟢 haiku | 16:06:12 | 16:06:24 | 0m11s | 0k | 4k | 85k | 183k | **273k** |

### 8. workflow · 2026-11-26 16:06:56 to 16:27:01 · ⏱️ 20m04s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Finish | 16:26:48 | 16:27:01 | 0m13s | 1 |
| Gate | 16:06:56 | 16:07:46 | 0m50s | 4 |
| Verify | 16:07:46 | 16:26:48 | 19m01s | 10 |

Tokens of this run: 0k · 41k · 1.26M · 4.20M · **5.51M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.18 | 🟢 haiku | 16:06:56 | 16:07:18 | 0m21s | 0k | 12k | 77k | 359k | **448k** |
| ✅ plan check T0.18 | 🟢 haiku | 16:07:18 | 16:07:21 | 0m03s | 0k | 0k | 61k | 107k | **169k** |
| ✅ start rule T0.18 | 🟢 haiku | 16:07:22 | 16:07:33 | 0m11s | 0k | 0k | 55k | 56k | **111k** |
| ✅ integrator prepare T0.18 | 🔵 sonnet | 16:07:34 | 16:07:46 | 0m11s | 0k | 0k | 56k | 121k | **177k** |
| ✅ verifier round 1 | 🟢 haiku | 16:07:46 | 16:13:36 | 5m49s | 0k | 5k | 177k | 58k | **241k** |
| ✅ K15 implementer (fix) | 🔵 sonnet | 16:13:36 | 16:14:01 | 0m24s | 0k | 1k | 68k | 424k | **494k** |
| ❌ K23 implementer (fix) | 🔵 sonnet | 16:13:36 | 16:13:58 | 0m21s | 0k | 3k | 74k | 692k | **770k** |
| ✅ K02 test-writer (fix) | 🔵 sonnet | 16:13:37 | 16:13:59 | 0m22s | 0k | 1k | 83k | 389k | **474k** |
| ✅ integrator Verify | 🔵 sonnet | 16:14:14 | 16:14:27 | 0m12s | 0k | 1k | 70k | 294k | **365k** |
| ✅ verifier round 2 | 🟢 haiku | 16:14:27 | 16:20:20 | 5m52s | 0k | 1k | 121k | 113k | **237k** |
| ❌ K23 implementer (fix) | 🔵 sonnet | 16:20:20 | 16:20:36 | 0m16s | 0k | 2k | 72k | 428k | **503k** |
| ✅ K02 test-writer (fix) | 🔵 sonnet | 16:20:20 | 16:20:41 | 0m21s | 0k | 2k | 78k | 449k | **530k** |
| ✅ integrator Verify | 🔵 sonnet | 16:20:42 | 16:20:50 | 0m08s | 0k | 1k | 69k | 294k | **365k** |
| ✅ verifier round 3 | 🟢 haiku | 16:20:50 | 16:26:48 | 5m57s | 0k | 2k | 126k | 110k | **238k** |
| ✅ scribe T0.18 | 🟢 haiku | 16:26:48 | 16:27:01 | 0m13s | 0k | 4k | 69k | 300k | **374k** |

### 9. workflow · 2026-11-26 16:27:16 to 16:38:51 · ⏱️ 11m34s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Finish | 16:37:26 | 16:38:51 | 1m24s | 4 |
| Gate | 16:27:16 | 16:28:06 | 0m49s | 4 |
| Review | 16:33:58 | 16:37:26 | 3m27s | 1 |
| Verify | 16:28:06 | 16:33:57 | 5m50s | 1 |

Tokens of this run: 0k · 98k · 1.20M · 11.11M · **12.41M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.18 | 🟢 haiku | 16:27:16 | 16:27:37 | 0m21s | 0k | 12k | 78k | 360k | **450k** |
| ✅ plan check T0.18 | 🟢 haiku | 16:27:38 | 16:27:41 | 0m03s | 0k | 0k | 61k | 107k | **169k** |
| ✅ start rule T0.18 | 🟢 haiku | 16:27:41 | 16:27:52 | 0m11s | 0k | 0k | 55k | 56k | **111k** |
| ✅ integrator prepare T0.18 | 🔵 sonnet | 16:27:53 | 16:28:06 | 0m13s | 0k | 0k | 60k | 116k | **177k** |
| ✅ verifier round 1 | 🟢 haiku | 16:28:06 | 16:33:57 | 5m50s | 0k | 0k | 121k | 110k | **232k** |
| ✅ reviewer round 1 | 🟣 opus | 16:33:58 | 16:37:26 | 3m27s | 0k | 42k | 403k | 8.74M | **9.18M** |
| ✅ scribe T0.18 | 🟢 haiku | 16:37:26 | 16:37:58 | 0m31s | 0k | 16k | 173k | 280k | **471k** |
| ✅ explainer T0.18 | 🔵 sonnet | 16:37:26 | 16:38:43 | 1m17s | 0k | 24k | 133k | 1.23M | **1.39M** |
| ✅ docs check T0.18 1 | 🟢 haiku | 16:38:43 | 16:38:46 | 0m02s | 0k | 0k | 55k | 56k | **111k** |
| ✅ scribe T0.18 (timings) | 🟢 haiku | 16:38:47 | 16:38:51 | 0m03s | 0k | 0k | 55k | 60k | **116k** |
<!-- /timings -->
