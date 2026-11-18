# 🎬 UC-030: Focus on a Drone

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ UC-029: Create an Operator](UC-029-create-an-operator.md) · 📄 **Page 56 / 108** · [BR-001: Geofence and Altitude ceiling ▶️](../business-rules/BR-001-geofence-and-altitude-ceiling.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> The [👤 Pilot](../../glossary.md#per-pilot) sees one [🗃️ Drone](../../glossary.md#ent-drone) large in the [🔤 Focus view](../../glossary.md#term-focus-view) of [⚙️ Ground control](../../glossary.md#sys-ground-control), opened by an event the Drone detects or by a click, without losing sight of the [🗃️ Squad](../../glossary.md#ent-squad), the critical Alerts or the safety controls.

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
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Watches the Focus view, opens a queued event, goes back to the previous view |
| [🗃️ Drone](../../glossary.md#ent-drone) | Entity | Detects an event, then is shown large with its video and Telemetry |
| [🗃️ Squad](../../glossary.md#ent-squad) | Entity | Stays visible, smaller, on the map and in the Squad panel |
| [⚙️ Ground control](../../glossary.md#sys-ground-control) | System | Opens the Focus view, queues new events, keeps critical Alerts and the safety controls uncovered |

## <a id="preconditions"></a>🚦 Preconditions

1. The [🗃️ Mission](../../glossary.md#ent-mission) is [🔄 Mission: Flying](../../glossary.md#st-mission-flying). Sample: M-2026-0412 Inspection of Les Vignes, Squad Alpha and Bravo (RGB camera), Charlie and Delta (thermal camera).
2. The Pilot is [🔄 Pilot: Supervising](../../glossary.md#st-pilot-supervising) in the 🛰️ Flight view ([🎬 UC-025: Monitor a Mission in Ground control](UC-025-monitor-a-mission-in-ground-control.md)), and no Focus view is open.
3. The Pilot has set the severity from which a detected event opens the Focus view. Severities are those of the Alerts: Information, Warning, Critical; the default setting is Warning and above.

## <a id="trigger"></a>⚡ Trigger

A Drone detects an event (a person, a fire, a hot spot or an obstacle) at or above the Pilot's severity setting, or the Pilot clicks a Drone on the map or its tile in the [🔤 Mosaic](../../glossary.md#term-mosaic).

## <a id="main-flow"></a>➡️ Main flow

1. Charlie, [🔄 Drone: Airborne](../../glossary.md#st-drone-airborne), detects a hot spot of severity Warning, at the Pilot's setting.
2. Ground control opens the Focus view of Charlie: its live video and [🔤 Telemetry](../../glossary.md#term-telemetry) large, the map and the Squad still visible but smaller. Critical [🔤 Alerts](../../glossary.md#term-alert), ✋ Hold the Squad and 🛑 Abort are never covered ([📏 BR-027](../business-rules/BR-027-the-pilot-s-attention-is-preserved.md), [📏 BR-023](../business-rules/BR-023-fixed-safety-controls.md)).
3. While the Focus view of Charlie is open, Bravo detects a person. Ground control does not switch: Bravo's event queues with a badge. Only one Focus view is open at a time.
4. The Pilot clicks the badge. The Focus view switches to Bravo; Charlie's event stays in the Alerts area.
5. The Pilot goes back to the previous view in one action, with Back to the Flight view. The Flight view is shown as it was.

## <a id="flowchart"></a>🔀 Flow chart

```mermaid
flowchart LR
    P1(["👤 Pilot"]):::persona
    S1[["⚙️ Ground control"]]:::system
    E1[("🗃️ Drone")]:::entity
    E2[("🗃️ Squad")]:::entity
    D1{"❓ At or above the severity setting?"}:::decision
    A1["Open the Focus view"]:::action
    A2["Queue the next event"]:::action
    A3["Switch to the queued Drone"]:::action
    OK(["✅ Back to the previous view"]):::success
    KO(["❌ Event listed, no Focus view"]):::failure

    E1 -- "detects an event" --> D1
    D1 -- "yes" --> A1
    D1 -- "no" --> KO
    P1 -- "clicks the Drone or its tile" --> A1
    S1 -- "opens, never covering critical Alerts" --> A1
    A1 -- "keeps visible, smaller" --> E2
    A1 --> A2
    E1 -- "detects another event" --> A2
    A2 --> A3
    P1 -- "clicks the badge" --> A3
    A3 --> OK
    P1 -- "goes back in one action" --> OK

    classDef persona fill:#dbeafe,stroke:#1d4ed8,stroke-width:2px,color:#0b1f4d
    classDef entity fill:#dcfce7,stroke:#15803d,stroke-width:2px,color:#052e16
    classDef system fill:#ede9fe,stroke:#6d28d9,stroke-width:2px,color:#2e1065
    classDef action fill:#f1f5f9,stroke:#475569,color:#0f172a
    classDef decision fill:#fef3c7,stroke:#b45309,color:#451a03
    classDef success fill:#d1fae5,stroke:#047857,color:#022c22
    classDef failure fill:#fee2e2,stroke:#b91c1c,color:#450a0a
```

## <a id="screens"></a>🖼️ Screens

One row per state of the flow chart: every action, success and failure node. Each state shows its light then its dark screen; click one to open it full size. A state with nothing to show reads `➖ No screen: <why>`.

| State | Persona | Entity | Source | Screen |
| --- | --- | --- | --- | --- |
| <a id="screen-a1"></a>A1: Open the Focus view | [🔄 Pilot: Supervising](../../glossary.md#st-pilot-supervising) | [🔄 Drone: Airborne](../../glossary.md#st-drone-airborne)<br>[🗃️ Squad](../../glossary.md#ent-squad) | ✏️ Mock-up | [![UC-030 A1: Open the Focus view](../../screens/UC-030/a1.png)](../../screens/UC-030/a1.png) [![UC-030 A1: Open the Focus view (dark)](../../screens/UC-030/a1.dark.png)](../../screens/UC-030/a1.dark.png) |
| <a id="screen-a2"></a>A2: Queue the next event | [🔄 Pilot: Supervising](../../glossary.md#st-pilot-supervising) | [🔄 Drone: Airborne](../../glossary.md#st-drone-airborne) | ✏️ Mock-up | [![UC-030 A2: Queue the next event](../../screens/UC-030/a2.png)](../../screens/UC-030/a2.png) [![UC-030 A2: Queue the next event (dark)](../../screens/UC-030/a2.dark.png)](../../screens/UC-030/a2.dark.png) |
| <a id="screen-a3"></a>A3: Switch to the queued Drone | [🔄 Pilot: Supervising](../../glossary.md#st-pilot-supervising) | [🔄 Drone: Airborne](../../glossary.md#st-drone-airborne) | ✏️ Mock-up | [![UC-030 A3: Switch to the queued Drone](../../screens/UC-030/a3.png)](../../screens/UC-030/a3.png) [![UC-030 A3: Switch to the queued Drone (dark)](../../screens/UC-030/a3.dark.png)](../../screens/UC-030/a3.dark.png) |
| <a id="screen-ok"></a>OK: Back to the previous view | [🔄 Pilot: Supervising](../../glossary.md#st-pilot-supervising) | [🗃️ Squad](../../glossary.md#ent-squad) | ✏️ Mock-up | [![UC-030 OK: Back to the previous view](../../screens/UC-030/ok.png)](../../screens/UC-030/ok.png) [![UC-030 OK: Back to the previous view (dark)](../../screens/UC-030/ok.dark.png)](../../screens/UC-030/ok.dark.png) |
| <a id="screen-ko"></a>KO: Event listed, no Focus view | [🔄 Pilot: Supervising](../../glossary.md#st-pilot-supervising) | [🔄 Drone: Airborne](../../glossary.md#st-drone-airborne) | ✏️ Mock-up | [![UC-030 KO: Event listed, no Focus view](../../screens/UC-030/ko.png)](../../screens/UC-030/ko.png) [![UC-030 KO: Event listed, no Focus view (dark)](../../screens/UC-030/ko.dark.png)](../../screens/UC-030/ko.dark.png) |

## <a id="alternative-flows"></a>↪️ Alternative and error flows

| # | At step | Condition | What happens |
| --- | --- | --- | --- |
| A1 | 1 | The Pilot clicks a Drone on the map, or its tile in the Mosaic | The Focus view of that Drone opens, as in step 2. |
| A2 | 1 | The detected event is below the Pilot's severity setting, such as an obstacle of severity Information seen by Delta | No Focus view opens: the event is listed in the Alerts area, where the Pilot can open it with a click. |
| A3 | 3 | A critical Alert arrives while the Focus view is open | The Alert shows in full above the Focus view, with ✋ Hold the Squad and 🛑 Abort still in the title bar ([📏 BR-027](../business-rules/BR-027-the-pilot-s-attention-is-preserved.md)). |

## <a id="business-rules"></a>📏 Business rules applied

| Rule | Where it applies |
| --- | --- |
| [📏 BR-027: The Pilot's attention is preserved](../business-rules/BR-027-the-pilot-s-attention-is-preserved.md) | Steps 2 to 5 and alternative A3: one Focus view at a time, new events queued with a badge, the map and the Squad visible, critical Alerts never covered, the previous view one action away |
| [📏 BR-023: Fixed safety controls](../business-rules/BR-023-fixed-safety-controls.md) | Steps 2 to 5: Hold the Squad and abort stay in the title bar of the Focus view |

## <a id="postconditions"></a>🏁 Postconditions

- ✅ **Success:** the Pilot has looked at each Drone that needed attention, one at a time, and is back in the view used before, with no event lost: each is in the Alerts area.
- ❌ **Failure:** an event below the severity setting does not open the Focus view; it is listed in the Alerts area and the Pilot's view does not change.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-021: Ground control monitoring](../features/FS-021-ground-control-monitoring.md)
- [🎬 UC-025: Monitor a Mission in Ground control](UC-025-monitor-a-mission-in-ground-control.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ UC-029: Create an Operator](UC-029-create-an-operator.md) · 📄 **Page 56 / 108** · [BR-001: Geofence and Altitude ceiling ▶️](../business-rules/BR-001-geofence-and-altitude-ceiling.md)
<!-- /spec:nav-bottom -->
