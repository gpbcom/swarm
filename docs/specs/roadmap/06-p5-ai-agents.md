# 🛣️ P5: AI agents, MCP and A2A

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ P4: Agriculture](05-p4-agriculture.md) · 📄 **Page 101 / 108** · [P6: Light shows ▶️](07-p6-light-shows.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Sprints:** S36 to S43 · **Dates:** 8 May 2028 to 25 Aug 2028 · **Tickets:** about 30, plus one slot reserved for the Patrol beta

> [!NOTE]
> P5 adds the three AI agents of Swarm (the [⚙️ Mission assistant](../glossary.md#sys-mission-assistant), the [⚙️ Co-pilot](../glossary.md#sys-co-pilot) and the [⚙️ Report writer](../glossary.md#sys-report-writer)), opens Swarm to [🔤 Outside agents](../glossary.md#term-outside-agent) through MCP and A2A behind the human gate of [📏 BR-021](../functional/business-rules/BR-021-ai-agents-propose-people-decide.md), and comes now because Inspection, Patrol and Agriculture are flown by then, so the agents have real Missions, Flight logs and Deliverables to work on.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🎯 Goal](#goal)
2. [🧺 Scope](#scope)
3. [🪜 Epics](#epics)
4. [🗓️ Sprint plan](#sprints)
5. [🎤 Demo](#demo)
6. [🚪 Exit criteria](#exit)
7. [⛓️ Dependencies](#dependencies)
8. [🎲 Risks](#risks)
9. [🧑‍💻 Work split](#work-split)
<!-- /spec:summary -->

## <a id="goal"></a>🎯 Goal

At the end of P5, on 25 August 2028 (milestone M5, AI agents in beta), the design-partner [🗃️ Operator](../glossary.md#ent-operator) uses the three agents on its real work, and has MCP and A2A enabled:

- **Mission assistant** ([📘 FS-017](../functional/features/FS-017-mission-assistant.md)): the [👤 Mission planner](../glossary.md#per-mission-planner) describes the need in words in **💬 Assistant** of the [⚙️ Mission studio](../glossary.md#sys-mission-studio); the Mission assistant proposes the area, the [🗃️ Squad](../glossary.md#ent-squad) with a [🗃️ Payload](../glossary.md#ent-payload) per [🗃️ Drone](../glossary.md#ent-drone), the routes and the time slot, gives its reasons and the rules it checked, and nothing takes effect until the Mission planner accepts ([🎬 UC-021](../functional/use-cases/UC-021-plan-a-mission-with-the-mission-assistant.md)).
- **Co-pilot** ([📘 FS-018](../functional/features/FS-018-live-co-pilot.md)): during a flight, the Co-pilot spots trends (a [🗃️ Battery](../glossary.md#ent-battery) draining faster, a [🔤 Link](../glossary.md#term-link) weakening, wind rising), explains [🔤 Alerts](../glossary.md#term-alert) in plain words, speaks the critical ones, and proposes [🗃️ Re-plans](../glossary.md#ent-re-plan) that wait for the [👤 Pilot](../glossary.md#per-pilot) ([🎬 UC-004](../functional/use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md), [🎬 UC-026](../functional/use-cases/UC-026-handle-an-alert.md)). It reads aggregates, never the raw stream, and is never in the safety loop.
- **Report writer** ([📘 FS-019](../functional/features/FS-019-mission-reports.md)): after each Mission, the Report writer drafts the Mission report in the [👤 Client](../glossary.md#per-client)'s language, with the common skeleton and the section of its [🔤 Activity](../glossary.md#term-activity); the Mission planner asks for changes in a conversation and publishes it; only then does the Client receive it with its [🗃️ Evidence record](../glossary.md#ent-evidence-record) ([🎬 UC-022](../functional/use-cases/UC-022-receive-the-mission-report.md)).
- **MCP and A2A**: each Operator can enable an MCP server and the A2A Agent Cards of its three agents. An Outside agent acts as the delegate of one person, with that person's rights; signing the [🗃️ Pre-flight check](../glossary.md#ent-pre-flight-check) and launching wait for the person's confirmation on their own device with their PIN, and abort, manual control and [🔤 Hold](../glossary.md#term-hold) stay in [⚙️ Ground control](../glossary.md#sys-ground-control) ([🛡️ the human gate](../technical/06-security.md#human-gate)).
- **Serving**: the `agents` service runs as three Kubernetes Deployments, `agents-mcp`, `agents-a2a` and `agents-worker`, each behind its own Kubernetes Service and scaled by KEDA, as decided in [💬 Agents, MCP and A2A](../technical/04-engine.md#agents) (decision T39).
- **LLM provider**: every agent runs on the [🔤 LLM provider](../glossary.md#term-llm-provider) and models the Operator chose: Claude models by default in the cloud, an open-weight model on the Operator's own servers on premises.

## <a id="scope"></a>🧺 Scope

**Features**

| Feature | What P5 delivers of it |
| --- | --- |
| [📘 FS-017: Mission assistant](../functional/features/FS-017-mission-assistant.md) | All of it: the conversation, the Draft proposal with reasons and rules, edits, acceptance recorded with the person's name, the LLM provider per Operator, MCP and A2A for Outside agents |
| [📘 FS-018: Live Co-pilot](../functional/features/FS-018-live-co-pilot.md) | All of it: trends, explanations, Re-plan proposals with their reasons, critical Alerts spoken and never muted, other spoken Alerts mutable |
| [📘 FS-019: Mission reports](../functional/features/FS-019-mission-reports.md) | The AI draft: the common skeleton, the sections per Activity (Inspection, Agriculture, Patrol; Light show added in [🛣️ P6](07-p6-light-shows.md)), changes in a conversation, publication by a person. The manual report template of [🛣️ P2](03-p2-inspection-product.md) stays as the fallback |
| [📘 FS-021: Ground control monitoring](../functional/features/FS-021-ground-control-monitoring.md) | The Co-pilot's explanation in the Alerts area, next to the actions available |
| [📘 FS-012: Operators, deployment and languages](../functional/features/FS-012-operators-deployment-and-languages.md) | Only its LLM provider part: the provider and models of each Operator, set at creation with the cloud default, now used by the agents and changeable in the Back office; the rest of FS-012 comes in [🛣️ P7](08-p7-scale-and-reach.md) |

**Use cases**

| Use case | What P5 delivers of it |
| --- | --- |
| [🎬 UC-021: Plan a Mission with the Mission assistant](../functional/use-cases/UC-021-plan-a-mission-with-the-mission-assistant.md) | All of it, alternatives A1 to A4, five screens moved to 📸 Screenshot |
| [🎬 UC-022: Receive the Mission report](../functional/use-cases/UC-022-receive-the-mission-report.md) | All of it, with the Report writer drafting; alternatives A1 to A3; five screens moved to 📸 Screenshot |
| [🎬 UC-004: Supervise a Squad and approve a Re-plan](../functional/use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md) | The Co-pilot part: the Re-plan proposed by the Co-pilot with its reasons, on top of the Re-plans the Squad proposes since [🛣️ P1](02-p1-first-flight.md) |
| [🎬 UC-026: Handle an Alert](../functional/use-cases/UC-026-handle-an-alert.md) | The Co-pilot part: step 2 (the explanation and the proposed actions) and alternative A4 (critical Alerts spoken) |

**Business rules**

| Rule | Where P5 enforces it |
| --- | --- |
| [📏 BR-021: AI agents propose, people decide](../functional/business-rules/BR-021-ai-agents-propose-people-decide.md) | An agent can only create a `Proposal`; accepting it is a person's act, recorded with the name; for Outside agents, the human gate in the gateway and the missions service, never in the agent |
| [📏 BR-013: Re-plan approval](../functional/business-rules/BR-013-re-plan-approval.md) | A Co-pilot Re-plan that changes the area covered waits for the Pilot, with the countdown the Operator set |
| [📏 BR-020: Defects confirmed by a person](../functional/business-rules/BR-020-defects-confirmed-by-a-person.md) | The Report writer reads only Confirmed Defects |
| [📏 BR-009: Evidence integrity](../functional/business-rules/BR-009-evidence-integrity.md) | The published report gets its Evidence record; every delegated call is recorded in the evidence ledger |
| [📏 BR-008: Operator isolation](../functional/business-rules/BR-008-operator-isolation.md) | One MCP endpoint and one set of Agent Cards per Operator; agent tools read only the Operator's NATS subjects and rows |
| [📏 BR-012: Pilot override always available](../functional/business-rules/BR-012-pilot-override-always-available.md) | While a Co-pilot proposal waits, the Pilot can still Hold, take manual control or abort; none of these is exposed to an Outside agent |
| [📏 BR-017: Every screen in four languages](../functional/business-rules/BR-017-every-screen-in-four-languages.md) | Every new screen, every spoken Alert and every Mission report in English, French, German and Spanish |

**Technical pages**

| Page | What P5 builds on |
| --- | --- |
| [💬 Agents, MCP and A2A](../technical/04-engine.md#agents) | LangGraph graphs with `TaskNode` classes, typed tools, the MCP server, A2A, evaluations, and the three Deployments with their Services and KEDA scalers |
| [💬 MCP and A2A endpoints](../technical/05-api.md#mcp-a2a) | MCP over Streamable HTTP with OAuth 2.1, Agent Cards at `/.well-known/agent.json`, `202 Accepted` with a pending confirmation, separate rate limits |
| [🛡️ The human gate for Outside agents](../technical/06-security.md#human-gate) | The table of acts and how each one is gated |
| [🔑 Secrets and keys](../technical/06-security.md#secrets) | The LLM provider keys of each Operator in Vault; configuration holds names only |
| [📨 Events and proposals](../technical/02-data-models.md#events) | `Proposal`, and the `actor` of each event: a person, a Swarm agent, or an Outside agent with the person it acts for |
| [🧱 Main models](../technical/02-data-models.md#models) | `Proposal`, `AgentSession`, `Delegation` in the agents service |
| [🔲 Cells](../technical/07-scalability.md#cells) | Every MCP server and A2A agent behind a Kubernetes Service and scaled by KEDA |
| [🚢 Delivery](../technical/09-deployment.md#delivery) | KEDA in every cell with its NATS JetStream and Prometheus scalers and the HTTP add-on; the `agents` chart with its three `ScaledObject` resources |
| [🎯 Service level objectives](../technical/08-observability.md#slos) | The SLO review and the dashboards the agents are added to |

## <a id="epics"></a>🪜 Epics

| # | Epic | Delivers (UC/BR links) | Where (services, apps, packages) | Tickets | Parallel tasks for the agents |
| --- | --- | --- | --- | --- | --- |
| E5.1 | Agents service, LLM providers, proposals and evaluations | [📏 BR-021](../functional/business-rules/BR-021-ai-agents-propose-people-decide.md), [📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md) | `services/agents` (layers `api`, `service`, `storage`, `models`), `services/missions` (Proposal flow), `packages/python` (NATS client, lifecycle), `frontends/back-office` (LLM provider settings), `tests/` evaluations | T5.01 to T5.05 (5) | Service skeleton and factories; provider adapters behind one interface; Proposal models with their validators; read tools and their tests; evaluation runner in CI; OpenTelemetry spans for every model call |
| E5.2 | Mission assistant | [🎬 UC-021](../functional/use-cases/UC-021-plan-a-mission-with-the-mission-assistant.md), [📏 BR-021](../functional/business-rules/BR-021-ai-agents-propose-people-decide.md) | `services/agents` (graph), `services/planner` and `services/missions` (called as tools), `frontends/mission-studio` | T5.06 to T5.09 (4) | Graph nodes; rule checks reused from the missions service; the **💬 Assistant** panel and the proposal on the map; evaluation set; screenshots of UC-021 |
| E5.3 | Report writer | [🎬 UC-022](../functional/use-cases/UC-022-receive-the-mission-report.md), [📏 BR-020](../functional/business-rules/BR-020-defects-confirmed-by-a-person.md), [📏 BR-009](../functional/business-rules/BR-009-evidence-integrity.md), [📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md) | `services/agents` (graph), `services/processing` (report rendering), `services/evidence`, `frontends/back-office`, `frontends/client-portal` | T5.11 to T5.14 (4) | Graph and section templates per Activity; review conversation in the Back office; publication with its Evidence record; evaluation set; screenshots of UC-022 |
| E5.4 | Co-pilot | [🎬 UC-004](../functional/use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md), [🎬 UC-026](../functional/use-cases/UC-026-handle-an-alert.md), [📏 BR-013](../functional/business-rules/BR-013-re-plan-approval.md), [📏 BR-012](../functional/business-rules/BR-012-pilot-override-always-available.md) | `services/agents` (graph), TimescaleDB continuous aggregates, `services/planner` (Re-plans), `frontends/ground-control`, `packages/ts/i18n` | T5.15 to T5.19 (5) | Trend detection on 1-second aggregates; proposals through the planner; explanation in the Alerts area; spoken Alerts in four languages; evaluation on Replays of real flights |
| E5.5 | MCP server on `agents-mcp` | [📏 BR-021](../functional/business-rules/BR-021-ai-agents-propose-people-decide.md), [📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md) | `services/agents` (MCP Python SDK), `services/gateway` (routes, rate limits), Keycloak, `deploy/charts/agents` | T5.20, T5.21, T5.22, T5.27 (4) | MCP tools mirroring REST; OAuth 2.1 delegation tokens; Deployment, Service and `ScaledObject`; Valkey session store; k6 scenario |
| E5.6 | A2A on `agents-a2a` and long runs on `agents-worker` | [📏 BR-021](../functional/business-rules/BR-021-ai-agents-propose-people-decide.md) | `services/agents`, NATS JetStream work queue, Valkey, `deploy/charts/agents`, `frontends/back-office` (registered outside agents) | T5.10, T5.25, T5.26, T5.28 (4) | Agent Cards and task streams; worker consumer; two Deployments with their Services and `ScaledObject` resources; registry of outside agents |
| E5.7 | Human gate for Outside agents | [📏 BR-021](../functional/business-rules/BR-021-ai-agents-propose-people-decide.md), [📏 BR-012](../functional/business-rules/BR-012-pilot-override-always-available.md), [📏 BR-009](../functional/business-rules/BR-009-evidence-integrity.md) | `services/gateway`, `services/missions`, `services/notifier`, `services/evidence`, `frontends/client-portal` and `frontends/ground-control` (confirmation) | T5.23, T5.24, T5.29 (3) | Gate table as code and tests; pending confirmations with push Notification and PIN; abuse and injection test set |
| E5.9 | Patrol beta support (reserved) | [🎬 UC-018](../functional/use-cases/UC-018-respond-to-a-site-alarm.md), [🎬 UC-019](../functional/use-cases/UC-019-request-a-patrol-on-demand.md) | Whichever services and apps the Patrol beta needs fixed | T5.31 (1) | The fix, its regression test and its screenshot update, as for any ticket |
| E5.8 | Scale proof and beta | [📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md) | `tests/load`, `deploy/environments`, Grafana dashboards | T5.30 (1) | KEDA load test of the three Deployments; dashboards and alerts; enablement for the design partner |

## <a id="sprints"></a>🗓️ Sprint plan

P5 starts while [🛣️ P4: Agriculture](05-p4-agriculture.md) finishes its spring campaign: 2 tickets in S36 and S37, none in S38, so that about 5 tickets are merged per sprint with P4's. **The Patrol beta (milestone M3, 30 June 2028) takes one slot in S38 (P4's T4.26) and one in S39 (T5.31)** for the fixes it raises. S39 then merges 4 P5 tickets plus that slot, S40 5, S41 and S42 6 (about 6 per sprint is accepted from S41 to S52), and S43 5, until milestone M5. [🛣️ P6: Light shows](07-p6-light-shows.md) starts in S41 alongside.

| Sprint | Dates | Tickets | Sprint goal | What can be shown |
| --- | --- | --- | --- | --- |
| S36 | 8 to 19 May 2028 | T5.01 Agents service skeleton; T5.02 LLM provider per Operator | The `agents` service runs in the dev cell and calls the LLM provider of the Operator, with keys from Vault | A graph that answers on Claude models in the cloud cell and on an open-weight model in staging, chosen per Operator |
| S37 | 22 May to 2 Jun 2028 | T5.03 Proposal flow; T5.04 Agent tools | An agent can read Missions, the Fleet and Flight logs through typed tools and can only create Proposals | A Proposal created by a test graph, then accepted by a person, with the name recorded |
| S38 | 5 to 16 Jun 2028 | No P5 ticket: the sprint's capacity goes to P4 and to the Patrol beta slot (T4.26) | The agents draft the evaluation sets and the prompts of the Mission assistant, to be reviewed in S39 | The Proposal flow of S37 on the design partner's sample data |
| S39 | 19 to 30 Jun 2028 | T5.05 Evaluations and AI telemetry; T5.06 Mission assistant graph; T5.07 Rule checks in proposals; T5.08 Mission studio Assistant; T5.31 Patrol beta fixes (reserved slot) | Prompts, tools and test sets run in CI; the Mission planner gets a Draft proposal for M-2026-0412 with its reasons and rules; the Patrol beta gets its fixes before M3 | [🎬 UC-021](../functional/use-cases/UC-021-plan-a-mission-with-the-mission-assistant.md) end to end in the dev cell; the CI run failing on a deliberate drop in score; the cost and latency dashboard |
| S40 | 3 to 14 Jul 2028 | T5.09 Mission assistant evaluation set; T5.10 `agents-worker` Deployment; T5.11 Report writer graph; T5.12 Draft review conversation; T5.13 Publication with its Evidence record | Long runs execute on `agents-worker`, scaled by KEDA from zero; the Mission report of M-2026-0412 is drafted, reviewed, published and received | [🎬 UC-022](../functional/use-cases/UC-022-receive-the-mission-report.md) end to end, Priya Shah receiving the report in English; `agents-worker` scaling from 0 to 3 pods on a burst and back |
| S41 | 17 to 28 Jul 2028 | T5.14 Report evaluation set; T5.15 Co-pilot graph on aggregates; T5.16 Co-pilot Re-plan proposals; T5.17 Explanations in Ground control; T5.18 Spoken Alerts; T5.19 Co-pilot evaluation on Replays | The Co-pilot reads the 1-second aggregates of a flying Mission; the Pilot gets its explanation and Re-plan in Ground control; critical Alerts are spoken | [🎬 UC-004](../functional/use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md) with the Co-pilot on the simulated Squad, then on the weekly real flight of the staging test field |
| S42 | 31 Jul to 11 Aug 2028 | T5.20 MCP server tools; T5.21 OAuth 2.1 delegation; T5.22 `agents-mcp` Deployment; T5.23 Human gate in the gateway and the missions service; T5.24 Confirmation on the person's own device; T5.25 A2A Agent Cards and tasks | An Outside agent connects through MCP as the delegate of a person; a launch it asks for waits for the person's PIN | An MCP client acting for Sam Carter asks for a launch: `202 Accepted`, push Notification on Sam's phone, PIN, launch |
| S43 | 14 to 25 Aug 2028 | T5.26 `agents-a2a` Deployment; T5.27 Agent rate limits and ledger; T5.28 Registered outside agents; T5.29 Abuse and injection tests; T5.30 KEDA load test and beta enablement | MCP and A2A enabled for the design partner; the three Deployments hold their load test | The [end-of-phase demonstration](#demo); milestone M5 |

**Tickets in detail**

| Ticket | Sprint | Epic | What it does | Done when |
| --- | --- | --- | --- | --- |
| T5.01 | S36 | E5.1 | `services/agents` with the AGENT.md layers, runnables and factories; one LangGraph graph per agent, nodes as `TaskNode` classes with `__call__`; one image | The service passes the conventions tests, starts in the dev cell and runs a test graph |
| T5.02 | S36 | E5.1 | LLM provider per Operator: one interface, a Claude adapter (cloud default) and an open-weight adapter (on premises); the provider and models chosen in the Back office; keys in Vault, named by `_key` fields | The same graph runs on both providers; switching the Operator's provider changes the next run, with no restart; no key in configuration or logs |
| T5.03 | S37 | E5.1 | `Proposal`, `AgentSession` and `Delegation` models; the Proposal flow in `services/missions`: Proposed, then Accepted or Rejected by a person, who is recorded with the time | [📏 BR-021](../functional/business-rules/BR-021-ai-agents-propose-people-decide.md) examples 1 and 2 pass as tests; no code path lets an agent accept its own Proposal |
| T5.04 | S37 | E5.1 | Typed tools: reads through NATS request-reply and the read replicas, writes only as Proposals; each tool scoped to the Operator of the session | A tool asked for another Operator's data gets nothing ([📏 BR-008](../functional/business-rules/BR-008-operator-isolation.md)); every tool has its unit tests |
| T5.05 | S39 | E5.1 | Evaluation runner in CI: prompts, tools and test sets versioned in the repository, a score per agent, a drop fails the build; OpenTelemetry spans with model, tokens, cost and latency per call | CI fails on a deliberate regression; the Grafana panel shows cost and latency per Operator and per agent |
| T5.06 | S39 | E5.2 | Mission assistant graph: understands the need, proposes the area and its [🗃️ Geofence](../glossary.md#ent-geofence) under the [🔤 Altitude ceiling](../glossary.md#term-altitude-ceiling), the Squad with a Payload and a task per Drone, the routes from the planner, and the time slot | [📘 FS-017](../functional/features/FS-017-mission-assistant.md) AC-1 passes on the sample need of [🎬 UC-021](../functional/use-cases/UC-021-plan-a-mission-with-the-mission-assistant.md) |
| T5.07 | S39 | E5.2 | Rule checks in the proposal: the rules of the missions service run on the proposal, each listed passed or failed with its reason; a failed rule stays failed after acceptance | Alternatives A1 and A2 of [🎬 UC-021](../functional/use-cases/UC-021-plan-a-mission-with-the-mission-assistant.md) pass |
| T5.08 | S39 | E5.2 | **💬 Assistant** in the Mission studio: the conversation, the proposal on the map, edits in words or in the proposal, accept or reject; on acceptance the Draft opens in **🖊️ Design** | Screens A1, A2, A3, OK and KO of [🎬 UC-021](../functional/use-cases/UC-021-plan-a-mission-with-the-mission-assistant.md#screens) match their mock-ups, then are captured as 📸 Screenshot |
| T5.09 | S40 | E5.2 | Mission assistant evaluation set: needs for Inspection, Patrol and Agriculture, with the expected Squad, Payloads and rule results | The set runs in CI with its threshold, set by the person |
| T5.10 | S40 | E5.6 | `agents-worker` Deployment behind its Kubernetes Service (ClusterIP, health and metrics only), taking long runs from a JetStream work queue; KEDA `ScaledObject` on consumer lag (target 10 runs per pod, 0 to 100 replicas) | A burst of runs scales the worker from 0 and back to 0 in staging; a killed pod loses no run |
| T5.11 | S40 | E5.3 | Report writer graph: the common skeleton (summary, Mission, Squad, work done against the request, Scorecard, Deliverables, incidents, Evidence records) and the sections per Activity (Inspection, Agriculture, Patrol), in the Client's language, only Confirmed Defects | The draft of M-2026-0412 holds the 9 Confirmed Defects and none of the 3 Dismissed; alternative A2 of [🎬 UC-022](../functional/use-cases/UC-022-receive-the-mission-report.md) passes |
| T5.12 | S40 | E5.3 | Review in **📦 Deliverables** of the Back office: the draft, a conversation to ask the Report writer for changes, every version kept as a draft, reject with a reason | Alternative A1 of [🎬 UC-022](../functional/use-cases/UC-022-receive-the-mission-report.md) passes; screens A1, A2 and KO captured |
| T5.13 | S40 | E5.3 | Publication by a person only: the Mission report becomes [🔄 Deliverable: Published](../glossary.md#st-deliverable-published), gets its Evidence record and reaches the [⚙️ Client portal](../glossary.md#sys-client-portal) | [📘 FS-019](../functional/features/FS-019-mission-reports.md) AC-1 passes; alternative A3 passes; screens A3 and OK captured |
| T5.14 | S41 | E5.3 | Report evaluation set: every figure of the report traced to the Mission's data, no Suspected Defect, the right language | The set runs in CI with its threshold |
| T5.15 | S41 | E5.4 | Co-pilot graph on the 1-second continuous aggregates and the Alerts of a flying Mission; trends of Battery, Link and wind | The Co-pilot spots a Battery draining faster than planned in a simulated Squad before the low battery warning |
| T5.16 | S41 | E5.4 | Co-pilot Re-plan proposals, computed by the planner, with their reasons, waiting for the Pilot with the countdown the Operator set; the Squad's own Re-plans still work offline | [📘 FS-018](../functional/features/FS-018-live-co-pilot.md) AC-1 passes; [🎬 UC-004](../functional/use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md) A1 and A2 pass with a Co-pilot proposal |
| T5.17 | S41 | E5.4 | The Co-pilot's explanation in the Alerts area of Ground control, with the actions available and their effect | Step 2 of [🎬 UC-026](../functional/use-cases/UC-026-handle-an-alert.md) passes; screen A2 of UC-026 and screen A2 of UC-004 captured |
| T5.18 | S41 | E5.4 | Spoken Alerts in Ground control, in the Pilot's language: critical Alerts (Drone Lost, Geofence, weather beyond limits) always spoken and never mutable, the others mutable | Alternative A4 of [🎬 UC-026](../functional/use-cases/UC-026-handle-an-alert.md) passes; a critical Alert is spoken even with the core out of reach |
| T5.19 | S41 | E5.4 | Co-pilot evaluation on [🔤 Replays](../glossary.md#term-replay) of real Flight logs (campaigns [🛫 C-01](10-flight-test-campaigns.md#c-01) to [🛫 C-04](10-flight-test-campaigns.md#c-04)) and simulator scenarios: right trend, right proposal, no proposal when none is needed | The set runs in CI with its threshold; the safety tick and Pilot command budgets are unchanged with the Co-pilot running |
| T5.20 | S42 | E5.5 | MCP server with the MCP Python SDK, Streamable HTTP, one endpoint per Operator, tools mirroring the REST resources and the Proposal flow, off until the Operator enables it in the Back office | An MCP client lists Missions and creates a Draft for an Operator that enabled it, and gets nothing for one that did not |
| T5.21 | S42 | E5.5 | OAuth 2.1 with Keycloak for MCP and A2A: the token names the person and the Outside agent; `Delegation` recorded; every event carries both as its `actor` | A token without a person is refused; the Flight log and the evidence ledger show both names |
| T5.22 | S42 | E5.5 | `agents-mcp` Deployment behind its Kubernetes Service (ClusterIP, port 8080); KEDA `ScaledObject` on in-flight MCP requests per pod (target 50) plus CPU, 2 to 40 replicas in production, scale to zero in dev through the KEDA HTTP add-on; sessions (`Mcp-Session-Id`) in Valkey; graceful drain of 60 seconds; the gateway routes `/mcp/…` | A session survives the loss of the pod that opened it; scale-in drops no request |
| T5.23 | S42 | E5.7 | The human gate in the gateway and the missions service, never in the agent: read, propose and drafts allowed; approve a Re-plan, publish a Deliverable or Scorecard, invite a Client as the person's delegate with both names; sign the Pre-flight check and launch pending; abort, manual control and Hold the Squad not exposed | Each row of [🛡️ the human gate](../technical/06-security.md#human-gate) has its test, through MCP and through A2A |
| T5.24 | S42 | E5.7 | Pending confirmation: `202 Accepted`, push Notification to the person's own device, PIN, expiry; the act completes only after the PIN | A launch asked by an Outside agent completes only after the person's PIN; a wrong or late PIN leaves it pending, then refused |
| T5.25 | S42 | E5.6 | A2A: Agent Cards of the Mission assistant, the Co-pilot and the Report writer at `/.well-known/agent.json` per Operator; tasks, streaming updates and artefacts per the A2A protocol; long tasks handed to `agents-worker` | An outside A2A client delegates a report draft to the Report writer and receives it as an artefact |
| T5.26 | S43 | E5.6 | `agents-a2a` Deployment behind its Kubernetes Service (ClusterIP, port 8080); KEDA `ScaledObject` on in-flight A2A requests and open task streams per pod (target 50) plus CPU, 2 to 40 replicas in production; task state in Valkey and JetStream; the gateway routes `/a2a/…` and `/.well-known/agent.json` | A task stream survives the loss of its pod; nothing reaches an agent pod except through the gateway |
| T5.27 | S43 | E5.5 | Separate rate limits for agents in the gateway; every MCP and A2A call recorded in the evidence ledger | An Outside agent over its limit is slowed without affecting people; every call of the demo is found in the ledger |
| T5.28 | S43 | E5.6 | Swarm's agents call the outside agents an Operator registered in the Back office, under the same gate | A registered outside agent answers a Mission assistant task; an unregistered one is never called |
| T5.29 | S43 | E5.7 | Abuse and injection tests: instructions hidden in Mission names, Client requests or Defect notes; replayed confirmations; tokens of another Operator; attempts to reach abort or manual control | The set runs in CI; every case is refused and recorded |
| T5.30 | S43 | E5.8 | KEDA load test of the three Deployments in staging with k6 and a burst of runs; dashboards and alerts for the agents; four languages checked; MCP and A2A enabled for the design partner in its OVHcloud cell | The [exit criteria](#exit) pass; milestone M5 |
| T5.31 | S39 | E5.9 | Reserved slot for the Patrol beta (M3, 30 June 2028): the fixes its Dock site raises, chosen by the person at the start of S39 | Each fix merged with its test before M3; the slot is not used for P5 work |

## <a id="demo"></a>🎤 Demo

Given on Friday 25 August 2028 to the design partner ([🤝 P-01](11-hardware-and-partners.md#p-01)), in its OVHcloud cell, opened early in S24 for the design partner beside a self-hosted beta cell, both provisioned with Terraform (decision T43). Sample cast: the Operator Aerowing Services, the Mission planner Léa Martin, the Pilot Sam Carter, the Client Helio Energy with its contact Priya Shah, the Site Les Vignes solar farm, the Mission M-2026-0412 Inspection of Les Vignes, the Drones Alpha, Bravo, Charlie and Delta.

1. **Describe.** Léa Martin opens M-2026-0412, [🔄 Mission: Requested](../glossary.md#st-mission-requested), in **💬 Assistant** of the Mission studio and writes the need: a thermal inspection of the panels of Les Vignes and an orthomosaic of the whole Site, on a morning.
2. **Propose.** The Mission assistant proposes the area and its Geofence, Alpha with a thermal camera on the panels, Bravo with an RGB camera for the orthomosaic, the routes and the time slot 10:00 to 11:00, with its reasons and every rule checked.
3. **Edit and accept.** Léa adds Charlie with a zoom camera for the inverters; the proposal and its checks update. She accepts: Swarm records her name and the Mission becomes [🔄 Mission: Draft](../glossary.md#st-mission-draft) in **🖊️ Design** ([🎬 UC-021](../functional/use-cases/UC-021-plan-a-mission-with-the-mission-assistant.md)).
4. **Fly with the Co-pilot.** In the Simulator, Sam Carter supervises the Squad. Charlie's Battery drains faster than planned: the Co-pilot explains it in plain words, and when Charlie Returns home it proposes a Re-plan sharing Charlie's area between Alpha, Bravo and Delta, with its reason and the effect on the duration. Sam approves within the 60 seconds; the [🗃️ Flight log](../glossary.md#ent-flight-log) records his name ([🎬 UC-004](../functional/use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md), [🎬 UC-026](../functional/use-cases/UC-026-handle-an-alert.md)).
5. **Critical Alert.** A Drone nears the Geofence: Ground control speaks the Alert. Sam tries to mute it and cannot; he mutes a non-critical one.
6. **Report.** After landing and the Defect review, the Report writer drafts the Mission report in English. Léa asks for a shorter summary in the conversation, gets a new draft, and publishes it. Priya Shah downloads it in the Client portal with its Evidence record ([🎬 UC-022](../functional/use-cases/UC-022-receive-the-mission-report.md)).
7. **Outside agent through MCP.** An MCP client of Aerowing Services, acting for Léa, lists the Missions of the week and creates a Draft Mission: allowed, recorded with both names. Acting for Sam, it asks to launch the Mission: Swarm answers `202 Accepted`, Sam's phone shows the push Notification, he enters his PIN, and only then does the launch go ahead. It then asks to abort: the tool does not exist outside Ground control.
8. **A2A.** An outside A2A client reads the Agent Card of the Report writer and delegates a report draft; the draft comes back as an artefact and stays a draft until Léa publishes it.
9. **Scale.** The load test report: `agents-mcp` and `agents-a2a` scaled from 2 pods under a k6 burst and back, `agents-worker` from 0 on a burst of runs and back to 0, no request lost during scale-in, and the cost and latency of every model call on the dashboard.

## <a id="exit"></a>🚪 Exit criteria

P5 closes at milestone M5 when every box below is ticked.

- [ ] [📘 FS-017](../functional/features/FS-017-mission-assistant.md#acceptance) AC-1: given a description of an Inspection, when the Mission assistant answers, then it proposes a Draft Mission that the Mission planner must accept.
- [ ] [📘 FS-018](../functional/features/FS-018-live-co-pilot.md#acceptance) AC-1: given a Battery draining faster than planned, when the Co-pilot notices, then it proposes a Re-plan with its reason, which waits for the Pilot.
- [ ] [📘 FS-019](../functional/features/FS-019-mission-reports.md#acceptance) AC-1: given a completed Inspection, when the Mission planner publishes the drafted report, then the Client receives it with its Evidence record.
- [ ] [📏 BR-021](../functional/business-rules/BR-021-ai-agents-propose-people-decide.md#examples) examples 1 and 2 pass, and every row of [🛡️ the human gate](../technical/06-security.md#human-gate) has a passing test through MCP and through A2A.
- [ ] [🎬 UC-021](../functional/use-cases/UC-021-plan-a-mission-with-the-mission-assistant.md) and [🎬 UC-022](../functional/use-cases/UC-022-receive-the-mission-report.md) pass end to end in Playwright against the real images, with every alternative; the Co-pilot parts of [🎬 UC-004](../functional/use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md) and [🎬 UC-026](../functional/use-cases/UC-026-handle-an-alert.md) pass in the Simulator.
- [ ] The evaluations of the three agents and the abuse and injection set pass in CI, with the thresholds the person set in S39.
- [ ] KEDA, in the staging cell: `agents-mcp` and `agents-a2a` keep 2 replicas at rest and scale out on in-flight requests (target 50 per pod) under the k6 load; `agents-worker` scales from 0 on JetStream consumer lag (target 10 runs per pod) and back to 0; scale-in drains in-flight requests within 60 seconds with no failed request; in dev, the three scale to zero through the HTTP add-on.
- [ ] Each Deployment is reached only through its Kubernetes Service, and each Service only through the gateway routes `/mcp/…`, `/a2a/…` and `/.well-known/agent.json`.
- [ ] Budgets of [⏱️ Budgets](../technical/07-scalability.md#budgets) hold in the nightly load test with the agents running: REST inside a cell p95 under 100 ms for reads and under 250 ms for writes, including MCP tool calls that do not call a model; safety tick under 5 ms for 500 Drones and Pilot command p99 under 50 ms, unchanged with the Co-pilot on; Telemetry p95 under 400 ms through the cell.
- [ ] The cost and latency of the model calls per Operator are on the dashboards, within the targets the person set in S39 ([🎲 R-09](12-risks.md#r-09)).
- [ ] The screens of [🎬 UC-021](../functional/use-cases/UC-021-plan-a-mission-with-the-mission-assistant.md#screens) (A1, A2, A3, OK, KO) and [🎬 UC-022](../functional/use-cases/UC-022-receive-the-mission-report.md#screens) (A1, A2, A3, OK, KO), screen A2 of [🎬 UC-004](../functional/use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md#screens) and screen A2 of [🎬 UC-026](../functional/use-cases/UC-026-handle-an-alert.md#screens) are 📸 Screenshot in light and dark mode.
- [ ] Every new screen, spoken Alert and Mission report is available in English, French, German and Spanish ([📏 BR-017](../functional/business-rules/BR-017-every-screen-in-four-languages.md)).
- [ ] `python3 .claude/skills/write-specs/scripts/specs.py check` prints nothing.
- [ ] MCP and A2A are enabled for the design-partner Operator in its OVHcloud cell, and its Mission planners and Pilots have used the three agents on real Missions.

## <a id="dependencies"></a>⛓️ Dependencies

**Previous phases**

| From | What P5 needs |
| --- | --- |
| [🛣️ P0: Foundations](01-p0-foundations.md) | Keycloak, NATS JetStream, Valkey, PostgreSQL with TimescaleDB, the shared Python packages (models, lifecycle, logging), the OpenTelemetry base, the i18n framework, the self-hosted k3s dev cell |
| [🛣️ P1: First flight](02-p1-first-flight.md) | The planner and its Re-plans, Re-plan approval with its countdown in Ground control, the Alerts area, the Mission studio with **🖊️ Design**, the Pre-flight check and launch that the human gate protects |
| [🛣️ P2: Inspection product](03-p2-inspection-product.md) | KEDA, already scaling processing on queue depth; Deliverables and their review in the Back office, Defects confirmed by a person, the Client portal, the evidence ledger, the Debrief, the Scorecard, Replays, the manual report template the Report writer replaces |
| [🛣️ P3: Patrol](04-p3-patrol.md) | Web Push Notifications, used for the confirmation on the person's own device; the timeline of events and [🗃️ Alarms](../glossary.md#ent-alarm) for the Patrol section of the report |
| [🛣️ P4: Agriculture](05-p4-agriculture.md) | The spray map for the Agriculture section of the report; the Flight logs of [🛫 C-04](10-flight-test-campaigns.md#c-04) for the Co-pilot evaluation |

**Cross-cutting items**

| Item | Sprint | Why P5 needs it |
| --- | --- | --- |
| [🤝 P-08](11-hardware-and-partners.md#p-08) LLM provider accounts | S36 | T5.02 and every model call after it |
| [🤝 P-06](11-hardware-and-partners.md#p-06) Hosting providers | S36 | The self-hosted dev and staging cells where KEDA and the three Deployments are proved; the design partner's OVHcloud cell, opened in S24 beside a self-hosted beta cell, both provisioned with Terraform (decision T43), where MCP and A2A are enabled for M5 |
| [🤝 P-01](11-hardware-and-partners.md#p-01) Design-partner Operator | S39 to S43 | Uses the agents on real Missions; its Mission planners and Pilots give the feedback for the evaluation sets |
| [🛫 C-01](10-flight-test-campaigns.md#c-01) to [🛫 C-04](10-flight-test-campaigns.md#c-04) Flight test campaigns | Before S41 | Their Flight logs feed the Co-pilot evaluation on Replays |
| [🤝 H-08](11-hardware-and-partners.md#h-08) GPU server for the on-premises test | S46 | Not needed in P5: the open-weight model is proved in staging; the on-premises run comes in [🛣️ P7](08-p7-scale-and-reach.md) |

## <a id="risks"></a>🎲 Risks

| Risk | Why it matters in P5 | Response in P5 |
| --- | --- | --- |
| [🎲 R-09](12-risks.md#r-09) LLM cost, latency or quality | Three agents on every Mission, with long reports and live explanations | Cost, latency and score measured from S39 (T5.05); targets set by the person before the first agent ships; evaluation sets block a regression; long runs on `agents-worker` so a slow model never blocks a request; smaller models for tool calls, caching, and a switch of provider since Swarm is provider-agnostic; the agents stay optional, so an Operator can switch one off without losing the feature it helps with |
| [🎲 R-10](12-risks.md#r-10) Security incident or key compromise | Outside agents reach Swarm with a person's rights; LLM provider keys of each Operator | The gate is enforced in the gateway and the missions service, never in the agent; abort, manual control and Hold are not exposed; keys in Vault; abuse and injection tests in CI (T5.29); MCP and A2A off until the Operator enables them |
| [🎲 R-01](12-risks.md#r-01) Review bottleneck | P5 overlaps the P4 campaign and the start of P6, and its prompts are code to review | Only 4 P5 tickets in S36 to S38, none in S38; evaluation sets give the person a score, not a transcript, to review; the human gate (T5.23, T5.24) gets a line-by-line review |
| [🎲 R-05](12-risks.md#r-05) Design partner lost | M5 needs a partner using the agents | Every demo step also runs on the sample cast in the simulation environment, so only the partner part of M5 would slip |
| [🎲 R-08](12-risks.md#r-08) Scope too large for 24 months | Three agents, two protocols and a gate in eight sprints | T5.28 (calling registered outside agents) and the Patrol and Agriculture report sections move first if P5 slips; the gate, the Proposal flow and the three Deployments never move |

## <a id="work-split"></a>🧑‍💻 Work split

**What the person does**

- **Reviews** the 30 tickets, most of them from S39; reads every prompt change as code, and the human gate (T5.23, T5.24) and the Proposal flow (T5.03) line by line.
- **Decides** the default models per agent for the cloud, the open-weight model for on premises, the evaluation thresholds and the cost and latency targets (S39), which MCP tools are exposed in the beta, and when to enable MCP and A2A for the design partner.
- **Flies** the weekly real flight on the staging test field as the Pilot from S41, with the Co-pilot on.
- **Partners:** opens the LLM provider accounts ([🤝 P-08](11-hardware-and-partners.md#p-08)), runs the sessions where the design partner's Mission planners and Pilots use the agents, gives the demonstration.

**What the agents do, in parallel**

- Split each ticket into tasks that run at the same time: the graph and its nodes, the tools and their tests, the screens with their Playwright tests, the Helm chart with its Deployment, Service and `ScaledObject`, the evaluation set, the screenshots.
- Keep four tracks apart: the agents (E5.2, E5.3, E5.4), the protocols (E5.5, E5.6), the gate (E5.7) and the platform (E5.1, E5.8), so that the gate never waits for an agent.
- Grow the evaluation sets from every real Mission of the design partner, with the person's approval of each new case.
- Run the KEDA load test and the abuse set every night in staging from S42, and open draft tickets for what fails.

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ P4: Agriculture](05-p4-agriculture.md) · 📄 **Page 101 / 108** · [P6: Light shows ▶️](07-p6-light-shows.md)
<!-- /spec:nav-bottom -->
