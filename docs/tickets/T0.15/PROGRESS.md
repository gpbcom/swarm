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
| 2026-11-23 18:45 | Wave 1: 8 of 8 tasks done | workers | ✅ |
| 2026-11-23 18:45 | Integrate (Waves) | integrator | ✅ 8 integrated, 0 blocked, not committed |
| 2026-11-23 18:45 | Wave 2: 1 blocking file(s) sent to their owners: packages/python/swarm-models/tests/models/people/test_person.py | workers | 🔁 |
| 2026-11-23 18:45 | Integrate (Waves) | integrator | ✅ 1 integrated, 0 blocked, not committed |
| 2026-11-23 18:45 | Wave 2: 2 of 3 tasks done | workers | ❌ |
| 2026-11-23 18:45 | Integrate (Waves) | integrator | ✅ 2 integrated, 1 blocked, not committed |
| 2026-11-23 18:45 | Stopped in wave 2: K09 not done | run | ❌ |
| 2026-11-23 18:54 | Wave 3: 2 blocking file(s) sent to their owners: packages/ts/i18n/vitest.config.ts, packages/python/swarm-i18n/tests/service/catalogs/conftest.py | workers | 🔁 |
| 2026-11-23 18:54 | Integrate (Waves) | integrator | ✅ 2 integrated, 0 blocked, not committed |
| 2026-11-23 18:54 | Wave 3: 3 of 3 tasks done | workers | ✅ |
| 2026-11-23 18:54 | Integrate (Waves) | integrator | ✅ 3 integrated, 0 blocked, not committed |
| 2026-11-23 18:54 | Wave 4: 2 of 3 tasks done | workers | ❌ |
| 2026-11-23 18:54 | Integrate (Waves) | integrator | ✅ 2 integrated, 0 blocked, not committed |
| 2026-11-23 18:54 | Stopped in wave 4: K18 not done | run | ❌ |
| 2026-11-23 18:48 | K09 integrated by hand: blocked only by the schema bundle and the swarm-i18n package, which K14 and K13 write in wave 3 (L-37) | main session | ✅ |
| 2026-11-23 18:56 | K18 integrated by hand: done as briefed; the frame texts in packages/ts/ui, which no task owned, reported as blocked | main session | ✅ |
| 2026-11-23 18:58 | Plan changed: task K20 added (wave 5, after K18): the frames take their side bar items, Hold and Abort from the messages in the four languages. Approved by the person | 👤 person | 🟢 Approved |
| 2026-11-23 19:03 | Waves done (20 of 20). Run stopped before its own checks: T0.11, T0.15 and T0.18 share files and are checked together, on the person's decision | main session | ⏸️ |
| 2026-11-26 16:47 | Review finding fixed by hand: the '➖ No screen' reason of TICKET.md (line 33) and PLAN.md (Assumptions) no longer says the ticket changes no frontends/ folder, in the reviewer's words. K18 and K20, to whom it was sent, own neither file | main session | ✅ |
| 2026-11-26 16:51 | Verify 1 (1 not applicable) | verifier | ✅ passed |
| 2026-11-26 16:51 | Review 1 (full) | reviewer | ⚠️ 1 blocking, 7 follow-ups |
| 2026-11-26 16:51 | Review 2 (confirm fixes) | reviewer | ✅ 0 blocking, 1 follow-ups |
| 2026-11-26 16:51 | Waiting for the person's code review: nothing is committed or pushed until PLAN.md says **Push:** 🟢 Approved (TKT-18) | main session | 👀 |
| 2026-11-26 17:13 | Code reviewed and push approved by the person ("The T0.15 and T0.18 ticket is done. Go ahead with those."); pushed together with T0.11, which shares their files | 👤 person | 🟢 Approved |

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| frontends/ground-control/src/App.tsx | The frame table gives the language in the status bar of the Client portal only ("Client · language"); Ground control ("📡 Links · Jurisdiction · Pilot · time"), Mission studio and Back office have none. Show `status.language` in the Client portal only, or update the visual identity's frame table if the product owner wants it everywhere. Same in frontends/mission-studio/src/App.tsx and frontends/back-office/src/App.tsx. Owner: K18. |
| packages/python/swarm-i18n/src/swarm_i18n/api/cli/check_catalogs.py | In main(), the `except SECatalogError` (lines 30-32) and the `if missing:` branch (lines 33-36) do not log, and line 28 picks the catalogue root with a conditional expression. Log the error at ERROR (type(error).__name__), the missing count at WARNING or DEBUG, and turn the root choice into an if/else with a DEBUG line in each branch. Owner: K17. |
| packages/python/swarm-i18n/src/swarm_i18n/storage/catalogs/po_catalog_store.py | `READ_MODE` (line 46) is declared and documented but never used: files are read with read_text. Remove it. Owner: K15. |
| packages/python/swarm-i18n/src/swarm_i18n/service/catalogs/catalog_checker.py | The Python check only walks the msgids of swarm.pot, so an entry added to en/LC_MESSAGES/swarm.po without the template passes, whereas findMissing() in packages/ts/i18n reports such an id as `unknown`. Consider an UNKNOWN problem for ids present in a catalogue but absent from the template. Owner: K16. |
| frontends/client-portal/src/main.tsx | The shells pass `language={undefined}` (English) and Person.language is not persisted anywhere yet (no people table, no `locale` in the Keycloak realm). Wire the signed-in person's language into I18nProvider and persist it once the front-end sign-in and the people storage exist (T0.16 or the ticket that adds sign-in to the shells). Record it as a follow-up ticket. |
| packages/ts/i18n/src/messages/fr.json | The French, German and Spanish texts (for example "Escadrille" for Squad, "Mettre l'escadrille en attente" for Hold the Squad) and the Babel seed translations were proposed by the agents; no specification gives them. Have the product owner review them (PLAN.md points to T1.35). Owner: K18, K20, K15. |
| AGENT.md | Line 202, "(swarm-models now holds `Language` and `Person.language`)": drop "now", which goes stale; state where `Language` lives instead. Owner: K19. |
| docs/tickets/T0.15/TICKET.md | Line 47 of the Assumptions section still gives the old reason for having no screen ("because the roadmap row names no use case"). Align it with the new Screens touched reason: the shells are the empty frames of T0.14 and show no use case state. Owner: ticket-writer. |

