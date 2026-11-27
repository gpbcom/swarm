# 🧠 Harness lessons

Every problem the ticket harness has caused or let through, while planning or running the tickets of the
[roadmap](../specs/roadmap/README.md). The rules are in [`.claude/rules/tickets.md`](../../.claude/rules/tickets.md);
this page keeps what happened, so that each problem is closed once and never met twice.

## How this page works

- One lesson per problem, with an ID (`L-<nn>`) that never changes and is never reused.
- A new lesson is added at the end of [📋 Lessons](#lessons), with a row in the [summary](#summary), the day it is met.
- Each lesson has the same parts: **Seen**, **What happened**, **Cause**, **Fix**, **Rule**.
- A lesson is closed (🟢) only with the three things the harness asks of every gap: the fix, a test that fails without
  it, and the rule with its enforcers in [`.claude/rules/enforcement.json`](../../.claude/rules/enforcement.json).

| Status | Means |
| --- | --- |
| 🔴 Open | Not fixed. The next run can meet it again |
| 🟡 Worked around | Handled by hand or by a habit of the session, with no test or rule behind it |
| 🟢 Closed | Fixed, tested and ruled |
| ⚪ By design | Expected behaviour, recorded so nobody "fixes" it |

## <a id="summary"></a>📑 Summary

| ID | Date | Problem | Status |
| --- | --- | --- | --- |
| [L-01](#l-01) | 2026-11-18 | A finding went to one owner when its files belonged to several tasks | 🟢 Closed |
| [L-02](#l-02) | 2026-11-20 | A wrong wave-1 test stopped T0.09 four times | 🟢 Closed |
| [L-03](#l-03) | 2026-11-20 | A ticket could be pushed before the person saw its code | 🟢 Closed |
| [L-04](#l-04) | 2026-11-20 | A workflow name loaded an old `ticket-run.js` from a worktree | 🟡 Worked around |
| [L-05](#l-05) | 2026-11-20 | `progress.py timings` wrote a stray file in a worktree | 🟡 Worked around |
| [L-06](#l-06) | 2026-11-20 | `automerge` refused a pull request that changes `.github/workflows/` | ⚪ By design |
| [L-07](#l-07) | 2026-11-20 | A roadmap change broke CI through the counts hard-coded in `test_board.py` | 🟡 Worked around |
| [L-08](#l-08) | 2026-11-20 | `gh pr checks --json` does not exist in the installed `gh` | 🟡 Worked around |
| [L-09](#l-09) | 2026-11-20 | `tickets.py watch` ends at once while a group is being planned | 🔴 Open |
| [L-10](#l-10) | 2026-11-20 | `ticket-plan` still announces a worktree on `feature/<ID>` | 🔴 Open |
| [L-11](#l-11) | 2026-11-20 | `board.py move` marks an epic and its phase Running when a ticket is only planned | 🔴 Open |
| [L-12](#l-12) | 2026-11-20 | Plans written at once guessed the paths of a prerequisite ticket | 🔴 Open |
| [L-13](#l-13) | 2026-11-20 | Plans change files outside their ticket's area, which the area lock does not see | 🔴 Open |
| [L-14](#l-14) | 2026-11-20 | Planning a group changes `.claude/github.json`, and `prepare` then refuses every run | 🔴 Open |
| [L-15](#l-15) | 2026-11-20 | Tracked files changed in the main checkout by an unknown hand | 🟡 Worked around |
| [L-16](#l-16) | 2026-11-20 | `watch` and `next` offer to start tickets whose runs are already launched | 🔴 Open |
| [L-17](#l-17) | 2026-11-20 | `docs/tickets/README.md` is out of date | 🔴 Open |
| [L-18](#l-18) | 2026-11-20 | A plan can leave an acceptance criterion to the person without saying so at approval | 🔴 Open |
| [L-19](#l-19) | 2026-11-20 | Workers' file writes wait on permission prompts, and a declined prompt stops a whole wave | 🔴 Open |
| [L-20](#l-20) | 2026-11-20 | A ticket run dies with the Claude Code session that launched it | 🔴 Open |
| [L-21](#l-21) | 2026-11-20 | `tickets.py watch` counts more tasks done than the plan has | 🔴 Open |
| [L-22](#l-22) | 2026-11-20 | A ticket's checks fail on the half-built work of the other tickets in the shared checkout | 🟢 Closed |
| [L-23](#l-23) | 2026-11-20 | The git guard judges the session's branch, not the folder a command runs in | 🔴 Open |
| [L-24](#l-24) | 2026-11-20 | The 2-minute report is too thin and not ergonomic: no progress bars, no phase, no space, no links to the files | 🔴 Open |
| [L-25](#l-25) | 2026-11-20 | A fix round on a test file traded one error for another, and the retry was spent (seen twice) | 🔴 Open |
| [L-26](#l-26) | 2026-11-20 | A task's "done when" needs a file a later wave writes, so it can never be done in its wave | 🔴 Open |
| [L-27](#l-27) | 2026-11-20 | A worker changed another ticket's files, and its hand-off made them this ticket's own | 🔴 Open |
| [L-28](#l-28) | 2026-11-20 | A wrong import of the project's own code was taken for a missing tool, so no fixer was sent | 🟢 Closed |
| [L-29](#l-29) | 2026-11-20 | A file several tickets change is committed whole by the first one that finishes | 🔴 Open |
| [L-30](#l-30) | 2026-11-20 | `gh pr edit` fails on the deprecated Projects (classic), so `finish` could not update the pull request | 🟢 Closed |
| [L-31](#l-31) | 2026-11-20 | The start rule is read by a model, which reported the ticket's test errors as a refusal (seen twice) | 🟢 Closed |
| [L-32](#l-32) | 2026-11-20 | A failing check was sent to the owner of the first file it was given, not of the file it failed on | 🟢 Closed |
| [L-27](#l-27) | 2026-11-20 | The updates of a ticket run name the files and lines they change without linking to them | 🔴 Open |
| [L-33](#l-33) | 2026-11-20 | `automerge` gave up when another merge moved `develop` at the same moment | 🔴 Open |
| [L-34](#l-34) | 2026-11-23 | A fix round of one ticket changed another running ticket's files, and took them as its own | 🟢 Closed |
| [L-35](#l-35) | 2026-11-23 | The runner `cd`-ed into the JSON that `ticket_tree.py home` prints, and failed the plan check | 🟢 Closed |
| [L-36](#l-36) | 2026-11-23 | `finish` pushed the commit, then failed on `gh pr edit` and left the ticket open | 🟢 Closed |
| [L-37](#l-37) | 2026-11-23 | A task blocked only by files a later wave writes stopped the ticket | 🟢 Closed |
| [L-38](#l-38) | 2026-11-23 | Continuing a ticket hit the area lock of a ticket admitted with it | 🟢 Closed |
| [L-39](#l-39) | 2026-11-23 | The clean check tree has no `swarm_core` wheel, so the flight engine's tests cannot be collected | 🟢 Closed |
| [L-40](#l-40) | 2026-11-26 | The runner read a warning as a refusal: it guessed the exit code | 🟢 Closed |
| [L-41](#l-41) | 2026-11-26 | A review finding in the ticket's own TICKET.md went to code tasks, which could not change it | 🟢 Closed |
| [L-42](#l-42) | 2026-11-26 | Finishing one ticket made the next one's changes table stale, and its finish refused | 🟢 Closed |
| [L-43](#l-43) | 2026-11-26 | The ticket checks run pytest on one worker, CI on two: a test only CI refuses passed every check | 🟢 Closed |
| [L-44](#l-44) | 2026-11-26 | The 5 % bench gate refused a pull request that changes no Rust code | 🔴 Open |
| [L-45](#l-45) | 2026-11-27 | A plan's summary gave a task count its graph did not hold, and no check saw it | 🟢 Closed |
| [L-46](#l-46) | 2026-11-27 | A scribe put links on the status line, so the plan could not be approved | 🟢 Closed |
| [L-47](#l-47) | 2026-11-27 | The plan workflow's last message still sends each ticket to its own worktree | 🟢 Closed |
| [L-48](#l-48) | 2026-11-27 | Plans written on develop stopped every run of the group at its gate | 🟢 Closed |
| [L-49](#l-49) | 2026-11-27 | The group report counted a fixed task twice, and showed 32/23 tasks | 🟢 Closed |
| [L-50](#l-50) | 2026-11-27 | The verifier ran checks.py with the 2-minute default, then waited 10 minutes for a finished run | 🟢 Closed |
| [L-51](#l-51) | 2026-11-27 | Two tickets running at once both needed pnpm-lock.yaml, and neither could pass its checks | 🟢 Closed |
| [L-52](#l-52) | 2026-11-27 | The git guard refused every commit and merge the person asked for while a ticket was open | 🔴 Open |
| [L-53](#l-53) | 2026-11-27 | The ticket checks never ran the PostgreSQL tests or the image e2e, so CI found the failures | 🔴 Open |
| [L-54](#l-54) | 2026-11-27 | The shared branch ran an older harness than develop, and the start rule let a ticket clash on the lock file | 🔴 Open |
| [L-55](#l-55) | 2026-11-27 | The git guard refused the read-only `git merge-base` as a merge | 🔴 Open |
| [L-56](#l-56) | 2026-11-27 | The group report kept a stopped ticket as running | 🔴 Open |
| [L-57](#l-57) | 2026-11-27 | A task needed files no task owned, and the run stopped only after a wasted retry | 🔴 Open |
| [L-58](#l-58) | 2026-11-27 | A fixer of the verify rounds reported the file to fix, and nothing sent it to its owner | 🔴 Open |
| [L-59](#l-59) | 2026-11-27 | A pytest failure was named after the folder `tests` with a warning for detail, so it had no owner | 🔴 Open |
| [L-60](#l-60) | 2026-11-27 | The five-files rule counted only committed files, so a ticket's new files passed its checks and failed CI | 🔴 Open |

## <a id="lessons"></a>📋 Lessons

### <a id="l-01"></a>L-01: A finding went to one owner when its files belonged to several tasks

- **Seen:** T0.08, fix rounds of the verifier and the reviewer.
- **What happened:** the chart names came from `.Chart.Name` under an alias. The finding touched files of several
  tasks, but only one task received it, so the fix round could not fix it.
- **Cause:** fix routing picked a single owner per finding.
- **Fix:** `ownersOf` in [`ticket-run.js`](../../.claude/workflows/ticket-run.js) sends a finding to every task that
  owns one of its files. The chart name was fixed with the literal `vault-config` in `_helpers.tpl`.
- **Rule:** [TKT-6](../../.claude/rules/tickets.md#tkt-6) (a failure goes back to the agent that owns the files).

### <a id="l-02"></a>L-02: A wrong wave-1 test stopped T0.09 four times

- **Seen:** T0.09, implementer retries.
- **What happened:** tests written first had wrong helpers (`start` and `stop`), a wrong `Msg.respond` call, a wrong
  `CredentialKind` import and a wrong `LinkProxy.close` order. Each retry of the implementer failed the same way, and
  the person fixed the tests by hand.
- **Cause:** a blocked worker could only fail; nothing sent the wrong file back to the task that owned it.
- **Fix:** a worker reports `blocked_by`, and the workflow sends each file to its owner of an earlier wave before the
  retry.
- **Rule:** [TKT-19](../../.claude/rules/tickets.md#tkt-19).

### <a id="l-03"></a>L-03: A ticket could be pushed before the person saw its code

- **Seen:** T0.09.
- **What happened:** a finished ticket was committed and pushed in the same run, and its pull request merged by
  GitHub once CI passed. The person never saw the code before it left the machine.
- **Cause:** the plan approval was the only human gate.
- **Fix:** the run stops at `**Push:** 🟡 Awaiting code review` in `PLAN.md`; only `**Push:** 🟢 Approved` lets the
  next run commit and push.
- **Rule:** [TKT-18](../../.claude/rules/tickets.md#tkt-18).

### <a id="l-04"></a>L-04: A workflow name loaded an old `ticket-run.js` from a worktree

- **Seen:** T0.09, during the re-run that was to push.
- **What happened:** the session had changed folder into the ticket's worktree. `Workflow({name: "ticket-run"})`
  loaded that worktree's copy of the script, which predated the push gate of [L-03](#l-03). It was stopped before it
  pushed.
- **Cause:** a saved workflow's name resolves against the session's current folder, not the main checkout.
- **Fix:** ticket workflows are launched with `scriptPath` set to the main checkout's
  [`ticket-run.js`](../../.claude/workflows/ticket-run.js), and the launch summary is compared with the current
  description. TKT-16 also removed the ticket worktrees. Nothing checks it: it is a habit of the session.
- **Rule:** none yet. A test or a hook that refuses a ticket workflow loaded from outside the main checkout would
  close it.

### <a id="l-05"></a>L-05: `progress.py timings` wrote a stray file in a worktree

- **Seen:** T0.09, end of run.
- **What happened:** `progress.py timings --write` resolved the ticket folder against the folder it ran in and wrote a
  `PROGRESS.md` outside the ticket's real folder.
- **Cause:** the script did not know the main checkout from a worktree.
- **Fix:** `main_checkout()`, `ticket_folder()` and `project_dir()` in
  [`progress.py`](../../.claude/scripts/reports/progress.py) always resolve to the main checkout.
- **Rule:** [TKT-10](../../.claude/rules/tickets.md#tkt-10). No test proves the worktree case yet.

### <a id="l-06"></a>L-06: `automerge` refused a pull request that changes `.github/workflows/`

- **Seen:** pull request #347 (T0.09).
- **What happened:** the pull request passed CI but was not merged. It was labelled `needs-person` and merged by
  hand at the person's request.
- **Cause:** a merge made with `GITHUB_TOKEN` may not carry changes to `.github/workflows/`.
- **Fix:** none needed. A pull request that changes CI is merged by a person, or by the `RELEASE_TOKEN` of a release.
- **Rule:** [TKT-15](../../.claude/rules/tickets.md#tkt-15), [TKT-26](../../.claude/rules/tickets.md#tkt-26).

### <a id="l-07"></a>L-07: A roadmap change broke CI through the counts hard-coded in `test_board.py`

- **Seen:** pull request #380 (the AI Assistant in the specifications and the roadmap).
- **What happened:** adding 6 epics and 23 tickets made
  [`tests/harness/board/test_board.py`](../../tests/harness/board/test_board.py) fail in CI, because it expects the
  exact numbers of phases, epics, tickets and blocked-by links.
- **Cause:** the counts are written by hand in the test, and nothing local runs that test when the roadmap changes.
- **Fix:** the counts were updated by hand (commit `3363e68`).
- **Rule:** none. Deriving the counts from `ticket-graph.json`, or running the board tests in `roadmap_gantt.py
  check`, would catch it before CI.

### <a id="l-08"></a>L-08: `gh pr checks --json` does not exist in the installed `gh`

- **Seen:** waiting for the CI of pull request #380.
- **What happened:** a watch loop built on `gh pr checks --json` failed at once.
- **Cause:** the installed `gh` has no `--json` on `pr checks`.
- **Fix:** read the exit code: `8` pending, `0` passed, `1` failed.
- **Rule:** none. Any harness script that reads checks must use the exit code, or `gh api`.

### <a id="l-09"></a>L-09: `tickets.py watch` ends at once while a group is being planned

- **Seen:** `/issue-plan P0`.
- **What happened:** the 2-minute reports of [TKT-9](../../.claude/rules/tickets.md#tkt-9) stopped as soon as they
  started, while 11 plans were being written.
- **Cause:** `report()` in [`tickets.py`](../../.claude/scripts/tickets/tickets.py) ends the watch when no ticket is running
  or in review; a ticket being planned is neither.
- **Fix:** to do. A ticket whose plan is being written must keep the watch alive.
- **Rule:** [TKT-9](../../.claude/rules/tickets.md#tkt-9), [TKT-20](../../.claude/rules/tickets.md#tkt-20).

### <a id="l-10"></a>L-10: `ticket-plan` still announces a worktree on `feature/<ID>`

- **Seen:** `/issue-plan P0`.
- **What happened:** the end message of the `ticket-plan` workflow tells the person the ticket gets its own worktree
  on `feature/<ID>`.
- **Cause:** the message was not updated when [TKT-16](../../.claude/rules/tickets.md#tkt-16) moved every ticket to
  the main checkout on `feature/tickets`.
- **Fix:** to do, with a test that the workflow's messages name `feature/tickets`.
- **Rule:** [TKT-16](../../.claude/rules/tickets.md#tkt-16).

### <a id="l-11"></a>L-11: `board.py move` marks an epic and its phase Running when a ticket is only planned

- **Seen:** `/issue-plan P0`.
- **What happened:** planning the P0 tickets moved their epics and the P0 phase to 🔄 Running on the board.
- **Cause:** the cascade of `board.py move` to the parent issues treats 📝 Planned as work started.
- **Fix:** to do. A parent is Running only when one of its tickets runs.
- **Rule:** [TKT-17](../../.claude/rules/tickets.md#tkt-17).

### <a id="l-12"></a>L-12: Plans written at once guessed the paths of a prerequisite ticket

- **Seen:** `/issue-plan P0`.
- **What happened:** T0.11, T0.16 and T0.18 build on the gateway application that T0.12 creates. Planned at the same
  time as T0.12, they each guessed its files: `api/rest/gateway_app.py`, `api/http/gateway_app.py`,
  `api/rest/application.py` and `models/gateway_config.py`, where T0.12's plan has `api/rest/gateway_rest_app.py`
  and `models/config/gateway_config.py`. The person had the three plans corrected before approving them.
- **Cause:** `/issue-plan` plans every ticket of a group at once, so a planner never sees the plan of a prerequisite
  that does not exist yet. `check_plan.py` does not check that a file a task changes, without creating it, exists or
  is created by a prerequisite's plan.
- **Fix:** to do. Either plan a ticket after its prerequisites' plans, or make `check_plan.py` refuse such a path.
- **Rule:** [TKT-3](../../.claude/rules/tickets.md#tkt-3), [TKT-20](../../.claude/rules/tickets.md#tkt-20).

### <a id="l-13"></a>L-13: Plans change files outside their ticket's area, which the area lock does not see

- **Seen:** `/issue-plan P0`, then `/issue-run P0`.
- **What happened:** T0.15's task K18 changes files under `frontends/`, outside T0.15's areas. T0.14, whose area is
  `packages/ts/tokens`, changed the specification scripts (`spec_check.py`, `spec_model.py`, `specs.py`) and
  `.github/workflows/automerge.yml` and `desktop.yml`, while T0.10 changed `.github/workflows/ci.yml` beside it.
- **Cause:** the area lock of [TKT-16](../../.claude/rules/tickets.md#tkt-16) reads the areas of
  `ticket-graph.json`, not the `files` of the plan. Two tickets can then change the same file in the one checkout.
- **Fix:** to do. `check_plan.py` should refuse a file outside the ticket's areas, or the lock should use the plan's
  files.
- **Rule:** [TKT-16](../../.claude/rules/tickets.md#tkt-16).

### <a id="l-14"></a>L-14: Planning a group changes `.claude/github.json`, and `prepare` then refuses every run

- **Seen:** `/issue-run P0`, at 14:11.
- **What happened:** the four runs started (T0.10, T0.12, T0.13, T0.14) all stopped at once:
  `ticket_tree.py prepare` refused to leave `develop` because tracked files had changes. One of them was
  `.claude/github.json`, which `board.py` had changed when `/issue-plan` moved the cards to 📝 Planned.
- **Cause:** the board's state is kept in a tracked file that the harness itself changes, and `prepare` refuses any
  change to a tracked file on `develop`.
- **Fix:** worked around by hand: the file was put aside, `prepare` was run once, and the file put back on
  `feature/tickets`. To do: keep the board's state out of the tracked files (as `.git/swarm/board.json` already is), or
  let `prepare` carry the harness's own files.
- **Rule:** [TKT-16](../../.claude/rules/tickets.md#tkt-16), [TKT-23](../../.claude/rules/tickets.md#tkt-23) (a
  command must not break the next one).

### <a id="l-15"></a>L-15: Tracked files changed in the main checkout by an unknown hand

- **Seen:** `/issue-run P0`, the same refusal as [L-14](#l-14).
- **What happened:** two files of `packages/python/swarm-models` (`export_schemas.py` and `command.py`) had lost their
  module docstring at 10:53, with no ticket open on them. Nobody could say which agent, hook or command did it.
- **Cause:** unknown. Nothing records who changes a tracked file outside a ticket.
- **Fix:** the docstrings were restored, and the removed lines kept as a patch. To do: find the source, and have
  `prepare` name the tool or session behind a change when it can.
- **Rule:** [TKT-5](../../.claude/rules/tickets.md#tkt-5) (a worker changes only its task's files).

### <a id="l-16"></a>L-16: `watch` and `next` offer to start tickets whose runs are already launched

- **Seen:** `/issue-run P0`.
- **What happened:** the first reports after the launch still printed `▶️ CAN START` for the four tickets just
  started, because their runs had not yet reached `prepare`. Only the session's memory of what it launched kept them
  from being started twice.
- **Cause:** a ticket becomes 🔄 running when its run has prepared it, not when it is launched.
- **Fix:** to do. Record the launch (a lock in `.git/swarm/<ID>/`) before the workflow starts, so that `next` and
  `watch` leave it out.
- **Rule:** [TKT-20](../../.claude/rules/tickets.md#tkt-20), [TKT-23](../../.claude/rules/tickets.md#tkt-23)
  (nothing is done twice).

### <a id="l-17"></a>L-17: `docs/tickets/README.md` is out of date

- **Seen:** 2026-11-20, while writing this page.
- **What happened:** the [ticket index](README.md) still counts 262 tickets (the roadmap has 285), shows every P0
  ticket ⬜ To do although T0.01 to T0.09 are merged, says a run ends with a local merge into `develop`, and does not
  mention the push gate, `/issue-plan`, `/issue-run` or `tickets.py approve`.
- **Cause:** the page is written by hand, and no check compares it with the roadmap or the merged tickets.
- **Fix:** to do. Generate it from `ticket-graph.json` and `done_tickets()`, and check it.
- **Rule:** [TKT-23](../../.claude/rules/tickets.md#tkt-23) (done is defined once).

### <a id="l-18"></a>L-18: A plan can leave an acceptance criterion to the person without saying so at approval

- **Seen:** `/issue-plan P0`, plan of T0.17.
- **What happened:** T0.17's plan cannot show the end-to-end trace its ticket asks for: wiring the services is left to
  the person, and the plan passed `check_plan.py`.
- **Cause:** `check_plan.py` checks the graph, the waves and the file ownership, not that every acceptance criterion
  of `TICKET.md` is met by a task.
- **Fix:** to do. Each acceptance criterion should name the task that meets it, or say who else does.
- **Rule:** [TKT-2](../../.claude/rules/tickets.md#tkt-2), [TKT-3](../../.claude/rules/tickets.md#tkt-3).

### <a id="l-19"></a>L-19: Workers' file writes wait on permission prompts, and a declined prompt stops a whole wave

- **Seen:** `/issue-run P0`, wave 2 of T0.10 and T0.14, at 14:15.
- **What happened:** with four tickets running, the workers' Write and Edit calls in their worktrees
  (`.claude/worktrees/wf_*`) raised permission prompts in the person's session. Some were declined, and the answer
  ("STOP what you are doing and wait") reached the workers, which stopped without handing off. Their bash fallbacks were
  refused too, by the auto-mode classifier or by the worktree guard ("too complex to verify"). T0.10 stopped with K11,
  K13, K14 and K15 not done, T0.14 with K10.
- **Cause:** nothing in the project settings allows the workers to write inside their own worktree, so every write
  depends on the person answering a prompt they cannot tell apart from the main session's.
- **Fix:** to do. Allow `Write` and `Edit` under `.claude/worktrees/` in `.claude/settings.json` (the worktree guard
  already keeps each worker to its task's files), and have the workflow report a permission refusal as an
  `environment` stop, not as a task failure.
- **Rule:** [TKT-5](../../.claude/rules/tickets.md#tkt-5), [TKT-6](../../.claude/rules/tickets.md#tkt-6) (an
  environment failure stops the run at once and goes to the person).

### <a id="l-20"></a>L-20: A ticket run dies with the Claude Code session that launched it

- **Seen:** `/issue-run P0`, after 14:17.
- **What happened:** the Claude Code session restarted. The runs of T0.12 and T0.13, still in their first wave, and the
  2-minute group watch ended with it, with no stop recorded in `PROGRESS.md` and 54 worktrees left behind.
- **Cause:** workflows and monitors are background tasks of the session; nothing outside it notices that they died.
- **Fix:** to do. `tickets.py watch` and `list` should flag a ticket marked running whose run has had no activity for a
  while, and `prune` should remove the worktrees of a run that is gone. Re-running continues where it stopped
  ([TKT-11](../../.claude/rules/tickets.md#tkt-11)), so no integrated work is lost.
- **Rule:** [TKT-9](../../.claude/rules/tickets.md#tkt-9), [TKT-11](../../.claude/rules/tickets.md#tkt-11).

### <a id="l-21"></a>L-21: `tickets.py watch` counts more tasks done than the plan has

- **Seen:** `/issue-run P0`, report of 14:39, T0.10 in its checks.
- **What happened:** the report showed `🧩 19/18 tasks` for T0.10, while `ticket_tree.py status --ticket T0.10` listed
  exactly the 18 task ids of the plan as integrated.
- **Cause:** not found yet. The watch counts something besides the integrated task ids, most likely a fix round
  integrated after the waves.
- **Fix:** to do. The count should be the set of the plan's task ids found in `integrated`, never more than the total.
- **Rule:** [TKT-9](../../.claude/rules/tickets.md#tkt-9) (an exact report).

### <a id="l-22"></a>L-22: A ticket's checks fail on the half-built work of the other tickets in the shared checkout

- **Seen:** `/issue-run P0`, verification of T0.10 at 14:40, with T0.12, T0.13 and T0.14 running beside it.
- **What happened:** T0.10's 18 tasks were integrated, then its checks failed 7 times, and 5 fix rounds could not
  help. None of the failures was in T0.10's files:
  - `services/simulator` (T0.13) and `services/fleet` (T0.12) held only their tests, written first, and no
    `pyproject.toml` yet. The uv workspace glob `services/*` then broke every `uv run`: ruff, ruff format, mypy and
    pytest;
  - `pnpm -r` linted, type-checked and tested `packages/ts/ui`, whose tests (T0.14, wave 1) wait for code not written
    yet.

  The fixers were sent files of other tickets, rightly refused to touch them
  ([TKT-19](../../.claude/rules/tickets.md#tkt-19)), and the run stopped.
- **Cause:** every running ticket shares the main checkout ([TKT-16](../../.claude/rules/tickets.md#tkt-16)). The
  verifier's `checks.py` picks the checks from the ticket's own files, but the tools themselves (`uv`, `pnpm -r`) read
  the whole workspace, other tickets' uncommitted work included. Tests come first
  ([TKT-4](../../.claude/rules/tickets.md#tkt-4)), so another ticket is red by design for most of its run.
- **Fix:** [`checks.py`](../../.claude/scripts/tickets/checks.py) runs every check in a clean temporary worktree of the shared
  branch's commit, into which it copies only the ticket's own changes (and deletes the files the ticket deleted),
  then removes it; Cargo shares the main checkout's build folder. Run on T0.10's real work beside the three other
  tickets, the same 51 files passed all 15 checks that had failed 7 times in the shared checkout. The test
  `test_the_checks_run_on_a_clean_tree_of_the_ticket_s_own_work_only` of
  [`tests/harness/checks/test_checks.py`](../../tests/harness/checks/test_checks.py) fails without it.
- **Rule:** [TKT-6](../../.claude/rules/tickets.md#tkt-6) (the checks run in a clean tree of the ticket's own work),
  [TKT-16](../../.claude/rules/tickets.md#tkt-16) (several tickets at once).

### <a id="l-23"></a>L-23: The git guard judges the session's branch, not the folder a command runs in

- **Seen:** committing the fix of [L-22](#l-22) on `feature/harness-isolated-checks`, in its own worktree
  (`../swarm-harness-isolated-checks`), while the session sat in the main checkout on `feature/tickets`.
- **What happened:** `cd ../swarm-harness-isolated-checks && git commit ...` was refused as a commit on a ticket's
  branch (TKT-5). The person ran the commit, the push and the pull request.
- **Cause:** [`guard_git.py`](../../.claude/hooks/guard_git.py) reads the branch of the hook's working folder (the
  session's), and ignores a `cd <folder> &&` or `git -C <folder>` in the command. The session cannot move to a folder
  outside the project either. So harness work cannot be committed from a session whose main checkout runs tickets, and
  the reverse also holds: a command that `cd`s into `feature/tickets` from elsewhere would pass.
- **Seen again:** the guard's pattern for `git merge` also matches `git merge-base`, a read-only command, and refused a
  script that only compared branches (17:10, preparing the merge of `develop` into `feature/tickets`).
- **Fix:** to do. The guard resolves the folder the git command acts on (`cd`, `-C`) and judges that folder's branch,
  with a test for each case; the write patterns match whole sub-commands (`merge`, not `merge-base`).
- **Rule:** [TKT-5](../../.claude/rules/tickets.md#tkt-5), [TKT-15](../../.claude/rules/tickets.md#tkt-15).

### <a id="l-24"></a>L-24: The 2-minute report is too thin and not ergonomic: no progress bars, no phase, no space

- **Seen:** `/issue-run P0`, every report of `tickets.py watch P0`.
- **What happened:** each report repeats the board state of all 11 tickets, one long line each, with their areas and
  their prerequisites. It does not show what a running ticket is doing (which wave, checks, review, documents) or how far
  it is, and a report where nothing changed looks the same as one where a ticket moved. The person asked for a
  colourised, synthetic update.
- **Cause:** `report()` in [`tickets.py`](../../.claude/scripts/tickets/tickets.py) prints the board (states, areas,
  prerequisites), not the runs. The run's phase is in the events of each ticket's `PROGRESS.md` and in the run's
  journal, which the watch does not read. The count of tasks is also wrong ([L-21](#l-21)).
- **Fix:** to do. **The update MUST be colourised with icons, and MUST tell more about what each ticket is doing
  than a line of state**: a block per running ticket with progress bars, its phase, who works on what, what just
  ended and what comes next, then one line for the waiting tickets. A first one-line-per-ticket version was judged
  too thin by the person.

  **It MUST also be ergonomic: modern, with more space.** The second version (one dense block of lines per ticket)
  was judged hard to read. Each ticket is a card with a rail on its left, blank lines between its parts, labels and
  bars aligned in columns, the phases as a stepper, and the report is relayed in a monospace block so the columns
  hold:

  ```text
  🎫 P0  ·  🕒 15:06  ·  🔄 3 running  ·  🔍 1 to review  ·  🏁 0/11 merged

  ╭─ 🔄 T0.12  Service skeletons with row-level security                ⏱️ 10m  🪙 304k
  │
  │   ✅ Gate ── 🔄 Waves ── ⬜ Verify ── ⬜ Review ── ⬜ Finish
  │
  │   Tasks   ▰▰▰▰▰▰▱▱▱▱   20 / 31
  │   Waves   ▰▰▰▰▱▱▱▱▱▱    3 / 8     now in wave 4
  │
  │   👷  K20   swarm_storage: pool, unit of work, migrator     🔵 sonnet   5m42s
  │   ✅  K22   swarm_rest idempotency                           6 files
  │   ⏭️  wave 5   K23 · K25 · K26 · K27
  ╰─

  ╭─ 🔍 T0.10  Images, scans, signatures and Playwright
  │   Awaits your code review: docs/tickets/T0.10/EXPLAIN.md, then Push: 🟢 Approved in PLAN.md
  ╰─

  ⛓️  Waiting   T0.11 ← T0.12   ·   T0.15 ← T0.12, T0.14   ·   T0.16 ← T0.11, T0.14, T0.15   ·   4 more
  ```

  **It MUST also hold clickable links to the files and lines each task created or changed, for quick access.** A
  report in a monospace block cannot hold links, so the report is written in Markdown instead: a heading per ticket,
  the stepper and the bars in inline code, and a table of its tasks whose last column links every file the task
  changed to its first changed line, relative to the workspace root:

  ```markdown
  #### 🔄 T0.12 · Service skeletons with row-level security · ⏱️ 16 min · 🪙 655k

  `✅ Gate ── 🔄 Waves ── ⬜ Verify ── ⬜ Review ── ⬜ Finish`

  `Tasks ▰▰▰▰▰▰▰▰▱▱ 26/31`  `Waves ▰▰▰▰▰▰▱▱▱▱ 5/8`  now in wave 6

  | | Task | Agent | Files |
  | --- | --- | --- | --- |
  | 👷 | K24 swarm_rest runnables | 🔵 sonnet · 1m10s | |
  | ✅ | K23 swarm_rest REST conventions | 5 files | [problem_handlers.py](packages/python/swarm-rest/src/swarm_rest/api/rest/problem_handlers.py#L1) · [entity_tag.py](packages/python/swarm-rest/src/swarm_rest/api/rest/entity_tag.py#L1) · +3 |

  ⏭️ wave 7: K28 · K29 · K30
  ```

  The file names come from the `files_changed` of each task's result in the run's journal, the line from
  `git diff -U0` (line 1 for a new file). A task that changed more than four files shows four and `+N`.

  - the task bar counts the plan's task ids integrated (never more than the plan has, [L-21](#l-21)), the wave bar
    the waves whose every task is integrated;
  - the phases line is the run's own (✅ done ▸ 🔄 running ▸ ⬜ waiting), with 🔧 fixes, ❌ stopped and why, and
    🔍 awaits your code review where they apply;
  - **now** names each running agent by its task ID and the start of its title, with its model icon (🟣 opus 🔵
    sonnet 🟢 haiku) and how long it has run; **just ended** names what finished since the last report, with its
    result (files changed, checks passed, ❌ failed and why); **next** says what starts when the current step ends;
  - a ticket that changed since the last report is marked 🆕, and a run with no activity for 20 minutes ⚠️ stalled;
  - the board's long lines (areas, prerequisites) go to `tickets.py resolve`, which keeps them.
- **Rule:** [TKT-9](../../.claude/rules/tickets.md#tkt-9) (the reports), to be updated with this format and a test of
  the report's lines.

### <a id="l-25"></a>L-25: A fix round on a test file traded one lint error for another, and the retry was spent

- **Seen:** `/issue-run P0`, wave 4 of T0.14, at 15:00.
- **What happened:** K16 (the frames of `packages/ts/ui`) was done: its tests and the type check passed. Lint failed
  only on `test/frames.test.tsx`, written by K07 in wave 1. The fix round of
  [TKT-19](../../.claude/rules/tickets.md#tkt-19) sent it to K07, which replaced `as HTMLElement` with a `!` after an
  optional chain: `non-nullable-type-assertion-style` was gone, `no-non-null-assertion` and
  `no-non-null-asserted-optional-chain` came in. The retry of K16 met the new errors and the run stopped.
- **Seen again:** wave 4 of T0.13, at 15:28. K29 (the Flight log store) was blocked by
  `services/simulator/tests/storage/edge/test_flight_log_store.py`, which built `FlightLogEntry` objects with
  `uuid4()` ids where version 7 is required. K07's fix built them with `uuid.UUID(int=..., version=7)`, which Python 3.12
  refuses: the file no longer even collected, and the run stopped again.
- **Seen a third time:** wave 5 of T0.13, at 15:40. K33's test file
  `services/simulator/tests/service/factories/flights/test_squad_flight_factory.py` had two bugs, one behind the other:
  a `str` passed where a `Path` was needed, then every stand-in Drone built with `system_id` 1. Each fix round
  revealed the next one, and the single retry stopped the run each time.
- **Cause:** the owner fixing a blocking file is not asked to run the linter and the type check on that file before
  handing it back, so a fix can break another rule of the same file. One retry leaves no room for that.
- **Fix:** to do. A retry is granted while each round fixes something new, up to a bound. The brief of a
  blocking-file fix ends with the checks of that file's layer (lint and type check for
  TypeScript, ruff and mypy for Python), and the fixer hands back only when they pass.
- **Rule:** [TKT-19](../../.claude/rules/tickets.md#tkt-19), [TKT-13](../../.claude/rules/tickets.md#tkt-13) (the
  touched layer is checked before a task is handed back).

### <a id="l-26"></a>L-26: A task's "done when" needs a file a later wave writes, so it can never be done in its wave

- **Seen:** `/issue-run P0`, wave 3 of T0.13, at 15:13.
- **What happened:** K26 (the `MAVLink` state machine of the synthetic Drone) was finished twice: its 17 drone tests
  and 6 route tests passed, and clippy was clean on its own targets. Its `done_when` asks for
  `cargo clippy --workspace --all-targets -- -D warnings`, which compiles
  [`tests/udp.rs`](../../rust/swarm-synthetic-drones/tests/udp.rs). That test reads
  `env!("CARGO_BIN_EXE_swarm-synthetic-drones")`, and the binary comes from K31, three waves later. K26 reported
  `blocked`, the retry met the same wall, and the run stopped.
- **Cause:** `check_plan.py` checks the graph, the waves and the file ownership, not that a task's `done_when` can pass
  with only the files of its wave and the earlier ones. [TKT-19](../../.claude/rules/tickets.md#tkt-19) already says
  that a file a later wave writes is missing, not wrong, but the workflow still counts the task as not done.
- **Fix:** to do. Two parts:
  - the planner scopes each `done_when` to what exists by its wave (here
    `cargo clippy -p swarm-synthetic-drones --lib --test drone --test route`), and the workspace-wide checks belong to
    the verifier;
  - a task whose only blockers are files of later waves counts as done once it has handed off, with the blockers
    logged.
- **Rule:** [TKT-3](../../.claude/rules/tickets.md#tkt-3), [TKT-4](../../.claude/rules/tickets.md#tkt-4),
  [TKT-19](../../.claude/rules/tickets.md#tkt-19).

### <a id="l-27"></a>L-27: The updates of a ticket run name the files and lines they change without linking to them

- **Seen:** `/ticket-run T0.13`, at 15:15.
- **What happened:** the person asked that the updates of a run contain clickable links to the files and lines
  created or modified, for quick access, and that this be written in this page.
- **Cause:** to do. The progress reports and the events of `PROGRESS.md` name the files in plain text, and the
  links of [TKT-14](../../.claude/rules/tickets.md#tkt-14) cover only `EXPLAIN.md` and `IMPLEMENTATION.md`.
- **Fix:** to do. The updates that name a changed file or line link to it, relative to `docs/tickets/<ID>/`, as
  TKT-14 asks of the explainer.
- **Rule:** [TKT-14](../../.claude/rules/tickets.md#tkt-14) (the link form); the rule for the updates is not written yet.

### <a id="l-27"></a>L-27: A worker changed another ticket's files, and its hand-off made them this ticket's own

- **Seen:** `/issue-run P0`, checks of T0.12 at 15:20.
- **What happened:** T0.12's checks failed in the clean tree of [L-22](#l-22): `uv` found
  `services/simulator/` without its `pyproject.toml`. T0.12's own files held 19 files of
  `services/simulator/src/simulator/models/config/exceptions/`, which belong to T0.13. They came with the hand-off of
  T0.12's K21 (the `swarm_rest` models), applied as `021-K21.patch`. K21 had renamed exception files to an `s_e_`
  prefix in every `exceptions/` folder of its worktree, T0.13's included, since `ticket_tree.py start` copies every
  running ticket's work into a worker's worktree. T0.13's own files did not list them, so its commit would have left
  them out. The fixers sent to `swarm-catalog/src` and the tests could do nothing.
- **Cause:** nothing stops a worker from changing a file outside its task's `files`
  ([TKT-19](../../.claude/rules/tickets.md#tkt-19) asks it not to), `handoff` takes every change of the worktree, and
  `integrate` adds every file of the patch to the ticket's own files, even one another ticket owns.
- **Fix:** worked around by hand: the 19 paths were moved from `.git/swarm/T0.12/state.json` to T0.13's, with an event
  in each `PROGRESS.md`. To do: `handoff` keeps only the files of the task's `files` and reports the others, and
  `integrate` refuses a file another open ticket owns.
- **Rule:** [TKT-5](../../.claude/rules/tickets.md#tkt-5) (a worker changes only its task's files),
  [TKT-16](../../.claude/rules/tickets.md#tkt-16) (each ticket touches only its own files).

### <a id="l-28"></a>L-28: A wrong import of the project's own code was taken for a missing tool, so no fixer was sent

- **Seen:** `/issue-run P0`, checks of T0.12 at 15:23, once [L-22](#l-22) and [L-27](#l-27) were out of the way.
- **What happened:** pytest could not collect 7 test files: the `swarm-rest` tests import `tests.api.…`, which does not
  resolve from the repository root, and `tests/postgres/test_postgres_fixture.py` imports `POSTGRES_APP_ROLE` from a
  `conftest` that resolves to the one of `swarm-nats`. Those are mistakes in the ticket's code. The run stopped as an
  environment problem, which goes to no agent ([TKT-6](../../.claude/rules/tickets.md#tkt-6)), so nobody was asked to
  fix them, and every re-run would have stopped the same way.
- **Cause:** `checks.py` flagged any output holding `ModuleNotFoundError` or `No module named` as the environment's
  fault, whatever the module.
- **Fix:** [`checks.py`](../../.claude/scripts/tickets/checks.py) flags a missing module as the environment's only when it is
  not the project's own code (`tests`, `conftest`, a folder of the repository, a package of `services/*/src` or
  `packages/python/*/src`). The parametrised test
  `test_a_missing_module_of_the_project_is_the_code_s_fault_not_the_environment_s` of
  [`tests/harness/checks/test_checks.py`](../../tests/harness/checks/test_checks.py) fails without it.
- **Rule:** [TKT-6](../../.claude/rules/tickets.md#tkt-6) (an environment failure is a missing tool or third-party
  module; a missing module of the project goes to its owner).

### <a id="l-29"></a>L-29: A file several tickets change is committed whole by the first one that finishes

- **Seen:** `/issue-run P0`, the commit of T0.10 (`0612aa6`, pull request #388) at 15:36.
- **What happened:** `AGENT.md` was among the own files of T0.10, T0.12, T0.13 and T0.14, and `README.md` among
  those of T0.10 and T0.14. `ticket_tree.py finish` commits a ticket's own files as they are in the shared checkout,
  so T0.10's commit took both files whole: with T0.14's lines on the desktop shell and T0.12's on the REST contract
  and `packages/ts/api-client`, code that was not committed yet. Merged alone, `develop` would describe code it does
  not have.
- **Cause:** the area lock of [TKT-16](../../.claude/rules/tickets.md#tkt-16) does not cover the shared files
  (`AGENT.md`, `README.md`, the lock files, the root `pyproject.toml`, `.github/workflows/`), several plans own them
  at once ([L-13](#l-13)), and `finish` commits files, not each ticket's own lines.
- **Fix:** to do. Either a shared file belongs to one open ticket at a time (the start rule waits, or `check_plan.py`
  refuses it), or `finish` commits only the ticket's own hunks of a shared file (from the patches it integrated),
  leaving the others' lines uncommitted.
- **Rule:** [TKT-5](../../.claude/rules/tickets.md#tkt-5) (one commit holds only the ticket's own work),
  [TKT-16](../../.claude/rules/tickets.md#tkt-16).

### <a id="l-30"></a>L-30: `gh pr edit` fails on the deprecated Projects (classic), so `finish` could not update the pull request

- **Seen:** `/issue-run P0`, the finish of T0.14 at 15:39, on pull request #388 that T0.10 had opened.
- **What happened:** the commit of T0.14 was made and pushed, but `ticket_tree.py finish` stopped: `gh pr edit` failed
  with the GraphQL error "Projects (classic) is being deprecated" on `repository.pullRequest.projectCards`. The pull
  request kept T0.10's title and had no `Closes` line for T0.14, so merging it would not have closed issue #89.
- **Cause:** the installed `gh` reads the classic project cards of a pull request before editing it, and GitHub now
  refuses that query. Creating a pull request does not hit it, so the first ticket of a branch passes and the second
  fails.
- **Fix:** worked around by hand: the title and body were written with
  `gh api -X PATCH repos/gpbcom/swarm/pulls/388 -f title=... -f body=...`, exactly as `finish` builds them. To do:
  `pull_request()` in [`ticket_tree.py`](../../.claude/scripts/tickets/ticket_tree.py) updates the pull request with the REST
  API and adds the label with `gh api .../issues/<n>/labels`, with a test using a stand-in `gh`.
- **Closed:** 2026-11-26, refactor phase 1. Enforced by [`test_ticket_tree.py`](../../tests/harness/ticket_tree/test_ticket_tree.py): `finish` updates an open pull request through the REST API.
- **Rule:** [TKT-15](../../.claude/rules/tickets.md#tkt-15) (one `Closes` per finished ticket),
  [TKT-24](../../.claude/rules/tickets.md#tkt-24) (GitHub's answers may change; a harness script does not stop on them).

### <a id="l-31"></a>L-31: The start rule is read by a model, which reported the ticket's test errors as a refusal

- **Seen:** `/issue-run P0`, relaunch of T0.13 at 15:41.
- **What happened:** the run stopped at its gate with "The start rule refuses this ticket for now (TKT-16)". The
  problem it listed was a pytest collection error of T0.13's own tests, which the start rule never looks at.
  `python3 .claude/scripts/tickets/tickets.py check --ticket T0.13` printed nothing and exited 0: the rule passed. The run was
  launched again at once.
- **Cause:** the gate of [`ticket-run.js`](../../.claude/workflows/ticket-run.js#L279-L283) asks an agent of type
  `verifier` to "run exactly" `tickets.py check`. The verifier's own instructions are to run `checks.py`: it ran the
  ticket's checks and returned their failures in the start rule's schema. A deterministic decision went through a
  model, and through an agent made for another job.
- **Seen again:** relaunch of T0.13 at 17:20, after `develop` was merged into `feature/tickets`. The agent even wrote that
  `tickets.py check` exited 0 and printed nothing, and still returned the ticket's own pytest failures as a refusal.
  T0.13 was started with `--force`, on the person's decision.
- **Fix:** every step of [`ticket-run.js`](../../.claude/workflows/ticket-run.js) and
  [`ticket-plan.js`](../../.claude/workflows/ticket-plan.js) that runs one deterministic command (the plan check, the
  start rule, the done check, the `TICKET.md` and `PLAN.md` checks, the documents check) goes to a new `runner` agent
  ([`runner.md`](../../.claude/agents/runner.md), haiku, Bash only), which runs exactly that command and reports its exit
  code and output. The workflow's `runExactly` decides from the exit code; the `verifier` only runs `checks.py`. The
  tests `test_a_command_run_exactly_goes_to_the_runner_and_the_exit_code_decides` and
  `test_the_start_rule_is_run_by_the_runner_never_the_verifier` of
  [`test_ticket_workflows.py`](../../tests/harness/wiring/test_ticket_workflows.py) fail without it.
- **Rule:** [TKT-16](../../.claude/rules/tickets.md#tkt-16) (the start rule),
  [TKT-6](../../.claude/rules/tickets.md#tkt-6) (deterministic, not a model's judgement).

### <a id="l-32"></a>L-32: A failing check was sent to the owner of the first file it was given, not of the file it failed on

- **Seen:** `/issue-run P0`, the last check rounds of T0.12, at 15:37.
- **What happened:** ruff found three `PLW1510` errors (`subprocess.run` without `check=`), in
  `services/missions/tests/api/cli/test_missions_console_scripts.py`, its migrate-command test and
  `packages/python/swarm-storage/tests/storage/postgres/migrations/test_alembic_migrator.py`. The failure named
  `packages/python/swarm-rest/src/swarm_rest/__init__.py`, the first file ruff was given, so it went to K18, which owns
  it, found nothing wrong there and changed nothing. The rounds ran out and the run stopped.
- **Cause:** `Checks.check` in [`checks.py`](../../.claude/scripts/tickets/checks.py) recorded the `file` it was called with
  (`files[0]`), whatever the tool's output said.
- **Fix:** `failing_files()` reads the ticket's files the output names (ignoring lines that list many of them, such as
  an echoed command), and the check records one failure per file named, each with its lines, so each goes to its
  owner. The test `test_a_failure_goes_to_the_file_the_tool_names_not_to_the_first_file_it_was_given` of
  [`tests/harness/checks/test_checks.py`](../../tests/harness/checks/test_checks.py) fails without it. Run on T0.12's
  real ruff output, it names the three files.
- **Rule:** [TKT-6](../../.claude/rules/tickets.md#tkt-6) (a failure goes back to the agent that owns the file).

### <a id="l-33"></a>L-33: `automerge` gave up when another merge moved `develop` at the same moment

- **Seen:** pull request #389, at 15:01, while #391 merged.
- **What happened:** every check of #389 passed. `automerge.yml` tried to merge it while #391 was being merged, and
  GitHub answered "Base branch was modified. Review and try the merge again." The run failed and nothing tried again:
  #389 stayed open and green until someone noticed.
- **Cause:** the merge step of [`automerge.yml`](../../.github/workflows/automerge.yml) calls `gh pr merge` once. Two
  pull requests whose checks end together race for `develop`, and the loser is never retried.
- **Fix:** worked around by re-running the failed run (`gh run rerun`). To do: retry the merge a few times with a
  pause when GitHub answers that the base branch was modified, with a test under `tests/ci/release/` using the
  stand-in `gh`.
- **Rule:** [TKT-15](../../.claude/rules/tickets.md#tkt-15) (merged by GitHub once CI passes).

### <a id="l-34"></a>L-34: A fix round of one ticket changed another running ticket's files, and took them as its own

- **Seen:** T0.12, run `wf_86814e91-ecb`, 2026-11-23 at 13:23, with T0.13 running beside it.
- **What happened:** the import-groups rule (#395) failed T0.12's checks on the root `tests/` folder. The fix brief
  said "Files you may change: tests", so the fix agent also regrouped the imports of five test files of T0.13
  (`tests/simulator/test_command_isolation.py`, `tests/deploy/images/test_simulator_image.py`, ...). The integrator
  added them to T0.12's own files. T0.12's clean check tree then held a simulator test without the simulator service
  or its helpers: pytest could not collect it, the failure was flagged `environment`, and the run stopped.
- **Cause:** the fix brief names a folder (`tests`), not files, and `ticket_tree.py integrate` adds every file of a
  hand-off to the ticket's own files without checking that another open ticket already owns it. The collection error
  of a project module was also taken for a missing tool (TKT-6 says it is not).
- **Fix:** worked around by removing the five files from `.git/swarm/T0.12/state.json` (they stay T0.13's) and
  running T0.12 again. To do: `integrate` refuses a file another open ticket owns, the fix brief lists files and
  never another ticket's, and `checks.py` does not flag a collection error of a repository module as `environment`,
  each with its test under `tests/harness/`.
- **Seen again:** the same day, T0.13's failures (import groups in `services/simulator`) were reported against the
  folder `tests` pytest was given, so the fix went to a task allowed to change `tests/` only: it reported `blocked`
  twice and the run stopped. T0.12's review fixes were blocked three rounds running because the tests the reviewer
  asked for were outside each fix task's files, and a blocked fix is never integrated. Worked around: the main
  session regrouped the simulator imports on the person's decision, T0.12 got a new task K33 owning every file of
  the fix, and the import-only changes to T0.10's and T0.14's committed files went into a commit of their own.
  To do as well: a failure names the files it failed on (from the test ids or messages), never only the folder given
  to the tool, and a review finding whose fix needs files of several tasks becomes one fix task owning all of them.
- **Closed:** 2026-11-26, refactor phase 1. Enforced by [`test_ticket_tree.py`](../../tests/harness/ticket_tree/test_ticket_tree.py) (`integrate` refuses another open ticket's file), [`test_checks_environment.py`](../../tests/harness/checks/failures/test_checks_environment.py), [`test_checks_failing_files.py`](../../tests/harness/checks/failures/test_checks_failing_files.py) and [`test_ticket_workflows.py`](../../tests/harness/wiring/test_ticket_workflows.py) (no fix task from a folder, one fix task for several owners).
- **Rule:** [TKT-16](../../.claude/rules/tickets.md#tkt-16) (each ticket touches only its own files) and
  [TKT-6](../../.claude/rules/tickets.md#tkt-6) (a missing project module is not the environment).

### <a id="l-35"></a>L-35: The runner `cd`-ed into the JSON that `ticket_tree.py home` prints

- **Seen:** T0.12, run `wf_bf707eb0-e5b`, 2026-11-23 at 14:31.
- **What happened:** the plan check stopped the run with `cd: {"home": "/home/.../swarm"}: No such file or
  directory`. `check_plan.py T0.12` itself prints nothing and exits 0.
- **Cause:** `runExactly` in [`ticket-run.js`](../../.claude/workflows/ticket-run.js) puts the `WHERE` prefix ("run
  `ticket_tree.py home`, then work from there") in front of the one command the haiku runner must run. The runner
  ran two commands, and `home` prints JSON, not a bare path, so it `cd`-ed into the JSON text.
- **Fix:** running it again failed the same way (`wf_3c322a8f-137`): the `runner` agent, new with #394, does it every
  time. Worked around in this session's copy of the script only: the plan check runs with no prefix, as the start
  rule already does (`wf_e1adbb8b-cbf`). To do: `ticket-run.js` gives the runner `cd <path> && <command>` as its one
  command and never the `WHERE` prefix, with a test in `tests/harness/wiring/`.
- **Closed:** 2026-11-26, refactor phase 1. Enforced by [`test_ticket_workflows.py`](../../tests/harness/wiring/test_ticket_workflows.py): the runner gets one command, with its folder as a `cd`.
- **Rule:** [TKT-6](../../.claude/rules/tickets.md#tkt-6) (checks are run by scripts, not judged by a model).

### <a id="l-36"></a>L-36: `finish` pushed the commit, then failed on `gh pr edit` and left the ticket open

- **Seen:** T0.12, run `wf_87d5bcc7-3a2`, 2026-11-23 at 15:19; most likely T0.14 on 2026-11-20 too, whose
  `.git/swarm/T0.14/` was still there three days after its commit.
- **What happened:** the commit `T0.12: Service skeletons with row-level security` was pushed, then
  `gh pr edit` failed with "GraphQL: Projects (classic) is being deprecated (repository.pullRequest.projectCards)".
  Pull request #388 kept the title "Tickets T0.10, T0.14" and no `Closes` line for T0.12, and `finish` stopped before
  removing the ticket's state, so `tickets.py list` still shows the ticket as open.
- **Cause:** `pull_request()` in [`ticket_tree.py`](../../.claude/scripts/tickets/ticket_tree.py) updates the pull
  request with `gh pr edit`, whose GraphQL query reads the deprecated classic project cards and fails on this
  repository. The ticket's state is removed only after that step.
- **Fix:** worked around by setting the title and the body with `gh api -X PATCH repos/gpbcom/swarm/pulls/388` once
  T0.13 was pushed too. To do: `pull_request()` updates through the REST API (`gh api -X PATCH`, labels through
  `gh api .../issues/<n>/labels`), and `finish` removes the ticket's state once the commit is pushed, whatever the
  pull request step does, with tests under `tests/harness/ticket_tree/` using a stand-in `gh` that fails `pr edit`.
- **Closed:** 2026-11-26, refactor phase 1. Enforced by [`test_ticket_tree.py`](../../tests/harness/ticket_tree/test_ticket_tree.py): the REST API update, and the state removed once pushed even when the pull request step fails.
- **Rule:** [TKT-5](../../.claude/rules/tickets.md#tkt-5) and [TKT-15](../../.claude/rules/tickets.md#tkt-15).

### <a id="l-37"></a>L-37: A task blocked only by files a later wave writes stopped the ticket

- **Seen:** T0.15, run `wf_160ff812-f00`, 2026-11-23 at 18:46.
- **What happened:** K09 (wave 2) finished its work and handed it off, but reported `blocked` twice:
  - first by the schema bundle `swarm_models.schema.json`, which K14 regenerates in wave 3;
  - then also by the `swarm-i18n` package, which K13 scaffolds in wave 3.
  The workflow sends only earlier-wave files to their owners (TKT-19). It retried K09 once, and stopped the ticket
  with "K09 not done after one retry".
- **Cause:** a worker treats any failing check as a blocker, even when the failure comes from a file the plan has a
  later task write. The workflow then counts a task reported `blocked` as not done, whatever blocks it.
- **Fix:** worked around by running `ticket_tree.py integrate --ticket T0.15 --task K09` and running T0.15 again. In
  the session copy of `ticket-run.js`, `laterOnly` now counts a task as done when every file in its `blocked_by` is
  owned by tasks of later waves, and the retry brief says such a failure does not block. To do: the same in
  [`ticket-run.js`](../../.claude/workflows/ticket-run.js) and in the workers' instructions, with a test in
  `tests/harness/wiring/`.
- **Closed:** 2026-11-26, refactor phase 1. Enforced by [`test_ticket_workflows.py`](../../tests/harness/wiring/test_ticket_workflows.py): a task blocked only by later-wave files counts as done.
- **Rule:** [TKT-19](../../.claude/rules/tickets.md#tkt-19) (a file a later wave writes is missing, not wrong).

### <a id="l-38"></a>L-38: Continuing a ticket hit the area lock of a ticket admitted with it

- **Seen:** T0.18, run `wf_1c999bba-f76`, 2026-11-23 at 19:01.
- **What happened:** T0.11 and T0.18 were started together at 18:40, when `tickets.py next P0` let both start. When T0.18
  ran again to continue from wave 4 (TKT-11), `tickets.py check` refused it: T0.11, open and stopped at its checks,
  changes `services/gateway`. The person had to allow `--force` for T0.18, and for T0.11's next run.
- **Cause:**
  - The start rule's area lock only looks at which tickets are open now. It does not see that the ticket being run
    is already open itself, admitted at the same time as the other one.
  - `next` let both start because neither was open yet, while their plans both change `services/gateway`
    ([L-13](#l-13)).
- **Fix:** worked around with `--force`, on the person's decision, logged in each `PROGRESS.md`. To do:
  - `tickets.py check` applies the area lock only to a ticket that is not open yet; an open ticket continuing its run
    passes it;
  - `next` never starts together two tickets whose areas or plan files overlap.
  Each with its test in `tests/harness/tickets/`.
- **Closed:** 2026-11-26, refactor phase 1. Enforced by [`test_tickets_area_lock.py`](../../tests/harness/tickets/test_tickets_area_lock.py): an open ticket passes the area lock, and `next` never starts two overlapping tickets.
- **Rule:** [TKT-16](../../.claude/rules/tickets.md#tkt-16) (start rule and area locks),
  [TKT-11](../../.claude/rules/tickets.md#tkt-11) (re-running continues).

### <a id="l-39"></a>L-39: The clean check tree has no `swarm_core` wheel, so the flight engine's tests cannot be collected

- **Seen:** T0.18, joint checks of T0.11, T0.15 and T0.18, run `wf_30b3014c-c05`, 2026-11-23 at 19:24.
- **What happened:** `checks.py` ran pytest in its clean worktree.
  - `uv run` made a fresh `.venv` there, and four flight-engine test modules failed to import with
    `No module named 'swarm_core'`. The failure was rightly flagged `environment`, so the run stopped without a fix round.
  - The same stop held back a real failure: `cargo clippy` refuses the dead code of `LiveSubscription` in the
    generated [`generated.rs`](../../rust/swarm-models/src/generated.rs).
- **Cause:**
  - `swarm_core` is a PyO3 wheel built by maturin, deliberately outside the uv workspace (AGENT.md, Mono-repo), so
    `uv sync` never builds it.
  - CI installs it (T0.18's K16), and each worker built and installed it in its own worktree, but `checks.py` does
    neither.
  - A ticket's environment failure also stops the fix round for its other, real failures.
- **Fix:** to do:
  - `checks.py` builds the wheel with `maturin build` once per run, and installs it in the clean tree's venv when a
    Python project imports `swarm_core`;
  - the Verify phase still sends the failures that are not `environment` to their owners;
  - each with its test in `tests/harness/checks/`.
- **Seen again:** 2026-11-26, run `wf_3285dd11-abe`.
  - With the wheel now built in the clean tree, maturin failed with E0432: `LatestFrames` not found.
  - The cause: `isolated_tree` copied the ticket's files with `shutil.copy2`, which keeps their old modification
    times. Cargo shares the main checkout's `target` folder and judges freshness by time, so it reused a
    `swarm-core-mavlink` built a little earlier from `develop`'s sources.
  - Fixed in the main checkout's `checks.py` (uncommitted): `shutil.copy`, so every copied file is newer than any
    artifact.
- **Closed:** 2026-11-26, refactor phase 1. Enforced by [`test_checks_swarm_core.py`](../../tests/harness/checks/runs/test_checks_swarm_core.py), and `rust.yml`'s bench job touches the pull request's sources ([`test_rust_workflow.py`](../../tests/ci/workflows/checks/test_rust_workflow.py)).
- **Rule:** [TKT-6](../../.claude/rules/tickets.md#tkt-6) (checks run in a clean tree; an environment failure goes to no
  agent).

### <a id="l-40"></a>L-40: The runner read a warning as a refusal: it guessed the exit code

- **Seen:** T0.18, run `wf_272b02d1-0b0`, 2026-11-26.
- **What happened:** the gate ran `tickets.py check --ticket T0.18 --force`.
  - With `--force`, the script prints the area-lock problem as a warning and exits 0.
  - The `runner` agent reported exit code 1, and the run stopped as if the start rule had refused the ticket.
- **Cause:** the Bash tool shows no exit code when a command succeeds. The haiku runner inferred one from the text,
  which reads like a refusal. [L-31](#l-31) moved the decision to the exit code, but the exit code itself still came
  from a model's reading.
- **Fix:**
  - Worked around in the session copy of `ticket-run.js`: `runExactly` appends `; echo "SWARM_EXIT_CODE=$?"` to the
    command, and the number it prints decides, whatever the runner says.
  - To do: the same in [`ticket-run.js`](../../.claude/workflows/ticket-run.js) and `ticket-plan.js`, with a test in
    `tests/harness/wiring/`.
- **Closed:** 2026-11-26, refactor phase 1. Enforced by [`test_ticket_workflows.py`](../../tests/harness/wiring/test_ticket_workflows.py): the exit code the command prints decides.
- **Rule:** [TKT-6](../../.claude/rules/tickets.md#tkt-6) and [TKT-16](../../.claude/rules/tickets.md#tkt-16) (the
  start rule's verdict is the script's exit code, reported unchanged).

### <a id="l-41"></a>L-41: A review finding in the ticket's own TICKET.md went to code tasks, which could not change it

- **Seen:** T0.15, run `wf_700b1ad6-598`, 2026-11-26 at 16:45.
- **What happened:** the reviewer's only blocking finding was the `➖ No screen` reason in `docs/tickets/T0.15/TICKET.md`,
  which had become false once K18 and K20 changed the shells and the frames. `ownersOf` sent it to K18 and K20, the
  tasks the finding names, and both reported `blocked`: neither owns `TICKET.md`.
- **Cause:** no task of a plan owns the ticket's own `TICKET.md` and `PLAN.md`, which the ticket-writer and the scribe
  write. A finding on them has no owner the fix round can reach.
- **Fix:**
  - Worked around: the main session corrected both lines in the reviewer's words before the confirm round.
  - To do: `fixRound` sends a finding on `docs/tickets/<ID>/TICKET.md` to the `ticket-writer`, and one on `PLAN.md`
    to the `scribe`, never to the code tasks it names, with a test in `tests/harness/wiring/`.
- **Closed:** 2026-11-26, refactor phase 1. Enforced by [`test_ticket_workflows.py`](../../tests/harness/wiring/test_ticket_workflows.py): findings on `TICKET.md` and `PLAN.md` go to the ticket-writer and the scribe.
- **Rule:** [TKT-12](../../.claude/rules/tickets.md#tkt-12) (only blocking findings are fixed, by their owner),
  [TKT-2](../../.claude/rules/tickets.md#tkt-2).

### <a id="l-42"></a>L-42: Finishing one ticket made the next one's changes table stale, and its finish refused

- **Seen:** T0.11, T0.15 and T0.18, pushed together in #396, 2026-11-26.
- **What happened:** after `finish --ticket T0.11` committed the shared files (`uv.lock` among them), `finish --ticket
  T0.15` refused: its `EXPLAIN.md` changes table was out of date. The same happened to T0.18 after T0.15's commit.
- **Cause:** the changes table is the ticket's diff against `HEAD`, so a commit of another ticket that takes a shared
  file changes it. `finish` checks the table but does not rewrite it.
- **Fix:**
  - Worked around: `ticket_tree.py changes --ticket <ID> --write` before each `finish`.
  - To do: `finish` rewrites the table when the only change comes from shared files another ticket committed, with
    a test in `tests/harness/ticket_tree/`.
  - Better still: no two open tickets share a file ([L-13](#l-13), [L-29](#l-29), [L-38](#l-38)).
- **Closed:** 2026-11-26, refactor phase 1. Enforced by [`test_ticket_tree_finish_documents.py`](../../tests/harness/ticket_tree/test_ticket_tree_finish_documents.py): `finish` rewrites a stale changes table.
- **Rule:** [TKT-14](../../.claude/rules/tickets.md#tkt-14) (the changes table is generated, never by hand),
  [TKT-16](../../.claude/rules/tickets.md#tkt-16).

### <a id="l-43"></a>L-43: The ticket checks run pytest on one worker, CI on two: a test only CI refuses passed every check

- **Seen:** #396 (T0.11, T0.15, T0.18), 2026-11-26, job `python / services (gateway)`.
- **What happened:** `test_caller.py` of T0.11 parametrised tests with `uuid4()` values computed at collection time.
  With `pytest -n 2`, as CI runs it, the two xdist workers collected different test ids and pytest refused the run.
  Every check of the ticket had passed, because `checks.py` runs `uv run pytest -q`, on one worker.
- **Cause:** `checks.py` does not run pytest the way CI does.
- **Fix:**
  - Fixed in the test (`0f67ac9`, the person's go-ahead): fixed UUIDs.
  - To do: `checks.py` runs pytest with `-n 2` as AGENT.md and CI do, with a test in `tests/harness/checks/`.
- **Closed:** 2026-11-26, refactor phase 1. Enforced by [`test_checks_python.py`](../../tests/harness/checks/runs/test_checks_python.py): pytest runs with `-n 2`.
- **Rule:** [TKT-6](../../.claude/rules/tickets.md#tkt-6) (the verifier runs the AGENT.md tools, as CI does).

### <a id="l-44"></a>L-44: The 5 % bench gate refused a pull request that changes no Rust code

- **Seen:** #400 (refactor phase 4, front end only), 2026-11-26, job `rust / bench`.
- **What happened:** the gate reported `route_follower_step_1000: +7.24 % regression`. The pull request changes no
  Rust file. A re-run of the job was needed to merge it.
- **Cause:**
  - The base and the pull request are benchmarked one after the other on one shared GitHub runner, whose speed varies
    by several percent.
  - The bench job runs for every pull request that selects Rust, and a change to a lock file or the pipeline selects
    everything.
  - The gate only really compared since #399 fixed the base folder of the refactor.
- **Fix:** to do, with a test in `tests/ci/`. Either:
  - run the bench job only when a Rust file changed;
  - or have the gate re-run a suspect benchmark, and refuse only when the slowdown repeats.
- **Rule:** AGENT.md, CI/CD (`cargo bench` with the 5 % gate on pull requests).

### <a id="l-45"></a>L-45: A plan's summary gave a task count its graph did not hold, and no check saw it

- **Seen:** T0.16 re-planned after the layout refactor, 2026-11-27, `docs/tickets/T0.16/PLAN.md`.
- **What happened:** the summary said "The 27 tasks" while the task graph held 25 (K01 to K27 without K19 and K25).
  The scribe reported it, and `check_plan.py`, `plan.py check` and `ticket_refs.py check` all passed.
- **Cause:** the planner wrote the summary before dropping two tasks, and the scribe writes the summary as given. No
  check compares the prose of a plan with its graph.
- **Fix:**
  - Corrected by hand on the person's decision.
  - [`check_plan.py`](../../.claude/skills/ticket/scripts/check_plan.py) refuses, in the `## Summary` section, a
    count of tasks or waves the graph does not hold (`25 tasks in 12 waves`, `over 7 waves`, `the 27 tasks`); counts
    per wave and numbers in words are left alone. Chosen over `plan.py render` writing the counts, which would leave
    a wrong number in the prose and make every rendered plan stale. Run on the plans already merged, it finds two
    more: T0.12 (31 tasks across 8 waves for 33 in 9) and T0.15 (19 tasks for 20).
- **Closed:** 2026-11-27. Enforced by [`test_summary_counts.py`](../../tests/harness/check_plan/test_summary_counts.py).
- **Rule:** [TKT-3](../../.claude/rules/tickets.md#tkt-3) (a count in the summary is the graph's).

### <a id="l-46"></a>L-46: A scribe put links on the status line, so the plan could not be approved

- **Seen:** T0.17 re-planned after the layout refactor, 2026-11-27, `docs/tickets/T0.17/PLAN.md`.
- **What happened:** the status line read `**Plan:** 🟡 Awaiting approval · **Ticket:** [TICKET.md](TICKET.md) ·
  **Progress:** [PROGRESS.md](PROGRESS.md)`. `check_plan.py` refused it, which is right, but the workflow still
  ended "completed", and `tickets.py approve` would have left the plan out of the group's approval.
- **Cause:** the scribe's prompt does not say that the status line holds the status alone, and the workflow does not
  send a failed plan check back to the scribe.
- **Fix:**
  - The links moved to their own line by hand, on the person's decision.
  - [`scribe.md`](../../.claude/agents/scribe.md) and the brief of
    [`ticket-plan.js`](../../.claude/workflows/ticket-plan.js) (`STATUS_RULE`) give the exact status line, alone on
    its line with no link or other field. A failed `check_plan.py` goes back to the scribe once (`scribe plan fix`),
    then is checked again before the workflow ends; the json block stays the planner's.
- **Closed:** 2026-11-27. Enforced by [`test_ticket_workflows.py`](../../tests/harness/wiring/test_ticket_workflows.py)
  (`test_the_scribe_writes_the_status_line_alone_on_its_line`,
  `test_a_failed_plan_check_goes_back_to_the_scribe_once_before_the_workflow_ends`).
- **Rule:** [TKT-3](../../.claude/rules/tickets.md#tkt-3) (the status line is alone on its line).

### <a id="l-47"></a>L-47: The plan workflow's last message still sends each ticket to its own worktree

- **Seen:** the four plans of T0.16, T0.17, T0.19 and T0.20, 2026-11-27.
- **What happened:** each run ended with "run /ticket-run <ID>: it gives the ticket its own worktree on
  feature/<ID>, so other tickets can run at the same time (TKT-16)".
- **Cause:** the `next` text of `.claude/workflows/ticket-plan.js` predates the rewrite of TKT-16, under which every
  running ticket shares the main checkout on `feature/tickets`.
- **Fix:** the `next` text of [`ticket-plan.js`](../../.claude/workflows/ticket-plan.js) follows TKT-16 and TKT-20:
  approve the status line, or `tickets.py approve <refs>` once for a group, then `/ticket-run <ID>` or
  `/issue-run <refs>`, in the main checkout on `feature/tickets`. A plan that still fails its check says so instead.
- **Closed:** 2026-11-27. Enforced by [`test_ticket_workflows.py`](../../tests/harness/wiring/test_ticket_workflows.py)
  (`test_the_last_message_of_ticket_plan_follows_the_shared_checkout_and_the_group_approval`, which refuses
  `feature/${ID}` and "own worktree").
- **Rule:** [TKT-16](../../.claude/rules/tickets.md#tkt-16) and [TKT-20](../../.claude/rules/tickets.md#tkt-20).

### <a id="l-48"></a>L-48: Plans written on develop stopped every run of the group at its gate

- **Seen:** `/issue-run T0.16 T0.17 T0.19 T0.20`, 2026-11-27, runs `wf_e21a0272-671` (T0.16) and `wf_eede6610-cb7`
  (T0.19).
- **What happened:** `/issue-plan` had written the four plans in the main checkout, uncommitted on `develop`, where it
  stood. Both runs stopped at once: `ticket_tree.py prepare` refuses a `develop` with changes to tracked files.
- **Cause:** `/issue-plan` and `/ticket-plan` write `docs/tickets/<ID>/` wherever the checkout is, and `prepare`
  moves `develop` to `feature/tickets` only when it is clean, although TKT-16 wants exactly those files uncommitted
  on `feature/tickets`.
- **Fix:**
  - The checkout was put on `feature/tickets` by hand (`git checkout -B feature/tickets origin/develop`, with
    `develop` equal to `origin/develop`), as `prepare` does, then the runs were started again.
  - [`ticket_tree.py`](../../.claude/scripts/tickets/ticket_tree.py) `prepare`, on `develop`, carries the uncommitted
    changes under `docs/tickets/` (this page included) and in the board cache `.claude/github.json`
    (`CARRIED_PREFIXES`) to `feature/tickets`, and still refuses any other change to a tracked file, naming it. When
    `origin/develop` changed the same files, the checkout fails and `prepare` says so.
- **Closed:** 2026-11-27. Enforced by
  [`test_ticket_tree_prepare.py`](../../tests/harness/ticket_tree/test_ticket_tree_prepare.py).
- **Rule:** [TKT-16](../../.claude/rules/tickets.md#tkt-16) (`prepare` carries the plans written on `develop`).

### <a id="l-49"></a>L-49: The group report counted a fixed task twice, and showed 32/23 tasks

- **Seen:** `tickets.py watch T0.16 T0.17 T0.19 T0.20`, 2026-11-27, from 10:27.
- **What happened:** T0.19 showed `🧩 26/23`, then `32/23` tasks, and T0.16 `29/25`, once fixes and retries
  (TKT-6, TKT-19) were integrated.
- **Cause:** the count is the number of integration records, and a task integrated again after its fix adds a record.
- **Fix:** [`tickets.py`](../../.claude/scripts/tickets/tickets.py) `watch` reads the task ids from the plan's json
  block (`plan_task_ids`) and counts those found among the integrated records, so a task integrated again, or a
  `FIX-` task, adds nothing. `resolve` and `list` show no task count.
- **Closed:** 2026-11-27. Enforced by [`test_groups.py`](../../tests/harness/tickets/test_groups.py)
  (`test_watch_counts_a_task_integrated_again_after_its_fix_once`).
- **Rule:** [TKT-11](../../.claude/rules/tickets.md#tkt-11) (a task integrated twice is one task).

### <a id="l-50"></a>L-50: The verifier ran checks.py with the 2-minute default, then waited 10 minutes for a finished run

- **Seen:** T0.19, run `wf_fd50a6ce-232`, verification round 2, 2026-11-27, 10:38 to 10:49.
- **What happened:** `checks.py` passed the Bash tool's 120-second default and went to the background. The checks
  ended at 10:40, but the verifier waited for them until its own timeout, and reported at 10:49.
- **Cause:** the verifier's instructions do not give the Bash call a timeout, and a ticket's checks (the clean tree,
  `uv sync`, the wheel, pnpm and every suite) take several minutes.
- **Fix:** [`verifier.md`](../../.claude/agents/verifier.md) and the brief of
  [`ticket-run.js`](../../.claude/workflows/ticket-run.js) (`VERIFY`, used by both verifier calls) run `checks.py` in
  the foreground with the Bash tool's timeout set to `600000` ms, never with `run_in_background`. The verdict file was
  left out: in the foreground the verifier reads the verdict from the command's last line, as before.
- **Closed:** 2026-11-27. Enforced by [`test_ticket_workflows.py`](../../tests/harness/wiring/test_ticket_workflows.py)
  (`test_the_verifier_runs_checks_py_in_the_foreground_with_the_ten_minute_timeout`).
- **Rule:** [TKT-6](../../.claude/rules/tickets.md#tkt-6) (the verifier runs `checks.py` with the 10-minute timeout).

### <a id="l-51"></a>L-51: Two tickets running at once both needed pnpm-lock.yaml, and neither could pass its checks

- **Seen:** T0.16 (run `wf_70b03198-2ef`) and T0.19 (run `wf_fd50a6ce-232`), 2026-11-27, verification.
- **What happened:** the main checkout's `pnpm-lock.yaml` held the new dependencies of both tickets. T0.19 owned the
  file, so its clean tree had T0.16's back-office entries without T0.16's `package.json`: "3 dependencies removed".
  T0.16 could not own the file, so its clean tree had its `package.json` without the lock entries: "3 dependencies
  added". Each fix task changed no file, and both tickets stopped after their fix rounds.
- **Also:** the four message catalogues of `@swarm/i18n` (`frontend/packages/i18n/src/messages/*.json`). T0.19 owned
  them for one map label, so `ticket_tree.py integrate` kept T0.16's 132 lines of Back office messages out of the
  checkout (they stay in `.git/swarm/T0.16/applied/012-K12.patch`), and T0.16's tests ran with missing translations.
- **And then:** at 11:07 a `pnpm --filter @swarm/back-office test` run in the main checkout rewrote `pnpm-lock.yaml`:
  pnpm 12 checks the dependencies before a script and installs them, so it put T0.16's back-office entries back
  into T0.19's lock, and T0.19's push run failed its frozen-lockfile check again at 12:06.
- **Cause:** the start rule's area lock (TKT-16) covers apps, front ends and packages, not the shared files that
  several tickets append to: the lock files (`pnpm-lock.yaml`, `uv.lock`, `rust/Cargo.lock`) and the message
  catalogues. A file owned by one open ticket is refused to every other, with no report to the person. And a pnpm
  script run where several tickets' manifests sit uncommitted rewrites the shared lock file by itself.
- **Fix:**
  - [`check_plan.py`](../../.claude/skills/ticket/scripts/check_plan.py) (`LOCK_FILES`): a task that changes a
    `package.json` (root, `frontend/`, `qa/`) owns `pnpm-lock.yaml`, a `pyproject.toml` of the uv workspace `uv.lock`,
    a `Cargo.toml` of `rust/` `rust/Cargo.lock`, the desktop shell's its own `Cargo.lock`; a plan that breaks it is
    refused, naming the task and the lock file. The open plans of T0.16, T0.17, T0.19 and T0.20 already pass.
  - [`tickets.py`](../../.claude/scripts/tickets/tickets.py) (`SHARED_FILES`, one constant): the lock files, the four
    FormatJS catalogues and the `.pot` and `.po` files of `swarm_storage` are a **shared file lock**. `check` refuses a
    ticket while another open ticket's plan, or its recorded files, lists one of the shared files its own plan lists,
    naming the file and the ticket; `next` never starts two such tickets together. Chosen over regenerating the lock
    in the clean tree: that would hide the other ticket's entries in the checkout and still leave the catalogues,
    which no tool regenerates, to one ticket.
  - [`ticket_tree.py`](../../.claude/scripts/tickets/ticket_tree.py) `integrate` already listed a refused file under
    `refused` (L-34), and the workflow logged it. It now also prints it on stderr with its owner and the applied patch
    that keeps the change, and records it in the ticket's state, which `tickets.py watch` shows.
  - [`.claude/settings.json`](../../.claude/settings.json) sets `pnpm_config_verify_deps_before_run=warn` for every
    session and agent: a pnpm script warns about missing dependencies and never installs, so it never rewrites the
    lock. `frontend-implementer` and `test-writer` run `pnpm install --frozen-lockfile` in a fresh worktree, and only
    the task that owns the lock runs `pnpm install` without it. A run from the person's own terminal is not covered:
    `pnpm-workspace.yaml` could set `verifyDepsBeforeRun: warn` for every checkout, CI included, which is the person's
    choice.
- **Closed:** 2026-11-27. Enforced by [`test_manifest_locks.py`](../../tests/harness/check_plan/test_manifest_locks.py),
  [`test_tickets_area_lock.py`](../../tests/harness/tickets/test_tickets_area_lock.py) (the shared file lock in `check`
  and `next`), [`test_ticket_tree.py`](../../tests/harness/ticket_tree/test_ticket_tree.py)
  (`test_integrate_refuses_a_file_another_open_ticket_owns`) and
  [`test_harness_settings.py`](../../tests/harness/wiring/test_harness_settings.py) (a pnpm 12 script run with the
  settings' environment leaves the lock file alone).
- **Rule:** [TKT-16](../../.claude/rules/tickets.md#tkt-16) (the shared file lock, no pnpm script installs) and
  [TKT-3](../../.claude/rules/tickets.md#tkt-3) (a task that changes a manifest owns its lock file).

### <a id="l-52"></a>L-52: The git guard refused every commit and merge the person asked for while a ticket was open

- **Seen:** the image fix of #409 and the merge of #410, 2026-11-27.
- **What happened:** the person asked Claude to commit a fix and to merge #410. `.claude/hooks/guard_git.py` refused
  `git commit` and `gh pr merge` on `feature/tickets`, even run from `/tmp`, so the person typed each command by hand.
- **Cause:** the guard knows only one writer on the shared branch, `ticket_tree.py finish`; it has no way to tell a
  fix the person asked for from an agent stepping outside TKT-5.
- **Also:** 2026-11-27 17:00, `gh pr merge 409` was refused at the person's word with no ticket open at all: the guard
  reads the branch `feature/tickets`, not the open tickets, so the last merge of a group always needs the person.
- **Fix:** to do, with a test in `tests/harness/gitflow/`: the guard answers `ask` (the person confirms in the
  dialog) instead of refusing, for the main session only, never for a worker.
- **Rule:** [TKT-5](../../.claude/rules/tickets.md#tkt-5) and [TKT-15](../../.claude/rules/tickets.md#tkt-15).

### <a id="l-53"></a>L-53: The ticket checks never ran the PostgreSQL tests or the image e2e, so CI found the failures

- **Seen:** T0.16 and T0.19 in #409, 2026-11-27.
- **What happened:** the verifier passed both tickets, then CI failed on `test_schema_service.py` (the gateway's
  revision was hard-coded as `0001` while T0.16 added `0002`) and on Ground control's Playwright run against its
  image (the map did not render in the built image).
- **Cause:** `checks.py` runs pytest only on the changed tests, where the PostgreSQL tests skip without the binaries,
  and never builds the images nor runs `infra/compose/e2e.yaml`.
- **Fix:** to do, with a test in `tests/harness/checks/`: a ticket that changes migrations runs every test of their
  app, the PostgreSQL ones reported `environment` when the binaries are missing; a ticket that changes a front end
  builds its image and runs its e2e.
- **Also:** T0.20 in #409, 2026-11-27. The UC-029 screens, captured with this machine's Chromium, differed by 3 to 5 % in CI (`images / e2e`). Fixed at the person's word: every visual test and every capture renders in the browser server of the pinned image `mcr.microsoft.com/playwright:v<version>-noble` ([`browser-server.ts`](../../qa/e2e/src/browser-server.ts)), and the eight screens were recaptured in it. The ticket checks still never run the visual tests.
- **Rule:** [TKT-6](../../.claude/rules/tickets.md#tkt-6) (done means every applicable check passed).

### <a id="l-54"></a>L-54: The shared branch ran an older harness than develop, and the start rule let a ticket clash on the lock file

- **Seen:** the group T0.16 T0.17 T0.19 T0.20, 2026-11-27, after #410 merged.
- **What happened:** #410 added the shared-file lock of [L-51](#l-51) on `develop`, but `feature/tickets` was
  branched before it, so the main checkout's `tickets.py` had no such lock. `tickets.py watch` printed
  `▶️ CAN START T0.17` and `tickets.py check --ticket T0.17` exited 0, though T0.17's plan and the open T0.20 both own
  `pnpm-lock.yaml`. T0.17 was held back by hand.
- **Cause:** the harness runs from the checked-out branch, and the shared branch is never rebased while tickets are
  open (TKT-5), so a harness fix reaches it only when every open ticket is merged.
- **Fix:** to do, with a test in `tests/harness/tickets/`: the start rule and the workflows read the harness of
  `origin/develop` when it is newer, or `ticket_tree.py prepare` refuses to start a ticket while `.claude/` on the
  shared branch is behind `origin/develop`, and says so.
- **Rule:** [TKT-16](../../.claude/rules/tickets.md#tkt-16) and [TKT-24](../../.claude/rules/tickets.md#tkt-24).

### <a id="l-55"></a>L-55: The git guard refused the read-only `git merge-base` as a merge

- **Seen:** 2026-11-27, checking whether #410 was on `feature/tickets`.
- **What happened:** `git merge-base --is-ancestor` was refused as "`git merge` is not run by hand".
- **Cause:** the pattern `WRITES` of [`guard_git.py`](../../.claude/hooks/guard_git.py) ends with `\b`, which matches
  between `merge` and `-base`.
- **Fix:** to do, with a test in `tests/harness/gitflow/`: end the verb with `(?![-\w])`, and test that
  `git merge-base`, `git commit-tree` and `git stash list` (read-only) are not taken for writes.
- **Rule:** [TKT-5](../../.claude/rules/tickets.md#tkt-5).

### <a id="l-56"></a>L-56: The group report kept a stopped ticket as running

- **Seen:** T0.20 (run `wf_5d5c1231-418`), 2026-11-27.
- **What happened:** the run ended, stopped after three verification rounds, and `tickets.py watch` kept showing
  `🔄 T0.20 · running` with `16/13 tasks`, with nothing telling the person it waited for them.
- **Cause:** the state comes from the ticket being open in `.git/swarm/`, not from its last run; a stopped run
  leaves no mark the report reads. The task count repeats [L-49](#l-49).
- **Fix:** to do, with a test in `tests/harness/tickets/`: the run writes its end (stopped, why, next step) in
  `.git/swarm/<ID>/state.json`, and the report shows `✋ stopped` with that reason.
- **Rule:** [TKT-9](../../.claude/rules/tickets.md#tkt-9) and [TKT-17](../../.claude/rules/tickets.md#tkt-17).

### <a id="l-57"></a>L-57: A task needed files no task owned, and the run stopped only after a wasted retry

- **Seen:** T0.17 (run `wf_7d6c388f-e31`), 2026-11-27, wave 4.
- **What happened:** K31 had to wire `traceSquadFrame` into the live Web Worker, but its `files` held only
  `frontend/packages/live/src/tracing/frame_tracing.ts`, `index.ts` and `package.json`. It reported
  `live-worker-core.ts` and the live `tsconfig.json` as blockers. The workflow logged "not sent, because no earlier
  task owns them", retried K31 unchanged, and K31 was blocked again on the same files, so the run stopped.
- **Cause:** the planner gave the task a brief wider than its files, and `check_plan.py` cannot see that. The
  workflow treats a blocker no task owns like a missing file of a later wave, and retries.
- **Fix:** to do, with a test in `tests/harness/`: a blocker in a file that no task of the plan owns stops the
  run at once, without a retry, and names the plan change to approve (the file, the task that needs it). A wider
  check of the planner's output could compare each brief's named paths with its `files`.
- **Rule:** [TKT-3](../../.claude/rules/tickets.md#tkt-3), [TKT-11](../../.claude/rules/tickets.md#tkt-11) and
  [TKT-19](../../.claude/rules/tickets.md#tkt-19).

### <a id="l-58"></a>L-58: A fixer of the verify rounds reported the file to fix, and nothing sent it to its owner

- **Seen:** T0.17 (run `wf_44762818-4a1`), 2026-11-27, verification rounds 1 and 2.
- **What happened:** `test_cell_chart.py` failed because the new `infra/charts/cell/Chart.lock` has a digest that
  does not match `Chart.yaml`, and `helm dependency update` refuses dependencies without a `version`. The failure was
  sent to K13, the owner of the test. K13 reported `blocked` both times, naming `Chart.lock` and what to change, but
  the file belongs to K37 and no fixer ever received it, so every round failed the same way.
- **Cause:** `fixRound` in [`ticket-run.js`](../../.claude/workflows/ticket-run.js) integrates the fixers' hand-offs
  but never reads their `blocked_by`. Only the waves send a blocked file back to its owner (TKT-19).
- **Fix:** to do, with a test in `tests/harness/`: after a fix round, every `blocked_by` of a fixer goes to the
  owner of that file, in the same round, before the next verification.
- **Rule:** [TKT-6](../../.claude/rules/tickets.md#tkt-6) and [TKT-19](../../.claude/rules/tickets.md#tkt-19).

### <a id="l-59"></a>L-59: A pytest failure was named after the folder `tests` with a warning for detail, so it had no owner

- **Seen:** T0.17 (run `wf_cb1354f7-4ab`), 2026-11-27, verification.
- **What happened:** one test failed out of 5,398, `tests/scripts/test_swarm_apps.py::TestSwarmApps::test_the_gateway_configuration_is_its_default`.
  `checks.py` reported the failure with the file `tests` (the folder pytest was given) and, for detail, the first
  lines of the output: a `PytestDeprecationWarning` of pytest-asyncio, truncated. No task owns `tests`, so the
  workflow sent it to nobody and stopped after one round. The real failure was only in
  `docs/tickets/T0.17/tests-evidences/pytest.txt`.
- **Cause:** the failure parser of `checks.py` falls back to the target it ran when it finds no `FAILED <file>::`
  line in the part of the output it keeps, and it keeps the head of the output instead of its summary.
- **Fix:** to do, with a test in `tests/harness/checks/`: read the `FAILED` and `ERROR` lines of pytest's short
  summary wherever they are, name each failing test's file, and drop warning lines from the detail.
- **Rule:** [TKT-6](../../.claude/rules/tickets.md#tkt-6) (each failure names the file the tool reports it in).

### <a id="l-60"></a>L-60: The five-files rule counted only committed files, so a ticket's new files passed its checks and failed CI

- **Seen:** T0.17 in #409 (`6d05264`), 2026-11-27, `python / repository`.
- **What happened:** T0.17 added five chart tests to `tests/infra/charts/observability/`, which already held T0.19's
  `test_telemetry_latency_dashboard.py`: six code files. Its checks passed, and CI failed
  `test_no_folder_of_the_repository_holds_more_than_five_code_files`.
- **Cause:** the rule lists the files git tracks. In the clean tree of `checks.py` a ticket's own files are copied in,
  not committed, so the rule never sees them. Every check built on `git ls-files` is blind to the ticket under test.
- **Fix:** to do, with a test in `tests/conventions/repository/`: the rule counts tracked and untracked files that
  are not ignored (`git ls-files --cached --others --exclude-standard`), or `checks.py` stages the own files in its
  clean tree before the checks run. The folder was fixed by moving the dashboard test into `dashboards/`.
- **Rule:** [TKT-6](../../.claude/rules/tickets.md#tkt-6) and AGENT.md, File shape.

## <a id="already-ruled"></a>📜 Lessons already turned into rules

Problems met before this page existed, each closed by a rule whose **Why** tells the story:

| Rule | Problem it closed |
| --- | --- |
| [TKT-12](../../.claude/rules/tickets.md#tkt-12) | Every review round was a fresh full review, so a ticket never converged |
| [TKT-22](../../.claude/rules/tickets.md#tkt-22) | SPEC-12's screenshots were enforced by nothing in the ticket harness |
| [TKT-23](../../.claude/rules/tickets.md#tkt-23) | Commands assumed they ran once, on fresh input, and redid finished work |
| [TKT-24](../../.claude/rules/tickets.md#tkt-24) | Pull request #345 failed three times in CI: no local `develop`, shallow history, no GitHub |
| [TKT-25](../../.claude/rules/tickets.md#tkt-25) | 135 local branches and 22 worktrees, none with work of its own |
| [TKT-26](../../.claude/rules/tickets.md#tkt-26) | `master` stayed on the first commit while 359 commits reached `develop` |
