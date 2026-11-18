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
| [TKT-5](#tkt-5) | Every worker runs in its own worktree and commits there; only the integrator merges; nothing is pushed |
| [TKT-6](#tkt-6) | A ticket is done when checks, review and documents are complete |
| [TKT-7](#tkt-7) | Each agent has a fixed model and effort, chosen for cost and quality |
| [TKT-8](#tkt-8) | Agents never invent facts; assumptions are recorded and reviewed |
| [TKT-9](#tkt-9) | The person gets a progress update every 2 minutes while a ticket workflow runs |
| [TKT-10](#tkt-10) | `PROGRESS.md` records the elapsed time of every step and of the whole ticket, and the tokens consumed |
| [TKT-11](#tkt-11) | Running a ticket again continues where it stopped |
| [TKT-12](#tkt-12) | The review converges: only blocking findings are fixed, later rounds only confirm the fixes |

## <a id="tkt-1"></a>TKT-1: Roadmap tickets, one folder each

**Rule:** the ID is the roadmap ticket ID (`T1.07`). The folder `docs/tickets/T1.07/` holds:

| File | Holds | Written by |
| --- | --- | --- |
| `TICKET.md` | What to deliver, links, acceptance criteria | ticket-writer |
| `PLAN.md` | The task graph, its waves, the approval status | planner (content), scribe (file) |
| `PROGRESS.md` | 📝 Events (decisions, merges, verdicts, stops) with their time, and ⏱️ Timings with the tokens consumed (TKT-10) | scribe, progress script |
| `EXPLAIN.md` | What changed, why, and how to test it | scribe |
| `tests-evidences/` | Outputs of the checks, test reports, screenshots | verifier, scribe |

**Why:** one place per ticket for the person and every agent, traceable to the roadmap.

**Check:** the folder exists with these files before a ticket is called done.

## <a id="tkt-2"></a>TKT-2: TICKET.md

**Rule:** `TICKET.md` has, in order: title and status; roadmap link (phase page and ticket anchor), sprint, epic;
the features, use cases and business rules it delivers (links with IDs); the technical pages it builds on;
acceptance criteria (the ticket's "done when" plus the features' Given/when/then criteria it closes); out of scope.
It states nothing that the specifications or the roadmap do not state.

**Why:** the plan and the review are only as good as the ticket they start from.

**Check:** the reviewer compares the delivered work with `TICKET.md`.

## <a id="tkt-3"></a>TKT-3: The plan and its approval

**Rule:** `PLAN.md` starts with `**Plan:** 🟡 Awaiting approval`. It holds the task graph twice: a table for the
person, and a ` ```json ` block that the workflow reads. Each task has: `id` (`K01`...), `title`, `agent` (an agent of
`.claude/agents/`), `depends_on`, `files` (the files it alone may change), `brief`, `done_when`. The waves are computed
from `depends_on`. **The person approves by changing the line to `**Plan:** 🟢 Approved`**; `/ticket-run` refuses any
other status.

**Why:** the person's single gate is the plan: once approved, the graph runs to the end without supervision.

**Check:** `/ticket-run` reads the status first and stops when it is not approved.

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

## <a id="tkt-5"></a>TKT-5: Worktrees, commits and merges

**Rule:**

- The ticket branch is `ticket/<ID>`, created from `develop` by `/ticket-run`.
- Every worker runs in its own git worktree, branched from the ticket branch, changes only its task's files, and
  commits there with the message `<ID> <task id>: <summary>`.
- After each wave, the **integrator** merges the wave's branches into `ticket/<ID>` in task order and resolves
  conflicts; the next wave starts from the result.
- When the ticket is done (TKT-6), the integrator merges `ticket/<ID>` into `develop` locally.
- **Nothing is ever pushed** by the harness.

**Why:** parallel agents must never edit the same checkout; merges in one place keep history readable.

**Check:** `git log ticket/<ID>` shows one commit per task and one merge per wave.

## <a id="tkt-6"></a>TKT-6: Done

**Rule:** a ticket is done when:

1. the **verifier** reports every applicable check passing, as decided and run by `.claude/scripts/checks.py`
   (deterministic, not a model's judgement): the AGENT.md tools on changed project code (ruff, mypy, pytest, cargo,
   pnpm, Terraform) and `specs.py check`; a check whose target does not exist yet is not applicable, never failed;
2. the **reviewer** approves the diff against `TICKET.md`, the specifications and the rules (AGENT.md, SPEC, TKT);
3. `EXPLAIN.md` and `PROGRESS.md` are written, with the evidence in `tests-evidences/`.

A failed check or a requested change goes back to the agent that owns the files, at most twice; then the ticket
stops and the person is told.

**Why:** "done" must mean merged code that works and that someone else can understand.

**Check:** `/ticket-run` ends with the verifier's and the reviewer's verdicts in `PROGRESS.md`.

## <a id="tkt-7"></a>TKT-7: Models and cost (balanced tier)

**Rule:** each agent's model and effort are set in its file and changed only here:

| Agent | Model | Effort | Why |
| --- | --- | --- | --- |
| planner, reviewer | opus | high | Errors here cost the most: a bad plan or a missed defect wastes whole waves |
| implementer, test-writer, frontend-implementer, integrator, ticket-writer | sonnet | medium | Most coding work, at a fraction of opus's cost |
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

**Rule:** `/ticket-run <ID>` skips every task whose commit (`<ID> <task id>:`) is already on `ticket/<ID>`, and starts
from the first wave with work left. A change to an approved plan (a task's brief or check) is approved by the person
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