<!-- timings -->
## ⏱️ Timings

Measured from the agents' transcripts by `python3 .claude/scripts/reports/progress.py timings --ticket T0.15` (TKT-10).

| Measure | Value |
| --- | --- |
| 🕒 Ticket started | 2026-11-20 13:43:42 |
| 🕒 Last activity | 2026-11-26 16:52:56 |
| ⏱️ **Overall ticket time** (first start to last activity) | **147h09m13s** |
| 🤖 Time with agents working (sum of runs) | 49m18s |
| ⏸️ Time between runs (approvals, fixes) | 146h19m55s |
| 🔁 Workflow runs | 5 |
| 🪙 **Tokens consumed** (input, output, cache write, cache read) | **61.52M** |

#### 🪙 Tokens by model

| Model | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- |
| 🟢 haiku | 0k | 141k | 2.01M | 5.95M | **8.10M** |
| 🔵 sonnet | 1k | 494k | 3.71M | 34.40M | **38.61M** |
| 🟣 opus | 0k | 191k | 769k | 13.85M | **14.81M** |
| **All models** | 1k | 827k | 6.49M | 54.20M | **61.52M** |

### 1. ticket-plan · 2026-11-20 13:43:42 to 13:55:49 · ⏱️ 12m07s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Ticket | 13:43:42 | 13:44:32 | 0m49s | 2 |
| Check | 13:44:33 | 13:44:36 | 0m03s | 1 |
| Plan | 13:44:37 | 13:54:23 | 9m46s | 1 |
| Write | 13:54:24 | 13:55:49 | 1m25s | 2 |

Tokens of this run: 0k · 221k · 986k · 10.98M · **12.18M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ done check T0.15 | 🟢 haiku | 13:43:42 | 13:43:55 | 0m12s | 0k | 0k | 96k | 102k | **200k** |
| ✅ ticket-writer T0.15 | 🔵 sonnet | 13:43:57 | 13:44:32 | 0m34s | 0k | 17k | 177k | 998k | **1.19M** |
| ✅ check TICKET.md T0.15 | 🟢 haiku | 13:44:33 | 13:44:36 | 0m03s | 0k | 0k | 51k | 99k | **151k** |
| ✅ planner T0.15 | 🟣 opus | 13:44:37 | 13:54:23 | 9m46s | 0k | 152k | 389k | 8.90M | **9.44M** |
| ✅ scribe T0.15 | 🟢 haiku | 13:54:24 | 13:55:46 | 1m22s | 0k | 50k | 219k | 778k | **1.05M** |
| ✅ check PLAN.md T0.15 | 🟢 haiku | 13:55:47 | 13:55:49 | 0m02s | 0k | 0k | 51k | 99k | **151k** |

