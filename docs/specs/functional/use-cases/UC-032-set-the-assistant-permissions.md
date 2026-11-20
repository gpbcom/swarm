# 🎬 UC-032: Set the Assistant permissions

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ UC-031: Ask the Assistant](UC-031-ask-the-assistant.md) · 📄 **Page 60 / 120** · [UC-033: Cover a Squad shortfall through the ERP ▶️](UC-033-cover-a-squad-shortfall-through-the-erp.md)
<!-- /spec:nav-top -->

**Status:** 🟡 Draft · **Updated:** 2026-11-20

> [!NOTE]
> The [👤 Swarm administrator](../../glossary.md#per-swarm-administrator) sets the ceiling of the [🗃️ Assistant permission](../../glossary.md#ent-assistant-permission)s of an [🗃️ Operator](../../glossary.md#ent-operator), the [👤 Mission planner](../../glossary.md#per-mission-planner) sets the level of each role within it, and a [👤 Pilot](../../glossary.md#per-pilot) narrows their own levels.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [👤 Personas and entities](#actors)
2. [🚦 Preconditions](#preconditions)
3. [⚡ Trigger](#trigger)
4. [➡️ Main flow](#main-flow)
5. [🔀 Flow chart](#flowchart)
6. [🖼️ Screens](#screens)
7. [↪️ Alternative and error flows](#alternative-flows)
8. [📏 Business rules applied](#business-rules)
9. [🏁 Postconditions](#postconditions)
10. [🔗 Referenced by](#referenced-by)
<!-- /spec:summary -->

## <a id="actors"></a>👤 Personas and entities

| Name | Kind | Role in this use case |
| --- | --- | --- |
| [👤 Swarm administrator](../../glossary.md#per-swarm-administrator) | Persona | Sets the ceiling of each action for the Operator |
| [👤 Mission planner](../../glossary.md#per-mission-planner) | Persona | Sets the level of each action for each role of the Operator |
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Narrows their own levels |
| [🗃️ Operator](../../glossary.md#ent-operator) | Entity | Aerowing Services, whose Assistant permissions are set |
| [🗃️ Assistant permission](../../glossary.md#ent-assistant-permission) | Entity | One level per action and role: Off, Read, Propose or Act |
| [⚙️ Back office](../../glossary.md#sys-back-office) | System | Shows the ceiling and the levels, and refuses a level above the ceiling |

## <a id="preconditions"></a>🚦 Preconditions

1. The Operator Aerowing Services has the default Assistant permissions of a new Operator: Propose for every action its people may do ([📏 BR-028: Assistant permissions are layered](../business-rules/BR-028-assistant-permissions-are-layered.md)).
2. The Swarm administrator is signed in to **Back office · Swarm administration**.
3. Léa Martin, the Mission planner who manages the people of Aerowing Services, is signed in to its Back office.

## <a id="trigger"></a>⚡ Trigger

Aerowing Services asks to let its Fleet maintainers place Purchase orders, and to let the Assistant of its Pilots hold a Squad when the weather goes beyond the limits.

## <a id="main-flow"></a>➡️ Main flow

1. The Swarm administrator opens Aerowing Services in Swarm administration and raises the ceiling of "Place a Purchase order" and of "Hold" to Act.
2. Léa Martin opens **🔧 Settings › Assistant** in the Back office: the actions of Swarm grouped by area, one column per role, each cell Off, Read, Propose or Act, with the ceiling shown.
3. Léa Martin sets "Place a Purchase order" to Act for the Fleet maintainers, with a confirmation before each order, and "Hold" to Act for the Pilots, which the screen marks as a [🔤 Flight-critical act](../../glossary.md#term-flight-critical-act) ([📏 BR-029: Flight-critical acts need a Pilot on duty](../business-rules/BR-029-flight-critical-acts-need-a-pilot-on-duty.md)).
4. Swarm checks each level against the ceiling and saves them ([📏 BR-028: Assistant permissions are layered](../business-rules/BR-028-assistant-permissions-are-layered.md)). Every person of each role gets the new levels, and the change is recorded with Léa Martin's name.
5. The Pilot Sam Carter lowers "Hold" to Propose for himself, in the Assistant settings of his own account.

## <a id="flowchart"></a>🔀 Flow chart

```mermaid
flowchart LR
    P1(["👤 Swarm administrator"]):::persona
    P2(["👤 Mission planner"]):::persona
    P3(["👤 Pilot"]):::persona
    E1[("🗃️ Operator")]:::entity
    E2[("🗃️ Assistant permission")]:::entity
    S1[["⚙️ Back office"]]:::system
    A1["Set the ceiling of the Operator"]:::action
    A2["Set the level of each role"]:::action
    D1{"❓ Is every level within the ceiling?"}:::decision
    A3["Narrow my own levels"]:::action
    OK(["✅ Permissions in force"]):::success
    KO(["❌ Level above the ceiling refused"]):::failure

    P1 -- "sets" --> A1
    A1 -- "for" --> E1
    A1 -- "bounds" --> E2
    P2 -- "sets" --> A2
    S1 -- "shows the ceiling in" --> A2
    A2 --> D1
    D1 -- "yes" --> OK
    D1 -- "no" --> KO
    OK -- "applies" --> E2
    P3 -- "narrows" --> A3
    A3 -- "lowers" --> E2

    classDef persona fill:#dbeafe,stroke:#1d4ed8,stroke-width:2px,color:#0b1f4d
    classDef entity fill:#dcfce7,stroke:#15803d,stroke-width:2px,color:#052e16
    classDef system fill:#ede9fe,stroke:#6d28d9,stroke-width:2px,color:#2e1065
    classDef action fill:#f1f5f9,stroke:#475569,color:#0f172a
    classDef decision fill:#fef3c7,stroke:#b45309,color:#451a03
    classDef success fill:#d1fae5,stroke:#047857,color:#022c22
    classDef failure fill:#fee2e2,stroke:#b91c1c,color:#450a0a
```

## <a id="screens"></a>🖼️ Screens

One row per state of the flow chart: every action, success and failure node. Click a screen to open it full size. A state with nothing to show reads `➖ No screen: <why>`.

| State | Persona | Entity | Source | Screen |
| --- | --- | --- | --- | --- |
| <a id="screen-a1"></a>A1: Set the ceiling of the Operator | [👤 Swarm administrator](../../glossary.md#per-swarm-administrator) | [🗃️ Operator](../../glossary.md#ent-operator) | ✏️ Mock-up | [![UC-032 A1: Set the ceiling of the Operator](../../screens/UC-032/a1.png)](../../screens/UC-032/a1.png) [![UC-032 A1: Set the ceiling of the Operator (dark)](../../screens/UC-032/a1.dark.png)](../../screens/UC-032/a1.dark.png) |
| <a id="screen-a2"></a>A2: Set the level of each role | [👤 Mission planner](../../glossary.md#per-mission-planner) | [🗃️ Assistant permission](../../glossary.md#ent-assistant-permission) | ✏️ Mock-up | [![UC-032 A2: Set the level of each role](../../screens/UC-032/a2.png)](../../screens/UC-032/a2.png) [![UC-032 A2: Set the level of each role (dark)](../../screens/UC-032/a2.dark.png)](../../screens/UC-032/a2.dark.png) |
| <a id="screen-a3"></a>A3: Narrow my own levels | [👤 Pilot](../../glossary.md#per-pilot) | [🗃️ Assistant permission](../../glossary.md#ent-assistant-permission) | ✏️ Mock-up | [![UC-032 A3: Narrow my own levels](../../screens/UC-032/a3.png)](../../screens/UC-032/a3.png) [![UC-032 A3: Narrow my own levels (dark)](../../screens/UC-032/a3.dark.png)](../../screens/UC-032/a3.dark.png) |
| <a id="screen-ok"></a>OK: Permissions in force | [👤 Mission planner](../../glossary.md#per-mission-planner) | [🗃️ Assistant permission](../../glossary.md#ent-assistant-permission) | ✏️ Mock-up | [![UC-032 OK: Permissions in force](../../screens/UC-032/ok.png)](../../screens/UC-032/ok.png) [![UC-032 OK: Permissions in force (dark)](../../screens/UC-032/ok.dark.png)](../../screens/UC-032/ok.dark.png) |
| <a id="screen-ko"></a>KO: Level above the ceiling refused | [👤 Mission planner](../../glossary.md#per-mission-planner) | [🗃️ Assistant permission](../../glossary.md#ent-assistant-permission) | ✏️ Mock-up | [![UC-032 KO: Level above the ceiling refused](../../screens/UC-032/ko.png)](../../screens/UC-032/ko.png) [![UC-032 KO: Level above the ceiling refused (dark)](../../screens/UC-032/ko.dark.png)](../../screens/UC-032/ko.dark.png) |

## <a id="alternative-flows"></a>↪️ Alternative and error flows

| # | At step | Condition | What happens |
| --- | --- | --- | --- |
| A1 | 3 | Léa Martin sets an action above the ceiling, such as "Launch" at Act while its ceiling is Propose | Refused: the cell stays at the ceiling and the screen says who can raise it (KO) |
| A2 | 5 | Sam Carter tries to raise one of his levels above the level of the Pilot role | Refused: a person may only lower their own levels |
| A3 | 1 | The Swarm administrator lowers a ceiling below the level a role has | The level of that role comes down to the new ceiling, and Léa Martin is told which levels changed |
| A4 | 3 | An action is set to Act with a confirmation | The Assistant prepares the act and asks the person for a one-tap confirmation before doing it |

## <a id="business-rules"></a>📏 Business rules applied

| Rule | Where it applies |
| --- | --- |
| [📏 BR-028: Assistant permissions are layered](../business-rules/BR-028-assistant-permissions-are-layered.md) | Steps 1 to 5, A1 to A3 |
| [📏 BR-029: Flight-critical acts need a Pilot on duty](../business-rules/BR-029-flight-critical-acts-need-a-pilot-on-duty.md) | Step 3 |

## <a id="postconditions"></a>🏁 Postconditions

- ✅ **Success:** Fleet maintainers' Assistant may place Purchase orders after a confirmation, the Pilots' Assistant may hold a Squad under the conditions of BR-029, Sam Carter keeps "Hold" at Propose for himself, and each change is recorded with the name of the person who made it.
- ❌ **Failure:** The level above the ceiling is refused; the levels in force do not change.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-023: AI Assistant](../features/FS-023-ai-assistant.md)
- [🎬 UC-034: Let the Assistant hold a Squad](UC-034-let-the-assistant-hold-a-squad.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ UC-031: Ask the Assistant](UC-031-ask-the-assistant.md) · 📄 **Page 60 / 120** · [UC-033: Cover a Squad shortfall through the ERP ▶️](UC-033-cover-a-squad-shortfall-through-the-erp.md)
<!-- /spec:nav-bottom -->
