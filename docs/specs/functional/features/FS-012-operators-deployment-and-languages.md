# 📘 FS-012: Operators, deployment and languages

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-011: Drone adapters](FS-011-drone-adapters.md) · 📄 **Page 16 / 108** · [FS-013: Light shows ▶️](FS-013-light-shows.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> Swarm serves many [🗃️ Operators](../../glossary.md#ent-operator) in the cloud, or one company on premises, and speaks English, French, German and Spanish.

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

One product for drone service companies and for organisations that must keep their data at home. Each Operator is isolated; its [👤 Mission planner](../../glossary.md#per-mission-planner) invites its [👤 Clients](../../glossary.md#per-client) and their [👤 Site agents](../../glossary.md#per-site-agent). Every person chooses their language.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Swarm administrator](../../glossary.md#per-swarm-administrator) | Persona | Creates Operators and their first accounts |
| [👤 Mission planner](../../glossary.md#per-mission-planner) | Persona | Invites Clients |
| [👤 Client](../../glossary.md#per-client) | Persona | Invited to the Client portal |
| [🗃️ Operator](../../glossary.md#ent-operator) | Entity | Isolated organisation |
| [⚙️ Back office](../../glossary.md#sys-back-office) | System | Manages Operators and access |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-008: Operator isolation](../business-rules/BR-008-operator-isolation.md) | Operator isolation |
| [📏 BR-017: Every screen in four languages](../business-rules/BR-017-every-screen-in-four-languages.md) | Every screen in four languages |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-029: Create an Operator](../use-cases/UC-029-create-an-operator.md) | [👤 Swarm administrator](../../glossary.md#per-swarm-administrator) |
| [🎬 UC-015: Invite a Client to the Client portal](../use-cases/UC-015-invite-a-client-to-the-client-portal.md) | [👤 Mission planner](../../glossary.md#per-mission-planner), [👤 Client](../../glossary.md#per-client) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** two Operators in the cloud **when** one searches for Missions **then** they never see the other's | [📏 BR-008](../business-rules/BR-008-operator-isolation.md) | [🎬 UC-015](../use-cases/UC-015-invite-a-client-to-the-client-portal.md) |
| AC-2 | **Given** an invited Client who chose German **when** they open the Client portal **then** every screen is in German | [📏 BR-017](../business-rules/BR-017-every-screen-in-four-languages.md) | [🎬 UC-015](../use-cases/UC-015-invite-a-client-to-the-client-portal.md) |
| AC-3 | **Given** a new drone service company **when** the Swarm administrator creates its Operator **then** its first Mission planner is invited and sees no other Operator's data | [📏 BR-008](../business-rules/BR-008-operator-isolation.md) | [🎬 UC-029](../use-cases/UC-029-create-an-operator.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Creating Operators | The [👤 Swarm administrator](../../glossary.md#per-swarm-administrator) creates each Operator and its first Mission planner; in the cloud a member of the Swarm team, on premises the company's IT administrator |
| Required to create an Operator | Name, deployment (cloud or on premises), at least one Jurisdiction, the first Mission planner's e-mail. The LLM provider (Claude in the cloud) and the Anchoring (qualified timestamping authority) have defaults |
| Notifications | Every [🔤 Notification](../../glossary.md#term-notification) appears in the part of Swarm the person uses (🔔) and by e-mail; Site agents and Pilots on duty also get it by push on a mobile |

## <a id="out-of-scope"></a>🚫 Out of scope

- Billing of Operators

## <a id="open-questions"></a>❓ Open questions

> [!WARNING]
> None.

## <a id="references"></a>🔗 References

- 🧭 [Functional overview](../README.md)
- 📖 [Glossary](../../glossary.md)
- 🎤 [Interview decisions](../../../research/interview.md)
- 🔭 [Market landscape](../../../research/landscape.md)

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ FS-011: Drone adapters](FS-011-drone-adapters.md) · 📄 **Page 16 / 108** · [FS-013: Light shows ▶️](FS-013-light-shows.md)
<!-- /spec:nav-bottom -->