### 2. workflow · 2026-11-23 18:40:57 to 18:45:50 · ⏱️ 4m53s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 18:40:57 | 18:41:42 | 0m45s | 4 |
| Waves | 18:41:43 | 18:45:50 | 4m07s | 17 |

Tokens of this run: 0k · 268k · 1.66M · 14.80M · **16.72M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.15 | 🟢 haiku | 18:40:57 | 18:41:17 | 0m20s | 0k | 11k | 119k | 367k | **499k** |
| ✅ plan check T0.15 | 🟢 haiku | 18:41:17 | 18:41:20 | 0m03s | 0k | 0k | 57k | 108k | **166k** |
| ✅ start rule T0.15 | 🟢 haiku | 18:41:21 | 18:41:30 | 0m08s | 0k | 0k | 57k | 108k | **166k** |
| ✅ integrator prepare T0.15 | 🔵 sonnet | 18:41:30 | 18:41:42 | 0m11s | 0k | 0k | 54k | 118k | **173k** |
| ✅ K01 test-writer | 🔵 sonnet | 18:41:43 | 18:42:19 | 0m36s | 0k | 10k | 72k | 702k | **784k** |
| ✅ K02 test-writer | 🔵 sonnet | 18:41:43 | 18:42:50 | 1m07s | 0k | 20k | 87k | 1.63M | **1.73M** |
| ✅ K03 test-writer | 🔵 sonnet | 18:41:43 | 18:42:30 | 0m47s | 0k | 16k | 84k | 1.08M | **1.18M** |
| ✅ K04 test-writer | 🔵 sonnet | 18:41:43 | 18:42:50 | 1m07s | 0k | 34k | 106k | 867k | **1.01M** |
| ✅ K05 test-writer | 🔵 sonnet | 18:41:43 | 18:42:39 | 0m55s | 0k | 16k | 96k | 1.37M | **1.48M** |
| ✅ K06 test-writer | 🔵 sonnet | 18:41:44 | 18:42:33 | 0m49s | 0k | 54k | 71k | 1.22M | **1.35M** |
| ✅ K07 test-writer | 🔵 sonnet | 18:41:44 | 18:42:15 | 0m30s | 0k | 9k | 73k | 716k | **799k** |
| ✅ K08 test-writer | 🔵 sonnet | 18:41:44 | 18:42:07 | 0m22s | 0k | 3k | 71k | 500k | **575k** |
| ✅ integrator Waves | 🔵 sonnet | 18:42:51 | 18:43:01 | 0m10s | 0k | 1k | 66k | 419k | **487k** |
| ❌ K09 implementer | 🔵 sonnet | 18:43:02 | 18:43:40 | 0m38s | 0k | 7k | 72k | 581k | **662k** |
| ✅ K10 frontend-implementer | 🔵 sonnet | 18:43:02 | 18:44:24 | 1m21s | 0k | 62k | 96k | 2.17M | **2.33M** |
| ✅ K12 implementer | 🔵 sonnet | 18:43:02 | 18:43:19 | 0m16s | 0k | 2k | 62k | 552k | **617k** |
| ✅ K01 test-writer (fix) | 🔵 sonnet | 18:44:28 | 18:44:38 | 0m10s | 0k | 2k | 61k | 237k | **301k** |
| ✅ integrator Waves | 🔵 sonnet | 18:44:38 | 18:44:49 | 0m11s | 0k | 2k | 72k | 546k | **620k** |
| ❌ K09 implementer | 🔵 sonnet | 18:44:50 | 18:45:27 | 0m37s | 0k | 6k | 75k | 719k | **801k** |
| ✅ integrator Waves | 🔵 sonnet | 18:45:27 | 18:45:40 | 0m12s | 0k | 3k | 114k | 423k | **540k** |
| ✅ scribe T0.15 | 🟢 haiku | 18:45:40 | 18:45:50 | 0m10s | 0k | 3k | 81k | 356k | **442k** |

### 3. workflow · 2026-11-23 18:46:50 to 18:54:44 · ⏱️ 7m53s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 18:46:50 | 18:47:34 | 0m43s | 4 |
| Waves | 18:47:34 | 18:54:44 | 7m09s | 15 |

