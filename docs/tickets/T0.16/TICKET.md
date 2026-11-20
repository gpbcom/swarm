# T0.16: Create an Operator (UC-029)

**Status:** 🟡 Planned

## Roadmap

- **Ticket:** [T0.16](../../specs/roadmap/01-p0-foundations.md#s04) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S04](../../specs/roadmap/01-p0-foundations.md#s04), 15 to 26 Feb 2027: first use case and M0 (M0: Foundations ready)
- **Epic:** [E0.5 Identity and Operators](../../specs/roadmap/01-p0-foundations.md#epics): UC-029, BR-008 and FS-012 AC-3, on Keycloak (global layer), `services/gateway`, `services/missions`, `services/fleet` (skeletons) and `frontends/back-office`

## What it delivers

- UC-029 in the Back office: ➕ Create an Operator with its name, deployment, Jurisdictions, LLM provider and Anchoring with their defaults, in `frontends/back-office`, as [🖥️ GUI and WebUI: apps and shared packages](../../specs/technical/10-frontends.md#apps).
- The checks of step 3: name taken (A1) and required field missing (A2), refused as specified, in `services/gateway`, as [🔌 API layer: REST](../../specs/technical/05-api.md#rest).
- The Operator directory and its cell assignment, in the global layer, as [🏗️ Architecture: cells and the global layer](../../specs/technical/01-architecture.md#cells).
- The invitation of the first Mission planner by e-mail and her first sign-in, with Keycloak, as [🔐 Security: identity](../../specs/technical/06-security.md#identity).

## Features, use cases and business rules

- [📘 FS-012: Operators, deployment and languages](../../specs/functional/features/FS-012-operators-deployment-and-languages.md): AC-3 closed by this ticket.
- [🎬 UC-029: Create an Operator](../../specs/functional/use-cases/UC-029-create-an-operator.md): every step, with alternative flows A1 and A2. A3 (on premises) is installed in P7.
- [📏 BR-008: Operator isolation](../../specs/functional/business-rules/BR-008-operator-isolation.md): the new Operator's data is visible to its own people only.

## Technical pages it builds on

- [🖥️ GUI and WebUI: apps and shared packages](../../specs/technical/10-frontends.md#apps): the `back-office` app, used by the Swarm administrator among others.
- [🏗️ Architecture: cells and the global layer](../../specs/technical/01-architecture.md#cells): Keycloak identity, the Operator directory and routing of each Operator to its cell.
- [🔐 Security: identity](../../specs/technical/06-security.md#identity): Keycloak realm, each Operator an organisation.
- [🔐 Security: roles and Operator isolation](../../specs/technical/06-security.md#authorisation): roles per persona, checks in the gateway and in PostgreSQL.
- [🔌 API layer: REST](../../specs/technical/05-api.md#rest): the `/v1` API of the gateway.

## Screens touched

- [🖼️ UC-029 A1: Enter the Operator](../../specs/functional/use-cases/UC-029-create-an-operator.md#screen-a1)
- [🖼️ UC-029 KO: Operator not created](../../specs/functional/use-cases/UC-029-create-an-operator.md#screen-ko)
- [🖼️ UC-029 A2: Invite the first Mission planner](../../specs/functional/use-cases/UC-029-create-an-operator.md#screen-a2)
- [🖼️ UC-029 OK: Operator created and isolated](../../specs/functional/use-cases/UC-029-create-an-operator.md#screen-ok)

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

1. **Given** a new drone service company, **when** the Swarm administrator creates its Operator, **then** its first Mission planner is invited and sees no other Operator's data, passing as an automated test with two Operators. ([📏 BR-008](../../specs/functional/business-rules/BR-008-operator-isolation.md), [🎬 UC-029](../../specs/functional/use-cases/UC-029-create-an-operator.md))
2. **Given** an Operator named Aerowing Services already exists, **when** the Swarm administrator enters the same name, **then** the Back office does not create the Operator and says that the name is taken (A1). ([📏 BR-008](../../specs/functional/business-rules/BR-008-operator-isolation.md), [🎬 UC-029](../../specs/functional/use-cases/UC-029-create-an-operator.md))
3. **Given** a required field is missing, such as the Jurisdiction, **when** the Swarm administrator submits the entry, **then** the Back office does not create the Operator and names the missing field (A2). ([📏 BR-008](../../specs/functional/business-rules/BR-008-operator-isolation.md), [🎬 UC-029](../../specs/functional/use-cases/UC-029-create-an-operator.md))

## Out of scope

- The on-premises installation (A3), installed in P7, see [P0 scope](../../specs/roadmap/01-p0-foundations.md#scope).
- The screenshots of the UC-029 screens and the visual tests, see [T0.20](../../specs/roadmap/01-p0-foundations.md#s04).
- Inviting Clients, which comes in P2, see [P0 scope](../../specs/roadmap/01-p0-foundations.md#scope).

## Assumptions

- The roadmap row has no anchor of its own, so the ticket links to the S04 section that holds it, and the epic to the epics table.
- The three acceptance criteria are drawn from AC-3 of FS-012 and from alternative flows A1 and A2 of UC-029, which the roadmap row names as "done when".
- The screens are listed as touched because the ticket changes `frontends/back-office` (TKT-21); the screen capture itself is planned by this ticket's plan, with the pipeline of T0.20.
