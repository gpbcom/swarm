# CLAUDE.md

@AGENT.md

## The harness

This repository is a proof of concept for mastering the Claude Code harness; drone swarm piloting is the pretext (see
`README.md`). Its harness is versioned with the code, in `.claude/`.

- **Specifications:** `docs/specs/`, written with the `write-specs` skill under the SPEC rules
  (`.claude/rules/specs.md`, loaded by the `specs-rules` skill). Glossary first, then business rules, use cases, and
  features; every use case has an in-page Mermaid flow chart and a screen in light and dark mode for every state.
- **Generated content** (summaries, navigation, page list, matrix, back links, flow chart colours,
  `visual-identity.css`, the PNG screens) is written by `python3 .claude/skills/write-specs/scripts/specs.py build` and
  `render`, never by hand.
- **Done means checked:** `python3 .claude/skills/write-specs/scripts/specs.py check` prints nothing before any work on
  the specifications is reported as done.
- **Research and decisions:** `docs/research/landscape.md` (what exists) and `docs/research/interview.md` (what the
  product owner decided). A specification never states a fact that is not in one of them or given by the product owner.
- **Tickets:** the tickets of the roadmap (`docs/specs/roadmap/`) are worked by an agent graph, under the TKT rules
  (`.claude/rules/tickets.md`). `/ticket-plan <ID>` writes `docs/tickets/<ID>/TICKET.md` and a task graph in
  `PLAN.md`, then stops; the person approves the plan (`**Plan:** 🟢 Approved`); `/ticket-run <ID>` runs the waves in
  parallel worktrees, integrates, verifies, reviews and merges into `develop` locally.
- **Agents:** `.claude/agents/` (planner and reviewer on opus, workers on sonnet, mechanical work on haiku, TKT-7);
  workflows in `.claude/workflows/`.
- **Progress every 2 minutes** (TKT-9): when a ticket workflow starts, arm the Monitor tool with
  `python3 .claude/scripts/progress.py watch --every 120 --run <run id>` and relay each exhaustive report to the
  person in full, with its colour icons (phases, every agent with model, duration, tokens and result, tokens by model).
- **Commits:** the ticket harness commits on worktree and ticket branches and merges into `develop` locally. Nothing
  is ever pushed, and no commit is made outside the harness unless the person asks.
