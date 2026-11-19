# 🎬 UC-002: Simulate a Mission

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ UC-001: Design a Mission](UC-001-design-a-mission.md) · 📄 **Page 28 / 109** · [UC-003: Run the Pre-flight check and launch ▶️](UC-003-run-the-pre-flight-check-and-launch.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> The [👤 Mission planner](../../glossary.md#per-mission-planner) runs a Planned [🗃️ Mission](../../glossary.md#ent-mission) in the [⚙️ Simulator](../../glossary.md#sys-simulator) from the [⚙️ Mission studio](../../glossary.md#sys-mission-studio), and gets its coverage, timing, battery use and conflicts, then accepts the result or sends the Mission back to Draft.

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
| [👤 Mission planner](../../glossary.md#per-mission-planner) | Persona | Starts the simulation, reviews the results, accepts them or sends the Mission back to Draft |
| [🗃️ Mission](../../glossary.md#ent-mission) | Entity | Simulated while Planned; stays Planned, or goes back to Draft |
| [🗃️ Squad](../../glossary.md#ent-squad) | Entity | Flown as a virtual Squad, never as real Drones |
| [🗃️ Flight log](../../glossary.md#ent-flight-log) | Entity | Records the simulated flight, marked Simulated |
| [⚙️ Mission studio](../../glossary.md#sys-mission-studio) | System | Starts the simulation and shows its results |
| [⚙️ Simulator](../../glossary.md#sys-simulator) | System | Flies the virtual Squad with the real flight software of each Drone model |

## <a id="preconditions"></a>🚦 Preconditions

1. The Mission M-2026-0412 Inspection of Les Vignes is [🔄 Mission: Planned](../../glossary.md#st-mission-planned) ([🎬 UC-001](UC-001-design-a-mission.md)).
2. The Mission planner Léa Martin of Aerowing Services has it open in the Mission studio.

## <a id="trigger"></a>⚡ Trigger

The Mission planner opens **🕹️ Simulate** and starts the simulation.

## <a id="main-flow"></a>➡️ Main flow

1. The Mission planner starts the simulation of the Planned Mission for its time slot, 3 December 2026 from 10:00.
2. The Simulator flies a virtual Squad of the same [🗃️ Drones](../../glossary.md#ent-drone) (Alpha, Bravo, Charlie), each with the real flight software of its [🗃️ Drone model](../../glossary.md#ent-drone-model). No command reaches a real Drone, and the Flight log is marked Simulated ([📏 BR-014](../business-rules/BR-014-simulation-isolation.md)).
3. The Mission studio shows the virtual Squad on the map as it flies, with the area covered, the simulated time and the battery of each Drone.
4. At the end, the Mission studio shows the results: coverage, duration, battery use per Drone, and the conflicts found, such as two Drones closer than the [🔤 Separation distance](../../glossary.md#term-separation-distance) ([📏 BR-002](../business-rules/BR-002-separation-distance.md)).
5. No conflict is found: the Mission planner accepts the result. Swarm records who accepted it, and the Mission stays Planned, ready for the [🗃️ Pre-flight check](../../glossary.md#ent-pre-flight-check).

## <a id="flowchart"></a>🔀 Flow chart

```mermaid
flowchart LR
    P1(["👤 Mission planner"]):::persona
    S1[["⚙️ Mission studio"]]:::system
    S2[["⚙️ Simulator"]]:::system
    E1[("🗃️ Mission")]:::entity
    E2[("🗃️ Squad")]:::entity
    E3[("🗃️ Flight log")]:::entity
    A1["Start the simulation"]:::action
    A2["Fly the virtual Squad"]:::action
    A3["Review coverage, timing, battery and conflicts"]:::action
    D1{"❓ No conflict, and the result accepted?"}:::decision
    OK(["✅ Result accepted, Mission stays Planned"]):::success
    KO(["❌ Conflict found, Mission sent back to Draft"]):::failure

    P1 -- "starts" --> A1
    A1 -- "reads the Planned" --> E1
    A1 -- "hands the Mission to" --> S2
    S2 -- "flies" --> A2
    A2 -- "uses a virtual" --> E2
    A2 -- "writes, marked Simulated" --> E3
    A2 --> A3
    S1 -- "shows the results" --> A3
    P1 -- "reviews" --> A3
    A3 --> D1
    D1 -- "yes" --> OK
    D1 -- "no" --> KO
    KO -- "sets back to Draft" --> E1

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
| <a id="screen-a1"></a>A1: Start the simulation | [👤 Mission planner](../../glossary.md#per-mission-planner) | [🔄 Mission: Planned](../../glossary.md#st-mission-planned) | ✏️ Mock-up | [![UC-002 A1: Start the simulation](../../screens/UC-002/a1.png)](../../screens/UC-002/a1.png) [![UC-002 A1: Start the simulation (dark)](../../screens/UC-002/a1.dark.png)](../../screens/UC-002/a1.dark.png) |
| <a id="screen-a2"></a>A2: Fly the virtual Squad | [👤 Mission planner](../../glossary.md#per-mission-planner) | [🗃️ Squad](../../glossary.md#ent-squad)<br>[🗃️ Flight log](../../glossary.md#ent-flight-log) | ✏️ Mock-up | [![UC-002 A2: Fly the virtual Squad](../../screens/UC-002/a2.png)](../../screens/UC-002/a2.png) [![UC-002 A2: Fly the virtual Squad (dark)](../../screens/UC-002/a2.dark.png)](../../screens/UC-002/a2.dark.png) |
| <a id="screen-a3"></a>A3: Review coverage, timing, battery and conflicts | [👤 Mission planner](../../glossary.md#per-mission-planner) | [🔄 Mission: Planned](../../glossary.md#st-mission-planned) | ✏️ Mock-up | [![UC-002 A3: Review coverage, timing, battery and conflicts](../../screens/UC-002/a3.png)](../../screens/UC-002/a3.png) [![UC-002 A3: Review coverage, timing, battery and conflicts (dark)](../../screens/UC-002/a3.dark.png)](../../screens/UC-002/a3.dark.png) |
| <a id="screen-ok"></a>OK: Result accepted, Mission stays Planned | [👤 Mission planner](../../glossary.md#per-mission-planner) | [🔄 Mission: Planned](../../glossary.md#st-mission-planned) | ✏️ Mock-up | [![UC-002 OK: Result accepted, Mission stays Planned](../../screens/UC-002/ok.png)](../../screens/UC-002/ok.png) [![UC-002 OK: Result accepted, Mission stays Planned (dark)](../../screens/UC-002/ok.dark.png)](../../screens/UC-002/ok.dark.png) |
| <a id="screen-ko"></a>KO: Conflict found, Mission sent back to Draft | [👤 Mission planner](../../glossary.md#per-mission-planner) | [🔄 Mission: Draft](../../glossary.md#st-mission-draft) | ✏️ Mock-up | [![UC-002 KO: Conflict found, Mission sent back to Draft](../../screens/UC-002/ko.png)](../../screens/UC-002/ko.png) [![UC-002 KO: Conflict found, Mission sent back to Draft (dark)](../../screens/UC-002/ko.dark.png)](../../screens/UC-002/ko.dark.png) |

## <a id="alternative-flows"></a>↪️ Alternative and error flows

| # | At step | Condition | What happens |
| --- | --- | --- | --- |
| A1 | 4 | Alpha and Bravo come 2.1 m apart at 10:14:20, under the Separation distance of 3 m of the Mission | The conflict is shown on the map and in the results; the Mission planner sends the Mission back to Draft to change the routes (KO) ([📏 BR-002](../business-rules/BR-002-separation-distance.md)) |
| A2 | 4 | A Drone would land with less than its landing reserve (20 % battery by default, an Operator setting), or the area is not fully covered | The result names the Drone or the gap; the Mission planner sends the Mission back to Draft (KO) |
| A3 | 5 | The Mission planner is not satisfied with the result, even without a conflict | The Mission planner sends the Mission back to Draft (KO) |
| A4 | 2 | The simulated Mission tries to address a real Drone | The command is refused and logged ([📏 BR-014](../business-rules/BR-014-simulation-isolation.md)) |
| A5 | KO | The Mission planner changes the routes and saves | The Mission is checked again ([🎬 UC-001](UC-001-design-a-mission.md)) and can be simulated again once Planned |

## <a id="business-rules"></a>📏 Business rules applied

| Rule | Where it applies |
| --- | --- |
| [📏 BR-014: Simulation isolation](../business-rules/BR-014-simulation-isolation.md) | Step 2, A4 |
| [📏 BR-002: Separation distance](../business-rules/BR-002-separation-distance.md) | Step 4, A1 |

## <a id="postconditions"></a>🏁 Postconditions

- ✅ **Success:** the Mission stays Planned with an accepted simulation result, recorded with the name of the Mission planner. The Flight log of the simulation is kept, marked Simulated. No real Drone received a command.
- ❌ **Failure:** the Mission is back to Draft. The Mission planner sees each conflict with the Drones, the time and the place, and changes the Mission in **🖊️ Design**.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-001: Mission design](../features/FS-001-mission-design.md)
- [📘 FS-010: Simulator and training](../features/FS-010-simulator-and-training.md)
- [🎬 UC-001: Design a Mission](UC-001-design-a-mission.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ UC-001: Design a Mission](UC-001-design-a-mission.md) · 📄 **Page 28 / 109** · [UC-003: Run the Pre-flight check and launch ▶️](UC-003-run-the-pre-flight-check-and-launch.md)
<!-- /spec:nav-bottom -->
