# T0.16: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🎯 Constraints

- A name already taken (A1) and a missing required field (A2) must be refused and named, and the first Mission planner must see only her own Operator's data ([TICKET.md](TICKET.md), BR-008).
- One entity, one class per layer, and the API layer holds endpoints only ([`backend/swarm-api/src/swarm_api/v1/gateway/operator_router.py:22`](../../../backend/swarm-api/src/swarm_api/v1/gateway/operator_router.py#L22), AGENT.md Layout).
- Every model, enum and exception lives in `swarm_models`, and the generated Rust and TypeScript types follow it (AGENT.md, Shared models).
- With no explicit LLM provider choice, the default depends on the deployment (FS-012, glossary).
- A gateway answer follows the REST problem model, so a failure is a REST error.

## ⚖️ Choices at a glance

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | LLM provider default in the screen | Draft field null until chosen, default derived | Reset the provider in the deployment `onChange` | The server default is never exercised by this screen |
| [D2](#d2) | Telling the two 409s apart | Read the directory again after the POST | Parse the problem document | One extra GET on a conflict, wrong if that read fails |
| [D3](#d3) | Where the e-mail conflict is shown | Planner step, field error and banner | Back to the entry step with a generic banner | Two places handle a conflict |
| [D4](#d4) | Consistency between PostgreSQL and Keycloak | Invite inside the transaction, delete from Keycloak on failure | (not recorded) | Open point |

## <a id="d1"></a>D1: LLM provider default in the screen

**Chosen:** `llmProvider` is null until the person chooses, and `effectiveProvider` derives the default · **Where:** [`frontend/apps/back-office/src/operators/entry-checks.ts:29`](../../../frontend/apps/back-office/src/operators/entry-checks.ts#L29), with `DEFAULT_DRAFT` at [`frontend/apps/back-office/src/operators/entry-checks.ts:44`](../../../frontend/apps/back-office/src/operators/entry-checks.ts#L44) · **Source:** FIX-K24+K12+K08

| Option | For | Against |
| --- | --- | --- |
| ✅ Null until chosen | The select and the summary follow the deployment live, with no state to synchronise. The POST always sends an explicit value, so an Operator on premises is not stored with Claude | The default lives in the front end, so the server's own default is not used here |
| Reset `llmProvider` in the deployment radio's `onChange` | Keeps a plain value in the draft | An explicit choice would be lost when the deployment changes, and an extra state sync is needed |
| Send no `llm_provider` unless chosen | The server decides | The review found an on-premises Operator stored with Claude by mistake; the screen would depend on the server default |

**Trade-off:** the front end repeats the rule "open weight on premises, Claude in the cloud".

**Revisit when:** the server exposes the default of a deployment, so the screen can read it.

## <a id="d2"></a>D2: Telling the two 409s apart

**Chosen:** read the directory again after the POST · **Where:** [`frontend/apps/back-office/src/operators/OperatorsScreen.tsx:75`](../../../frontend/apps/back-office/src/operators/OperatorsScreen.tsx#L75) · **Source:** FIX-K24+K12+K08, review follow-up

| Option | For | Against |
| --- | --- | --- |
| ✅ Re-read the directory | No change to the gateway contract; one extra GET only on a conflict | A race can misclassify; if the read fails, the screen assumes the e-mail is taken |
| Parse the problem+json document | One answer, no second request | Needs a distinct problem type or field for `SEOperatorPlannerEmailTakenError`, which the gateway does not give yet |
| Check the directory only before the POST | No extra request on conflict | Does not see a name taken in the meantime, and does not detect the e-mail conflict |

**Trade-off:** a sturdier answer was left for a follow-up to keep the fix inside the Back office.

**Revisit when:** the gateway gives the e-mail conflict its own problem type.

## <a id="d3"></a>D3: Where the e-mail conflict is shown

**Chosen:** on the planner step, as a field error and the banner · **Where:** [`frontend/apps/back-office/src/operators/FirstMissionPlannerStep.tsx:114`](../../../frontend/apps/back-office/src/operators/FirstMissionPlannerStep.tsx#L114) · **Source:** FIX-K24+K12+K08

| Option | For | Against |
| --- | --- | --- |
| ✅ Stay on the planner step | The person fixes the right field, so the KO loop ends | The error stays until the next submit (follow-up) |
| Send back to the entry step with a generic banner | One path for every conflict | The entry data is not the cause, so the person would loop |

**Trade-off:** the screen has two conflict paths, one per cause.

**Revisit when:** the problem document names the field (see D2).

## <a id="d4"></a>D4: Consistency between PostgreSQL and Keycloak

**Chosen:** the invitation runs inside the database transaction, and a failure afterwards deletes the Keycloak organisation and user · **Where:** [`backend/swarm-service/src/swarm_service/gateway/operators/operator_service.py:248`](../../../backend/swarm-service/src/swarm_service/gateway/operators/operator_service.py#L248) · **Source:** read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ Invite inside the transaction, compensate in Keycloak | A failed database write leaves nothing in Keycloak; a failed invitation rolls the rows back | The compensation can itself fail (it is logged, see [`backend/swarm-service/src/swarm_service/gateway/operators/operator_service.py:190`](../../../backend/swarm-service/src/swarm_service/gateway/operators/operator_service.py#L190)) |

**Trade-off:** no alternative was named by a worker or the review; the reason for this ordering is an open point.

**Revisit when:** an outbox or a retry job is added for the Keycloak step.

## 📝 Assumptions behind the choices

- With no explicit choice, the LLM provider follows the deployment: supports [D1](#d1).
- A 409 whose name the directory does not list is the planner's e-mail already known: supports [D2](#d2) and [D3](#d3).
