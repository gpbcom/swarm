# 🤖 Agent harness interview

**Date:** 2026-11-18. **Interviewee:** the product owner. Source of `.claude/agents/`, `.claude/workflows/` and
`.claude/rules/tickets.md`.

| # | Topic | Decision |
| --- | --- | --- |
| H1 | Purpose | A graph harness: each roadmap ticket is split into tasks run by agents in parallel, as much as possible |
| H2 | Tier | Balanced: planner and reviewer on opus (high effort), workers on sonnet (medium, Rust high), mechanical work on haiku (low); at most 8 agents at once |
| H3 | Orchestration | Workflow scripts: `/ticket-plan` and `/ticket-run` |
| H4 | Ticket folder | XSA-like, lighter: TICKET, PLAN, PROGRESS, EXPLAIN, tests-evidences |
| H5 | Human gate | The person approves the plan; everything after runs without supervision, up to a local merge into `develop`; nothing is pushed |
| H6 | Worktrees | Every worker in its own worktree branched from the ticket branch (`worktree.baseRef: head`); the integrator merges after each wave |
