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
| [L-30](#l-30) | 2026-11-20 | `gh pr edit` fails on the deprecated Projects (classic), so `finish` could not update the pull request | 🟡 Worked around |
| [L-31](#l-31) | 2026-11-20 | The start rule is read by a model, which reported the ticket's test errors as a refusal (seen twice) | 🟢 Closed |
| [L-32](#l-32) | 2026-11-20 | A failing check was sent to the owner of the first file it was given, not of the file it failed on | 🟢 Closed |
| [L-27](#l-27) | 2026-11-20 | The updates of a ticket run name the files and lines they change without linking to them | 🔴 Open |
| [L-33](#l-33) | 2026-11-20 | `automerge` gave up when another merge moved `develop` at the same moment | 🔴 Open |

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
  [`tests/udp.rs`](../../packages/rust/swarm-synthetic-drones/tests/udp.rs). That test reads
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
