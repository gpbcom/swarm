---
name: issue-plan
description: Plan a GitHub issue with all its child issues, or a group of issues, of the Swarm roadmap in one go - every ticket under an epic or a phase issue, or several tickets - then stop for the person's single approval (TKT-20). Use when the person types /issue-plan with references such as #12 (a ticket, epic or phase issue), T0.10, E0.4, P1, or several of them, or asks to plan an epic, a phase or a set of issues.
---

# Plan an issue with its child issues, or a group of issues (TKT-20)

The arguments are references: `#12` (a ticket issue, or an epic or phase issue with every ticket under it), `T0.10`,
`E0.4`, `P1`, several separated by spaces.

1. Run `python3 .claude/scripts/tickets.py resolve <refs>` and show its output to the person in full: the tickets of
   the group in the order of their prerequisites, each with its state. A reference it refuses ends the skill: say why.
2. For every ticket of the group in state ⬜ **no plan**, call the **Workflow** tool with the saved workflow
   `ticket-plan` and the ticket ID as `args`, **all in the same message** so that they run at once. The person asked
   for this command, which allows the Workflow tool. Leave out the tickets that already have a plan.
3. Arm the **Monitor** tool (`timeout_ms` 1800000, re-armed at each expiry while a plan runs) with
   `python3 .claude/scripts/tickets.py watch <refs> --every 120`, and relay each report to the person in full, keeping
   its icons (TKT-9).
4. When every plan is written, stop the monitor and tell the person, in a few lines:
   - which `PLAN.md` files to read (`docs/tickets/<ID>/PLAN.md`) and any plan check that failed;
   - that one command approves them all: `python3 .claude/scripts/tickets.py approve <refs>`; it approves only the plans
     that pass `check_plan.py`, records it and moves the cards;
   - then `/issue-run <refs>` runs the group.

**Never run `tickets.py approve` on your own initiative, and never edit a `**Plan:**` line:** the approval is the
person's (TKT-3). If the person asks you to approve, run the command; the hook asks them to confirm.
