---
name: board
description: Show the Swarm roadmap board (GitHub project "Swarm roadmap") and the open tickets, from the terminal - what is Ready to start, Planned, Running, In review and Done, per phase, with every ticket's worktree and pull request (TKT-16, TKT-17). Use when the person asks what runs, what to start next, where a ticket stands, or types /board.
---

# Board

Show the board and the open tickets, then say in one or two lines what the person can do next.

1. Run `python3 .claude/scripts/github/board.py sync`, which recomputes every column from the repository and GitHub (skip it
   and say so if `gh` is missing or offline), then `python3 .claude/scripts/github/board.py show`.
2. Run `python3 .claude/scripts/tickets/tickets.py list --remote` for the open tickets, their worktree and pull request.
3. Relay both outputs in full, keeping the icons, in a code block.
4. Then, in at most three lines:
   - the ✅ Ready tickets that `python3 .claude/scripts/tickets/tickets.py check --ticket <ID>` accepts now (area locks
     included), the first ones on the critical path (label `critical-path`) first: those can be started with
     `/ticket-plan <ID>`;
   - the tickets 👀 In review whose checks failed, with their pull request;
   - the merged tickets whose worktree is still there: `python3 .claude/scripts/tickets/tickets.py prune` removes them.

Never move a card or change a ticket from this skill: the workflows do it (TKT-17).
