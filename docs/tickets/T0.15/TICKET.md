# T0.15: Four languages

**Status:** ✅ Done

## Roadmap

- **Ticket:** [T0.15](../../specs/roadmap/01-p0-foundations.md#s03) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S03](../../specs/roadmap/01-p0-foundations.md#s03), 1 to 12 February 2027: A person signs in; a service answers for one Operator only; simulated Drones fly
- **Epic:** [E0.7: Front-end foundation](../../specs/roadmap/01-p0-foundations.md#epics): token generation, Radix components, frames of the four parts of Swarm, Tauri 2 shell, FormatJS messages and Babel catalogues, visual test pipeline

## What it delivers

- `packages/ts/i18n` with FormatJS messages in English, French, German and Spanish, as [🖥️ GUI and WebUI: apps and shared packages](../../specs/technical/10-frontends.md#apps).
- Babel catalogues for Python messages, in `packages/python/`, translated in the person's language as in [🔩 Engine and services](../../specs/technical/04-engine.md).
- The language of each person stored with the person and applied at sign-in.
- A CI check, in `.github/workflows/`, that fails when a message lacks one of the four languages.
- The shells switching language without reloading.

## Features, use cases and business rules

- [📏 BR-017: Every screen in four languages](../../specs/functional/business-rules/BR-017-every-screen-in-four-languages.md)
- [📘 FS-012: Operators, deployment and languages](../../specs/functional/features/FS-012-operators-deployment-and-languages.md): every person chooses their language (AC-2).

## Technical pages it builds on

- [🖥️ GUI and WebUI: apps and shared packages](../../specs/technical/10-frontends.md#apps): the `i18n` package holds "FormatJS messages in English, French, German and Spanish".
- [🔩 Engine and services](../../specs/technical/04-engine.md): "texts translated with Babel in the person's language".
- [🏗️ Architecture](../../specs/technical/01-architecture.md): `packages/ts/` holds the shared TypeScript packages, `i18n` among them.

## Screens touched

- ➖ No screen: the four shells are the empty frames of T0.14 and show no use case state; the ticket only takes their side bar items, Hold, Abort and the status bar language from the messages in four languages.

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

1. **Given** a message added in English only, **when** CI runs, **then** it fails because the message lacks one of the four languages. ([📏 BR-017](../../specs/functional/business-rules/BR-017-every-screen-in-four-languages.md), [🎬 UC-023](../../specs/functional/use-cases/UC-023-configure-the-workspace-of-ground-control.md))
2. **Given** the shells are open, **when** the language is changed, **then** they switch language without reloading. ([📏 BR-017](../../specs/functional/business-rules/BR-017-every-screen-in-four-languages.md), [🎬 UC-023](../../specs/functional/use-cases/UC-023-configure-the-workspace-of-ground-control.md))
3. **Given** an invited Client who chose German, **when** they open the Client portal, **then** every screen is in German. ([📏 BR-017](../../specs/functional/business-rules/BR-017-every-screen-in-four-languages.md), [🎬 UC-015](../../specs/functional/use-cases/UC-015-invite-a-client-to-the-client-portal.md))

## Out of scope

- The screens that use the messages, see [E0.7](../../specs/roadmap/01-p0-foundations.md#epics) and the later phases.

## Assumptions

- No screen is linked, because the roadmap row names no use case; the shells' language switching is checked without a captured screen.
- Criterion 3 comes from FS-012 AC-2; its full check needs the Client portal, so here only the stored language and its application at sign-in are verified.
- The ticket anchor is the sprint anchor `#s03`, as the roadmap has no anchor per ticket.
