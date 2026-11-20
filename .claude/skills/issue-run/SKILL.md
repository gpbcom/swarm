---
name: issue-run
description: Run a GitHub issue with all its child issues, or a group of issues, of the Swarm roadmap - every approved ticket the start rule allows starts at once, each other one as soon as its prerequisites are done - with a report every 2 minutes, until the group is merged (TKT-16, TKT-20). Use when the person types /issue-run with references such as #12, T0.10, E0.4, P1, or asks to run an epic, a phase or a set of approved tickets.
---

# Run an issue with its child issues, or a group of issues (TKT-20)

The arguments are references: `#12` (a ticket issue, or an epic or phase issue with every ticket under it), `T0.10`,
`E0.4`, `P1`, several separated by spaces. Every ticket runs in the main checkout on `feature/tickets` (TKT-16).

1. Run `python3 .claude/scripts/tickets/tickets.py resolve <refs>` and show it in full. Sub-issues already done (merged on
   `develop`, or closed on GitHub) are left out, and `next` never returns a ticket that is running, in review or done:
   nothing is started twice. When it prints "nothing to do", say so and stop. Name the tickets that are not
   approved yet (⬜ no plan, 📝 plan awaits approval): they do not run; `/issue-plan <refs>` and
   `python3 .claude/scripts/tickets/tickets.py approve <refs>` come first.
2. Run `python3 .claude/scripts/tickets/tickets.py next <refs>`: one ticket ID per line, the approved tickets that may start
   now. Call the **Workflow** tool with the saved workflow `ticket-run` and each ID as `args`, **all in the same
   message**, so that they run at once. The person asked for this command, which allows the Workflow tool. Keep the
   list of tickets already started, and never start one twice.
3. Arm the **Monitor** tool (`timeout_ms` 1800000, re-armed at each expiry until the watch ends) with
   `python3 .claude/scripts/tickets/tickets.py watch <refs> --every 120`. Relay each report to the person in full, keeping its
   icons (TKT-9).
4. On each line `▶️ CAN START <ID>` of a report, for a ticket not started yet, call the Workflow tool with
   `ticket-run` and that ID. Each run stops for the person's code review (TKT-18): its card shows 🔍; when the person
   approves the push in its `PLAN.md`, run `ticket-run` for it again.
5. A run that stops (checks, review, environment) is reported to the person with its `next` step; the others go on.
6. The watch ends when the group is merged (🏁) or waits for the person (✋): give the last report, then what is left
   to do, and once everything is merged suggest `python3 .claude/scripts/tickets/tickets.py prune`.

Never pass `--force` unless the person asks for it, ticket by ticket.