Tokens of this run: 0k · 176k · 1.41M · 14.30M · **15.89M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.15 | 🟢 haiku | 18:46:50 | 18:47:08 | 0m18s | 0k | 10k | 75k | 241k | **327k** |
| ✅ plan check T0.15 | 🟢 haiku | 18:47:09 | 18:47:12 | 0m03s | 0k | 0k | 60k | 106k | **166k** |
| ✅ start rule T0.15 | 🟢 haiku | 18:47:13 | 18:47:22 | 0m08s | 0k | 0k | 54k | 55k | **109k** |
| ✅ integrator prepare T0.15 | 🔵 sonnet | 18:47:22 | 18:47:34 | 0m11s | 0k | 0k | 55k | 119k | **175k** |
| ❌ K11 frontend-implementer | 🔵 sonnet | 18:47:34 | 18:48:15 | 0m40s | 0k | 11k | 77k | 1.15M | **1.24M** |
| ❌ K13 implementer | 🔵 sonnet | 18:47:34 | 18:49:15 | 1m40s | 0k | 25k | 99k | 1.47M | **1.60M** |
| ✅ K14 implementer | 🔵 sonnet | 18:47:35 | 18:48:37 | 1m02s | 0k | 6k | 65k | 996k | **1.07M** |
| ✅ K10 frontend-implementer (fix) | 🔵 sonnet | 18:49:15 | 18:49:33 | 0m18s | 0k | 2k | 58k | 483k | **544k** |
| ✅ K04 test-writer (fix) | 🔵 sonnet | 18:49:15 | 18:49:38 | 0m23s | 0k | 6k | 68k | 483k | **558k** |
| ✅ integrator Waves | 🔵 sonnet | 18:49:39 | 18:49:51 | 0m12s | 0k | 1k | 71k | 428k | **501k** |
| ✅ K11 frontend-implementer | 🔵 sonnet | 18:49:52 | 18:50:21 | 0m29s | 0k | 7k | 66k | 754k | **828k** |
| ✅ K13 implementer | 🔵 sonnet | 18:49:52 | 18:51:15 | 1m23s | 0k | 22k | 108k | 1.42M | **1.55M** |
| ✅ integrator Waves | 🔵 sonnet | 18:51:16 | 18:51:26 | 0m10s | 0k | 1k | 64k | 365k | **431k** |
| ✅ K15 implementer | 🔵 sonnet | 18:51:26 | 18:53:04 | 1m37s | 0k | 41k | 106k | 2.42M | **2.57M** |
| ❌ K18 frontend-implementer | 🔵 sonnet | 18:51:27 | 18:52:57 | 1m30s | 0k | 14k | 94k | 1.37M | **1.47M** |
| ✅ K19 doc-writer | 🟢 haiku | 18:51:27 | 18:51:52 | 0m24s | 0k | 12k | 71k | 933k | **1.02M** |
| ❌ K18 frontend-implementer | 🔵 sonnet | 18:53:14 | 18:54:06 | 0m52s | 0k | 7k | 73k | 910k | **991k** |
| ✅ integrator Waves | 🔵 sonnet | 18:54:24 | 18:54:35 | 0m11s | 0k | 1k | 66k | 362k | **429k** |
| ✅ scribe T0.15 | 🟢 haiku | 18:54:35 | 18:54:44 | 0m08s | 0k | 3k | 71k | 234k | **309k** |

### 4. workflow · 2026-11-23 18:56:27 to 19:02:09 · ⏱️ 5m42s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 18:56:27 | 18:57:13 | 0m46s | 4 |
| Verify | 19:00:44 | 19:02:09 | 1m24s | 1 |
| Waves | 18:57:13 | 19:00:44 | 3m30s | 8 |

