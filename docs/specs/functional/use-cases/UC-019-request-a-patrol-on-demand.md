# 🎬 UC-019: Request a Patrol on demand

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ UC-018: Respond to a Site Alarm](UC-018-respond-to-a-site-alarm.md) · 📄 **Page 45 / 108** · [UC-020: Review the Defects of an Inspection ▶️](UC-020-review-the-defects-of-an-inspection.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> The [👤 Site agent](../../glossary.md#per-site-agent) requests a look at a point of the [🗃️ Site](../../glossary.md#ent-site) in the [⚙️ Client portal](../../glossary.md#sys-client-portal), and gets a [🗃️ Mission](../../glossary.md#ent-mission) only if a [👤 Pilot](../../glossary.md#per-pilot) accepts it in [⚙️ Ground control](../../glossary.md#sys-ground-control) within the waiting time.

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
| [👤 Site agent](../../glossary.md#per-site-agent) | Persona | Inès Garcia of Northgate Logistics: requests a look at the car park, never pilots |
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Sam Carter: accepts or declines the request |
| [🗃️ Site](../../glossary.md#ent-site) | Entity | Northgate warehouse, with its car park and its Docks |
| [🗃️ Mission](../../glossary.md#ent-mission) | Entity | The request: Mission: Requested, then Mission: Planned when a Pilot accepts it, or Mission: Declined |
| [🗃️ Patrol route](../../glossary.md#ent-patrol-route) | Entity | The path and the point to watch, the car park, on which the accepted Mission is planned |
| [⚙️ Client portal](../../glossary.md#sys-client-portal) | System | Takes the request and shows its answer to the Site agent |
| [⚙️ Ground control](../../glossary.md#sys-ground-control) | System | Shows the request to the Pilot |

## <a id="preconditions"></a>🚦 Preconditions

1. The Site agent Inès Garcia has access to the Client portal for the Site Northgate warehouse of Northgate Logistics.
2. The [🗃️ Operator](../../glossary.md#ent-operator) Aerowing Services flies [🔤 Patrols](../../glossary.md#term-patrol) at Northgate warehouse, from its [🗃️ Docks](../../glossary.md#ent-dock).
3. The Pilot Sam Carter is on duty in Ground control.

## <a id="trigger"></a>⚡ Trigger

On 3 December 2026 at 10:05, the Site agent sees an unknown van in the car park and opens **➕ Order** in the Client portal.

## <a id="main-flow"></a>➡️ Main flow

1. The Site agent chooses the point to watch on the map of the Site, the car park, and adds a note for the Pilot.
2. The Site agent sends the request. The Client portal creates the Mission "Patrol on demand: car park of Northgate" in the state Mission: Requested and sends it to the Pilots on duty of the Operator. The request waits 10 minutes for a Pilot, a waiting time the Operator can change ([📏 BR-019](../business-rules/BR-019-site-agents-request-never-pilot.md)).
3. The Site agent sees the request waiting for a Pilot. The Client portal offers no command over any Drone or Squad.
4. The Pilot sees the request in Ground control, with the point to watch, the note and the Drones Ready in the Docks of the Site.
5. The Pilot accepts the request within the 10 minutes. The Mission becomes Mission: Planned on its Patrol route, and the Pilot prepares the flight ([🎬 UC-003: Run the Pre-flight check and launch](UC-003-run-the-pre-flight-check-and-launch.md)).
6. The Site agent sees in the Client portal that the Pilot accepted the request.

## <a id="flowchart"></a>🔀 Flow chart

```mermaid
flowchart LR
    P1(["👤 Site agent"]):::persona
    P2(["👤 Pilot"]):::persona
    S1[["⚙️ Client portal"]]:::system
    S2[["⚙️ Ground control"]]:::system
    E1[("🗃️ Site")]:::entity
    E2[("🗃️ Mission")]:::entity
    E3[("🗃️ Patrol route")]:::entity
    A1["Request a look at the car park"]:::action
    A2["Wait for a Pilot"]:::action
    A3["Accept or decline the request"]:::action
    D1{"❓ Accepted within 10 minutes?"}:::decision
    OK(["✅ Request accepted"]):::success
    KO(["❌ Request declined"]):::failure

    P1 -- "opens Order in" --> S1
    P1 -- "points to the car park" --> A1
    A1 -- "on the map of" --> E1
    A1 -- "creates, Requested" --> E2
    A1 --> A2
    E2 -- "is shown in" --> S2
    P1 -- "waits up to 10 minutes" --> A2
    S2 -- "shows the request" --> A3
    P2 -- "reviews" --> A3
    A3 --> D1
    D1 -- "yes" --> OK
    D1 -- "no" --> KO
    OK -- "plans the Mission on" --> E3
    OK -- "is shown in" --> S1
    KO -- "is shown in" --> S1
    KO -- "is told to every Pilot on duty" --> P2

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
| <a id="screen-a1"></a>A1: Request a look at the car park | [👤 Site agent](../../glossary.md#per-site-agent) | [🗃️ Site](../../glossary.md#ent-site) | ✏️ Mock-up | [![UC-019 A1: Request a look at the car park](../../screens/UC-019/a1.png)](../../screens/UC-019/a1.png) [![UC-019 A1: Request a look at the car park (dark)](../../screens/UC-019/a1.dark.png)](../../screens/UC-019/a1.dark.png) |
| <a id="screen-a2"></a>A2: Wait for a Pilot | [👤 Site agent](../../glossary.md#per-site-agent) | [🔄 Mission: Requested](../../glossary.md#st-mission-requested) | ✏️ Mock-up | [![UC-019 A2: Wait for a Pilot](../../screens/UC-019/a2.png)](../../screens/UC-019/a2.png) [![UC-019 A2: Wait for a Pilot (dark)](../../screens/UC-019/a2.dark.png)](../../screens/UC-019/a2.dark.png) |
| <a id="screen-a3"></a>A3: Accept or decline the request | [👤 Pilot](../../glossary.md#per-pilot) | [🔄 Mission: Requested](../../glossary.md#st-mission-requested) | ✏️ Mock-up | [![UC-019 A3: Accept or decline the request](../../screens/UC-019/a3.png)](../../screens/UC-019/a3.png) [![UC-019 A3: Accept or decline the request (dark)](../../screens/UC-019/a3.dark.png)](../../screens/UC-019/a3.dark.png) |
| <a id="screen-ok"></a>OK: Request accepted | [👤 Site agent](../../glossary.md#per-site-agent) | [🔄 Mission: Planned](../../glossary.md#st-mission-planned) | ✏️ Mock-up | [![UC-019 OK: Request accepted](../../screens/UC-019/ok.png)](../../screens/UC-019/ok.png) [![UC-019 OK: Request accepted (dark)](../../screens/UC-019/ok.dark.png)](../../screens/UC-019/ok.dark.png) |
| <a id="screen-ko"></a>KO: Request declined | [👤 Site agent](../../glossary.md#per-site-agent) | [🔄 Mission: Declined](../../glossary.md#st-mission-declined) | ✏️ Mock-up | [![UC-019 KO: Request declined](../../screens/UC-019/ko.png)](../../screens/UC-019/ko.png) [![UC-019 KO: Request declined (dark)](../../screens/UC-019/ko.dark.png)](../../screens/UC-019/ko.dark.png) |

## <a id="alternative-flows"></a>↪️ Alternative and error flows

| # | At step | Condition | What happens |
| --- | --- | --- | --- |
| A1 | 5 | The Pilot declines the request | ❌ The Mission is Mission: Declined and will not fly. The Site agent and every Pilot on duty are told |
| A2 | 3 | The Site agent tries to launch, command or change a Drone or the Squad | Not possible: the Client portal has no such command ([📏 BR-019](../business-rules/BR-019-site-agents-request-never-pilot.md)) |
| A3 | 4 | No Pilot answers within 10 minutes | ❌ The Mission is Mission: Declined and will not fly. The Site agent and every Pilot on duty are told ([📏 BR-019](../business-rules/BR-019-site-agents-request-never-pilot.md)) |

## <a id="business-rules"></a>📏 Business rules applied

| Rule | Where it applies |
| --- | --- |
| [📏 BR-019: Site agents request, never pilot](../business-rules/BR-019-site-agents-request-never-pilot.md) | Steps 2, 3 and 5: the Site agent requests and never commands; the request becomes a Mission only when a Pilot accepts it within the 10 minutes, otherwise it is Declined |

## <a id="postconditions"></a>🏁 Postconditions

- ✅ **Success:** the Pilot has accepted the request. The Mission is Mission: Planned on its Patrol route, and the Pilot prepares it. The Site agent sees that it was accepted, and by whom.
- ❌ **Failure:** a Pilot declined the request, or no Pilot answered within 10 minutes. The Mission is Mission: Declined, nothing flies, and the Site agent and every Pilot on duty are told.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-015: Patrol](../features/FS-015-patrol.md)
- [🎬 UC-018: Respond to a Site Alarm](UC-018-respond-to-a-site-alarm.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ UC-018: Respond to a Site Alarm](UC-018-respond-to-a-site-alarm.md) · 📄 **Page 45 / 108** · [UC-020: Review the Defects of an Inspection ▶️](UC-020-review-the-defects-of-an-inspection.md)
<!-- /spec:nav-bottom -->
