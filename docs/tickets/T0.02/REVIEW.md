# T0.02: Review note

**Verdict:** ✅ Approved · **Branch:** `ticket/T0.02`

## What changed

- A ticket template (Phase, Screens touched, Budgets touched, Given/when/then) and a review note template, in the new `ticket` skill. `check_ticket.py` checks a TICKET.md against the template and `docs/specs/`, and `check_plan.py` checks a PLAN.md graph (TKT-3, TKT-4, `--min-parallel`).
- `/ticket-plan` checks TICKET.md, sends it back to the ticket-writer once, then checks PLAN.md. `/ticket-run` runs `check_plan.py` at the gate, after the approval check.
- Two hooks in `.claude/settings.json`. PostToolUse formats only the edited file (`formatters.json`). SubagentStop runs the checks of the touched layer in a worker's worktree (`layer-checks.json`). It sends a failing task back at most twice, skips tests on test-only changes, and treats a missing tool as a note, not a failure (new TKT-13).
- The reviewer returns a `note`, and the scribe writes it unchanged to `REVIEW.md` (TKT-1 and TKT-6 updated). Each worker agent carries one line about the hooks.
- Harness fix made by the person mid-run: the gate returns `plan.py outline`, and each worker reads its approved brief with `plan.py task`.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. **Given** a sample ticket, **when** it runs end to end through the harness, **then** it is split into at least three parallel tasks and merged into one branch | T0.02's own run: wave 1 ran 7 tasks in parallel, merged into `ticket/T0.02` (PROGRESS.md Events). `test_the_approved_plan_of_t0_01_passes_silently` and `test_the_sample_plan_passes_with_three_parallel_tasks_required` (`--min-parallel 3`). | ✅ Pass. A full run with the hooks active is planned on T0.03 (approved plan assumption). |
| 2. **Given** the merged branch, **when** the run ends, **then** a review note is written and the checks are green | `tests-evidences/pytest.txt` (187 passed), `ruff-check.txt`, `ruff-format.txt`, `mypy.txt`, `specs-check.txt`, `ticket-refs.txt`, `plan-view.txt`. This note becomes REVIEW.md. | ✅ Pass |
| 3. **Given** the review note and the merged branch, **when** the person reviews them, **then** the review takes under an hour | This note | The person judges |

## Look at first

- **SubagentStop hook:** the worktree detection (git dir differs from the common dir), the base from `ticket/<ID>` or `develop`, the block counter in the worktree's git dir, and exit 2 only up to `max_blocks`. Commands are argv lists, never a shell. Files: `.claude/hooks/check_touched.py`, `.claude/hooks/layer-checks.json`.
- **PostToolUse hook:** formats only `services/`, `packages/` and `tests/` Python, Rust under `packages/rust/`, and Terraform. It never touches `.claude/` or `docs/`, and it runs in every checkout, not only in worktrees. Files: `.claude/hooks/format_edited.py`, `.claude/hooks/formatters.json`.
- **Brief handover:** a fix task that matches no plan task (`FIX-<file>`) is now told to read a brief that does not exist (follow-up). File: `.claude/workflows/ticket-run.js` (`workerPrompt`, `ownerOf`).
- **Gate:** the plan check stops the run, and a failing TICKET.md stops `/ticket-plan` after one fix. Files: `.claude/workflows/ticket-run.js`, `.claude/workflows/ticket-plan.js`.
- Identity, Operator isolation and Simulator isolation are not touched. No secret is in code or logs.

## Assumptions accepted

- K07, the check_ticket.py rules (comments stripped, Ticket link under the roadmap, ID shown in link text, anchors from `id=`, the Screens and Budgets targets): accepted, consistent with TKT-2, SPEC-3, SPEC-9 and SPEC-12.
- K07, T0.02's TICKET.md predates the template: accepted, as the approved plan says.
- K18, the commands documented as the workflows, usage taken from the docstrings, progress.py and checks.py described without running them: accepted.
- K18, "the PLAN.md json block does not parse": not accepted as fact. The block parses (19 tasks), and the claim had no effect on the delivered work.
- K19, the SKILL.md link dropped and the change re-applied by hand: accepted. The link is re-added as a follow-up.

## Follow-ups

- `ticket-run.js`: give orphan `FIX-` tasks their old Brief and Done when lines instead of `plan.py task`.
- `SKILL.md`: "fixed at most twice" should be "once". "TKT-1 to TKT-12" should be "TKT-1 to TKT-13". Only the SubagentStop hook is limited to worktrees.
- `docs/tickets/README.md`: re-add the link to `.claude/skills/ticket/SKILL.md`.
- `ticket-plan.js`: keep the ticket-writer's fix result, so the returned `specs` and assumptions are current.
