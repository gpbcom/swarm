# T0.16: Review note

**Verdict:** ✅ Approved (round 2, confirm fixes) · **Branch:** `feature/tickets`

## What changed

- The Back office offers both LLM providers. Until the Swarm administrator picks one, the provider follows the deployment: an open-weight model on premises, Claude in the cloud.
- The POST of a new Operator sends the provider in effect, so an Operator on premises is no longer stored with Claude by mistake.
- A 409 from the gateway is now read two ways. If the directory lists the name, the screen goes back to the entry step with A1 (name taken). If not, it stays on the first Mission planner step and says the e-mail address is already used.
- New messages in English, French, German and Spanish: the open-weight provider label and the e-mail-taken error.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. Given a new drone service company, when the Swarm administrator creates its Operator, then its first Mission planner is invited and sees no other Operator's data (two Operators) | `tests/swarm_api/v1/gateway/operator_router/test_gateway_operator_isolation.py`, tests-evidences/pytest.txt (5138 passed) | ✅ Pass |
| 2. Given Aerowing Services exists, when the same name is entered, then the Back office does not create it and says the name is taken (A1) | `create-operator.test.tsx`: "refuses the name of a listed Operator", "brings back the entry with the name error when the answer is a conflict"; tests-evidences/test.txt (back-office 28 passed) | ✅ Pass |
| 3. Given a required field is missing (Jurisdiction), when the entry is submitted, then nothing is created and the field is named (A2) | `create-operator.test.tsx`: "refuses a next step without a Jurisdiction and sends nothing" | ✅ Pass |

## Look at first

- How the two 409s are told apart, by reading the directory again after the conflict: `frontend/apps/back-office/src/operators/OperatorsScreen.tsx` (mutationFn and onSuccess).
- The provider default, and the fact that the POST sends it: `frontend/apps/back-office/src/operators/entry-checks.ts` (effectiveProvider, DEFAULT_DRAFT), plus `OperatorEntryStep.tsx` and `OperatorsScreen.tsx` (submit).
- Identity and Operator isolation were read line by line in round 1. These fixes touch only the Back office front end and its messages, not the gateway, Keycloak or PostgreSQL.

## Assumptions accepted

- With no explicit choice, the LLM provider follows the deployment (open-weight on premises, Claude in the cloud): accepted, as FS-012 and the glossary say.
- A 409 whose name the directory does not list means the planner's e-mail is already known: accepted. The gateway raises exactly these two conflicts.

## Follow-ups

- Clear the e-mail-taken error when the person edits the e-mail.
- Drop "(default)" from the Claude label, because the default now depends on the deployment. Also group the new error key with the other `operators.create.error.*` keys.
- Tell the two conflicts apart from the problem document (a distinct problem type for the e-mail conflict) instead of reading the directory again. If that read fails, the screen currently assumes the e-mail is taken.
