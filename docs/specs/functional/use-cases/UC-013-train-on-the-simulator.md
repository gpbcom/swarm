# 🎬 UC-013: Train on the Simulator

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ UC-012: Verify the Evidence record of a flight](UC-012-verify-the-evidence-record-of-a-flight.md) · 📄 **Page 41 / 120** · [UC-014: Connect a new Drone model ▶️](UC-014-connect-a-new-drone-model.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> The [👤 Pilot](../../glossary.md#per-pilot) flies a simulated [🗃️ Squad](../../glossary.md#ent-squad) in [⚙️ Ground control](../../glossary.md#sys-ground-control) and handles a failure injected by the [👤 Instructor](../../glossary.md#per-instructor), so that they train without any risk for a real [🗃️ Drone](../../glossary.md#ent-drone).

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
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Trains: launches, supervises and handles the injected failure |
| [👤 Instructor](../../glossary.md#per-instructor) | Persona | Runs the training session from a second Ground control and injects the failure |
| [🗃️ Mission](../../glossary.md#ent-mission) | Entity | The Planned Mission flown for training |
| [🗃️ Squad](../../glossary.md#ent-squad) | Entity | Virtual, flown by the Simulator |
| [🗃️ Drone](../../glossary.md#ent-drone) | Entity | Real Drones of the Fleet, which never receive a command of the session |
| [🗃️ Flight log](../../glossary.md#ent-flight-log) | Entity | Records the session, marked simulated |
| [⚙️ Ground control](../../glossary.md#sys-ground-control) | System | Shows the session, with the Simulator banner on every screen |
| [⚙️ Simulator](../../glossary.md#sys-simulator) | System | Flies the virtual Squad and applies the failure the Instructor injects |

## <a id="preconditions"></a>🚦 Preconditions

1. The [🗃️ Mission](../../glossary.md#ent-mission) M-2026-0412 Inspection of Les Vignes is Planned.
2. The [⚙️ Simulator](../../glossary.md#sys-simulator) has the flight software of every [🗃️ Drone model](../../glossary.md#ent-drone-model) of the Squad.
3. The Pilot Sam Carter is signed in to Ground control. The [👤 Instructor](../../glossary.md#per-instructor), a senior Pilot, has joined the same training session from a second Ground control.

## <a id="trigger"></a>⚡ Trigger

The Pilot starts a training session in Ground control.

## <a id="main-flow"></a>➡️ Main flow

1. The Pilot starts a training session on M-2026-0412 with a simulated Squad: Alpha, Bravo, Charlie and Delta. From now on, every screen of Ground control shows the banner "🕹️ Simulator: no real Drone receives commands" ([📏 BR-014](../business-rules/BR-014-simulation-isolation.md)).
2. The Pilot runs and signs the [🗃️ Pre-flight check](../../glossary.md#ent-pre-flight-check) of the simulated Squad, then launches.
3. The Simulator flies the virtual Squad with the real flight software of each Drone model. The Pilot supervises it as in a real flight.
4. Every command the Pilot gives goes to the Simulator. Swarm checks that it is addressed to a simulated Drone ([📏 BR-014](../business-rules/BR-014-simulation-isolation.md)).
5. During the session, the Instructor injects a failure from the second Ground control: the [🔤 Link](../../glossary.md#term-link) to Delta is lost. The Simulator applies it to the virtual Squad.
6. The Pilot handles the failure as in a real flight: they Hold the Squad, then resume once Delta's area is shared between the other Drones.
7. The simulated Squad lands. The Mission of the session is Completed and its [🗃️ Flight log](../../glossary.md#ent-flight-log) is marked simulated ([📏 BR-014](../business-rules/BR-014-simulation-isolation.md)). The Pilot can open its [🔤 Replay](../../glossary.md#term-replay) in the [🗃️ Debrief](../../glossary.md#ent-debrief).

## <a id="flowchart"></a>🔀 Flow chart

```mermaid
flowchart LR
    P1(["👤 Pilot"]):::persona
    P2(["👤 Instructor"]):::persona
    S1[["⚙️ Ground control"]]:::system
    S2[["⚙️ Simulator"]]:::system
    E1[("🗃️ Mission")]:::entity
    E2[("🗃️ Squad")]:::entity
    E3[("🗃️ Drone")]:::entity
    E4[("🗃️ Flight log")]:::entity
    A1["Start a training session"]:::action
    A2["Supervise the simulated Squad"]:::action
    D1{"❓ Addressed to a simulated Drone?"}:::decision
    A3["Handle the injected failure"]:::action
    OK(["✅ Training session completed"]):::success
    KO(["❌ Command to a real Drone refused"]):::failure

    P1 -- "starts" --> A1
    A1 -- "loads" --> E1
    S1 -- "shows the Simulator banner in" --> A1
    A1 -- "launches" --> A2
    S2 -- "flies a virtual" --> E2
    E2 -- "is shown in" --> A2
    P1 -- "supervises" --> A2
    A2 -- "sends a command" --> D1
    D1 -- "yes" --> A3
    D1 -- "no" --> KO
    KO -- "never reaches" --> E3
    P2 -- "runs the session in" --> S2
    P2 -- "injects a failure" --> A3
    S2 -- "applies the failure in" --> A3
    P1 -- "holds the Squad" --> A3
    A3 -- "lands" --> OK
    OK -- "is marked simulated in" --> E4

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
| <a id="screen-a1"></a>A1: Start a training session | [👤 Pilot](../../glossary.md#per-pilot)<br>[👤 Instructor](../../glossary.md#per-instructor) | [🔄 Mission: Planned](../../glossary.md#st-mission-planned) | ✏️ Mock-up | [![UC-013 A1: Start a training session](../../screens/UC-013/a1.png)](../../screens/UC-013/a1.png) [![UC-013 A1: Start a training session (dark)](../../screens/UC-013/a1.dark.png)](../../screens/UC-013/a1.dark.png) |
| <a id="screen-a2"></a>A2: Supervise the simulated Squad | [🔄 Pilot: Supervising](../../glossary.md#st-pilot-supervising) | [🔄 Mission: Flying](../../glossary.md#st-mission-flying) | ✏️ Mock-up | [![UC-013 A2: Supervise the simulated Squad](../../screens/UC-013/a2.png)](../../screens/UC-013/a2.png) [![UC-013 A2: Supervise the simulated Squad (dark)](../../screens/UC-013/a2.dark.png)](../../screens/UC-013/a2.dark.png) |
| <a id="screen-a3"></a>A3: Handle the injected failure | [🔄 Pilot: Supervising](../../glossary.md#st-pilot-supervising)<br>[👤 Instructor](../../glossary.md#per-instructor) | [🔄 Drone: Lost](../../glossary.md#st-drone-lost)<br>[🔄 Mission: Held](../../glossary.md#st-mission-held) | ✏️ Mock-up | [![UC-013 A3: Handle the injected failure](../../screens/UC-013/a3.png)](../../screens/UC-013/a3.png) [![UC-013 A3: Handle the injected failure (dark)](../../screens/UC-013/a3.dark.png)](../../screens/UC-013/a3.dark.png) |
| <a id="screen-ok"></a>OK: Training session completed | [👤 Pilot](../../glossary.md#per-pilot) | [🔄 Mission: Completed](../../glossary.md#st-mission-completed)<br>[🗃️ Flight log](../../glossary.md#ent-flight-log) | ✏️ Mock-up | [![UC-013 OK: Training session completed](../../screens/UC-013/ok.png)](../../screens/UC-013/ok.png) [![UC-013 OK: Training session completed (dark)](../../screens/UC-013/ok.dark.png)](../../screens/UC-013/ok.dark.png) |
| <a id="screen-ko"></a>KO: Command to a real Drone refused | [🔄 Pilot: Supervising](../../glossary.md#st-pilot-supervising) | [🗃️ Drone](../../glossary.md#ent-drone)<br>[🗃️ Flight log](../../glossary.md#ent-flight-log) | ✏️ Mock-up | [![UC-013 KO: Command to a real Drone refused](../../screens/UC-013/ko.png)](../../screens/UC-013/ko.png) [![UC-013 KO: Command to a real Drone refused (dark)](../../screens/UC-013/ko.dark.png)](../../screens/UC-013/ko.dark.png) |

## <a id="alternative-flows"></a>↪️ Alternative and error flows

| # | At step | Condition | What happens |
| --- | --- | --- | --- |
| A1 | 4 | A command of the session is addressed to a real Drone, such as Alpha (AW-001) of the Fleet | Swarm refuses it and records the refusal in the Flight log. No real Drone receives it. The Pilot sees an [🔤 Alert](../../glossary.md#term-alert) and the session goes on ([📏 BR-014](../business-rules/BR-014-simulation-isolation.md)). |
| A2 | 6 | The Pilot takes manual control of a Drone or aborts the session instead of holding the Squad | The Simulator carries out the command as in a real flight. The Flight log is still marked simulated. |
| A3 | 5 | The Instructor injects another failure | The Pilot handles it the same way; each injected failure and each decision of the Pilot is in the Flight log of the session. |

## <a id="business-rules"></a>📏 Business rules applied

| Rule | Where it applies |
| --- | --- |
| [📏 BR-014: Simulation isolation](../business-rules/BR-014-simulation-isolation.md) | Steps 1, 4 and 7: the banner, the refusal of any command to a real Drone, the Flight log marked simulated |

## <a id="postconditions"></a>🏁 Postconditions

- ✅ **Success:** the training session is Completed, its Flight log is marked simulated, and the Pilot can replay it in the Debrief. No real Drone received a command.
- ❌ **Failure:** a command addressed to a real Drone was refused and logged; the Pilot and the Instructor saw the refusal and the real Drone did not move.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-010: Simulator and training](../features/FS-010-simulator-and-training.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ UC-012: Verify the Evidence record of a flight](UC-012-verify-the-evidence-record-of-a-flight.md) · 📄 **Page 41 / 120** · [UC-014: Connect a new Drone model ▶️](UC-014-connect-a-new-drone-model.md)
<!-- /spec:nav-bottom -->
