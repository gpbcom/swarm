# T0.14: Design tokens, components and app shells

**Status:** ✅ Done

## Roadmap

- **Ticket:** [T0.14](../../specs/roadmap/01-p0-foundations.md#s03) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S03](../../specs/roadmap/01-p0-foundations.md#s03), 1 to 12 Feb 2027: A person signs in; a service answers for one Operator only; simulated Drones fly
- **Epic:** [E0.7 Front-end foundation](../../specs/roadmap/01-p0-foundations.md#epics): token generation, Radix components, the frames of the four parts of Swarm, the Tauri 2 shell, FormatJS messages and the visual test pipeline

## What it delivers

- `packages/ts/tokens`, generated from the visual identity by the same pipeline as `visual-identity.css`, with light and dark values, as [🎨 Design system](../../specs/technical/10-frontends.md#design-system).
- `packages/ts/ui` on Radix primitives, with the components of the component sheet, styled only with the tokens, as [🎨 Design system](../../specs/technical/10-frontends.md#design-system).
- The frame of each part of Swarm (title bar, side bar, status bar) as layout components, as [🎨 Visual identity: components](../../specs/visual-identity.md#components).
- Empty shells of `ground-control`, `mission-studio`, `back-office` and `client-portal`, as [🗂️ Apps and shared packages](../../specs/technical/10-frontends.md#apps).
- The Tauri 2 desktop shell building on Windows, macOS and Linux, as [🖥️ Desktop shell and inputs](../../specs/technical/10-frontends.md#desktop).

## Features, use cases and business rules

- [📏 BR-017: Every screen in four languages](../../specs/functional/business-rules/BR-017-every-screen-in-four-languages.md): the rule of epic E0.7, which the roadmap names for the epic; the languages themselves are delivered by T0.15.

## Technical pages it builds on

- [🗂️ Apps and shared packages](../../specs/technical/10-frontends.md#apps): the four apps under `frontends/`, the `desktop` shell, and `ui` and `tokens` under `packages/ts/` ("Components on Radix primitives, styled only with the design tokens"; "CSS variables generated from the visual identity").
- [🖥️ Desktop shell and inputs](../../specs/technical/10-frontends.md#desktop): "Tauri 2 wraps Ground control and Mission studio".
- [🎨 Design system](../../specs/technical/10-frontends.md#design-system): tokens generated into `packages/ts/tokens` by the pipeline that writes `visual-identity.css`; components use the tokens only; the frames are layout components.
- [🎨 Visual identity: colours](../../specs/visual-identity.md#colours): the tokens, each with a light and a dark value.
- [🎨 Visual identity: components](../../specs/visual-identity.md#components): the component sheet and the frame of each part of Swarm.

## Screens touched

- ➖ No screen: the four shells are empty frames, and no use case screen is shown by this ticket.

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

1. **Given** a token changed on the visual identity page, **when** one build runs, **then** the apps and the mock-ups show the change.
2. **Given** the four shells `ground-control`, `mission-studio`, `back-office` and `client-portal`, **when** each is opened in light mode and in dark mode, **then** each opens.
3. **Given** the Tauri 2 desktop shell, **when** it is built on Windows, macOS and Linux, **then** it builds on each.

## Out of scope

- The four languages and the language switch, see [T0.15](../../specs/roadmap/01-p0-foundations.md#s03).
- The visual tests and the screenshots of UC-029, see [T0.20](../../specs/roadmap/01-p0-foundations.md#s04).
- The first Ground control map screen, see [T0.19](../../specs/roadmap/01-p0-foundations.md#s04).

## Assumptions

- The roadmap row names no feature or use case, so none is linked. BR-017 is linked because the epic row names it, and no criterion cites it since language support belongs to T0.15.
- The roadmap row has no anchor of its own, so the ticket link points to the sprint anchor `#s03`.
- The ticket shows no use case screen, because the shells are empty, so it says "No screen".
