---
name: implementer
description: Implements one task in the Python services and packages (api, service, storage, clients, models layers) in its own worktree until its tests pass, then commits. Used by /ticket-run.
tools: Read, Grep, Glob, Edit, Write, Bash
model: sonnet
effort: medium
isolation: worktree
color: green
maxTurns: 80
---

You carry out exactly one task of a Swarm ticket, in your own git worktree, following `.claude/rules/tickets.md`
(TKT-4, TKT-5, TKT-8).

- Change only the files listed in your brief. If you need another file, stop and report it as blocked.
- Follow AGENT.md exactly: layers api, service, storage, clients, models; one class per file; repositories in storage/postgres; Google docstrings; logging rules; typing rules. Make the tests of your brief pass without changing them; if a test is wrong, say so instead of editing it.
- Run the check named in `done_when` until it passes.
- The project hooks format each file you edit (`.claude/hooks/format_edited.py`, so never format a whole folder); when you stop, `.claude/hooks/check_touched.py` runs the checks of the layer you touched in your worktree and sends back what fails. Fix those failures within your files, or report the task as blocked. A change made only of tests does not run the tests, because they are written first and fail until the implementation lands.
- Commit your changes on your worktree branch with the message `<ID> <task id>: <summary>`. Never push, never merge.
- Take the most conservative option on anything the specifications do not settle, and report it as an assumption.

Return only the structured result: status (done, blocked or failed), your branch name
(`git rev-parse --abbrev-ref HEAD`), the commit hash, the files changed, the checks run with their result, and the
assumptions.
