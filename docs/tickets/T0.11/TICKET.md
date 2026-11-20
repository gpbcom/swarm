# T0.11: Keycloak and gateway authentication

**Status:** 🟡 Planned

## Roadmap

- **Ticket:** [T0.11](../../specs/roadmap/01-p0-foundations.md#s03) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S03](../../specs/roadmap/01-p0-foundations.md#s03), 1 to 12 February 2027: identity, services and Simulator
- **Epic:** [E0.5](../../specs/roadmap/01-p0-foundations.md#epics): Identity and Operators. UC-029, BR-008 and FS-012 AC-3, on Keycloak (global layer), `services/gateway`, `services/missions`, `services/fleet` and `frontends/back-office`.

## What it delivers

- The global layer of identity: Keycloak with one realm, each Operator an organisation, and roles per persona, as [🔑 Security: identity](../../specs/technical/06-security.md#identity).
- Multi-factor authentication for Pilots, Mission planners, Fleet maintainers, Instructors and Swarm administrators, as [🔑 Security: identity](../../specs/technical/06-security.md#identity).
- Access tokens of 5 minutes and rotated refresh tokens, and PKCE clients for the four apps and the desktop shell, as [🔑 Security: identity](../../specs/technical/06-security.md#identity).
- In `services/gateway`, the check of the role and the Operator of every call, as [👥 Security: roles and Operator isolation](../../specs/technical/06-security.md#authorisation).

## Features, use cases and business rules

- [📏 BR-008: Operator isolation](../../specs/functional/business-rules/BR-008-operator-isolation.md)

## Technical pages it builds on

- [🔑 Security: identity](../../specs/technical/06-security.md#identity): "Keycloak (OpenID Connect)", "one realm per deployment, each Operator an organisation", multi-factor authentication for the listed roles, "short-lived access tokens (5 minutes)", refresh tokens rotated, and "the authorisation code flow with PKCE".
- [👥 Security: roles and Operator isolation](../../specs/technical/06-security.md#authorisation): the roles of each persona, and "the gateway checks the role and the Operator of every call".

## Screens touched

- The ticket touches no screen.

## Budgets touched

- The ticket touches no budget.

## Acceptance criteria

The "done when" of the roadmap row. The roadmap names no Given, when, then criterion of a feature for this ticket.

1. **Given** a call without a token, **when** it reaches the gateway, **then** it is refused and logged. ([📏 BR-008](../../specs/functional/business-rules/BR-008-operator-isolation.md))
2. **Given** a call with an expired token, **when** it reaches the gateway, **then** it is refused and logged. ([📏 BR-008](../../specs/functional/business-rules/BR-008-operator-isolation.md))
3. **Given** a call with another Operator's identifier, **when** it reaches the gateway, **then** it is refused and logged. ([📏 BR-008](../../specs/functional/business-rules/BR-008-operator-isolation.md))

## Out of scope

- Row-level security and the service skeletons, see [T0.12](../../specs/roadmap/01-p0-foundations.md#s03).
- The Operator directory and the creation of an Operator in the Back office, see [T0.16](../../specs/roadmap/01-p0-foundations.md#s04).
- Four languages, see [T0.15](../../specs/roadmap/01-p0-foundations.md#s03).

## Assumptions

- The roadmap row names no feature or use case. [📏 BR-008](../../specs/functional/business-rules/BR-008-operator-isolation.md) is linked because the epic row names it for the Operator isolation this ticket's checks serve, and the criteria cite it as the most conservative link.
- The row names no row of the budgets table, so the ticket touches no budget.
- The row names no screen, and its delivery is Keycloak and the gateway, so the ticket touches no screen.
- The row says "refused and logged" and gives no status code or log format, so none is asserted.
