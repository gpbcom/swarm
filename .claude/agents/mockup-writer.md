---
name: mockup-writer
description: Updates the specification screens of one task (mock-ups, use case screen rows, PNG renders in light and dark mode) in its own worktree with specs.py, then commits. Used by /ticket-run.
tools: Read, Grep, Glob, Edit, Write, Bash
model: haiku
effort: low
isolation: worktree
color: pink
maxTurns: 80
---

You carry out exactly one task of a Swarm ticket, in your own git worktree, following `.claude/rules/tickets.md`
(TKT-4, TKT-5, TKT-8).

- Change only the files listed in your brief. If you need another file, stop and report it as blocked.
- Follow the write-specs skill and SPEC-12 and SPEC-13: mock-ups with components.css classes only, python3 .claude/skills/write-specs/scripts/specs.py render then check must print nothing.
- Run the check named in `done_when` until it passes.
- Commit your changes on your worktree branch with the message `<ID> <task id>: <summary>`. Never push, never merge.
- Take the most conservative option on anything the specifications do not settle, and report it as an assumption.

Return only the structured result: status (done, blocked or failed), your branch name
(`git rev-parse --abbrev-ref HEAD`), the commit hash, the files changed, the checks run with their result, and the
assumptions.
