# T0.14: Progress

**Status:** 🟡 Planned

<!-- ticket:specs -->
## 📚 Specifications

The technical pages, features, use cases and business rules of [TICKET.md](TICKET.md), copied by `python3 .claude/scripts/ticket_refs.py sync`.

- [🎨 Design system](../../specs/technical/10-frontends.md#design-system)
- [🗂️ Apps and shared packages](../../specs/technical/10-frontends.md#apps)
- [🖥️ Desktop shell and inputs](../../specs/technical/10-frontends.md#desktop)
- [📏 BR-017: Every screen in four languages](../../specs/functional/business-rules/BR-017-every-screen-in-four-languages.md)
<!-- /ticket:specs -->

## 📝 Events

| Time | Event | By | Result |
| --- | --- | --- | --- |
| 2026-11-20 13:55 | Plan written: 22 tasks, 7 waves | scribe | ⏳ Awaiting approval |
| 2026-11-20 14:10 | Plan approved by the person (group approval) | 👤 person | 🟢 Approved |
| 2026-11-20 14:17 | Wave 1: 8 of 8 tasks done | workers | ✅ |
| 2026-11-20 14:17 | Integrate (Waves) | integrator | ✅ 8 integrated, 0 blocked, not committed |
| 2026-11-20 14:17 | Wave 2: 2 of 3 tasks done | workers | ❌ |
| 2026-11-20 14:17 | Integrate (Waves) | integrator | ✅ 2 integrated, 0 blocked, not committed |
| 2026-11-20 14:17 | Stopped in wave 2: K10 not done | scribe | ❌ |
| 2026-11-20 14:45 | Stopped by the person: the checks of a ticket fail on the other tickets' half-built work in the shared checkout ([L-22](../LESSONS.md#l-22)); the harness verifies in a clean worktree first, then the run continues (15 tasks integrated) | person | ⏸️ paused |
| 2026-11-20 15:00 | Wave 4: 2 blocking file(s) sent to their owners: packages/ts/ui/test/styles.test.ts, packages/ts/ui/test/frames.test.tsx | workers | 🔁 |
| 2026-11-20 15:00 | Integrate (Waves) | integrator | ✅ 2 integrated, 0 blocked, not committed |
| 2026-11-20 15:00 | Wave 4: 0 of 1 tasks done | workers | ❌ |
| 2026-11-20 15:00 | Stopped in wave 4: K16 not done | scribe | ❌ |
| 2026-11-20 15:26 | Wave 4: 1 blocking file(s) sent to their owners: packages/ts/ui/test/frames.test.tsx | workers | 🔁 |
| 2026-11-20 15:26 | Integrate (Waves) | integrator | ✅ 1 integrated, 2 blocked, not committed |
| 2026-11-20 15:26 | Wave 4: 1 of 1 tasks done | workers | ✅ |
| 2026-11-20 15:26 | Integrate (Waves) | integrator | ✅ 1 integrated, 0 blocked, not committed |
| 2026-11-20 15:26 | Wave 5: 5 blocking file(s) sent to their owners: frontends/ground-control/test/app.test.tsx, frontends/mission-studio/test/app.test.tsx, frontends/mission-studio/tsconfig.json, frontends/back-office/test/app.test.tsx, frontends/client-portal/test/app.test.tsx | workers | 🔁 |
| 2026-11-20 15:26 | Integrate (Waves) | integrator | ✅ 2 integrated, 0 blocked, not committed |
| 2026-11-20 15:26 | Wave 5: 4 of 4 tasks done | workers | ✅ |
| 2026-11-20 15:26 | Integrate (Waves) | integrator | ✅ 4 integrated, 0 blocked, not committed |
| 2026-11-20 15:26 | Wave 6: 1 of 1 tasks done | workers | ✅ |
| 2026-11-20 15:26 | Integrate (Waves) | integrator | ✅ 1 integrated, 0 blocked, not committed |
| 2026-11-20 15:26 | Wave 7: 1 of 1 tasks done | workers | ✅ |
| 2026-11-20 15:26 | Integrate (Waves) | integrator | ✅ 1 integrated, 0 blocked, not committed |
| 2026-11-20 15:26 | Verify 1 (3 not applicable) | verifier | ✅ passed |
| 2026-11-20 15:26 | Review 1 (full) | reviewer | ⚠️ 1 blocking, 8 follow-ups |
| 2026-11-20 15:26 | Integrate (Review) | integrator | ✅ 1 integrated, 0 blocked, not committed |
| 2026-11-20 15:26 | Review 2 (confirm fixes) | reviewer | ✅ 0 blocking, 2 follow-ups |
| 2026-11-20 15:26 | Waiting for the person's code review: nothing is committed or pushed until PLAN.md says **Push:** 🟢 Approved (TKT-18) | scribe | 👀 |
| 2026-11-20 15:33 | Code reviewed by the person, push approved (TKT-18) | person | 🟢 Approved |
| 2026-11-20 15:36 | Push approved after the code review | 👤 person | 🟢 |
| 2026-11-20 15:36 | Verify 1 (3 not applicable) | verifier | ✅ passed |

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| AGENT.md:252-399 | T0.10, T0.11, T0.12, T0.13 and T0.15 also claim AGENT.md (and README.md, pnpm-lock.yaml, automerge.yml) as their own files. T0.14's diff of AGENT.md therefore holds their text too: `images.yml`, cosign, swarm-storage, swarm-rest, the simulator and the PostgreSQL fixtures. If T0.14 runs `finish` first, develop gets documentation for code that is not there yet. Either let those tickets finish first, or give the harness ownership of hunks in shared files. The extra `packages/ts/e2e` importer in pnpm-lock.yaml does no harm: the frozen install passes without that package (tests-evidences/pnpm-install.txt). Owner: the harness (ticket_tree.py). |
| tests/conventions/mono_repo/test_frontend_workspace.py | tests/conventions/mono_repo/ now holds 7 Python files and tests/ci/workflows/ holds 7 (it already had 6). Split them into sub-folders, for example mono_repo/frontends/. Owners: K02, K03. |
| tests/harness/write_specs/test_tokens_package.py:21-38 | Move the module-level constants to helpers.py, or make them ClassVars of TestTokensPackage. Move the `root` and `built` fixtures to a conftest.py. Owner: K01. |
| packages/ts/ui/src/frames/GroundControlFrame.tsx:175 | The Mission state is plain text, not the badge the Frames table asks for (assumption K16). Once a Mission state is shown on a screen (T0.19), choose its Badge kind in the visual identity and render a Badge. The same applies to MissionStudioFrame. Owner: K16. |
| frontends/desktop/src-tauri/tauri.conf.json:28 | `style-src 'self'` blocks `<style>` elements added at run time, such as the scroll-lock style that Radix Dialog inserts. Setting styles through React's `style` prop is not affected. When the desktop first shows a Dialog, check the console. If it is blocked, add the narrow `style-src-elem` exception with a nonce, or `'unsafe-inline'` limited to style elements. Owner: K21. |
| frontends/ground-control/src/main.tsx:9 | Two apps find the root with `querySelector('#root')` and two with `getElementById('root')`. Ground control also uses single quotes where the others use double. Pick one form for all four. Owners: K17 to K20. |
| AGENT.md:312-317 | Rewrap the lines that run past 120 characters: the Mono-repo test paragraph, the front-end packages paragraph, and line 345 of .claude/rules/specs.md. Owner: K22, and K15 for specs.md. |
| frontends/ground-control | The four apps have no Dockerfile and no e2e/ folder yet, which the plan left to T0.10 and T0.20. Check that T0.20 covers the light and dark Playwright run of the four shells, which would be the real browser evidence for criterion 2. |
| pnpm-lock.yaml:196 | The lock file changed again in this fix round. Besides the `supports-color` peer re-resolution, it now holds the `packages/ts/api-client` importer and the `openapi-fetch`, `openapi-typescript` and `@redocly/*` entries, which come from T0.12's uncommitted work in the same checkout. T0.10 and T0.12 also list `pnpm-lock.yaml` among their own files. `pnpm install --frozen-lockfile` passes on T0.14's own files (tests-evidences/pnpm-install.txt, 10 projects), so this does not break anything now. Still, T0.14's single commit would carry T0.12's lock entries. Decide at `finish` which ticket commits the lock, or regenerate it on T0.14's own tree before the commit. Owner: K11 (integrator). |
| tests/ci/workflows/test_desktop_workflow.py | Add a test that the Linux step of `.github/workflows/desktop.yml` does not install `libappindicator3-dev`, so the package cannot come back. Today nothing in the tests mentions it. Owner: K11. |

<!-- timings -->
## ⏱️ Timings

Measured from the agents' transcripts by `python3 .claude/scripts/progress.py timings --ticket T0.14` (TKT-10).

| Measure | Value |
| --- | --- |
| 🕒 Ticket started | 2026-11-20 13:43:42 |
| 🕒 Last activity | 2026-11-20 15:37:26 |
| ⏱️ **Overall ticket time** (first start to last activity) | **1h53m43s** |
| 🤖 Time with agents working (sum of runs) | 1h03m38s |
| ⏸️ Time between runs (approvals, fixes) | 50m05s |
| 🔁 Workflow runs | 7 |
| 🪙 **Tokens consumed** (input, output, cache write, cache read) | **77.13M** |

#### 🪙 Tokens by model

| Model | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- |
| 🟢 haiku | 0k | 251k | 3.21M | 8.65M | **12.11M** |
| 🔵 sonnet | 1k | 1.16M | 4.75M | 44.38M | **50.30M** |
| 🟣 opus | 0k | 207k | 827k | 13.68M | **14.72M** |
| **All models** | 2k | 1.62M | 8.79M | 66.72M | **77.13M** |

### 1. ticket-plan · 2026-11-20 13:43:42 to 13:55:33 · ⏱️ 11m51s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Ticket | 13:43:42 | 13:44:35 | 0m52s | 2 |
| Check | 13:44:36 | 13:44:38 | 0m02s | 1 |
| Plan | 13:44:40 | 13:53:54 | 9m14s | 1 |
| Write | 13:53:55 | 13:55:33 | 1m38s | 2 |

Tokens of this run: 0k · 255k · 1.02M · 8.99M · **10.26M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ done check T0.14 | 🟢 haiku | 13:43:42 | 13:43:55 | 0m12s | 0k | 0k | 96k | 102k | **200k** |
| ✅ ticket-writer T0.14 | 🔵 sonnet | 13:43:57 | 13:44:35 | 0m38s | 0k | 16k | 220k | 1.23M | **1.47M** |
| ✅ check TICKET.md T0.14 | 🟢 haiku | 13:44:36 | 13:44:38 | 0m02s | 0k | 0k | 51k | 99k | **151k** |
| ✅ planner T0.14 | 🟣 opus | 13:44:40 | 13:53:54 | 9m14s | 0k | 146k | 348k | 6.75M | **7.25M** |
| ✅ scribe T0.14 | 🟢 haiku | 13:53:55 | 13:55:30 | 1m35s | 0k | 90k | 249k | 701k | **1.04M** |
| ✅ check PLAN.md T0.14 | 🟢 haiku | 13:55:31 | 13:55:33 | 0m02s | 0k | 0k | 51k | 99k | **151k** |

### 2. workflow · 2026-11-20 14:11:18 to 14:11:52 · ⏱️ 0m34s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 14:11:18 | 14:11:52 | 0m34s | 4 |

Tokens of this run: 0k · 12k · 357k · 425k · **795k** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.14 | 🟢 haiku | 14:11:18 | 14:11:33 | 0m15s | 0k | 9k | 107k | 110k | **227k** |
| ✅ plan check T0.14 | 🟢 haiku | 14:11:34 | 14:11:37 | 0m03s | 0k | 0k | 98k | 105k | **204k** |
| ✅ start rule T0.14 | 🟢 haiku | 14:11:37 | 14:11:46 | 0m08s | 0k | 1k | 98k | 105k | **204k** |
| ✅ integrator prepare T0.14 | 🔵 sonnet | 14:11:47 | 14:11:52 | 0m05s | 0k | 0k | 53k | 104k | **158k** |

### 3. workflow · 2026-11-20 14:12:58 to 14:17:29 · ⏱️ 4m31s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 14:12:58 | 14:13:43 | 0m44s | 4 |
| Waves | 14:13:43 | 14:17:29 | 3m45s | 15 |

Tokens of this run: 0k · 189k · 1.27M · 8.46M · **9.92M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.14 | 🟢 haiku | 14:12:58 | 14:13:16 | 0m17s | 0k | 9k | 62k | 210k | **283k** |
| ✅ plan check T0.14 | 🟢 haiku | 14:13:16 | 14:13:20 | 0m04s | 0k | 1k | 97k | 103k | **202k** |
| ✅ start rule T0.14 | 🟢 haiku | 14:13:20 | 14:13:29 | 0m08s | 0k | 0k | 93k | 55k | **149k** |
| ✅ integrator prepare T0.14 | 🔵 sonnet | 14:13:29 | 14:13:43 | 0m13s | 0k | 0k | 48k | 106k | **155k** |
| ✅ K01 test-writer | 🔵 sonnet | 14:13:43 | 14:14:35 | 0m51s | 0k | 14k | 64k | 573k | **652k** |
| ✅ K02 test-writer | 🔵 sonnet | 14:13:44 | 14:14:43 | 0m59s | 0k | 16k | 71k | 589k | **676k** |
| ✅ K03 test-writer | 🔵 sonnet | 14:13:44 | 14:14:59 | 1m15s | 0k | 25k | 83k | 1.07M | **1.18M** |
| ✅ K04 test-writer | 🔵 sonnet | 14:13:44 | 14:14:27 | 0m43s | 0k | 10k | 58k | 506k | **575k** |
| ✅ K05 test-writer | 🔵 sonnet | 14:13:44 | 14:14:33 | 0m48s | 0k | 15k | 57k | 513k | **586k** |
| ✅ K06 test-writer | 🔵 sonnet | 14:13:44 | 14:14:41 | 0m56s | 0k | 17k | 59k | 629k | **706k** |
| ✅ K07 test-writer | 🔵 sonnet | 14:13:44 | 14:14:52 | 1m07s | 0k | 26k | 67k | 519k | **614k** |
| ✅ K08 test-writer | 🔵 sonnet | 14:13:44 | 14:14:28 | 0m43s | 0k | 12k | 65k | 511k | **589k** |
| ✅ integrator Waves | 🔵 sonnet | 14:15:00 | 14:15:14 | 0m13s | 0k | 1k | 59k | 318k | **379k** |
| ✅ K09 implementer | 🔵 sonnet | 14:15:14 | 14:15:54 | 0m40s | 0k | 2k | 54k | 339k | **397k** |
| ❌ K10 frontend-implementer | 🔵 sonnet | 14:15:14 | 14:16:10 | 0m55s | 0k | 17k | 81k | 800k | **898k** |
| ✅ K11 implementer | 🔵 sonnet | 14:15:15 | 14:15:35 | 0m20s | 0k | 2k | 55k | 167k | **225k** |
| ❌ K10 frontend-implementer | 🔵 sonnet | 14:16:11 | 14:17:01 | 0m50s | 0k | 9k | 72k | 682k | **764k** |
| ✅ integrator Waves | 🔵 sonnet | 14:17:02 | 14:17:19 | 0m17s | 0k | 2k | 64k | 489k | **555k** |
| ✅ scribe T0.14 | 🟢 haiku | 14:17:20 | 14:17:29 | 0m09s | 0k | 2k | 57k | 270k | **329k** |

### 4. workflow · 2026-11-20 14:31:48 to 14:41:11 · ⏱️ 9m22s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 14:31:48 | 14:32:39 | 0m50s | 4 |
| Waves | 14:32:40 | 14:41:11 | 8m31s | 13 |

Tokens of this run: 0k · 481k · 1.53M · 14.74M · **16.76M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.14 | 🟢 haiku | 14:31:48 | 14:32:06 | 0m17s | 0k | 10k | 65k | 215k | **291k** |
| ✅ plan check T0.14 | 🟢 haiku | 14:32:07 | 14:32:10 | 0m03s | 0k | 0k | 94k | 56k | **151k** |
| ✅ start rule T0.14 | 🟢 haiku | 14:32:11 | 14:32:25 | 0m14s | 0k | 1k | 94k | 56k | **152k** |
| ✅ integrator prepare T0.14 | 🔵 sonnet | 14:32:26 | 14:32:39 | 0m13s | 0k | 0k | 50k | 108k | **159k** |
| ✅ K10 frontend-implementer | 🔵 sonnet | 14:32:40 | 14:34:20 | 1m40s | 0k | 18k | 83k | 1.31M | **1.41M** |
| ✅ integrator Waves | 🔵 sonnet | 14:34:20 | 14:34:48 | 0m28s | 0k | 2k | 56k | 506k | **564k** |
| ❌ K12 frontend-implementer | 🔵 sonnet | 14:34:49 | 14:35:47 | 0m57s | 0k | 8k | 64k | 1.02M | **1.09M** |
| ❌ K13 frontend-implementer | 🔵 sonnet | 14:34:49 | 14:36:17 | 1m27s | 0k | 46k | 121k | 2.00M | **2.17M** |
| ❌ K14 frontend-implementer | 🔵 sonnet | 14:34:49 | 14:37:14 | 2m24s | 0k | 157k | 235k | 2.76M | **3.15M** |
| ✅ K15 doc-writer | 🟢 haiku | 14:34:50 | 14:35:11 | 0m21s | 0k | 7k | 60k | 509k | **576k** |
| ✅ K10 frontend-implementer (fix) | 🔵 sonnet | 14:37:14 | 14:37:38 | 0m23s | 0k | 1k | 52k | 223k | **277k** |
| ✅ integrator Waves | 🔵 sonnet | 14:37:38 | 14:37:52 | 0m14s | 0k | 1k | 56k | 326k | **384k** |
| ✅ K12 frontend-implementer | 🔵 sonnet | 14:37:53 | 14:38:30 | 0m36s | 0k | 3k | 63k | 618k | **686k** |
| ✅ K13 frontend-implementer | 🔵 sonnet | 14:37:53 | 14:39:01 | 1m07s | 0k | 38k | 77k | 1.42M | **1.53M** |
| ✅ K14 frontend-implementer | 🔵 sonnet | 14:37:53 | 14:39:35 | 1m41s | 0k | 154k | 179k | 2.24M | **2.57M** |
| ✅ integrator Waves | 🔵 sonnet | 14:39:35 | 14:39:49 | 0m14s | 0k | 1k | 57k | 326k | **386k** |
| 🔄 K16 frontend-implementer | 🔵 sonnet | 14:39:50 | 14:41:11 | 1m21s | 0k | 26k | 119k | 1.05M | **1.20M** |

### 5. workflow · 2026-11-20 14:55:41 to 15:00:20 · ⏱️ 4m39s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 14:55:41 | 14:56:29 | 0m48s | 4 |
| Waves | 14:56:30 | 15:00:20 | 3m50s | 6 |

Tokens of this run: 0k · 128k · 670k · 4.25M · **5.05M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.14 | 🟢 haiku | 14:55:41 | 14:56:01 | 0m19s | 0k | 10k | 67k | 218k | **296k** |
| ✅ plan check T0.14 | 🟢 haiku | 14:56:01 | 14:56:05 | 0m04s | 0k | 0k | 49k | 105k | **155k** |
| ✅ start rule T0.14 | 🟢 haiku | 14:56:05 | 14:56:15 | 0m09s | 0k | 1k | 99k | 105k | **206k** |
| ✅ integrator prepare T0.14 | 🔵 sonnet | 14:56:16 | 14:56:29 | 0m13s | 0k | 0k | 51k | 110k | **162k** |
| ❌ K16 frontend-implementer | 🔵 sonnet | 14:56:30 | 14:58:34 | 2m03s | 0k | 105k | 113k | 2.11M | **2.33M** |
| ✅ K04 test-writer (fix) | 🔵 sonnet | 14:58:40 | 14:59:01 | 0m20s | 0k | 1k | 52k | 108k | **162k** |
| ✅ K07 test-writer (fix) | 🔵 sonnet | 14:58:41 | 14:59:02 | 0m21s | 0k | 1k | 53k | 218k | **272k** |
| ✅ integrator Waves | 🔵 sonnet | 14:59:02 | 14:59:22 | 0m19s | 0k | 2k | 63k | 495k | **561k** |
| ❌ K16 frontend-implementer | 🔵 sonnet | 14:59:22 | 15:00:04 | 0m41s | 0k | 3k | 58k | 513k | **576k** |
| ✅ scribe T0.14 | 🟢 haiku | 15:00:11 | 15:00:20 | 0m09s | 0k | 1k | 61k | 267k | **331k** |

### 6. workflow · 2026-11-20 15:00:49 to 15:28:27 · ⏱️ 27m38s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Finish | 15:26:50 | 15:28:27 | 1m36s | 4 |
| Gate | 15:00:49 | 15:01:39 | 0m50s | 4 |
| Review | 15:17:34 | 15:26:50 | 9m16s | 5 |
| Verify | 15:14:11 | 15:17:33 | 3m22s | 1 |
| Waves | 15:01:40 | 15:14:11 | 12m30s | 21 |

Tokens of this run: 0k · 523k · 3.18M · 28.38M · **32.08M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.14 | 🟢 haiku | 15:00:49 | 15:01:08 | 0m18s | 0k | 10k | 115k | 236k | **362k** |
| ✅ plan check T0.14 | 🟢 haiku | 15:01:08 | 15:01:13 | 0m04s | 0k | 1k | 101k | 108k | **210k** |
| ✅ start rule T0.14 | 🟢 haiku | 15:01:13 | 15:01:24 | 0m10s | 0k | 1k | 97k | 111k | **210k** |
| ✅ integrator prepare T0.14 | 🔵 sonnet | 15:01:25 | 15:01:39 | 0m14s | 0k | 0k | 52k | 112k | **165k** |
| ❌ K16 frontend-implementer | 🔵 sonnet | 15:01:40 | 15:03:34 | 1m54s | 0k | 116k | 108k | 2.14M | **2.36M** |
| ✅ K07 test-writer (fix) | 🔵 sonnet | 15:03:41 | 15:04:16 | 0m35s | 0k | 2k | 53k | 453k | **509k** |
| ✅ integrator Waves | 🔵 sonnet | 15:04:16 | 15:04:30 | 0m13s | 0k | 1k | 59k | 332k | **394k** |
| ✅ K16 frontend-implementer | 🔵 sonnet | 15:04:30 | 15:06:36 | 2m06s | 0k | 133k | 117k | 2.46M | **2.71M** |
| ✅ integrator Waves | 🔵 sonnet | 15:06:44 | 15:06:56 | 0m12s | 0k | 0k | 58k | 164k | **223k** |
| ❌ K17 frontend-implementer | 🔵 sonnet | 15:06:56 | 15:07:48 | 0m51s | 0k | 8k | 66k | 1.02M | **1.10M** |
| ❌ K18 frontend-implementer | 🔵 sonnet | 15:06:57 | 15:07:42 | 0m45s | 0k | 6k | 62k | 831k | **900k** |
| ❌ K19 frontend-implementer | 🔵 sonnet | 15:06:57 | 15:07:44 | 0m47s | 0k | 6k | 64k | 891k | **963k** |
| ❌ K20 frontend-implementer | 🔵 sonnet | 15:06:57 | 15:07:52 | 0m54s | 0k | 7k | 60k | 1.02M | **1.09M** |
| ✅ K08 test-writer (fix) | 🔵 sonnet | 15:07:57 | 15:08:14 | 0m17s | 0k | 1k | 54k | 228k | **285k** |
| ✅ K10 frontend-implementer (fix) | 🔵 sonnet | 15:07:57 | 15:08:09 | 0m12s | 0k | 1k | 56k | 165k | **223k** |
| ✅ integrator Waves | 🔵 sonnet | 15:08:34 | 15:08:55 | 0m21s | 0k | 1k | 73k | 281k | **356k** |
| ✅ K17 frontend-implementer | 🔵 sonnet | 15:08:56 | 15:09:48 | 0m51s | 0k | 8k | 65k | 939k | **1.01M** |
| ✅ K18 frontend-implementer | 🔵 sonnet | 15:08:57 | 15:09:50 | 0m53s | 0k | 9k | 68k | 1.13M | **1.20M** |
| ✅ K19 frontend-implementer | 🔵 sonnet | 15:08:57 | 15:09:46 | 0m48s | 0k | 6k | 62k | 772k | **841k** |
| ✅ K20 frontend-implementer | 🔵 sonnet | 15:08:58 | 15:09:46 | 0m48s | 0k | 5k | 62k | 771k | **839k** |
| ✅ integrator Waves | 🔵 sonnet | 15:10:06 | 15:10:39 | 0m33s | 0k | 1k | 66k | 278k | **346k** |
| ✅ K21 rust-implementer | 🔵 sonnet | 15:10:40 | 15:12:56 | 2m16s | 0k | 40k | 103k | 2.24M | **2.38M** |
| ✅ integrator Waves | 🔵 sonnet | 15:13:02 | 15:13:15 | 0m13s | 0k | 1k | 71k | 281k | **353k** |
| ✅ K22 doc-writer | 🟢 haiku | 15:13:16 | 15:14:00 | 0m44s | 0k | 21k | 90k | 1.80M | **1.92M** |
| ✅ integrator Waves | 🔵 sonnet | 15:14:01 | 15:14:11 | 0m09s | 0k | 0k | 71k | 281k | **353k** |
| ✅ verifier round 1 | 🟢 haiku | 15:14:11 | 15:17:33 | 3m22s | 0k | 1k | 105k | 159k | **266k** |
| ✅ reviewer round 1 | 🟣 opus | 15:17:34 | 15:21:49 | 4m14s | 0k | 49k | 392k | 5.95M | **6.39M** |
| ✅ K11 implementer (fix) | 🔵 sonnet | 15:21:49 | 15:21:59 | 0m10s | 0k | 0k | 51k | 111k | **163k** |
| ✅ integrator Review | 🔵 sonnet | 15:22:00 | 15:22:09 | 0m09s | 0k | 0k | 63k | 165k | **229k** |
| ✅ verifier after review 1 | 🟢 haiku | 15:22:09 | 15:25:52 | 3m42s | 0k | 2k | 101k | 332k | **437k** |
| ✅ reviewer round 2 | 🟣 opus | 15:25:53 | 15:26:50 | 0m57s | 0k | 10k | 87k | 983k | **1.08M** |
| ✅ scribe T0.14 | 🟢 haiku | 15:26:50 | 15:27:25 | 0m34s | 0k | 29k | 176k | 871k | **1.08M** |
| ✅ explainer T0.14 | 🔵 sonnet | 15:26:50 | 15:28:18 | 1m27s | 0k | 26k | 177k | 589k | **793k** |
| ✅ docs check T0.14 1 | 🟢 haiku | 15:28:18 | 15:28:22 | 0m03s | 0k | 0k | 57k | 100k | **158k** |
| ✅ scribe T0.14 (timings) | 🟢 haiku | 15:28:22 | 15:28:27 | 0m04s | 0k | 0k | 98k | 61k | **160k** |

### 7. workflow · 2026-11-20 15:32:25 to 15:37:26 · ⏱️ 5m00s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Finish | 15:36:39 | 15:37:26 | 0m46s | 5 |
| Gate | 15:32:25 | 15:33:17 | 0m52s | 4 |
| Verify | 15:33:18 | 15:36:39 | 3m21s | 1 |

Tokens of this run: 0k · 30k · 756k · 1.48M · **2.27M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.14 | 🟢 haiku | 15:32:25 | 15:32:51 | 0m25s | 0k | 13k | 120k | 241k | **376k** |
| ✅ plan check T0.14 | 🟢 haiku | 15:32:51 | 15:32:55 | 0m03s | 0k | 0k | 98k | 57k | **156k** |
| ✅ start rule T0.14 | 🟢 haiku | 15:32:55 | 15:33:05 | 0m09s | 0k | 1k | 102k | 108k | **212k** |
| ✅ integrator prepare T0.14 | 🔵 sonnet | 15:33:06 | 15:33:17 | 0m11s | 0k | 0k | 53k | 56k | **110k** |
| ✅ verifier round 1 | 🟢 haiku | 15:33:18 | 15:36:39 | 3m21s | 0k | 1k | 98k | 167k | **267k** |
| ✅ scribe T0.14 | 🟢 haiku | 15:36:39 | 15:37:09 | 0m29s | 0k | 10k | 122k | 531k | **665k** |
| ✅ docs check T0.14 1 | 🟢 haiku | 15:37:09 | 15:37:12 | 0m03s | 0k | 0k | 54k | 105k | **159k** |
| ✅ explainer T0.14 (fix links) | 🔵 sonnet | 15:37:13 | 15:37:19 | 0m05s | 0k | 0k | 51k | 58k | **109k** |
| ✅ docs check T0.14 2 | 🟢 haiku | 15:37:19 | 15:37:22 | 0m03s | 0k | 0k | 7k | 152k | **159k** |
| 🔄 integrator finish T0.14 | 🔵 sonnet | 15:37:22 | 15:37:26 | 0m03s | 0k | 0k | 47k | 4k | **51k** |
<!-- /timings -->
