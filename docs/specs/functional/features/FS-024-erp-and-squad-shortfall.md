# 📘 FS-024: ERP and Squad shortfall

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-023: AI Assistant](FS-023-ai-assistant.md) · 📄 **Page 28 / 120** · [UC-001: Design a Mission ▶️](../use-cases/UC-001-design-a-mission.md)
<!-- /spec:nav-top -->

**Status:** 🟡 Draft · **Updated:** 2026-11-20

> [!NOTE]
> Swarm works with the [⚙️ ERP](../../glossary.md#sys-erp) of the Operator: the [👤 Mission planner](../../glossary.md#per-mission-planner) sizes each [🗃️ Squad](../../glossary.md#ent-squad), and when the [🗃️ Fleet](../../glossary.md#ent-fleet) falls short the [⚙️ Assistant](../../glossary.md#sys-assistant) proposes how to cover it, from a [🗃️ Manufacturing order](../../glossary.md#ent-manufacturing-order) or a [🗃️ Purchase order](../../glossary.md#ent-purchase-order) to a smaller Squad.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🎯 Goal](#goal)
2. [👤 Personas and entities](#personas)
3. [📏 Business rules](#business-rules)
4. [🎬 Use cases](#use-cases)
5. [✅ Acceptance criteria](#acceptance)
6. [🗒️ Details](#details)
7. [🚫 Out of scope](#out-of-scope)
8. [❓ Open questions](#open-questions)
9. [🔗 References](#references)
<!-- /spec:summary -->

## <a id="goal"></a>🎯 Goal

A Mission planner should size the Squad from the work to do, then see at once whether the Fleet can fly it on the date. Some Operators build their own Drones and buy others: their ERP knows the stock, the bills of materials, the suppliers and the lead times. Swarm reads it to propose the right way to cover a [🔤 Squad shortfall](../../glossary.md#term-squad-shortfall), and keeps the ERP in step for Clients and Sites, quotes and invoices, Fleet costs and staff time.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Mission planner](../../glossary.md#per-mission-planner) | Persona | Sizes the Squad and chooses how to cover a shortfall |
| [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) | Persona | Registers the Drones built or bought, whose costs go to the ERP |
| [🗃️ Squad](../../glossary.md#ent-squad) | Entity | Sized from the work, with its flight profile |
| [🗃️ Fleet](../../glossary.md#ent-fleet) | Entity | Compared with the Squad on the Mission date |
| [🗃️ Drone model](../../glossary.md#ent-drone-model) | Entity | Built in-house or bought, as the ERP says |
| [🗃️ Manufacturing order](../../glossary.md#ent-manufacturing-order) | Entity | Placed in the ERP for a Drone model built in-house |
| [🗃️ Purchase order](../../glossary.md#ent-purchase-order) | Entity | Placed in the ERP for what is bought |
| [⚙️ ERP](../../glossary.md#sys-erp) | System | The Operator's business management system; Simple-ERP first |
| [⚙️ Assistant](../../glossary.md#sys-assistant) | System | Reads the ERP and proposes |
| [🔤 Squad shortfall](../../glossary.md#term-squad-shortfall) | Term | What the Fleet cannot supply |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-031: A Squad shortfall is covered through the ERP](../business-rules/BR-031-a-squad-shortfall-is-covered-through-the-erp.md) | Show the shortfall and how to cover it, within the Assistant permissions |
| [📏 BR-021: AI agents propose, people decide](../business-rules/BR-021-ai-agents-propose-people-decide.md) | An order reaches the ERP only when a person accepts it, unless the Operator set it to Act |
| [📏 BR-028: Assistant permissions are layered](../business-rules/BR-028-assistant-permissions-are-layered.md) | Who may let the Assistant place orders |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-033: Cover a Squad shortfall through the ERP](../use-cases/UC-033-cover-a-squad-shortfall-through-the-erp.md) | [👤 Mission planner](../../glossary.md#per-mission-planner) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a Mission that needs three Drones with a thermal camera and a Fleet with two Ready on the date **when** the Mission planner sizes the Squad **then** Swarm shows a Squad shortfall of one Drone | [📏 BR-031](../business-rules/BR-031-a-squad-shortfall-is-covered-through-the-erp.md) | [🎬 UC-033](../use-cases/UC-033-cover-a-squad-shortfall-through-the-erp.md) |
| AC-2 | **Given** a Drone model built in-house and an ERP connected **when** Swarm shows the shortfall **then** the Assistant proposes a Manufacturing order with the ready date the ERP gives, the earliest date of the Fleet alone and a smaller Squad with its trade-off | [📏 BR-031](../business-rules/BR-031-a-squad-shortfall-is-covered-through-the-erp.md) | [🎬 UC-033](../use-cases/UC-033-cover-a-squad-shortfall-through-the-erp.md) |
| AC-3 | **Given** "Place a Manufacturing order" at Propose **when** the Mission planner chooses the order **then** nothing reaches the ERP until the Mission planner accepts it | [📏 BR-021](../business-rules/BR-021-ai-agents-propose-people-decide.md) | [🎬 UC-033](../use-cases/UC-033-cover-a-squad-shortfall-through-the-erp.md) |
| AC-4 | **Given** a part of the Drone model missing from the stock **when** the Assistant proposes the Manufacturing order **then** it also proposes a Purchase order for that part, and the ready date follows its delivery | [📏 BR-031](../business-rules/BR-031-a-squad-shortfall-is-covered-through-the-erp.md) | [🎬 UC-033](../use-cases/UC-033-cover-a-squad-shortfall-through-the-erp.md) |
| AC-5 | **Given** a Drone model bought from its maker **when** the Fleet falls short of it **then** the Assistant proposes a Purchase order for the Drone | [📏 BR-031](../business-rules/BR-031-a-squad-shortfall-is-covered-through-the-erp.md) | [🎬 UC-033](../use-cases/UC-033-cover-a-squad-shortfall-through-the-erp.md) |
| AC-6 | **Given** no ERP connected **when** the Fleet falls short **then** the shortfall is shown with the smaller Squad, and the Assistant says why it cannot propose an order | [📏 BR-031](../business-rules/BR-031-a-squad-shortfall-is-covered-through-the-erp.md) | [🎬 UC-033](../use-cases/UC-033-cover-a-squad-shortfall-through-the-erp.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| ERP | Swarm reaches every ERP the same way, through one ERP port: Clients and Sites, quotes and invoices, Fleet assets and costs, staff time, Manufacturing orders and Purchase orders. Simple-ERP is the first; it is also reachable through MCP and A2A |
| Squad sizing | The Mission planner plans how many Drones of which types a Mission needs, and the flight profile from that |
| Covering a shortfall | A Manufacturing order, a Purchase order of the missing spares and raw materials, the earliest date the Squad can be complete, or a smaller Squad with its trade-off |
| Who builds Drones | Both: some Drone models are built in-house by the Operator, others bought from makers; the ERP knows which |
| Clients and Sites | Kept in step both ways: the ERP is the master of Clients (names, contacts, billing), Swarm of Sites (boundaries, Geofence, access) |
| Quotes and invoices | A Mission request creates a draft quote in the ERP; the Mission planner prices it there and the ERP sends it to the Client; Swarm shows its state on the Mission. A delivered Mission becomes an invoice with its Deliverables as proof |
| Fleet costs | Drones, Payloads and Batteries are assets in the ERP, with their purchase, maintenance and repair costs from the Fleet records of Swarm |
| Staff time | Per Mission, for payroll and the cost of each Mission: flight time and time on the Site of each Pilot, design time of the Mission planner, and the hours each person enters |
| Simple-ERP API | Committed to be ready by 25 September 2028 ([🤝 P-10](../../roadmap/11-hardware-and-partners.md#p-10)) |
| Use cases of the flows | The flows of Clients and Sites, quotes and invoices, Fleet costs and staff time get their use cases when the ERP port is designed (T5.49) |

## <a id="out-of-scope"></a>🚫 Out of scope

- Building the API of Simple-ERP itself: Simple-ERP has its own roadmap
- The Assistant's other Connectors: [📘 FS-023: AI Assistant](FS-023-ai-assistant.md)

## <a id="open-questions"></a>❓ Open questions

> [!WARNING]
> None.

## <a id="references"></a>🔗 References

- 🧭 [Functional overview](../README.md)
- 📖 [Glossary](../../glossary.md)

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ FS-023: AI Assistant](FS-023-ai-assistant.md) · 📄 **Page 28 / 120** · [UC-001: Design a Mission ▶️](../use-cases/UC-001-design-a-mission.md)
<!-- /spec:nav-bottom -->