Tokens of this run: 0k · 53k · 890k · 4.69M · **5.63M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.15 | 🟢 haiku | 18:56:27 | 18:56:46 | 0m19s | 0k | 11k | 79k | 245k | **336k** |
| ✅ plan check T0.15 | 🟢 haiku | 18:56:47 | 18:56:50 | 0m03s | 0k | 0k | 60k | 106k | **166k** |
| ✅ start rule T0.15 | 🟢 haiku | 18:56:50 | 18:56:59 | 0m08s | 0k | 0k | 57k | 108k | **166k** |
| ✅ integrator prepare T0.15 | 🔵 sonnet | 18:56:59 | 18:57:13 | 0m13s | 0k | 0k | 57k | 121k | **178k** |
| ✅ K20 frontend-implementer | 🔵 sonnet | 18:57:13 | 18:58:53 | 1m40s | 0k | 18k | 99k | 1.63M | **1.75M** |
| ✅ K16 implementer | 🔵 sonnet | 18:57:13 | 18:58:00 | 0m46s | 0k | 8k | 75k | 609k | **694k** |
| ✅ integrator Waves | 🔵 sonnet | 18:59:18 | 18:59:29 | 0m10s | 0k | 1k | 73k | 298k | **373k** |
| ❌ K17 implementer | 🔵 sonnet | 18:59:30 | 18:59:49 | 0m19s | 0k | 3k | 68k | 370k | **442k** |
| ✅ K16 implementer (fix) | 🔵 sonnet | 18:59:51 | 19:00:04 | 0m13s | 0k | 2k | 62k | 237k | **301k** |
| ✅ integrator Waves | 🔵 sonnet | 19:00:06 | 19:00:15 | 0m09s | 0k | 0k | 68k | 242k | **311k** |
| ✅ K17 implementer | 🔵 sonnet | 19:00:15 | 19:00:34 | 0m18s | 0k | 3k | 69k | 364k | **437k** |
| ✅ integrator Waves | 🔵 sonnet | 19:00:35 | 19:00:44 | 0m08s | 0k | 0k | 64k | 294k | **360k** |
| 🔄 verifier round 1 | 🟢 haiku | 19:00:44 | 19:02:09 | 1m24s | 0k | 0k | 54k | 57k | **112k** |

### 5. workflow · 2026-11-26 16:34:14 to 16:52:56 · ⏱️ 18m42s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Finish | 16:51:10 | 16:52:56 | 1m46s | 4 |
| Gate | 16:34:14 | 16:35:12 | 0m57s | 4 |
| Review | 16:41:14 | 16:51:09 | 9m55s | 5 |
| Verify | 16:35:12 | 16:41:13 | 6m01s | 1 |

Tokens of this run: 0k · 107k · 1.55M · 9.43M · **11.09M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.15 | 🟢 haiku | 16:34:14 | 16:34:47 | 0m33s | 0k | 16k | 88k | 900k | **1.01M** |
| ✅ plan check T0.15 | 🟢 haiku | 16:34:47 | 16:34:51 | 0m03s | 0k | 0k | 58k | 110k | **169k** |
| ✅ start rule T0.15 | 🟢 haiku | 16:34:51 | 16:35:00 | 0m08s | 0k | 0k | 54k | 56k | **111k** |
| ✅ integrator prepare T0.15 | 🔵 sonnet | 16:35:00 | 16:35:12 | 0m11s | 0k | 0k | 56k | 121k | **177k** |
| ✅ verifier round 1 | 🟢 haiku | 16:35:12 | 16:41:13 | 6m01s | 0k | 0k | 166k | 66k | **232k** |
| ✅ reviewer round 1 | 🟣 opus | 16:41:14 | 16:44:17 | 3m02s | 0k | 35k | 279k | 4.46M | **4.77M** |
| ❌ K18 frontend-implementer (fix) | 🔵 sonnet | 16:44:17 | 16:44:57 | 0m39s | 0k | 2k | 69k | 512k | **584k** |
| ❌ K20 frontend-implementer (fix) | 🔵 sonnet | 16:44:17 | 16:44:25 | 0m07s | 0k | 2k | 117k | 120k | **239k** |
| ✅ verifier after review 1 | 🟢 haiku | 16:44:57 | 16:50:42 | 5m45s | 0k | 0k | 114k | 58k | **173k** |
| ✅ reviewer round 2 | 🟣 opus | 16:50:43 | 16:51:09 | 0m26s | 0k | 3k | 100k | 494k | **598k** |
| ✅ scribe T0.15 | 🟢 haiku | 16:51:10 | 16:51:34 | 0m24s | 0k | 14k | 95k | 470k | **580k** |
| ✅ explainer T0.15 | 🔵 sonnet | 16:51:10 | 16:52:49 | 1m38s | 0k | 29k | 232k | 1.89M | **2.16M** |
| ✅ docs check T0.15 1 | 🟢 haiku | 16:52:49 | 16:52:52 | 0m02s | 0k | 0k | 55k | 56k | **111k** |
| ✅ scribe T0.15 (timings) | 🟢 haiku | 16:52:52 | 16:52:56 | 0m03s | 0k | 0k | 59k | 117k | **176k** |
<!-- /timings -->
