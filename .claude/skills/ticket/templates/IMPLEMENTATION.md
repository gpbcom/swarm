<!-- Implementation choices template (TKT-14). Written by the explainer when the ticket is done, before its single -->
<!-- commit, from the decisions the workers reported, the plan, the review note and the diff. -->
<!-- For the person and the next developer: why the code is built this way rather than another, and what it costs. -->
<!-- Every alternative is a real option for this ticket, named in the decisions, the specifications or the review; -->
<!-- never a straw man. A pro or con is a fact about this repository (a rule, a budget, a file), not a slogan. -->
<!-- EVERY file and line is a clickable relative link, never a bare path (TKT-14): -->
<!-- [`path/file.py:42`](../../../path/file.py#L42), [`path/file.py:42-50`](../../../path/file.py#L42-L50), -->
<!-- [`path/file.py`](../../../path/file.py). Check: python3 .claude/scripts/ticket_tree.py docs --ticket {{ID}} -->

# {{ID}}: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🎯 Constraints

<!-- What any solution had to respect, each with its source: acceptance criteria of TICKET.md, rules (AGENT.md, -->
<!-- SPEC, TKT), budgets of the technical pages, existing code it had to fit. These are what the choices trade on. -->

- {{Constraint}} ({{source link}}).

## ⚖️ Choices at a glance

<!-- One row per decision below, in the same order. -->

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | {{What had to be decided}} | {{Option chosen}} | {{Best rejected option}} | {{What the choice costs}} |

## <a id="d1"></a>D1: {{What had to be decided}}

**Chosen:** {{option}} · **Where:** [`{{path}}:{{line}}`](../../../{{path}}#L{{line}}) · **Source:** {{task id, plan, reviewer, or read from the diff}}

| Option | For | Against |
| --- | --- | --- |
| ✅ {{Chosen option}} | {{Facts in its favour}} | {{What it costs}} |
| {{Alternative}} | {{Facts in its favour}} | {{Why it lost here}} |

**Trade-off:** {{what was given up, and why it is the right price for this ticket}}.

**Revisit when:** {{the condition under which an alternative would win: a budget, a scale, a later ticket}}.

<!-- Repeat one section per decision: D2, D3... Order them by impact, the decision that would cost most to undo first. -->

## 📝 Assumptions behind the choices

<!-- The assumptions accepted by the reviewer (TKT-8) that a choice above relies on, with the decision it supports. -->
<!-- Write "None." when there are none. -->

- {{Assumption}}: supports [D{{n}}](#d{{n}}).
