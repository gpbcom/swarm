# T0.02: Explanation

**Status:** ✅ Done · **Ticket:** [TICKET.md](TICKET.md) · **Review:** [REVIEW.md](REVIEW.md)

## What changed for users

The people who work on Swarm now have a working method for roadmap tickets, versioned in `.claude/`:

- `/ticket-plan <ID>` writes `TICKET.md` and a task graph in `PLAN.md`, checks both, then stops for approval.
- `/ticket-run <ID>` refuses any plan that is not approved, runs the tasks in parallel git worktrees, merges them into `ticket/<ID>`, verifies and reviews the result, and merges it into `develop` locally. Nothing is pushed.
- Each ticket folder under `docs/tickets/<ID>/` holds `TICKET.md`, `PLAN.md`, `PROGRESS.md`, `EXPLAIN.md`, `REVIEW.md` and `tests-evidences/`.

The person's only gate is the plan approval. The review note is short, so that one review per ticket stays under an hour (acceptance criterion 3, judged by the person).

## What changed in the code

- **Ticket template and skill:** `.claude/skills/ticket/` holds `SKILL.md`, the templates of `TICKET.md` and `REVIEW.md`, and two checkers. `check_ticket.py` checks a TICKET.md against the template and `docs/specs/`. `check_plan.py` checks a PLAN.md graph, including TKT-3 and TKT-4 and the optional `--min-parallel` flag.
- **Workflows:** `.claude/workflows/ticket-plan.js` checks TICKET.md, sends it back to the ticket-writer once, then checks PLAN.md. `.claude/workflows/ticket-run.js` runs `check_plan.py` at the gate, after the approval check. Each worker reads its approved brief with `plan.py task`.
- **Hooks** in `.claude/settings.json`:
  - PostToolUse runs `.claude/hooks/format_edited.py`, which formats only the edited file, using `.claude/hooks/formatters.json`.
  - SubagentStop runs `.claude/hooks/check_touched.py`, which runs the checks of the touched layer in a worker's worktree, using `.claude/hooks/layer-checks.json`. It sends a failing task back at most twice, skips tests on test-only changes, and treats a missing tool as a note, not a failure (TKT-13).
- **Rules and agents:** `.claude/rules/tickets.md` gains TKT-13 and the reviewer's note is written to `REVIEW.md` (TKT-1 and TKT-6). `.claude/agents/` gets one line per worker about the hooks, and the ticket-writer and verifier are updated.
- **Scripts:** `.claude/scripts/tickets/plan.py` gains the `outline` and `task` commands.
- **Tests:** `tests/harness/` covers the checkers, the hooks and the wiring of the agents and workflows.
- **Ticket folder:** `docs/tickets/README.md` describes the three steps and links the template.

## How to test it

From the repository root:

```bash
uv run pytest tests/harness -n 2
uv run ruff check tests .claude
uv run ruff format --check <the files you edited>
python3 .claude/skills/ticket/scripts/check_plan.py docs/tickets/T0.02/PLAN.md
python3 .claude/skills/write-specs/scripts/specs.py check
```

The usage of each script follows its docstring. `progress.py` and `checks.py` are described from their docstrings and were not run for this document.

To test the whole flow, run `/ticket-plan` on a sample ticket, approve the plan by setting `**Plan:** 🟢 Approved`, then run `/ticket-run`. A full run with the hooks active is planned on T0.03.

## Evidence

- [pytest](tests-evidences/pytest.txt): 187 passed.
- [ruff check](tests-evidences/ruff-check.txt), [ruff format](tests-evidences/ruff-format.txt), [mypy](tests-evidences/mypy.txt).
- [specs check](tests-evidences/specs-check.txt) and [ticket refs](tests-evidences/ticket-refs.txt).
- [Plan view](tests-evidences/plan-view.txt): the rendered waves of the approved plan.
- [Progress events and timings](PROGRESS.md).

## Assumptions accepted by the reviewer

- K07, the `check_ticket.py` rules: comments are stripped before headings, links, IDs and criteria are checked, and the placeholder and em dash check reads the whole file. Links to a Ticket must target a page under `docs/specs/roadmap/` that contains the ticket ID, and their anchors are checked. Links to specification pages are detected by an FS-, UC- or BR- file name under `functional/`, and their text must show the ID. Anchors are checked only in Markdown targets, from `id="..."` attributes. A Screens link targets `docs/specs/screens/` or a `#screen-` row of a use case. A Budgets link targets exactly `07-scalability.md#budgets`. These match TKT-2, SPEC-3, SPEC-9 and SPEC-12.
- K07, `T0.02`'s TICKET.md predates the template, so it was neither checked nor changed, as the approved plan says.
- K18, `/ticket-plan` and `/ticket-run` are described through the workflows in `.claude/workflows/`. The usage lines follow the script docstrings, with `--min-parallel` optional and defaulting to 1, which matches `check_plan.py`.
- K18, the output of `progress.py` and `checks.py` is described from their docstrings, which is acceptable for documentation.
- K19, the SKILL.md link was dropped from `docs/tickets/README.md` while the file was not on the branch, and only the template link was kept. A follow-up re-adds it.
- K19, the change was re-applied by hand to the same section, so the diff stays within `docs/tickets/README.md`.
- K19, the commit message follows the brief and carries the attribution line.
- K18, "the PLAN.md json block does not parse": not accepted as fact. The block parses (19 tasks), and the claim had no effect on the delivered work.

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| `.claude/workflows/ticket-run.js:239` (`ownerOf`) with `workerPrompt` at `:119-127` | Since commit 3a63742, a fix task that matches no plan task (id `FIX-<file>`, brief `''`) is told to run `plan.py task --id FIX-<file>`. That command can only print `Unknown task`, and the fixer never sees its `done_when`. Test the id against `K\d{2}` instead of testing for an empty brief, or give FIX tasks a non-empty brief so they keep the old `Brief` / `Done when` lines. |
| `.claude/skills/ticket/SKILL.md` (Plan section) | SKILL.md says TICKET.md is "fixed at most twice". TKT-2 and `ticket-plan.js` send it back to the ticket-writer once and then stop. Change it to "once". |
| `.claude/skills/ticket/SKILL.md` (intro and Hooks section) | The intro cites "TKT-1 to TKT-12". Make it TKT-1 to TKT-13. Also, "The hooks do nothing outside a linked worktree" is only true of `check_touched.py`: `format_edited.py` formats matching files in any checkout. Say that the SubagentStop hook is the one limited to worktrees. |
| `docs/tickets/README.md` (line after the steps table) | SKILL.md is now on `ticket/T0.02`. Re-add the link to `.claude/skills/ticket/SKILL.md` that K19 dropped while it did not exist yet. |
| `.claude/workflows/ticket-plan.js` (Check phase) | The ticket-writer's fix result is not kept, so `ticket.specs` and `ticket.assumptions` returned at the end still come from the first, failing TICKET.md. Assign the fix result to `ticket` when it is present. |
