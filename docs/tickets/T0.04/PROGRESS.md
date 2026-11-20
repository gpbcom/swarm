# T0.04: Progress

**Status:** 🟡 Planned · **Ticket:** [TICKET.md](TICKET.md)

<!-- ticket:specs -->
## 📚 Specifications

The technical pages, features, use cases and business rules of [TICKET.md](TICKET.md), copied by `python3 .claude/scripts/tickets/ticket_refs.py sync`.

- [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci)
- [🗂️ Architecture: mono-repo](../../specs/technical/01-architecture.md#mono-repo)
<!-- /ticket:specs -->

## 📝 Events

| Time | Event | By | Result |
| --- | --- | --- | --- |
| 2026-11-19 10:19 | Plan written: 15 tasks, 3 waves | scribe | ⏳ Awaiting approval |
| 2026-11-19 10:21 | Plan approved | the person | ✅ Approved |
| 2026-11-19 10:30 | Wave 1: 8 of 8 tasks done | workers | ✅ |
| 2026-11-19 10:30 | Merge (Waves) | integrator | ✅ 8 merged, 0 blocked |
| 2026-11-19 10:30 | Wave 2: 2 of 2 tasks done | workers | ✅ |
| 2026-11-19 10:30 | Merge (Waves) | integrator | ✅ 2 merged, 0 blocked |
| 2026-11-19 10:30 | Wave 3: 5 of 5 tasks done | workers | ✅ |
| 2026-11-19 10:30 | Merge (Waves) | integrator | ✅ 5 merged, 0 blocked |
| 2026-11-19 10:30 | Verify 1 | verifier | ✅ passed |
| 2026-11-19 10:30 | Review 1 (full) | reviewer | ✅ 0 blocking, 8 follow-ups |
| 2026-11-19 10:30 | Merge into develop | integrator | ✅ merged locally, not pushed |

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| .github/workflows/specs.yml | Line 21-29 (K15): the step runs under `bash -eo pipefail`, so when `specs.py check` exits non-zero, the assignment `output="$(...)"` ends the script before the captured stdout is printed. The job still fails, but the log does not show what failed. Use `status=0; output="$(uv run python ... check 2>&1)" || status=$?` so the problems are printed before the step exits. |
| .github/workflows/ci.yml | Line 33-45 (K11): the detect step uses the default `bash -e` without pipefail. If `git diff --name-only` failed after the `cat-file` guard, the detector would read an empty stdin, select nothing, and every check would be skipped. Add `set -o pipefail` (or `shell: bash`) so a failed diff fails the job. Falling back to `--all` would also work. |
| .github/scripts/detect_changes.py | Line 67-81 (K09): `rust_applies` returns False when `packages/rust/Cargo.toml` exists but cannot be read or parsed, so a PR that breaks the manifest skips the Rust checks and goes green. When the manifest exists but is unreadable, return True so that cargo reports the error. This does not matter today because the workspace has no members. |
| .github/workflows/python.yml | Line 56-61 (K12): `-k "$SERVICE-"` matches any test ID that contains the text, so a future service named `way` would also run the slice of `gateway`. Anchor the match on the parametrize ID, for example with a `--service` option in conftest, or with a `-k` expression built from the exact IDs. |
| .github/workflows/ci.yml | Lines 21-24 and the reusable workflows (K11-K15): third-party actions (`astral-sh/setup-uv@v6`, `pnpm/action-setup@v4`, `Swatinem/rust-cache@v2`, `actions/*@v4/v5`) are pinned by major tag. Pin them by commit SHA, with the tag in a comment, before the publication steps of T0.10. |
| .github/workflows/ci.yml | Line 3-5 (K11): `push` with no branch filter plus `pull_request` runs the whole pipeline twice for every commit on a PR branch. Consider limiting `push` to `develop` and `master`. |
| docs/tickets/T0.04/tests-evidences/ruff-check.txt | Verifier: the ruff check and format evidence covers only `tests/ci/`. It does not cover `.github/scripts/detect_changes.py`, which the new `repository` job lints (K12 assumption), and actionlint was not run on the five workflows (K14). Add both outputs to `tests-evidences/` so the first CI run is not the first lint. |
| tests/ci/detect_changes/test_detect_changes.py | Line 12-18 (K01): `NOTHING` is a module-level constant. Move it to `helpers.py`, the place AGENT.md allows for shared test constants, or make it a `ClassVar` of `TestDetectChanges`. |

<!-- timings -->
## ⏱️ Timings

Measured from the agents' transcripts by `python3 .claude/scripts/reports/progress.py timings --ticket T0.04` (TKT-10).

| Measure | Value |
| --- | --- |
| 🕒 Ticket started | 2026-11-19 10:06:16 |
| 🕒 Last activity | 2026-11-19 10:30:55 |
| ⏱️ **Overall ticket time** (first start to last activity) | **24m38s** |
| 🤖 Time with agents working (sum of runs) | 21m51s |
| ⏸️ Time between runs (approvals, fixes) | 2m46s |
| 🔁 Workflow runs | 2 |
| 🪙 **Tokens consumed** (input, output, cache write, cache read) | **13.44M** |

#### 🪙 Tokens by model

| Model | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- |
| 🔵 sonnet | 0k | 110k | 895k | 4.78M | **5.78M** |
| 🟢 haiku | 0k | 120k | 590k | 1.80M | **2.51M** |
| 🟣 opus | 0k | 155k | 508k | 4.48M | **5.15M** |
| **All models** | 0k | 386k | 1.99M | 11.06M | **13.44M** |

### 1. ticket-plan · 2026-11-19 10:06:16 to 10:20:27 · ⏱️ 14m10s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Ticket | 10:06:16 | 10:06:35 | 0m19s | 1 |
| Check | 10:06:36 | 10:06:38 | 0m02s | 1 |
| Plan | 10:06:39 | 10:19:00 | 12m20s | 1 |
| Write | 10:19:00 | 10:20:27 | 1m27s | 2 |

Tokens of this run: 0k · 217k · 772k · 4.72M · **5.71M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ ticket-writer T0.04 | 🔵 sonnet | 10:06:16 | 10:06:35 | 0m19s | 0k | 8k | 142k | 383k | **534k** |
| ✅ check TICKET.md T0.04 | 🟢 haiku | 10:06:36 | 10:06:38 | 0m02s | 0k | 0k | 32k | 62k | **95k** |
| ✅ planner T0.04 | 🟣 opus | 10:06:39 | 10:19:00 | 12m20s | 0k | 128k | 354k | 3.57M | **4.05M** |
| ✅ scribe T0.04 | 🟢 haiku | 10:19:00 | 10:20:24 | 1m23s | 0k | 80k | 208k | 649k | **938k** |
| ✅ check PLAN.md T0.04 | 🟢 haiku | 10:20:24 | 10:20:27 | 0m03s | 0k | 0k | 33k | 63k | **96k** |

### 2. ticket-run · 2026-11-19 10:23:14 to 10:30:55 · ⏱️ 7m40s

| Phase | Start | End | Elapsed | Steps |
| --- | --- | --- | --- | --- |
| Gate | 10:23:14 | 10:23:30 | 0m16s | 3 |
| Waves | 10:23:30 | 10:25:41 | 2m10s | 18 |
| Verify | 10:25:41 | 10:25:54 | 0m12s | 1 |
| Review | 10:25:55 | 10:28:05 | 2m09s | 1 |
| Finish | 10:28:05 | 10:30:55 | 2m49s | 2 |

Tokens of this run: 0k · 168k · 1.22M · 6.33M · **7.72M** (input · output · cache write · cache read · total)

| Step | Model | Start | End | Elapsed | Input | Output | Cache write | Cache read | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✅ gate T0.04 | 🟢 haiku | 10:23:14 | 10:23:22 | 0m07s | 0k | 3k | 105k | 61k | **171k** |
| ✅ plan check T0.04 | 🟢 haiku | 10:23:22 | 10:23:25 | 0m02s | 0k | 0k | 32k | 62k | **96k** |
| ✅ integrator prepare T0.04 | 🔵 sonnet | 10:23:25 | 10:23:30 | 0m04s | 0k | 0k | 33k | 96k | **131k** |
| ✅ K01 test-writer | 🔵 sonnet | 10:23:30 | 10:24:13 | 0m42s | 0k | 13k | 56k | 402k | **473k** |
| ✅ K02 test-writer | 🔵 sonnet | 10:23:31 | 10:23:58 | 0m27s | 0k | 6k | 44k | 345k | **396k** |
| ✅ K03 test-writer | 🔵 sonnet | 10:23:31 | 10:24:11 | 0m40s | 0k | 15k | 55k | 381k | **451k** |
| ✅ K04 test-writer | 🔵 sonnet | 10:23:31 | 10:24:11 | 0m40s | 0k | 17k | 43k | 423k | **484k** |
| ✅ K05 test-writer | 🔵 sonnet | 10:23:31 | 10:23:59 | 0m27s | 0k | 7k | 39k | 298k | **345k** |
| ✅ K06 test-writer | 🔵 sonnet | 10:23:31 | 10:23:49 | 0m18s | 0k | 4k | 39k | 179k | **222k** |
| ✅ K07 test-writer | 🔵 sonnet | 10:23:31 | 10:23:52 | 0m20s | 0k | 8k | 41k | 324k | **374k** |
| ✅ K08 doc-writer | 🟢 haiku | 10:23:31 | 10:23:46 | 0m14s | 0k | 6k | 45k | 246k | **298k** |
| ✅ integrator Waves | 🔵 sonnet | 10:24:13 | 10:24:22 | 0m08s | 0k | 0k | 32k | 104k | **137k** |
| ✅ K09 implementer | 🔵 sonnet | 10:24:23 | 10:25:03 | 0m40s | 0k | 10k | 47k | 364k | **423k** |
| ✅ K10 implementer | 🔵 sonnet | 10:24:23 | 10:24:37 | 0m14s | 0k | 1k | 33k | 143k | **177k** |
| ✅ integrator Waves | 🔵 sonnet | 10:25:03 | 10:25:09 | 0m05s | 0k | 0k | 30k | 67k | **98k** |
| ✅ K11 implementer | 🔵 sonnet | 10:25:09 | 10:25:32 | 0m23s | 0k | 4k | 38k | 229k | **272k** |
| ✅ K12 implementer | 🔵 sonnet | 10:25:09 | 10:25:24 | 0m15s | 0k | 3k | 40k | 184k | **228k** |
| ✅ K13 rust-implementer | 🔵 sonnet | 10:25:09 | 10:25:21 | 0m11s | 0k | 2k | 37k | 215k | **255k** |
| ✅ K14 frontend-implementer | 🔵 sonnet | 10:25:09 | 10:25:21 | 0m11s | 0k | 1k | 35k | 145k | **181k** |
| ✅ K15 implementer | 🔵 sonnet | 10:25:09 | 10:25:25 | 0m15s | 0k | 1k | 33k | 181k | **216k** |
| ✅ integrator Waves | 🔵 sonnet | 10:25:32 | 10:25:41 | 0m08s | 0k | 1k | 31k | 135k | **168k** |
| ✅ verifier round 1 | 🟢 haiku | 10:25:41 | 10:25:54 | 0m12s | 0k | 0k | 33k | 62k | **96k** |
| ✅ reviewer round 1 | 🟣 opus | 10:25:55 | 10:28:05 | 2m09s | 0k | 27k | 153k | 915k | **1.10M** |
| ✅ integrator finish T0.04 | 🔵 sonnet | 10:28:05 | 10:28:15 | 0m10s | 0k | 1k | 38k | 169k | **209k** |
| 🔄 scribe T0.04 | 🟢 haiku | 10:28:15 | 10:30:55 | 2m39s | 0k | 27k | 99k | 586k | **713k** |
<!-- /timings -->
