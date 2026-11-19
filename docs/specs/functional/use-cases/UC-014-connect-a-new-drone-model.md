# 🎬 UC-014: Connect a new Drone model

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ UC-013: Train on the Simulator](UC-013-train-on-the-simulator.md) · 📄 **Page 40 / 109** · [UC-015: Invite a Client to the Client portal ▶️](UC-015-invite-a-client-to-the-client-portal.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> The [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) connects a new [🗃️ Drone model](../../glossary.md#ent-drone-model) through its [⚙️ Drone adapter](../../glossary.md#sys-drone-adapter) and runs the compatibility test of Swarm, in the [⚙️ Simulator](../../glossary.md#sys-simulator) then in one real flight: if it passes, the Drone model is Approved and its [🗃️ Drones](../../glossary.md#ent-drone) may fly; if it fails, they stay Grounded.

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
| [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) | Persona | Adds the Drone model, chooses its Drone adapter and starts the compatibility test |
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Flies the real test flight in a test area |
| [🗃️ Drone model](../../glossary.md#ent-drone-model) | Entity | Not approved until its test passes, then Approved for its current firmware |
| [🗃️ Drone](../../glossary.md#ent-drone) | Entity | Flies the real test; Grounded until its Drone model is Approved |
| [⚙️ Drone adapter](../../glossary.md#sys-drone-adapter) | System | Translates each command of Swarm for the family of the Drone model |
| [⚙️ Simulator](../../glossary.md#sys-simulator) | System | Flies a virtual Drone of the model with its real flight software, where the Drone model allows it |
| [⚙️ Back office](../../glossary.md#sys-back-office) | System | Holds the Drone models of the Fleet and records the test result |

## <a id="preconditions"></a>🚦 Preconditions

1. The Fleet maintainer, Noah Weber, is signed in to the Back office of the [🗃️ Operator](../../glossary.md#ent-operator) Aerowing Services.
2. Swarm has a Drone adapter for the family of the new Drone model. Drone adapters come in this order: MAVLink (PX4, ArduPilot) first, then Parrot, then the other vendors.
3. A Drone of that model is registered, such as Echo (AW-005), an ANAFI USA (see [🎬 UC-007: Register a Drone and track its readiness](UC-007-register-a-drone-and-track-its-readiness.md)).

## <a id="trigger"></a>⚡ Trigger

Aerowing Services buys Drones of a Drone model that is not yet in its Fleet, or the maker releases a new firmware version for a Drone model of the Fleet.

## <a id="main-flow"></a>➡️ Main flow

1. The [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) opens 🛸 Fleet, then Drone models, and adds ANAFI USA by Parrot with its limits (weight, speed, wind, range, payload) and the Parrot Drone adapter.
2. The Back office saves it as **Drone model: Not approved**: every Drone of that model, such as Echo, is **Drone: Grounded** ([📏 BR-015](../business-rules/BR-015-approved-drone-models-only.md)).
3. The Fleet maintainer starts the compatibility test. The Simulator flies a virtual ANAFI USA with its real flight software, and the Drone adapter sends each command of Swarm and checks that it obeys: take off, follow a route, [🔤 Hold](../../glossary.md#term-hold), [🔤 Return home](../../glossary.md#term-return-home), land, stay inside the [🗃️ Geofence](../../glossary.md#ent-geofence), and control its [🗃️ Payload](../../glossary.md#ent-payload).
4. Every step passes in the Simulator. The [👤 Pilot](../../glossary.md#per-pilot), Sam Carter, then flies Echo once in a test area, and the Drone adapter runs the same steps. The Back office shows each step as it runs.
5. Every step passes: the Back office sets ANAFI USA to **Drone model: Approved** for its current firmware. Echo becomes **Drone: Ready**, as nothing else grounds it ([📏 BR-011](../business-rules/BR-011-drone-readiness.md)).

## <a id="flowchart"></a>🔀 Flow chart

```mermaid
flowchart LR
    P1(["👤 Fleet maintainer"]):::persona
    P2(["👤 Pilot"]):::persona
    E1[("🗃️ Drone model")]:::entity
    E2[("🗃️ Drone")]:::entity
    S1[["⚙️ Drone adapter"]]:::system
    S2[["⚙️ Back office"]]:::system
    S3[["⚙️ Simulator"]]:::system
    A1["Add the Drone model and its Drone adapter"]:::action
    D1{"❓ Can the Simulator fly this Drone model?"}:::decision
    A2["Run the test in the Simulator"]:::action
    D2{"❓ Every step passed in the Simulator?"}:::decision
    A3["Fly the test in a test area"]:::action
    D3{"❓ Every step passed in flight?"}:::decision
    OK(["✅ Drone model approved"]):::success
    KO(["❌ Test failed, Drones stay Grounded"]):::failure

    P1 -- "adds" --> A1
    S2 -- "saves as Not approved" --> A1
    A1 -- "creates" --> E1
    A1 --> D1
    D1 -- "yes" --> A2
    D1 -- "no" --> A3
    P1 -- "starts" --> A2
    S3 -- "flies a virtual Drone" --> A2
    S1 -- "sends each command" --> A2
    A2 --> D2
    D2 -- "no" --> KO
    D2 -- "yes" --> A3
    P2 -- "flies" --> A3
    S1 -- "sends each command" --> A3
    A3 -- "flies" --> E2
    A3 --> D3
    D3 -- "yes" --> OK
    OK -- "approves" --> E1
    D3 -- "no" --> KO
    KO -- "keeps Grounded" --> E2
    E1 -- "new firmware, Not approved again" --> D1

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
| <a id="screen-a1"></a>A1: Add the Drone model and its Drone adapter | [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) | [🔄 Drone model: Not approved](../../glossary.md#st-drone-model-not-approved) | ✏️ Mock-up | [![UC-014 A1: Add the Drone model and its Drone adapter](../../screens/UC-014/a1.png)](../../screens/UC-014/a1.png) [![UC-014 A1: Add the Drone model and its Drone adapter (dark)](../../screens/UC-014/a1.dark.png)](../../screens/UC-014/a1.dark.png) |
| <a id="screen-a2"></a>A2: Run the test in the Simulator | [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) | [🔄 Drone model: Not approved](../../glossary.md#st-drone-model-not-approved) | ✏️ Mock-up | [![UC-014 A2: Run the test in the Simulator](../../screens/UC-014/a2.png)](../../screens/UC-014/a2.png) [![UC-014 A2: Run the test in the Simulator (dark)](../../screens/UC-014/a2.dark.png)](../../screens/UC-014/a2.dark.png) |
| <a id="screen-a3"></a>A3: Fly the test in a test area | [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer)<br>[👤 Pilot](../../glossary.md#per-pilot) | [🔄 Drone model: Not approved](../../glossary.md#st-drone-model-not-approved)<br>[🔄 Drone: Grounded](../../glossary.md#st-drone-grounded) | ✏️ Mock-up | [![UC-014 A3: Fly the test in a test area](../../screens/UC-014/a3.png)](../../screens/UC-014/a3.png) [![UC-014 A3: Fly the test in a test area (dark)](../../screens/UC-014/a3.dark.png)](../../screens/UC-014/a3.dark.png) |
| <a id="screen-ok"></a>OK: Drone model approved | [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) | [🔄 Drone model: Approved](../../glossary.md#st-drone-model-approved)<br>[🔄 Drone: Ready](../../glossary.md#st-drone-ready) | ✏️ Mock-up | [![UC-014 OK: Drone model approved](../../screens/UC-014/ok.png)](../../screens/UC-014/ok.png) [![UC-014 OK: Drone model approved (dark)](../../screens/UC-014/ok.dark.png)](../../screens/UC-014/ok.dark.png) |
| <a id="screen-ko"></a>KO: Test failed, Drones stay Grounded | [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) | [🔄 Drone model: Not approved](../../glossary.md#st-drone-model-not-approved)<br>[🔄 Drone: Grounded](../../glossary.md#st-drone-grounded) | ✏️ Mock-up | [![UC-014 KO: Test failed, Drones stay Grounded](../../screens/UC-014/ko.png)](../../screens/UC-014/ko.png) [![UC-014 KO: Test failed, Drones stay Grounded (dark)](../../screens/UC-014/ko.dark.png)](../../screens/UC-014/ko.dark.png) |

## <a id="alternative-flows"></a>↪️ Alternative and error flows

| # | At step | Condition | What happens |
| --- | --- | --- | --- |
| A1 | 3 | The Simulator cannot fly this Drone model | The test starts directly with the real flight of step 4. |
| A2 | 3 or 4 | A step fails, such as Return home in the real flight: Echo does not fly back to its take-off point | The test stops and the Back office names the failed step. ANAFI USA stays **Drone model: Not approved** and its Drones stay **Drone: Grounded** ([📏 BR-015](../business-rules/BR-015-approved-drone-models-only.md)). The Fleet maintainer can run the test again later (KO). |
| A3 | 4 | Echo does not answer through the Drone adapter | The step counts as failed: the Drones of the model stay **Drone: Grounded** (KO). |
| A4 | After 5 | The maker releases a new firmware version for ANAFI USA | The Drone model goes back to **Drone model: Not approved** and its Drones to **Drone: Grounded** until the test passes again with the new firmware (back to step 3). |
| A5 | 5 | Echo has another reason to be Grounded, such as an open fault | The Drone model is Approved, but Echo stays **Drone: Grounded** until the Fleet maintainer clears it ([🎬 UC-007: Register a Drone and track its readiness](UC-007-register-a-drone-and-track-its-readiness.md)). |

## <a id="business-rules"></a>📏 Business rules applied

| Rule | Where it applies |
| --- | --- |
| [📏 BR-015: Approved Drone models only](../business-rules/BR-015-approved-drone-models-only.md) | Steps 2 to 5: a Drone flies only when its Drone model has passed the compatibility test, in the Simulator then in a real flight, for its current firmware |
| [📏 BR-011: Drone readiness](../business-rules/BR-011-drone-readiness.md) | Step 5: once its Drone model is Approved, a Drone is Ready only if nothing else grounds it |

## <a id="postconditions"></a>🏁 Postconditions

- ✅ **Success:** ANAFI USA is **Drone model: Approved** with the Parrot Drone adapter for its current firmware. Its Drones can become **Drone: Ready** and join a [🗃️ Squad](../../glossary.md#ent-squad).
- ❌ **Failure:** ANAFI USA stays **Drone model: Not approved**. Its Drones stay **Drone: Grounded**, and the Fleet maintainer sees which step of the test failed, in the Simulator or in flight.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-011: Drone adapters](../features/FS-011-drone-adapters.md)
- [🎬 UC-007: Register a Drone and track its readiness](UC-007-register-a-drone-and-track-its-readiness.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ UC-013: Train on the Simulator](UC-013-train-on-the-simulator.md) · 📄 **Page 40 / 109** · [UC-015: Invite a Client to the Client portal ▶️](UC-015-invite-a-client-to-the-client-portal.md)
<!-- /spec:nav-bottom -->
