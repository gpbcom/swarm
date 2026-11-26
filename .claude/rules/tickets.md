# Ticket rules

These rules apply to every ticket of the roadmap (`docs/specs/roadmap/`), worked by the agent graph of
`.claude/agents/` and `.claude/workflows/`. They apply to the person and to every agent.

## How this file works

- Each rule has an ID (`TKT-<n>`) that never changes. New rules are added at the end with the next free ID.
- Each rule has the same parts: **Rule**, **Why**, **Check**.
- Each rule, here and in `.claude/rules/specs.md`, is listed in `.claude/rules/enforcement.json` with what enforces it
  (TKT-22).
- **A gap found in the harness is closed with three things:** the fix, a test that fails without it, and the rule that
  makes it a gap (a new rule or a changed one), with its enforcers in `.claude/rules/enforcement.json`.

| ID | Rule |
| --- | --- |
| [TKT-1](#tkt-1) | A ticket is a roadmap ticket, with one folder in `docs/tickets/<ID>/` |
| [TKT-2](#tkt-2) | `TICKET.md` states what to deliver and how it is accepted, from the specifications only |
| [TKT-3](#tkt-3) | `PLAN.md` is a task graph, and nothing is built before the person approves it |
| [TKT-4](#tkt-4) | Tasks are split to run in parallel as much as possible |
| [TKT-5](#tkt-5) | Every worker runs in its own worktree and hands its changes off uncommitted; the ticket is committed once, when it is done, and reaches `develop` through its pull request |
| [TKT-6](#tkt-6) | A ticket is done when checks, review and documents are complete |
| [TKT-7](#tkt-7) | Each agent has a fixed model and effort, chosen for cost and quality |
| [TKT-8](#tkt-8) | Agents never invent facts; assumptions are recorded and reviewed |
| [TKT-9](#tkt-9) | The person gets a progress update every 2 minutes while a ticket workflow runs |
| [TKT-10](#tkt-10) | `PROGRESS.md` records the elapsed time of every step and of the whole ticket, and the tokens consumed |
| [TKT-11](#tkt-11) | Running a ticket again continues where it stopped |
| [TKT-12](#tkt-12) | The review converges: only blocking findings are fixed, later rounds only confirm the fixes |
| [TKT-13](#tkt-13) | Hooks format the edited files and check the touched layer before a task is handed back |
| [TKT-14](#tkt-14) | `EXPLAIN.md` explains how the work works, file by file and line by line; `IMPLEMENTATION.md` justifies each choice against its alternatives |
| [TKT-15](#tkt-15) | GitFlow on GitHub: the tickets' branch `feature/tickets`, a pull request merged once CI passes, hooks that refuse the rest |
| [TKT-16](#tkt-16) | Several tickets run at once in the main checkout, on one shared branch, under a start rule and area locks |
| [TKT-17](#tkt-17) | The GitHub board mirrors the roadmap and every ticket's state, in Claude Code and VS Code too |
| [TKT-18](#tkt-18) | The person reviews the code before anything is committed or pushed |
| [TKT-19](#tkt-19) | A worker blocked by another task's file reports it, and that task's owner fixes it before the retry |
| [TKT-20](#tkt-20) | A GitHub issue with its child issues, or a group of issues, is planned at once, approved once and run as fast as the start rule allows |
| [TKT-21](#tkt-21) | A ticket that changes a front end lists the screens it shows and captures them as screenshots before it is done |
| [TKT-22](#tkt-22) | Every rule names what enforces it, and more than a reading alone |
| [TKT-23](#tkt-23) | "Done" has one definition, and every harness command can run again safely |
| [TKT-24](#tkt-24) | Harness scripts run anywhere: a shallow CI checkout, no local develop, no GitHub |
| [TKT-25](#tkt-25) | A branch lives as long as its work: only a live branch is rebased, the rest is deleted after a backup, and `master` is never rewritten |
| [TKT-26](#tkt-26) | A release reaches `master` by itself, with its changelog, its release notes and its test reports |

## <a id="tkt-1"></a>TKT-1: Roadmap tickets, one folder each

**Rule:** the ID is the roadmap ticket ID (`T1.07`). The folder `docs/tickets/T1.07/` holds:

| File | Holds | Written by |
| --- | --- | --- |
| `TICKET.md` | What to deliver, links, acceptance criteria | ticket-writer |
| `PLAN.md` | The task graph, its waves, the approval status | planner (content), scribe (file) |
| `PROGRESS.md` | 📝 Events (decisions, merges, verdicts, stops) with their time, and ⏱️ Timings with the tokens consumed (TKT-10) | scribe, progress script |
| `EXPLAIN.md` | How the delivered work works, the files and lines changed, how to test it (TKT-14) | explainer |
| `IMPLEMENTATION.md` | Each implementation choice against its alternatives, with the trade-off (TKT-14) | explainer |
| `REVIEW.md` | The reviewer's short review note for the person (TKT-6) | scribe, from the reviewer's note |
| `tests-evidences/` | Outputs of the checks, test reports, screenshots | verifier, scribe |

**Why:** one place per ticket for the person and every agent, traceable to the roadmap.

**Check:** the folder exists with these files before a ticket is called done.

## <a id="tkt-2"></a>TKT-2: TICKET.md

**Rule:** `TICKET.md` follows the template `.claude/skills/ticket/templates/TICKET.md`. It has, in order: title and
status; roadmap link (phase page, phase and ticket anchor), sprint, epic; the features, use cases and business rules it
delivers (links with IDs); the technical pages it builds on; the screens it touches (`Screens touched`) and the
budgets it touches (`Budgets touched`); acceptance criteria (the ticket's "done when" plus the features' Given/when/then
criteria it closes); out of scope. It states nothing that the specifications or the roadmap do not state.

**`TICKET.md`, `PLAN.md` and `PROGRESS.md` always refer to the specification:** `TICKET.md` links at least one
technical page section, feature (📘 FS), use case (🎬 UC) or business rule (📏 BR), each link resolving. When the
roadmap row names none, the ticket-writer links the specification sections that settle what the ticket builds (its
paths, layers, tools and terms), each with one line quoting what that section says for the ticket. When no section
does, the ticket is not planned: the specification is written first. `python3 .claude/scripts/tickets/ticket_refs.py sync`
copies these links into a generated **📚 Specifications** section of `PLAN.md` and `PROGRESS.md`, and every task
brief links the pages it applies.

**Why:** the plan and the review are only as good as the ticket they start from.

**Check:** `python3 .claude/scripts/tickets/ticket_refs.py check --ticket <ID>` prints nothing (run by `/ticket-plan` and by
the verifier's `checks.py`). `python3 .claude/skills/ticket/scripts/check_ticket.py <ID>` prints nothing when every FS,
UC and BR ID and every link resolves in `docs/specs/`, and the sections are in order; `/ticket-plan` runs it. A ticket
that fails goes back to the ticket-writer once, then the run stops. The reviewer compares the delivered work with
`TICKET.md`.

## <a id="tkt-3"></a>TKT-3: The plan and its approval

**Rule:** `PLAN.md` starts with `**Plan:** 🟡 Awaiting approval`. Its ` ```json ` block, folded at the end of the
page, is the only source of the task graph and the one the workflow reads. `python3 .claude/scripts/tickets/plan.py render
--ticket <ID>` writes from it, for the person, the waves table, a Mermaid dependency graph and one section per task
with every field; that view is never edited by hand, and `plan.py check` prints nothing when it is up to date. Each task has: `id` (`K01`...), `title`, `agent` (an agent of
`.claude/agents/`), `depends_on`, `files` (the files it alone may change), `brief`, `done_when`. The waves are computed
from `depends_on`. **The person approves by changing the line to `**Plan:** 🟢 Approved`**; `/ticket-run` refuses any
other status.

**Why:** the person's single gate is the plan: once approved, the graph runs to the end without supervision.

**Check:** `/ticket-run` reads the status first and stops when it is not approved. `python3 .claude/skills/ticket/scripts/check_plan.py <ID>`
prints nothing (graph, waves, file ownership and tests first): `/ticket-plan` runs it after writing `PLAN.md`, and
`/ticket-run` runs it at the gate.

## <a id="tkt-4"></a>TKT-4: Parallel by design

**Rule:**

- Tasks are as small and as independent as possible: one concern, one layer or one package each.
- Tests come first: `test-writer` tasks are in the first wave, and each implementation task depends on its tests.
- Within a wave, a file belongs to one task only; a task that needs a file owned by another waits for the next wave.
- At most **8 agents run at once** (balanced tier).
- Documentation, mock-ups and specification updates are separate tasks running beside the code.

**Why:** the person's review is the bottleneck ([R-01](../../docs/specs/roadmap/12-risks.md#r-01)); the more of a
ticket runs in parallel, the more tickets each sprint can close.

**Check:** the workflow moves any task that shares a file with another of its wave to the next wave, and logs it.

## <a id="tkt-5"></a>TKT-5: Worktrees, hand-offs and one commit per ticket

**Rule:**

- Every running ticket works in the **main checkout**, its *home*, on the branch `feature/tickets` that they all share
  (TKT-15, TKT-16). `python3 .claude/scripts/tickets/ticket_tree.py prepare` puts the main checkout on it (from
  `origin/develop` when no other ticket runs) and records the ticket's own files in `.git/swarm/<ID>/state.json`,
  starting with `docs/tickets/<ID>/`, where its documents stay.
- **No intermediate commit.** Until the ticket is done, its work (code, tests, documents) stays **uncommitted** in the
  main checkout, beside the other running tickets' work. No agent runs `git commit`, `git merge`, `git rebase`, `git
  stash`, `git reset` or `git push`: the PreToolUse hook `.claude/hooks/guard_git.py` refuses them on `feature/tickets`
  and in a worker's worktree. Every step goes through
  `ticket_tree.py`, which compares git *trees* (never commits) on a temporary index.
- Every worker runs in its own git worktree and changes only its task's files:
  - its first step, `ticket_tree.py start`, moves the worktree to the home's commit if `develop` moved since, copies
    the ticket's uncommitted work (earlier waves, `TICKET.md`, `PLAN.md`) into it and records the tree it starts from;
  - its last step, `ticket_tree.py handoff --task <task id>`, saves its own changes since that tree as a patch in the
    shared git directory (`.git/swarm/<ID>/pending/`).
- After each wave, the **integrator** runs `ticket_tree.py integrate` with the wave's task ids in task order: it applies
  each patch to the main checkout, adds the files it changes to the ticket's own files, stops at the first conflict for
  the integrator to resolve, removes the integrated worktrees and records the task ids (TKT-11). `ticket_tree.py diff`,
  `changes` and `docs`, and the verifier's `checks.py`, look at the ticket's own files only.
- When the ticket is done (TKT-6), the documents are written first, and the run stops for the person's code review
  (TKT-18). Once the person approves the push, the next run checks the code again, then the integrator runs
  `ticket_tree.py finish`:
  **one commit** on `feature/tickets`, titled with the title of `TICKET.md`, holding **only the ticket's own files**
  (the other running tickets stay uncommitted), pushed, and the pull request of `feature/tickets` opened or updated
  (TKT-15). One finish at a time: a lock in `.git/swarm/` serialises them. The commit and the push are the last writes
  of the run, so `PROGRESS.md` does not record them: git and the pull request do. Without a remote, `finish` merges the
  branch into `develop` locally with `--no-ff`.
- A ticket that stops keeps its work uncommitted in its home, and `/ticket-run` continues it (TKT-11).
- **Only `finish` pushes**, and only `feature/tickets`. Nothing is ever pushed to `develop` or `master` by hand
  (TKT-15).

**Why:** the history of `develop` gets one readable commit per ticket and its merge, instead of one commit per task
and one merge per wave, and a ticket that stops halfway leaves nothing half-finished in the history. Parallel agents
never edit the same checkout; parallel tickets share one, but each commits only its own files.

**Check:** `git log develop` shows one commit per ticket and its merge; `python3 .claude/scripts/tickets/ticket_tree.py status
--ticket <ID>` lists the tasks integrated so far; the tests of `tests/harness/ticket_tree/` pass.

## <a id="tkt-6"></a>TKT-6: Done

**Rule:** a ticket is done when:

1. the **verifier** reports every applicable check passing, as decided and run by `.claude/scripts/tickets/checks.py`
   (deterministic, not a model's judgement): the AGENT.md tools on changed project code (ruff, mypy, pytest, cargo,
   pnpm, Terraform) and `specs.py check`; a check whose target does not exist yet is not applicable, never failed.
   **The checks run in a clean temporary worktree of the shared branch's commit that holds only the ticket's own
   changes**, never in the shared checkout: `uv` and `pnpm -r` read the whole workspace, and the other running
   tickets' work is half built by design (tests first, TKT-4), so it would fail this ticket;
2. the **reviewer** approves the diff against `TICKET.md`, the specifications and the rules (AGENT.md, SPEC, TKT), and
   returns a short review note, written to `REVIEW.md`;
3. `EXPLAIN.md`, `IMPLEMENTATION.md` (TKT-14), `REVIEW.md` and `PROGRESS.md` are written, with the evidence in
   `tests-evidences/`;
4. a ticket that changes a front end has captured every screen it lists as `📸 Screenshot` (TKT-21);
5. the person has reviewed the code and approved the push (TKT-18);
6. the work and these documents are committed once and merged into `develop` (TKT-5).

A failed check or a requested change goes back to the agent that owns the files, at most twice; then the ticket
stops and the person is told. A check that fails because of the environment (a missing tool or third-party module, flagged
`environment` by `checks.py`) goes to no agent: the run stops at once and the person fixes the environment. A
missing module of the project itself (`tests.…`, a service or a package of the repository) is a wrong import in the
ticket's code, and goes to its owner like any failure. Each failure names the file the tool reports it in (not the first
file the tool was given), so that it goes to the owner of that file.

**Why:** "done" must mean merged code that works and that someone else can understand.

**Check:** `/ticket-run` ends with the verifier's and the reviewer's verdicts in `PROGRESS.md`; the tests of
`tests/harness/checks/` pass, one of them proving that another ticket's uncommitted change never reaches the clean
tree.

## <a id="tkt-7"></a>TKT-7: Models and cost (balanced tier)

**Rule:** each agent's model and effort are set in its file and changed only here:

| Agent | Model | Effort | Why |
| --- | --- | --- | --- |
| planner, reviewer | opus | high | Errors here cost the most: a bad plan or a missed defect wastes whole waves |
| implementer, test-writer, frontend-implementer, integrator, ticket-writer, explainer | sonnet | medium | Most coding work, at a fraction of opus's cost; explaining the work and its trade-offs needs to read code, which haiku does poorly |
| rust-implementer | sonnet | high | Hot path with strict budgets |
| mockup-writer, doc-writer, scribe, verifier, runner | haiku | low | Mechanical work: documents, screens, running checks; the runner runs one given command and reports its exit code |

- Workers of one wave share the same tools and folder, so their prompt prefix is cached across the wave.
- Agents read only what their brief names, and report in a few lines (the schema of the workflow).

**Why:** cost grows with the number of agents and the size of their context; quality matters most at the plan and
the review.

**Check:** the token use per agent is logged in `PROGRESS.md` from the workflow's report.

## <a id="tkt-8"></a>TKT-8: No invented facts

**Rule:** an agent that meets a question the specifications do not answer does not guess silently: it takes the
most conservative option, records it as an **assumption** in its result, and the scribe lists every assumption in
`PROGRESS.md`. The reviewer checks each assumption against the specifications and rejects any that contradicts them.

**Why:** the person approves the plan, not every detail; assumptions must stay visible.

**Check:** the reviewer's verdict lists the assumptions it accepted.

## <a id="tkt-9"></a>TKT-9: Progress every 2 minutes

**Rule:** as soon as `/ticket-plan` or `/ticket-run` is launched, the main session arms the Monitor tool with

```bash
python3 .claude/scripts/reports/progress.py watch --every 120 --run <run id>
```

(`timeout_ms` 1800000, re-armed at each expiry until the run ends). Each update is an **exhaustive report with colour
icons**:

| Line | Holds |
| --- | --- |
| Header | ⏳ running, 🏁 ended or ❌ failed; workflow and ticket; 🕒 time; ⏱️ elapsed minutes; 🪙 tokens |
| 📍 Phases | Every phase of the workflow: ✅ done ▸ 🔄 running ▸ ⬜ waiting |
| 👥 Agents | Counts done and running, then one line per agent: ✅ 🔄 ❌ state, label, model (🟣 opus 🔵 sonnet 🟢 haiku 🟠 fable), ⏱️ duration, 🪙 tokens, 📝 result summary |
| 💰 Tokens by model | The tokens of the run per model, to follow the cost tier of TKT-7 |

The session relays each report to the person in full, keeping the icons, and a last one when the run ends, fails or
stalls (⚠️ no change for 20 minutes). The same script with `once` gives the report on demand.

**Why:** a ticket run takes from minutes to hours in the background; the person must see it moving without asking.

**Check:** the conversation shows an update at least every 2 minutes for the whole run.

## <a id="tkt-10"></a>TKT-10: Elapsed time and tokens in PROGRESS.md

**Rule:** at the end of every ticket workflow (plan, run, re-run), whether it finishes or stops, the scribe runs

```bash
python3 .claude/scripts/reports/progress.py timings --ticket <ID> --write
```

which writes, between the `<!-- timings -->` markers of `PROGRESS.md`, measured from the agents' transcripts:

- the **overall ticket time** (first start to last activity), the time with agents working, the time between runs
  (approvals, fixes) and the number of runs;
- the **tokens consumed**: input, output, cache write and cache read, in total and **by model**;
- per run: per phase and **per step**, the start, end, elapsed time and tokens.

The 📝 Events table above it holds what the timings cannot measure: approvals, decisions, merges, verdicts, stops,
each with its time.

**Why:** the person decides the cost tier (TKT-7) and the pace of the roadmap from real durations and consumption.

**Check:** `PROGRESS.md` of every ticket has the timings block, updated after its last run.

## <a id="tkt-11"></a>TKT-11: Re-running continues

**Rule:** `/ticket-run <ID>` skips every task that `python3 .claude/scripts/tickets/ticket_tree.py status --ticket <ID>` lists
as integrated (the integrator records it when it applies the task's hand-off, TKT-5), and starts from the first wave
with work left. For a ticket started before TKT-5 dropped intermediate commits, a task with a commit
`<ID> <task id>:` on `ticket/<ID>` counts as integrated too. A change to an approved plan (a task's brief or check) is approved by the person
and recorded in 📝 Events before the re-run.

**Why:** a stop in wave 3 must not pay again for waves 1 and 2.

**Check:** the re-run's timings show no step for the skipped tasks.

## <a id="tkt-12"></a>TKT-12: The review converges

**Rule:**

- The reviewer classifies every finding as **blocking** (wrong behaviour, security or safety, an unmet acceptance
  criterion, a rule violation that breaks the checks, a budget missed) or **follow-up** (everything else). When in
  doubt, it is a follow-up.
- Only blocking findings go to the fixers. Follow-ups are listed in `PROGRESS.md` (and `EXPLAIN.md`) under
  **🔜 Follow-ups** and never hold the merge; the person may turn them into tickets.
- Round 1 is a **full review**. Every later round only **confirms the fixes**: it checks that each previous blocking
  finding is resolved and looks only at the diff of the fixes for blocking defects they introduced.
- The ticket is approved when no blocking finding is left. If blocking findings remain after the fix rounds of TKT-6,
  the run stops and the person decides; there is never a new full review in the same run.

**Why:** a fresh full review finds new things every time; without severity and a confirm-only mode, a ticket never
converges and every round costs an opus review.

**Check:** `PROGRESS.md` shows at most one full review per run, and the merge happens with follow-ups open.

## <a id="tkt-13"></a>TKT-13: Hooks format and check before hand-back

**Rule:**

- The PostToolUse hook `.claude/hooks/format_edited.py` formats only the edited file, with the formatter of its language
  listed in `.claude/hooks/formatters.json`.
- The SubagentStop hook `.claude/hooks/check_touched.py` runs, in a worker's worktree only, the checks of the layers the
  task touched (`.claude/hooks/layer-checks.json`). Failures go back to the agent at most twice; after that the verifier
  decides.
- Changes made only of tests do not run the tests, because the tests come first (TKT-4).
- A missing tool is not a failure: the hook reports it and lets the task finish, as the environment check of TKT-6 does.

**Why:** style never reaches the person's review ([R-01](../../docs/specs/roadmap/12-risks.md#r-01)), and a task comes
back green.

**Check:** the tests of `tests/harness/` pass, and `grep -n 'tkt-13' .claude/rules/tickets.md` finds the summary row and
the heading.

## <a id="tkt-14"></a>TKT-14: EXPLAIN.md and IMPLEMENTATION.md

**Rule:** when the ticket is done, before its single commit (TKT-5), the **explainer** writes two documents in
`docs/tickets/<ID>/`, from the templates of `.claude/skills/ticket/templates/`:

- **`EXPLAIN.md`: how it works.** What the ticket delivers; how the mechanism works, step by step in the order it runs,
  each step linked to the file and line that does it; the files and lines changed; how to test it; the evidence; the
  assumptions accepted and the follow-ups. The table of files and line ranges is written between the
  `<!-- changes -->` markers by `python3 .claude/scripts/tickets/ticket_tree.py changes --ticket <ID> --write`, never by
  hand, and leaves out the ticket's own folder.
- **`IMPLEMENTATION.md`: why this way.** The constraints any solution had to respect, then one section per decision:
  the option chosen, its real alternatives, what speaks for and against each in this repository (a rule, a budget, an
  acceptance criterion, the existing code), the trade-off accepted and when to revisit it.
- **Every file and every line they mention is a clickable link**, relative to `docs/tickets/<ID>/`:
  `[`path/file.py:42`](../../../path/file.py#L42)` for a line, `#L42-L50` for a range, no fragment for a whole file.
  A path in plain text or in backticks alone is refused; paths in fenced command blocks are commands and stay as they
  are. A deleted file, which has no line left to open, is the one exception.
- The decisions come from the workers, who report each choice where a reasonable alternative existed (choice,
  alternatives, trade-off, file and line), from `PLAN.md`, and from the explainer's reading of the diff. The reviewer
  checks them with the assumptions. Nothing is invented: an unknown reason is written as an open point (TKT-8).

**Why:** the person reviews in under an hour ([R-01](../../docs/specs/roadmap/12-risks.md#r-01)) and the next
developer, person or agent, inherits the code: one needs to know where things are and how they work, the other why
they are this way and what changing them would cost.

**Check:** `python3 .claude/scripts/tickets/ticket_tree.py docs --ticket <ID>` prints nothing before the commit (the changes
table is up to date, no placeholder is left, every file and line is a link, and every link opens an existing file at a
line inside it); `ticket_tree.py finish` refuses to commit otherwise, and the workflow sends its problems back to the
explainer once. Both files have every section of their template, and `grep -n 'tkt-14' .claude/rules/tickets.md` finds the summary row
and the heading.

## <a id="tkt-15"></a>TKT-15: GitFlow on GitHub

**Rule:**

- The repository is `gpbcom/swarm` on GitHub, private. `master` holds the releases, `develop` the next one (the default
  branch). Work happens on GitFlow branches only: `feature/<name>` (the roadmap tickets share `feature/tickets`,
  TKT-16; harness work is `feature/harness-<name>`), `bugfix/<name>`, `release/<version>`, `hotfix/<name>`.
- `develop` and `master` change **only through pull requests**, merged with a merge commit (squash and rebase merges
  are turned off). The pull request of `feature/tickets` goes to `develop`: one commit and one `Closes #<issue>` per
  finished ticket, titled with the ticket's `TICKET.md` title when it holds one ticket
  (`T0.10: Dev cell observability`), `Tickets T0.10, T0.12` when it holds several. A release goes `release/<version>` →
  `master`, tagged `v<version>`, then back to `develop` by its own pull request, all by itself (TKT-26); a hotfix the
  same way.
- `ticket_tree.py finish` labels the ticket's pull request `automerge`: the workflow `.github/workflows/automerge.yml`
  merges it once every check (`ci`, `gitflow`, `terraform`) has passed on its head commit, which closes its issue, then
  deletes its head branch unless it moved since (TKT-25). A failing check leaves it open for the person.
- `.github/workflows/gitflow.yml` checks every pull request: the branch is a GitFlow branch, it targets the right base,
  and a ticket's title starts with its ID.
- The git hooks of `.githooks/` (`python3 .claude/scripts/tickets/tickets.py setup`, once per clone) refuse a commit on
  `develop` or `master`, a commit by a worker, a branch outside GitFlow, a ticket commit without its ID, and a push to
  `develop` or `master`. `SWARM_GITFLOW_BYPASS=1` lets the person step outside on purpose. The PreToolUse hook
  `.claude/hooks/guard_git.py` refuses `--no-verify` everywhere and asks before any push to `develop` or `master`.
- Commits carry the gpbcom identity of this repository (`git config user.email`), never another one.

**Why:** pull requests give every merge its CI run, its review trail and its issue; GitFlow keeps releases apart from
the work in progress. A private repository of a free account has no branch protection, so the hooks and the
`automerge` and `gitflow` workflows hold the rules instead.

**Check:** the tests of `tests/harness/gitflow/` and `tests/ci/workflows/test_gitflow_workflows.py` pass;
`git log --merges develop` shows a merge of a pull request per ticket.

## <a id="tkt-16"></a>TKT-16: Several tickets at once

**Rule:**

- Every running ticket lives in the **main checkout**, on the shared branch `feature/tickets` (TKT-5), with its
  documents in `docs/tickets/<ID>/`. `/ticket-plan` and `/ticket-run` of several tickets run at the same time; each
  touches only its own files, recorded in `.git/swarm/<ID>/state.json`, and commits only those when it finishes. A
  ticket started before this rule keeps its own worktree on `feature/<ID>` until it is merged.
- **Start rule**, checked by `python3 .claude/scripts/tickets/tickets.py check --ticket <ID>` at the gate of `/ticket-run`:
  - every prerequisite of the ticket in `docs/specs/roadmap/gantt/ticket-graph.json` is **done**: merged on
    `origin/develop` (its `EXPLAIN.md` is there), or committed on `feature/tickets` (finished, its pull request open),
    since the shared branch already holds its code;
  - no open ticket changes one of the same areas (a service, a front end, a package): **area lock**, which keeps two
    tickets of the same checkout from changing the same files;
  - a field ticket (the fixes of a campaign) starts once its campaign has flown.

  `/ticket-run <ID> --force` starts anyway, on the person's decision, and logs the problems in `PROGRESS.md`. The verdict is the
  exit code of `tickets.py check`, reported unchanged by the `runner` agent: no agent judges the start rule (L-31).
- `python3 .claude/scripts/tickets/tickets.py list` shows the open tickets and the files each owns; `prune` removes the
  worktrees of tickets started before this rule once they are merged, and puts the main checkout back on `develop`
  once no ticket is open and `feature/tickets` is merged. VS Code's Source Control shows the uncommitted work of every
  running ticket at once, in the one checkout.
- At most 8 agents run per ticket (TKT-4); the person keeps the number of tickets open to what they can review
  ([⛓️ Parallel plan](../../docs/specs/roadmap/14-parallel-plan.md)).

**Why:** most tickets do not need each other ([⛓️ Parallel plan](../../docs/specs/roadmap/14-parallel-plan.md)):
running them one at a time leaves the agents idle while the person reviews. Area locks keep two tickets from changing
the same code, so their pull requests merge without conflicts.

**Check:** the tests of `tests/harness/tickets/` and `tests/harness/ticket_tree/` pass.

## <a id="tkt-17"></a>TKT-17: The board

**Rule:**

- The GitHub project **Swarm roadmap** mirrors the roadmap: one issue per phase, epic and ticket, the tickets as
  sub-issues of their epic and the epics of their phase, one milestone per phase, a **Blocked by** link per
  prerequisite of the ticket graph. `python3 .claude/scripts/github/board.py bootstrap` creates them once (resumable) and
  records them in `.claude/github.json`.
- Every ticket sits in one column: 📥 Backlog (a prerequisite is open), ✅ Ready, 📝 Planned (`/ticket-plan`),
  🔄 Running (`/ticket-run`), 👀 In review (pull request open), 🏁 Done (merged). The workflows move the card;
  `board.py sync` recomputes every column from the repository.
- The board shows in three places: the project's board view on GitHub, `python3 .claude/scripts/github/board.py show` (and
  `/board`) in a terminal, and the Claude Code status line (`.claude/scripts/reports/statusline.py`), which reads the local
  cache `.git/swarm/board.json` and never waits for GitHub.

**Why:** with several tickets running, the person needs one place that says what runs, what waits for review and what
can start next, from GitHub, from VS Code and from the terminal alike.

**Check:** the tests of `tests/harness/statusline/` pass; `board.py bootstrap --dry-run` counts every phase, epic and
ticket of the roadmap.

## <a id="tkt-18"></a>TKT-18: The person reviews the code before the push

**Rule:**

- The run that completes a ticket (checks passing, review approved, `EXPLAIN.md` and `IMPLEMENTATION.md` written)
  **commits nothing and pushes nothing**. It stops and writes, on its own line under the plan's status line of
  `PLAN.md`:

  ```markdown
  **Push:** 🟡 Awaiting code review
  ```

- The person reviews the code where it lies, uncommitted in the main checkout (`python3 .claude/scripts/tickets/ticket_tree.py
  diff --ticket <ID>` shows only this ticket's files; VS Code's Source Control shows every running ticket), with
  `EXPLAIN.md` as the guide. They may change it.
- **The person approves by changing the line to `**Push:** 🟢 Approved`**, then runs `/ticket-run <ID>` again. That run
  skips the waves and the review already done, runs the checks again (the person may have changed the code), checks
  the documents, then commits and pushes with the pull request (TKT-5, TKT-15).
- An approval written before every task is integrated does not count: the run does the work and stops for review
  again.

**Why:** the person answers for what reaches `develop`. Seeing the code before it leaves the machine costs one look at
a diff, and a pushed pull request is merged by GitHub as soon as CI passes (TKT-15), with no other chance to stop it.

**Check:** the workflow returns `awaitingReview` and makes no commit while `PLAN.md` does not say `**Push:** 🟢
Approved`; `grep -n 'tkt-18' .claude/rules/tickets.md` finds the summary row and the heading.

## <a id="tkt-19"></a>TKT-19: Blocking files go back to their owner

**Rule:**

- A worker never changes a file outside its task, and never works around a wrong one (no shim, no skipped test). When
  a file of another task stops it (most often a test of wave 1 with a wrong import, a wrong helper or a wrong call),
  it hands off what it did, reports `blocked`, and lists each such file in `blocked_by` with exactly what to change.
- Before retrying the blocked task, the workflow sends each of those files to the task that owns it, as in a fix round
  (the test-writer for a test), integrates the fix, and only then retries the blocked task, which starts from the
  corrected file.
- Only files of tasks of earlier waves are sent: a file a later wave writes is missing, not wrong. The others are
  logged and left to the retry.

**Why:** tests come first (TKT-4), so a wrong test only shows when an implementer runs it. Retrying the implementer
alone fails the same way, and stopped T0.09 four times until the person fixed the tests by hand.

**Check:** `grep -n 'tkt-19' .claude/rules/tickets.md` finds the summary row and the heading; the wave of the workflow
logs the blockers it sends before its retry.

## <a id="tkt-20"></a>TKT-20: An issue with its child issues, or a group of issues

**Rule:**

- A group of tickets is named by **references**: an issue number (`#12`: a ticket issue, or an epic or a phase issue
  with every ticket under it, through the sub-issues recorded in `.claude/github.json`), a ticket ID (`T0.10`), an epic
  ID (`E0.4`) or a phase ID (`P1`), several separated by spaces. `python3 .claude/scripts/tickets/tickets.py resolve <refs>`
  lists the tickets, every prerequisite before the tickets that need it, each with its state. **Done sub-issues are
  left out**: merged on `develop` (their `EXPLAIN.md` is there) or closed on GitHub. Running `/issue-plan` or
  `/issue-run` again on the same references never plans or starts them twice; `tickets.py next` never returns a
  ticket that is running, in review or done.
- **`/issue-plan <refs>`** plans every ticket of the group that has no `PLAN.md` yet, all at once (one `ticket-plan`
  workflow each), then stops.
- **One approval for the group:** the person reads the plans, then runs `python3 .claude/scripts/tickets/tickets.py approve
  <refs>`, which approves every plan of the group that awaits approval and passes `check_plan.py`, records it in each
  `PROGRESS.md` and moves the cards. The PreToolUse hook asks the person before Claude runs it: the approval stays
  theirs (TKT-3).
- **`/issue-run <refs>`** starts, at once, every approved ticket of the group that the start rule allows
  (`tickets.py next`), with no fixed number of lanes; it follows the group with `tickets.py watch <refs>` (a report
  every 2 minutes, TKT-9) and starts each ticket as soon as its `▶️ CAN START` line appears, until the group is merged.
  A ticket that stops is reported and the others go on; each still stops for the person's code review (TKT-18).

**Why:** an epic or a phase is the unit the person thinks in; planning and approving it in one go, and letting the
start rule pace the runs, keeps the agents busy while the person reviews ([⛓️ Parallel
plan](../../docs/specs/roadmap/14-parallel-plan.md)).

**Check:** the tests of `tests/harness/tickets/test_groups.py` pass; `grep -n 'tkt-20' .claude/rules/tickets.md` finds the
summary row and the heading.

## <a id="tkt-21"></a>TKT-21: Front-end tickets capture their screens

**Rule:**

- A ticket that changes a front end (its area in `docs/specs/roadmap/gantt/ticket-graph.json` holds `frontend/apps/`)
  links, under **Screens touched** of `TICKET.md`, every screen it shows: the PNG of the screen or its row on the use
  case page. When it really shows none, it says why, on its own line: `- ➖ No screen: <why>`.
- Its plan holds a **capture task** (`mockup-writer`) that depends on every `frontend-implementer` task and owns both
  PNGs of every listed screen (`docs/specs/screens/<UC-ID>/<node>.png` and `<node>.dark.png`), its mock-up and its use
  case page. The task captures each screen from the running app in light and dark mode with the screenshot pipeline of
  T0.20, sets the screen row's source to `📸 Screenshot` and deletes the mock-up (SPEC-12).
- The verifier fails the ticket while a listed screen is still `✏️ Mock-up`, while one of its PNGs was not captured
  by the ticket itself, or while its mock-up is left. Until T0.20 is merged, the check is not applicable: the screens
  stay mock-ups, and the capture task updates them to what the app shows.
- The reviewer checks that the list is complete and that each screenshot shows the state of its use case; a weak
  `➖ No screen` reason is a blocking finding.

**Why:** a screen described only by a mock-up drifts from the app as soon as the code changes. Capturing it in the
ticket that builds it keeps the specification's picture and the product the same, and the phases' exit criteria
(every use case screen moved to 📸) are met as the tickets merge, not in a catch-up at the end of the phase.

**Check:** `check_ticket.py` refuses a front-end ticket that lists no screen and gives no reason; `check_plan.py`
refuses its plan without a capture task after the front-end work; `checks.py` runs "screens captured"; the tests of
`tests/harness/check_ticket/`, `tests/harness/check_plan/test_screen_capture.py` and `tests/harness/checks/` pass.

## <a id="tkt-22"></a>TKT-22: Every rule names what enforces it

**Rule:**

- Every rule of `.claude/rules/specs.md` (SPEC) and of this file (TKT) has an entry in
  `.claude/rules/enforcement.json`: the tests, scripts, hooks, workflows, CI jobs and agents that enforce it, each
  with what it checks.
- At least one enforcer of each rule is not an agent's reading: a test, a script, a hook, a workflow or a CI job. A
  rule checked by reading only is a wish.
- An obligation a specification rule puts on the code is enforced where the code is built: in the ticket harness.
  SPEC-12's screenshots are checked by the plan, the verifier and the reviewer of every front-end ticket (TKT-21).
- A new rule, or a gap closed, adds its entry in the same change.

**Why:** SPEC-12 asked for screenshots once the app shows a state, and nothing in the ticket harness ever checked it:
front-end tickets would have merged with mock-ups. A rule without an enforcer is found missing only when it has
already failed.

**Check:** `tests/harness/wiring/test_enforcement.py` fails when a rule has no entry, an entry names a rule that does
not exist or a file that does not exist, or a rule has only agents as enforcers.

## <a id="tkt-23"></a>TKT-23: One definition of done, and commands that can run again

**Rule:**

- **Done is defined once**, by `done_tickets()` in `.claude/scripts/tickets/tickets.py`: a ticket merged on `origin/develop`
  (its `EXPLAIN.md` is there) or whose issue is closed on GitHub. A ticket **finished** has its commit on
  `feature/tickets`, its pull request open. Every script that needs it (`tickets.py`, `board.py`) uses that function.
- `/ticket-plan` (`tickets.py done`) and `/ticket-run` (`tickets.py check`) refuse a ticket done or finished, even with
  `--force`; `/issue-plan`, `/issue-run`, `tickets.py approve` and `tickets.py next` leave such tickets out.
- **Every harness command can run again on the same input** and does nothing twice: a resumed bootstrap counts what
  GitHub already holds as made, a re-run ticket continues where it stopped (TKT-11), a group skips what is done.
  Each such command has a test that runs it again, or on finished work.

**Why:** groups knew only merged tickets, not closed ones; `approve` would have approved the plan of a finished
ticket; the bootstrap stopped on a link it had made just before a stop; and `/ticket-run` would have run a merged
ticket again. Each came from a command that assumed it ran once, on fresh input.

**Check:** the tests of `tests/harness/tickets/test_groups.py` (done tickets never planned, approved or run again)
and of `tests/harness/board/test_board.py` (resume) pass; `grep -n 'done_tickets' .claude/scripts/github/board.py` finds the
board using it.

## <a id="tkt-24"></a>TKT-24: Harness scripts run anywhere

**Rule:** a harness script never needs, unless it is its purpose:

- a local `develop` branch (CI checks out a pull request alone): it finds `develop`, then `origin/develop`, then
  `HEAD` (`roadmap_gantt.develop_ref()`);
- the full history (CI's checkout is shallow): a date or a commit it cannot find falls back to `HEAD`;
- GitHub (CI has no login, a dry run touches nothing): reading GitHub is optional and a missing answer means "nothing
  known", never a stop.

**Why:** #345 failed three times in CI on these three assumptions, which every local run met.

**Check:** the tests of `tests/harness/board/test_board.py` (a dry run with a `gh` that always fails, `develop_ref`
without `develop`) pass, and CI runs every harness test in its own shallow checkout.

## <a id="tkt-25"></a>TKT-25: A branch lives as long as its work

**Rule:**

- Every branch, local and on GitHub, has one verdict against `origin/develop`, printed by `python3
  .claude/scripts/tickets/tickets.py branches`:

  | Verdict | Means | What happens |
  | --- | --- | --- |
  | 🔒 protected | `develop`, `master` | Never rebased, reset, force-pushed or deleted. `master` moves only through a release or a hotfix pull request (TKT-15) |
  | 🔄 open | The branch checked out in the main checkout, an open ticket's branch, `feature/tickets` and the workers' `worktree-*` branches while a ticket is open | Left alone |
  | 🧹 merged | An ancestor of `develop` | Deleted |
  | 🧹 integrated | Every change already in `develop` under other commits (`git cherry`), as after a history rewrite | Deleted |
  | 🧹 superseded | A worker's or a ticket's branch whose own commits all belong to done tickets (TKT-23): attempts `develop` replaced; a leftover `<repo>-tickets/<ID>` folder of a done ticket | Deleted, **never rebased** |
  | 🌱 live | Commits of its own | **The only branches rebased onto `develop`** |

- **"Rebase the branches" means the 🌱 live ones.** A 🧹 branch is never rebased: its rebase would bring back code
  that `develop` replaced, or replay commits already there.
- `tickets.py prune` deletes every 🧹 branch, locally and on GitHub, with its worktree, once the tickets are merged.
  **Nothing is deleted without a backup:** it first writes one bundle in `.git/swarm/backups/` holding every branch it
  deletes and, under `refs/swarm-backup/`, the uncommitted work of every worktree and folder it removes. It prints the
  command that restores them. `prune --dry-run` says what it would delete and changes nothing.
- A worker's worktree and branch never outlive the ticket: `ticket_tree.py integrate` removes them once integrated,
  and `prune` removes what a stopped run left.

**Why:** asked to "rebase all the branches on develop", the repository held 135 local branches, 7 merged branches on
GitHub and 22 worker worktrees, none of them with work of its own. Twelve worker branches held first attempts that
later fix rounds had replaced, and nine worktrees held uncommitted copies: rebasing them would have put old code back
on top of `develop`, and deleting them by hand would have lost it with no way back. `master`, 359 commits behind,
would have been rewritten outside GitFlow.

**Check:** the tests of `tests/harness/tickets/test_branches.py` (verdicts, backup before deletion, dry run, workers
kept while a ticket is open, GitHub branches, leftover folders) and of `tests/harness/gitflow/test_gitflow.py` (the
PreToolUse hook `.claude/hooks/guard_git.py` refuses a rebase, a reset or a forced push of `develop` or `master`; the
pre-push hook refuses deleting them) pass; `grep -n 'tkt-25' .claude/rules/tickets.md` finds the summary row and the
heading.

## <a id="tkt-26"></a>TKT-26: A release reaches master by itself

**Rule:**

- A release is started on `develop`, by the person, with `/release` or `gh workflow run release.yml --ref develop [-f
  version=x.y.z]` (the next minor version after the last `v*` tag by default, `0.1.0` first). Nobody commits by hand
  after that, and nobody merges by hand.
- `.github/workflows/release.yml` runs **every suite of CI** on that commit, with every service, package and front end
  selected. Only when all of them pass does it write, with `.github/scripts/release_notes.py`, on `release/<version>`:

  | File | Holds |
  | --- | --- |
  | `CHANGELOG.md` | A new section on top: one line per commit of each pull request merged since the last release, grouped by kind (tickets, harness, specifications, CI/CD and fixes, other) |
  | `docs/releases/v<version>/RELEASE_NOTES.md` | The tickets delivered with the features, use cases and business rules they deliver, the test summary, the changes by kind |
  | `docs/releases/v<version>/TEST_REPORT.md` | One row per test suite (passed, failed, skipped, time) and the verdict |
  | `docs/releases/v<version>/tests/` | The raw reports: the JUnit XML of pytest and the logs of cargo, Vitest and `specs.py check` |

  then opens the pull request to `master`, labelled `automerge`. **No release reaches `master` without its test
  reports:** `release_notes.py write` refuses to write anything when CI left no report.
- Every CI run keeps its test reports as `test-report-*` artifacts, failed runs included.
- `.github/workflows/automerge.yml` merges the release into `master` once every check passed (merge commit), tags
  `v<version>`, publishes the GitHub release with the release notes, and opens the way back to `develop`, which it
  merges the same way, then deletes `release/<version>` (TKT-25). GitHub deletes the release branch itself when a
  person's token merges it into `master`; `automerge.yml` then recreates it at the released commit for the way back.
  Only `release/` and `hotfix/` go to `master`.
- The secret `RELEASE_TOKEN` (a token of the repository with contents, pull requests and workflows in write) does what
  `GITHUB_TOKEN` may not: its pull requests start CI, and its merge into `master` may carry `.github/workflows/`.
  Without it, the release stops at once and says so.
- Starting a release is the person's decision: the PreToolUse hook asks before Claude runs it.

**Why:** `master` had stayed on the first commit while 359 commits reached `develop`, because a release needed a
person to branch, write the notes, merge into `master`, tag and merge back by hand. A release by hand is late, and its
notes and test reports are whatever someone remembers to write.

**Check:** the tests of `tests/ci/release/` (the release workflow, the reports of every suite, and `automerge.yml` run
under bash with a stand-in `gh`: the merge into `master`, the tag, the way back, the token) and of
`tests/ci/release_notes/` (version, changelog, release notes, test report, no release without reports) pass;
`grep -n 'tkt-26' .claude/rules/tickets.md` finds the summary row and the heading.
