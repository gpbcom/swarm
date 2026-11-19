<!-- Ticket template (TKT-2). Replace every {{NAME}} and delete these comments in the written ticket. -->
<!-- The ticket states only what the specifications and the roadmap state. Check it with check_ticket.py. -->

# {{ID}}: {{Title}}

**Status:** 🟡 Planned

## Roadmap

<!-- The phase page and the ticket anchor come from the roadmap row. -->

- **Ticket:** [{{ID}}](../../specs/roadmap/{{phase page}}#{{anchor}}) in [🛣️ {{Phase}}](../../specs/roadmap/{{phase page}})
- **Phase:** [🛣️ {{Phase}}](../../specs/roadmap/{{phase page}})
- **Sprint:** [{{Sprint}}](../../specs/roadmap/{{phase page}}#{{sprint anchor}}), {{dates}}: {{sprint goal}}
- **Epic:** [{{Epic}}](../../specs/roadmap/{{phase page}}#{{epic anchor}}): {{what the epic delivers}}

## What it delivers

<!-- Bullets, each one thing the ticket delivers, with a link to the technical page it follows. -->

- {{What is delivered}}, as [{{Technical page}}](../../specs/technical/{{page}}.md#{{anchor}}).

## Features, use cases and business rules

<!-- Example pattern, not a real ID: [📘 FS-{{nnn}}: {{Title}}](../../specs/functional/features/FS-{{nnn}}-{{slug}}.md) -->
<!-- Likewise for [🎬 UC-{{nnn}}: {{Title}}](../../specs/functional/use-cases/UC-{{nnn}}-{{slug}}.md) and [📏 BR-{{nnn}}: {{Title}}](../../specs/functional/business-rules/BR-{{nnn}}-{{slug}}.md). -->
<!-- When the roadmap names none, write the line below and nothing else. -->

- {{The roadmap names no feature, use case or business rule for this ticket.}}

## Technical pages it builds on

- [🏗️ {{Technical page title}}](../../specs/technical/{{page}}.md#{{anchor}}): {{what the ticket takes from it}}.

## Screens touched

<!-- Link to a screen PNG, or to a use case screen row, or write the line saying the ticket touches no screen. -->

- [🖼️ {{UC-ID}} {{node}}](../../specs/screens/{{UC-ID}}/{{node}}.png), or [🖼️ {{UC-ID}} {{node}}](../../specs/functional/use-cases/{{UC-ID}}-{{slug}}.md#screen-{{node}}).
- {{The ticket touches no screen.}}

## Budgets touched

<!-- Link to the budget rows of the scalability page, or write the line saying none. -->

- [⏱️ {{Budget}}](../../specs/technical/07-scalability.md#budgets): {{the budget row this ticket must keep}}.
- {{The ticket touches no budget.}}

## Acceptance criteria

<!-- One numbered item per criterion. Each names the business rule and the use case it verifies. -->
<!-- Format: **Given** {{context}}, **when** {{action}}, **then** {{result}}. (BR-{{nnn}}, UC-{{nnn}}) -->

1. **Given** {{context}}, **when** {{action}}, **then** {{result}}. ([📏 BR-{{nnn}}](../../specs/functional/business-rules/BR-{{nnn}}-{{slug}}.md), [🎬 UC-{{nnn}}](../../specs/functional/use-cases/UC-{{nnn}}-{{slug}}.md))

## Out of scope

<!-- Bullets, each one linked to the ticket or page that takes it. -->

- {{What is not delivered here}}, see [{{ticket}}](../../specs/roadmap/{{phase page}}#{{anchor}}).

## Assumptions

<!-- Facts the specifications do not settle. Each one is an assumption the reviewer checks (TKT-8). -->

- {{The most conservative option taken, and why}}.
