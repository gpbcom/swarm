# T0.20: Visual tests and UC-029 screenshots

**Status:** ✅ Done

## Roadmap

- **Ticket:** [T0.20](../../specs/roadmap/01-p0-foundations.md#s04) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S04](../../specs/roadmap/01-p0-foundations.md#s04), 15 to 26 Feb 2027: M0: Foundations ready
- **Epic:** [E0.7 Front-end foundation](../../specs/roadmap/01-p0-foundations.md#epics): Token generation; Radix components; frames of the four parts of Swarm; Tauri 2 shell; FormatJS messages and Babel catalogues; visual test pipeline

## What it delivers

- Playwright renders each screen with the sample data of the visual identity and compares it with the mock-up PNG in light and dark mode, and a large difference fails the build, as [🖥️ GUI and WebUI: design system](../../specs/technical/10-frontends.md#design-system).
- The four screens of UC-029 (A1, KO, A2, OK) captured as 📸 Screenshot and their mock-ups deleted, as [🎨 Visual identity: screens and screenshots](../../specs/visual-identity.md#screens).
- The work sits in `frontend/apps/back-office`, `tests/` and `docs/specs/screens/`.

## Features, use cases and business rules

- [🎬 UC-029: Create an Operator](../../specs/functional/use-cases/UC-029-create-an-operator.md)
- [📏 BR-008: Operator isolation](../../specs/functional/business-rules/BR-008-operator-isolation.md)

## Technical pages it builds on

- [🖥️ GUI and WebUI: design system](../../specs/technical/10-frontends.md#design-system): "Playwright renders each screen of the use cases with the specification's sample data and compares it with the mock-up PNG, in light and dark mode; a large difference fails the build. Once a screen matches, its row becomes 📸 Screenshot in the use case."
- [🧰 Deployment: CI/CD](../../specs/technical/09-deployment.md#ci): step 5 tests the images with Playwright against the real images started by `compose.e2e.yaml`, with visual comparison with the specification mock-ups.
- [🖼️ Visual identity: screens and screenshots](../../specs/visual-identity.md#screens): a screenshot is a capture of the real window at `screen.width` x `screen.height`, scale 1, once in light and once in dark mode; the sample data is the fixed cast.

## Screens touched

- [🖼️ UC-029 A1](../../specs/functional/use-cases/UC-029-create-an-operator.md#screen-a1): Enter the Operator.
- [🖼️ UC-029 KO](../../specs/functional/use-cases/UC-029-create-an-operator.md#screen-ko): Operator not created.
- [🖼️ UC-029 A2](../../specs/functional/use-cases/UC-029-create-an-operator.md#screen-a2): Invite the first Mission planner.
- [🖼️ UC-029 OK](../../specs/functional/use-cases/UC-029-create-an-operator.md#screen-ok): Operator created and isolated.

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

1. **Given** a screen of the Back office rendered by Playwright with the sample data, in light and in dark mode, **when** it differs from its mock-up PNG by more than the allowed difference, **then** the build fails. ([📏 BR-008](../../specs/functional/business-rules/BR-008-operator-isolation.md), [🎬 UC-029](../../specs/functional/use-cases/UC-029-create-an-operator.md))
2. **Given** the four screens A1, KO, A2 and OK of UC-029, **when** the ticket is done, **then** each is captured as 📸 Screenshot in light and dark mode at `screen.width` x `screen.height`, and its mock-up is deleted. ([📏 BR-008](../../specs/functional/business-rules/BR-008-operator-isolation.md), [🎬 UC-029](../../specs/functional/use-cases/UC-029-create-an-operator.md))
3. **Given** the UC-029 screenshots in place, **when** `specs.py check` runs, **then** it prints nothing. ([📏 BR-008](../../specs/functional/business-rules/BR-008-operator-isolation.md), [🎬 UC-029](../../specs/functional/use-cases/UC-029-create-an-operator.md))

## Out of scope

- Creating an Operator and the Back office screens themselves, see [T0.16](../../specs/roadmap/01-p0-foundations.md#s04).
- Screens of the other use cases, which move to 📸 Screenshot in the tickets that build them.

## Assumptions

- The roadmap names UC-029 but no business rule for this ticket, so BR-008, the rule UC-029 applies, is linked to give each criterion its rule.
- The roadmap row has no anchor of its own, so the ticket link points to the S04 sprint section.
- The allowed size of the "large difference" is not specified, so the ticket sets no figure; it is decided in the plan and recorded.
- The roadmap names no budget for this ticket, so none is listed.
