# Ticket rules

These rules apply to every ticket of the roadmap (`docs/specs/roadmap/`), worked by the agent graph of
`.claude/agents/` and `.claude/workflows/`. They apply to the person and to every agent.

## How this file works

- Each rule has an ID (`TKT-<n>`) that never changes. New rules are added at the end with the next free ID.
- Each rule has the same parts: **Rule**, **Why**, **Check**.

| ID | Rule |
| --- | --- |
| [TKT-1](#tkt-1) | A ticket is a roadmap ticket, with one folder in `docs/tickets/<ID>/` |
| [TKT-2](#tkt-2) | `TICKET.md` states what to deliver and how it is accepted, from the specifications only |
| [TKT-3](#tkt-3) | `PLAN.md` is a task graph, and nothing is built before the person approves it |
| [TKT-4](#tkt-4) | Tasks are split to run in parallel as much as possible |
| [TKT-5](#tkt-5) | Every worker runs in its own worktree and hands its changes off uncommitted; the ticket is committed once, when it is done; nothing is pushed |
| [TKT-6](#tkt-6) | A ticket is done when checks, review and documents are complete |
| [TKT-7](#tkt-7) | Each agent has a fixed model and effort, chosen for cost and quality |
| [TKT-8](#tkt-8) | Agents never invent facts; assumptions are recorded and reviewed |
| [TKT-9](#tkt-9) | The person gets a progress update every 2 minutes while a ticket workflow runs |
| [TKT-10](#tkt-10) | `PROGRESS.md` records the elapsed time of every step and of the whole ticket, and the tokens consumed |
| [TKT-11](#tkt-11) | Running a ticket again continues where it stopped |
| [TKT-12](#tkt-12) | The review converges: only blocking findings are fixed, later rounds only confirm the fixes |
| [TKT-13](#tkt-13) | Hooks format the edited files and check the touched layer before a task is handed back |
| [TKT-14](#tkt-14) | `EXPLAIN.md` explains how the work works, file by file and line by line; `IMPLEMENTATION.md` justifies each choice against its alternatives |

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
does, the ticket is not planned: the specification is written first. `python3 .claude/scripts/ticket_refs.py sync`
copies these links into a generated **📚 Specifications** section of `PLAN.md` and `PROGRESS.md`, and every task
brief links the pages it applies.

**Why:** the plan and the review are only as good as the ticket they start from.

**Check:** `python3 .claude/scripts/ticket_refs.py check --ticket <ID>` prints nothing (run by `/ticket-plan` and by
the verifier's `checks.py`). `python3 .claude/skills/ticket/scripts/check_ticket.py <ID>` prints nothing when every FS,
UC and BR ID and every link resolves in `docs/specs/`, and the sections are in order; `/ticket-plan` runs it. A ticket
that fails goes back to the ticket-writer once, then the run stops. The reviewer compares the delivered work with
`TICKET.md`.

## <a id="tkt-3"></a>TKT-3: The plan and its approval

**Rule:** `PLAN.md` starts with `**Plan:** 🟡 Awaiting approval`. Its ` ```json ` block, folded at the end of the
page, is the only source of the task graph and the one the workflow reads. `python3 .claude/scripts/plan.py render
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

- The ticket branch is `ticket/<ID>`, created from `develop`. `python3 .claude/scripts/ticket_tree.py prepare` puts the
  main checkout on it. When it has to switch branch, it refuses a checkout with changes outside `docs/tickets/<ID>/`,
  which the single commit would otherwise take.
- **No intermediate commit.** Until the ticket is done, its work (code, tests, documents) stays **uncommitted** in the
  main checkout on `ticket/<ID>`. No agent runs `git commit`, `git merge`, `git stash` or `git reset`; every step goes
  through `ticket_tree.py`, which compares git *trees* (never commits) on a temporary index.
- Every worker runs in its own git worktree, branched from `ticket/<ID>`, and changes only its task's files:
  - its first step, `ticket_tree.py start`, copies the ticket's uncommitted work (earlier waves, `TICKET.md`,
    `PLAN.md`) into the worktree and records the tree it starts from;
  - its last step, `ticket_tree.py handoff --task <task id>`, saves its own changes since that tree as a patch in the
    shared git directory (`.git/swarm/<ID>/pending/`).
- After each wave, the **integrator** runs `ticket_tree.py integrate` with the wave's task ids in task order: it applies
  each patch to the main checkout, stops at the first conflict for the integrator to resolve, removes the integrated
  worktrees and records the task ids (TKT-11).
- When the ticket is done (TKT-6), the documents are written first, then the integrator runs `ticket_tree.py finish`:
  **one commit** on `ticket/<ID>`, titled with the title of `TICKET.md`, merged into `develop` locally with `--no-ff`.
  The commit and the merge are the last writes of the run, so `PROGRESS.md` does not record them: git does.
- A ticket that stops keeps its work uncommitted on `ticket/<ID>`, and `/ticket-run` continues it (TKT-11).
- **Nothing is ever pushed** by the harness.

**Why:** the history of `develop` gets one readable commit per ticket instead of one commit per task and one merge
per wave, and a ticket that stops halfway leaves nothing half-finished in the history. Parallel agents still never edit
the same checkout.

**Check:** `git log develop` shows one commit per ticket and its merge; `python3 .claude/scripts/ticket_tree.py status
--ticket <ID>` lists the tasks integrated so far; the tests of `tests/harness/ticket_tree/` pass.

## <a id="tkt-6"></a>TKT-6: Done

**Rule:** a ticket is done when:

1. the **verifier** reports every applicable check passing, as decided and run by `.claude/scripts/checks.py`
   (deterministic, not a model's judgement): the AGENT.md tools on changed project code (ruff, mypy, pytest, cargo,
   pnpm, Terraform) and `specs.py check`; a check whose target does not exist yet is not applicable, never failed;
2. the **reviewer** approves the diff against `TICKET.md`, the specifications and the rules (AGENT.md, SPEC, TKT), and
   returns a short review note, written to `REVIEW.md`;
3. `EXPLAIN.md`, `IMPLEMENTATION.md` (TKT-14), `REVIEW.md` and `PROGRESS.md` are written, with the evidence in
   `tests-evidences/`;
4. the work and these documents are committed once and merged into `develop` (TKT-5).

A failed check or a requested change goes back to the agent that owns the files, at most twice; then the ticket
stops and the person is told. A check that fails because of the environment (a missing tool or module, flagged
`environment` by `checks.py`) goes to no agent: the run stops at once and the person fixes the environment.

**Why:** "done" must mean merged code that works and that someone else can understand.

**Check:** `/ticket-run` ends with the verifier's and the reviewer's verdicts in `PROGRESS.md`.

## <a id="tkt-7"></a>TKT-7: Models and cost (balanced tier)

**Rule:** each agent's model and effort are set in its file and changed only here:

| Agent | Model | Effort | Why |
| --- | --- | --- | --- |
| planner, reviewer | opus | high | Errors here cost the most: a bad plan or a missed defect wastes whole waves |
| implementer, test-writer, frontend-implementer, integrator, ticket-writer, explainer | sonnet | medium | Most coding work, at a fraction of opus's cost; explaining the work and its trade-offs needs to read code, which haiku does poorly |
| rust-implementer | sonnet | high | Hot path with strict budgets |
| mockup-writer, doc-writer, scribe, verifier | haiku | low | Mechanical work: documents, screens, running checks |

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
python3 .claude/scripts/progress.py watch --every 120 --run <run id>
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
python3 .claude/scripts/progress.py timings --ticket <ID> --write
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

**Rule:** `/ticket-run <ID>` skips every task that `python3 .claude/scripts/ticket_tree.py status --ticket <ID>` lists
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
  `<!-- changes -->` markers by `python3 .claude/scripts/ticket_tree.py changes --ticket <ID> --write`, never by
  hand, and leaves out the ticket's own folder.
- **`IMPLEMENTATION.md`: why this way.** The constraints any solution had to respect, then one section per decision:
  the option chosen, its real alternatives, what speaks for and against each in this repository (a rule, a budget, an
  acceptance criterion, the existing code), the trade-off accepted and when to revisit it.
- The decisions come from the workers, who report each choice where a reasonable alternative existed (choice,
  alternatives, trade-off, file and line), from `PLAN.md`, and from the explainer's reading of the diff. The reviewer
  checks them with the assumptions. Nothing is invented: an unknown reason is written as an open point (TKT-8).

**Why:** the person reviews in under an hour ([R-01](../../docs/specs/roadmap/12-risks.md#r-01)) and the next
developer, person or agent, inherits the code: one needs to know where things are and how they work, the other why
they are this way and what changing them would cost.

**Check:** `python3 .claude/scripts/ticket_tree.py changes --ticket <ID> --check` prints nothing before the commit,
both files have every section of their template, and `grep -n 'tkt-14' .claude/rules/tickets.md` finds the summary row
and the heading.
