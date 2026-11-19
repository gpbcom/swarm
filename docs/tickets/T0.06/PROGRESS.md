# T0.06: Progress

**Status:** 🟡 Planned · **Ticket:** [TICKET.md](TICKET.md)

<!-- ticket:specs -->
## 📚 Specifications

The technical pages, features, use cases and business rules of [TICKET.md](TICKET.md), copied by `python3 .claude/scripts/ticket_refs.py sync`.

- [🧱 Data models: conventions](../../specs/technical/02-data-models.md#conventions)
- [🧱 Data models: events](../../specs/technical/02-data-models.md#events)
- [🧱 Data models: main models](../../specs/technical/02-data-models.md#models)
- [🧱 Data models: telemetry frames and commands](../../specs/technical/02-data-models.md#telemetry)
- [🧱 Data models: versioning](../../specs/technical/02-data-models.md#versioning)
- [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo)
<!-- /ticket:specs -->

## 📝 Events

| Time | Event | By | Result |
| --- | --- | --- | --- |
| 2026-11-19 10:51 | Plan written: 28 tasks, 6 waves | scribe | ⏳ Awaiting approval |
| 2026-11-19 10:57 | Plan approved | the person | ✅ Approved |
| 2026-11-19 11:23 | Wave 1: 14 of 14 tasks done | workers | ✅ |
| 2026-11-19 11:23 | Merge (Waves) | integrator | ✅ 14 merged, 4 blocked |
| 2026-11-19 11:23 | Wave 2: 4 of 4 tasks done | workers | ✅ |
| 2026-11-19 11:23 | Merge (Waves) | integrator | ✅ 4 merged, 0 blocked |
| 2026-11-19 11:23 | Wave 3: 5 of 6 tasks done | workers | ❌ |
| 2026-11-19 11:23 | Merge (Waves) | integrator | ✅ 5 merged, 0 blocked |
| 2026-11-19 11:23 | Stopped in wave 3: K21 not done | workflow | ❌ |
| 2026-11-19 11:25 | K04 test fixed: `test_none_becomes_the_default[agent_name]` used a Swarm agent with no agent name, which `test_an_inconsistent_kind_is_refused` refuses; the case now uses a Person actor | the person (fix by the main session) | ✅ 88 passed |
| 2026-11-19 11:25 | K21 second attempt merged into ticket/T0.06 (`worktree-wf_0c19dd9d-ef0-30`) | the person (merge by the main session) | ✅ Re-run continues at wave 4 (TKT-11) |

| 2026-11-19 11:30 | Wave 4: 1 of 1 tasks done | workers | ✅ |
| 2026-11-19 11:30 | Merge (Waves) | integrator | ✅ 1 merged, 0 blocked |
| 2026-11-19 11:30 | Wave 5: 1 of 1 tasks done | workers | ✅ |
| 2026-11-19 11:30 | Merge (Waves) | integrator | ✅ 1 merged, 0 blocked |
| 2026-11-19 11:30 | Wave 6: 2 of 2 tasks done | workers | ✅ |
| 2026-11-19 11:30 | Merge (Waves) | integrator | ✅ 2 merged, 1 blocked |
| 2026-11-19 11:30 | Verify 1 (1 not applicable) | verifier | ❌ 2 failures |
| 2026-11-19 11:30 | Verify 2 (1 not applicable) | verifier | ❌ 2 failures |
| 2026-11-19 11:30 | Verify 3 (1 not applicable) | verifier | ❌ 2 failures |
| 2026-11-19 11:30 | Stopped: checks failing | workflow | ❌ Open failures: (1) ruff format: 2 files would be reformatted, `packages/python/swarm-lifecycle/src/swarm_lifecycle/models/enums.py` (the `SEActorInvalidKind` message to reformat); (2) test: `packages/ts/live` `node --experimental-strip-types --test test/*.test.ts` fails with 1 failing test (`pnpm recursive run` failed in `packages/ts/live`); neither is an environment failure. |
| 2026-11-19 11:34 | Fixed by the main session at the person's request: `ruff format` on `models/events/actor.py` (K21) and `api/cli/export_schemas.py` (K26), the two files the verifier meant (`checks.py` named the wrong file, so the fix went to K15) | the person | ✅ ruff format, ruff check, mypy and 508 tests pass |
| 2026-11-19 11:34 | Environment fixed: `/usr/bin/node` v22.22.1 has no TypeScript type stripping; `~/.local/bin/node` now links to nvm Node v22.17.1, which is the nvm default | the person | ✅ `packages/ts/live` test: 8 passed |
| 2026-11-19 11:40 | Verify 1 (1 not applicable) | verifier | ✅ passed |
| 2026-11-19 11:40 | Review 1 (full) | reviewer | ✅ 0 blocking, 9 follow-ups |

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| packages/python/swarm-models/src/swarm_models/models/operators/operator.py:15 | K19: the Operator docstring says "A person who pilots drones", but in the glossary (ent-operator) an Operator is the organisation that uses Swarm. The text also calls it "operator" in lower case. Rewrite the docstring and field descriptions with the glossary meaning and spelling, check `cell_assignment.py` the same way, then regenerate the schema bundle, `generated.rs` and `models.ts`, which all copy the wrong text today. |
| packages/python/swarm-models/src/swarm_models/models/commands/enums/command_kind.py:17 | K23: the MANUAL_CONTROL docstring reads "Hand the control to the Operator". Under the glossary and 06-security, the Pilot takes manual control. Fix the wording and regenerate. |
| packages/python/swarm-models/src/swarm_models/models/base/swarm_model.py:58 | K15 and the model tasks K19 to K23: two-sentence messages sit on one source line, in every parse_* helper and most model validators. Put one sentence per line, with `# noqa: E501` on the first line. |
| packages/python/swarm-models/src/swarm_models/models/base/swarm_model.py:166 | K15: with `maximum_exclusive=True`, parse_float's message still shows an inclusive range (`[0, 360]`, even though 360 is refused). Say that the maximum is excluded. |
| packages/python/swarm-models/src/swarm_models/models/telemetry/telemetry_frame.py:85 | K22: the bounds (lat_e7, lon_e7, heading_deg, the *_pct fields, seq, t_us) exist only in mode='before' validators, so the JSON Schema, and with it the Rust and TypeScript types, carries none of them. Also declare them as Field(ge=..., le=..., lt=...), so the generated types hold the same limits. |
| packages/python/swarm-models/src/swarm_models/service/schemas/schema_exporter.py:85 | K25 and K28: the whole class docstrings (Attributes and Notes sections included) end up as schema descriptions. Pydantic's field titles also make json-schema-to-typescript emit duplicate aliases (ActorKind1, Id1 to Id3, OperatorId1 to OperatorId3). Consider short schema descriptions and dropping field titles before more models are added. |
| packages/python/swarm-models/src/swarm_models/models/commands/command.py:58 | K23 and K20: several validators raise without a `Raises:` section, in Command (id, mission_id, drone_id, issued_by) and in Person and Role (id, operator_id, name, person_id). Add one to each. |
| packages/python/swarm-models/src/swarm_models/storage/schemas/schema_folder.py:25 | K24: DEFAULT_ROOT uses `Path(__file__).parents[4]`, which works only from the source tree or an editable install. If the package is ever installed as a wheel, pass the root explicitly or ship the bundle as package data. |
| packages/python/swarm-models/src/swarm_models/models/telemetry/telemetry_frame.py:96 | K22: TelemetryFrame validates every field in Python before-validators, which skip pydantic-core's fast path. No budget applies yet. Measure it when frames enter the live path (T0.18, T0.19). |

<!-- timings -->
## ⏱️ Timings

Measured from the agents' transcripts by `python3 .claude/scripts/progress.py timings --ticket T0.06` (TKT-10).

| Measure | Value |
| --- | --- |
| 🕒 Ticket started | 2026-11-19 10:32:05 |
| 🕒 Last activity | 2026-11-19 11:41:34 |
| ⏱️ **Overall ticket time** (first start to last activity) | **1h09m29s** |
| 🤖 Time with agents working (sum of runs) | 38m40s |
| ⏸️ Time between runs (approvals, fixes) | 30m48s |
| 🔁 Workflow runs | 4 |
| 🪙 **Tokens consumed** (input, output, cache write, cache read) | **39.68M** |

#### 🪙 Tokens by model

| Model | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- |
| 🔵 sonnet | 1k | 630k | 2.63M | 22.22M | **25.48M** |
| 🟢 haiku | 0k | 196k | 1.01M | 2.78M | **3.99M** |
| 🟣 opus | 0k | 288k | 573k | 9.34M | **10.20M** |
| **All models** | 1k | 1.12M | 4.22M | 34.35M | **39.68M** |

### 1. ticket-plan · 2026-11-19 10:32:05 to 10:51:07 · ⏱️ 19m02s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Ticket | 10:32:05 | 10:32:26 | 0m21s | 1 |
| Check | 10:32:27 | 10:32:30 | 0m03s | 1 |
| Plan | 10:32:31 | 10:48:33 | 16m02s | 1 |
| Write | 10:48:33 | 10:51:07 | 2m33s | 2 |

Tokens of this run: 0k · 370k · 798k · 6.73M · **7.90M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ ticket-writer T0.06 | 🔵 sonnet | 10:32:05 | 10:32:26 | 0m21s | 0k | 12k | 158k | 503k | **674k** |
| ✅ check TICKET.md T0.06 | 🟢 haiku | 10:32:27 | 10:32:30 | 0m03s | 0k | 0k | 33k | 64k | **98k** |
| ✅ planner T0.06 | 🟣 opus | 10:32:31 | 10:48:33 | 16m02s | 0k | 255k | 342k | 5.27M | **5.87M** |
| ✅ scribe T0.06 | 🟢 haiku | 10:48:33 | 10:51:03 | 2m29s | 0k | 101k | 225k | 827k | **1.15M** |
| ✅ check PLAN.md T0.06 | 🟢 haiku | 10:51:04 | 10:51:07 | 0m02s | 0k | 0k | 37k | 61k | **98k** |

### 2. ticket-run · 2026-11-19 11:14:22 to 11:23:56 · ⏱️ 9m34s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 11:14:22 | 11:15:20 | 0m58s | 3 |
| Waves | 11:15:21 | 11:23:56 | 8m35s | 29 |
| Verify | | | not run | 0 |
| Review | | | not run | 0 |
| Finish | | | not run | 0 |

Tokens of this run: 0k · 594k · 2.00M · 18.45M · **21.04M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.06 | 🟢 haiku | 11:14:22 | 11:14:49 | 0m27s | 0k | 18k | 55k | 61k | **135k** |
| ✅ plan check T0.06 | 🟢 haiku | 11:14:49 | 11:14:52 | 0m02s | 0k | 0k | 32k | 62k | **96k** |
| ✅ integrator prepare T0.06 | 🔵 sonnet | 11:14:53 | 11:15:20 | 0m27s | 0k | 0k | 37k | 93k | **131k** |
| ✅ K01 test-writer | 🔵 sonnet | 11:15:21 | 11:16:18 | 0m57s | 0k | 17k | 66k | 521k | **605k** |
| ✅ K02 test-writer | 🔵 sonnet | 11:15:21 | 11:16:13 | 0m52s | 0k | 19k | 60k | 477k | **558k** |
| ✅ K03 test-writer | 🔵 sonnet | 11:15:21 | 11:16:28 | 1m07s | 0k | 30k | 70k | 577k | **679k** |
| ✅ K04 test-writer | 🔵 sonnet | 11:15:21 | 11:16:57 | 1m36s | 0k | 44k | 100k | 845k | **989k** |
| ✅ K05 test-writer | 🔵 sonnet | 11:15:21 | 11:17:15 | 1m54s | 0k | 59k | 111k | 723k | **895k** |
| ✅ K06 test-writer | 🔵 sonnet | 11:15:21 | 11:16:22 | 1m00s | 0k | 24k | 67k | 528k | **621k** |
| ✅ K07 test-writer | 🔵 sonnet | 11:15:21 | 11:15:48 | 0m27s | 0k | 4k | 43k | 297k | **345k** |
| ✅ K08 test-writer | 🔵 sonnet | 11:15:21 | 11:16:16 | 0m54s | 0k | 14k | 62k | 609k | **686k** |
| ✅ K09 test-writer | 🔵 sonnet | 11:15:49 | 11:16:25 | 0m36s | 0k | 11k | 40k | 538k | **590k** |
| ✅ K10 test-writer | 🔵 sonnet | 11:16:14 | 11:16:45 | 0m31s | 0k | 7k | 41k | 299k | **349k** |
| ✅ K11 test-writer | 🔵 sonnet | 11:16:17 | 11:16:49 | 0m32s | 0k | 10k | 37k | 379k | **427k** |
| ✅ K12 test-writer | 🔵 sonnet | 11:16:18 | 11:16:49 | 0m30s | 0k | 7k | 40k | 341k | **389k** |
| ✅ K13 test-writer | 🔵 sonnet | 11:16:22 | 11:16:35 | 0m13s | 0k | 1k | 36k | 114k | **152k** |
| ✅ K14 doc-writer | 🟢 haiku | 11:16:25 | 11:16:43 | 0m17s | 0k | 9k | 71k | 392k | **473k** |
| ✅ integrator Waves | 🔵 sonnet | 11:17:16 | 11:17:36 | 0m19s | 0k | 3k | 48k | 367k | **419k** |
| ✅ K15 implementer | 🔵 sonnet | 11:17:36 | 11:18:46 | 1m10s | 0k | 49k | 71k | 1.31M | **1.43M** |
| ✅ K16 rust-implementer | 🔵 sonnet | 11:17:36 | 11:18:55 | 1m19s | 0k | 23k | 54k | 786k | **864k** |
| ✅ K17 frontend-implementer | 🔵 sonnet | 11:17:36 | 11:18:50 | 1m14s | 0k | 19k | 65k | 1.50M | **1.59M** |
| ✅ K18 implementer | 🔵 sonnet | 11:17:36 | 11:17:49 | 0m13s | 0k | 1k | 35k | 143k | **181k** |
| ✅ integrator Waves | 🔵 sonnet | 11:18:56 | 11:19:14 | 0m18s | 0k | 1k | 39k | 206k | **247k** |
| ✅ K19 implementer | 🔵 sonnet | 11:19:15 | 11:20:15 | 0m59s | 0k | 18k | 66k | 739k | **825k** |
| ✅ K20 implementer | 🔵 sonnet | 11:19:16 | 11:20:33 | 1m17s | 0k | 27k | 76k | 799k | **903k** |
| ❌ K21 implementer | 🔵 sonnet | 11:19:16 | 11:21:55 | 2m38s | 0k | 57k | 116k | 2.20M | **2.38M** |
| ✅ K22 implementer | 🔵 sonnet | 11:19:16 | 11:20:48 | 1m32s | 0k | 35k | 113k | 815k | **964k** |
| ✅ K23 implementer | 🔵 sonnet | 11:19:16 | 11:20:23 | 1m07s | 0k | 26k | 70k | 500k | **597k** |
| ✅ K24 implementer | 🔵 sonnet | 11:19:16 | 11:19:48 | 0m32s | 0k | 7k | 46k | 401k | **454k** |
| ❌ K21 implementer | 🔵 sonnet | 11:21:56 | 11:23:32 | 1m35s | 0k | 33k | 90k | 1.39M | **1.52M** |
| ✅ integrator Waves | 🔵 sonnet | 11:23:33 | 11:23:44 | 0m11s | 0k | 1k | 38k | 202k | **242k** |
| ✅ scribe T0.06 | 🟢 haiku | 11:23:46 | 11:23:56 | 0m10s | 0k | 4k | 89k | 208k | **302k** |

### 3. ticket-run · 2026-11-19 11:25:07 to 11:30:19 · ⏱️ 5m11s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 11:25:07 | 11:25:51 | 0m43s | 3 |
| Waves | 11:25:51 | 11:28:23 | 2m31s | 7 |
| Verify | 11:28:23 | 11:30:09 | 1m46s | 7 |
| Review | | | not run | 0 |
| Finish | 11:30:09 | 11:30:19 | 0m09s | 1 |

Tokens of this run: 0k · 63k · 686k · 4.18M · **4.93M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.06 | 🟢 haiku | 11:25:07 | 11:25:41 | 0m33s | 0k | 20k | 61k | 204k | **286k** |
| ✅ plan check T0.06 | 🟢 haiku | 11:25:41 | 11:25:45 | 0m03s | 0k | 0k | 32k | 62k | **95k** |
| ✅ integrator prepare T0.06 | 🔵 sonnet | 11:25:46 | 11:25:51 | 0m05s | 0k | 0k | 33k | 96k | **129k** |
| ✅ K25 implementer | 🔵 sonnet | 11:25:51 | 11:26:13 | 0m21s | 0k | 4k | 42k | 229k | **276k** |
| ✅ integrator Waves | 🔵 sonnet | 11:26:15 | 11:26:25 | 0m09s | 0k | 0k | 33k | 130k | **164k** |
| ✅ K26 implementer | 🔵 sonnet | 11:26:25 | 11:26:55 | 0m30s | 0k | 5k | 41k | 348k | **395k** |
| ✅ integrator Waves | 🔵 sonnet | 11:26:57 | 11:27:10 | 0m12s | 0k | 0k | 31k | 168k | **200k** |
| ✅ K27 rust-implementer | 🔵 sonnet | 11:27:10 | 11:28:09 | 0m59s | 0k | 8k | 52k | 929k | **990k** |
| ✅ K28 frontend-implementer | 🔵 sonnet | 11:27:10 | 11:27:38 | 0m28s | 0k | 2k | 37k | 437k | **477k** |
| ✅ integrator Waves | 🔵 sonnet | 11:28:10 | 11:28:23 | 0m12s | 0k | 0k | 30k | 134k | **165k** |
| ✅ verifier round 1 | 🟢 haiku | 11:28:23 | 11:28:53 | 0m30s | 0k | 1k | 34k | 94k | **130k** |
| ❌ K15 implementer (fix) | 🔵 sonnet | 11:28:54 | 11:29:05 | 0m11s | 0k | 2k | 35k | 241k | **279k** |
| ❌ FIX-frontends implementer (fix) | 🔵 sonnet | 11:28:54 | 11:29:06 | 0m12s | 0k | 2k | 37k | 208k | **248k** |
| ✅ verifier round 2 | 🟢 haiku | 11:29:06 | 11:29:27 | 0m20s | 0k | 1k | 34k | 129k | **165k** |
| ❌ K15 implementer (fix) | 🔵 sonnet | 11:29:27 | 11:29:39 | 0m11s | 0k | 1k | 34k | 212k | **248k** |
| ❌ FIX-frontends implementer (fix) | 🔵 sonnet | 11:29:27 | 11:29:43 | 0m15s | 0k | 2k | 39k | 283k | **325k** |
| ✅ verifier round 3 | 🟢 haiku | 11:29:43 | 11:30:09 | 0m25s | 0k | 1k | 31k | 99k | **133k** |
| ✅ scribe T0.06 | 🟢 haiku | 11:30:09 | 11:30:19 | 0m09s | 0k | 2k | 42k | 172k | **218k** |

### 4. ticket-run · 2026-11-19 11:36:42 to 11:41:34 · ⏱️ 4m52s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 11:36:42 | 11:37:18 | 0m36s | 3 |
| Waves | | | not run | 0 |
| Verify | 11:37:19 | 11:37:41 | 0m22s | 1 |
| Review | 11:37:41 | 11:40:27 | 2m45s | 1 |
| Finish | 11:40:27 | 11:41:34 | 1m06s | 3 |

Tokens of this run: 0k · 86k · 730k · 4.99M · **5.81M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.06 | 🟢 haiku | 11:36:42 | 11:37:10 | 0m28s | 0k | 18k | 56k | 63k | **139k** |
| ✅ plan check T0.06 | 🟢 haiku | 11:37:10 | 11:37:14 | 0m03s | 0k | 0k | 37k | 61k | **99k** |
| ✅ integrator prepare T0.06 | 🔵 sonnet | 11:37:14 | 11:37:18 | 0m03s | 0k | 0k | 34k | 31k | **66k** |
| ✅ verifier round 1 | 🟢 haiku | 11:37:19 | 11:37:41 | 0m22s | 0k | 0k | 34k | 98k | **133k** |
| ✅ reviewer round 1 | 🟣 opus | 11:37:41 | 11:40:27 | 2m45s | 0k | 32k | 230k | 4.07M | **4.34M** |
| ✅ scribe T0.06 | 🟢 haiku | 11:40:27 | 11:40:52 | 0m25s | 0k | 12k | 100k | 117k | **230k** |
| ✅ explainer T0.06 | 🔵 sonnet | 11:40:27 | 11:41:33 | 1m05s | 0k | 21k | 208k | 540k | **770k** |
| 🔄 integrator finish T0.06 | 🔵 sonnet | 11:41:33 | 11:41:34 | 0m01s | 0k | 0k | 27k | 4k | **31k** |
<!-- /timings -->
