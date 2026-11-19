# 🎬 UC-024: Configure each Drone of the Squad on the Site

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ UC-023: Configure the Workspace of Ground control](UC-023-configure-the-workspace-of-ground-control.md) · 📄 **Page 50 / 109** · [UC-025: Monitor a Mission in Ground control ▶️](UC-025-monitor-a-mission-in-ground-control.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> The [👤 Pilot](../../glossary.md#per-pilot) changes a [🗃️ Battery](../../glossary.md#ent-battery), a [🗃️ Drone](../../glossary.md#ent-drone) or a [🗃️ Payload](../../glossary.md#ent-payload) of the [🗃️ Squad](../../glossary.md#ent-squad) on the Site before launch, and gets a [🗃️ Mission](../../glossary.md#ent-mission) checked again and ready to sign.

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
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Reviews and changes each Drone of the Squad, then signs the Pre-flight check again |
| [👤 Mission planner](../../glossary.md#per-mission-planner) | Persona | Is told of the changes made on the Site |
| [🗃️ Squad](../../glossary.md#ent-squad) | Entity | Alpha, Bravo, Charlie and Delta, each with its own Drone model, Payload and Battery |
| [🗃️ Drone](../../glossary.md#ent-drone) | Entity | Charlie is replaced by the spare Echo |
| [🗃️ Battery](../../glossary.md#ent-battery) | Entity | The Battery of Bravo is swapped |
| [🗃️ Payload](../../glossary.md#ent-payload) | Entity | A Payload that does not fit is refused |
| [🗃️ Mission](../../glossary.md#ent-mission) | Entity | Checked again after the changes |
| [🗃️ Pre-flight check](../../glossary.md#ent-pre-flight-check) | Entity | Run and signed again |
| [🗃️ Flight log](../../glossary.md#ent-flight-log) | Entity | Records each change made on the Site |
| [⚙️ Ground control](../../glossary.md#sys-ground-control) | System | Checks each change and the Mission again |

## <a id="preconditions"></a>🚦 Preconditions

1. The Mission M-2026-0412 Inspection of Les Vignes is Verified: its [🗃️ Pre-flight check](../../glossary.md#ent-pre-flight-check) was signed by the Pilot Sam Carter.
2. The Squad is Alpha, Bravo and Charlie (X500) and Delta (ANAFI USA). The spare Echo (X500, thermal camera) is in the [🗃️ Field kit](../../glossary.md#ent-field-kit) on the [🗃️ Site](../../glossary.md#ent-site) Les Vignes solar farm.
3. The Squad has not launched.

## <a id="trigger"></a>⚡ Trigger

The Pilot opens 🛸 Squad in [⚙️ Ground control](../../glossary.md#sys-ground-control) to change the Squad before launch.

## <a id="main-flow"></a>➡️ Main flow

1. The Pilot reviews each Drone of the Squad: its [🗃️ Drone model](../../glossary.md#ent-drone-model), its Payload and task, its Battery and its readiness.
2. The Pilot swaps the Battery of Bravo for a fully charged one.
3. Charlie shows an open fault and is Grounded ([📏 BR-011](../business-rules/BR-011-drone-readiness.md)). The Pilot replaces Charlie by the spare Echo, of the same Drone model and with the same Payload.
4. Ground control checks each change: Echo is Ready, the new Battery is above the health threshold set for its Drone model, and each Payload fits its Drone model and can perform its task ([📏 BR-011](../business-rules/BR-011-drone-readiness.md), [📏 BR-022](../business-rules/BR-022-payload-compatibility.md)).
5. Ground control checks the Mission again with the new Squad ([📏 BR-025](../business-rules/BR-025-on-site-changes-are-checked-again.md)). The Mission is Planned again: the signature of the earlier Pre-flight check no longer applies.
6. Ground control tells the [👤 Mission planner](../../glossary.md#per-mission-planner) Léa Martin of the changes and records them in the [🗃️ Flight log](../../glossary.md#ent-flight-log) ([📏 BR-025](../business-rules/BR-025-on-site-changes-are-checked-again.md)).
7. The Pilot runs the Pre-flight check again and signs it. The Mission is Verified and can launch.

## <a id="flowchart"></a>🔀 Flow chart

```mermaid
flowchart LR
    P1(["👤 Pilot"]):::persona
    P2(["👤 Mission planner"]):::persona
    S1[["⚙️ Ground control"]]:::system
    E1[("🗃️ Squad")]:::entity
    E2[("🗃️ Drone")]:::entity
    E3[("🗃️ Battery")]:::entity
    E4[("🗃️ Payload")]:::entity
    E5[("🗃️ Mission")]:::entity
    E6[("🗃️ Pre-flight check")]:::entity
    E7[("🗃️ Flight log")]:::entity
    A1["Review each Drone of the Squad"]:::action
    A2["Swap a Battery and replace Charlie by Echo"]:::action
    D1{"❓ Ready and compatible?"}:::decision
    A3["Check the Mission again"]:::action
    OK(["✅ Pre-flight check signed again"]):::success
    KO(["❌ Payload refused"]):::failure

    P1 -- "reviews" --> A1
    A1 -- "lists each Drone of" --> E1
    A1 --> A2
    P1 -- "changes" --> A2
    A2 -- "replaces Charlie by Echo" --> E2
    A2 -- "swaps" --> E3
    A2 --> D1
    D1 -- "no" --> KO
    KO -- "keeps the former" --> E4
    D1 -- "yes" --> A3
    S1 -- "checks again" --> A3
    A3 -- "sets back to Planned" --> E5
    A3 -- "tells the changes to" --> P2
    A3 -- "records the changes in" --> E7
    A3 --> OK
    P1 -- "signs" --> OK
    OK -- "records" --> E6

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
| <a id="screen-a1"></a>A1: Review each Drone of the Squad | [👤 Pilot](../../glossary.md#per-pilot) | [🔄 Mission: Verified](../../glossary.md#st-mission-verified)<br>[🔄 Drone: Ready](../../glossary.md#st-drone-ready) | ✏️ Mock-up | [![UC-024 A1: Review each Drone of the Squad](../../screens/UC-024/a1.png)](../../screens/UC-024/a1.png) [![UC-024 A1: Review each Drone of the Squad (dark)](../../screens/UC-024/a1.dark.png)](../../screens/UC-024/a1.dark.png) |
| <a id="screen-a2"></a>A2: Swap a Battery and replace Charlie by Echo | [👤 Pilot](../../glossary.md#per-pilot) | [🔄 Drone: Grounded](../../glossary.md#st-drone-grounded)<br>[🔄 Drone: Ready](../../glossary.md#st-drone-ready) | ✏️ Mock-up | [![UC-024 A2: Swap a Battery and replace Charlie by Echo](../../screens/UC-024/a2.png)](../../screens/UC-024/a2.png) [![UC-024 A2: Swap a Battery and replace Charlie by Echo (dark)](../../screens/UC-024/a2.dark.png)](../../screens/UC-024/a2.dark.png) |
| <a id="screen-a3"></a>A3: Check the Mission again | [👤 Pilot](../../glossary.md#per-pilot)<br>[👤 Mission planner](../../glossary.md#per-mission-planner) | [🔄 Mission: Planned](../../glossary.md#st-mission-planned)<br>[🗃️ Flight log](../../glossary.md#ent-flight-log) | ✏️ Mock-up | [![UC-024 A3: Check the Mission again](../../screens/UC-024/a3.png)](../../screens/UC-024/a3.png) [![UC-024 A3: Check the Mission again (dark)](../../screens/UC-024/a3.dark.png)](../../screens/UC-024/a3.dark.png) |
| <a id="screen-ok"></a>OK: Pre-flight check signed again | [👤 Pilot](../../glossary.md#per-pilot) | [🔄 Mission: Verified](../../glossary.md#st-mission-verified)<br>[🗃️ Pre-flight check](../../glossary.md#ent-pre-flight-check) | ✏️ Mock-up | [![UC-024 OK: Pre-flight check signed again](../../screens/UC-024/ok.png)](../../screens/UC-024/ok.png) [![UC-024 OK: Pre-flight check signed again (dark)](../../screens/UC-024/ok.dark.png)](../../screens/UC-024/ok.dark.png) |
| <a id="screen-ko"></a>KO: Payload refused | [👤 Pilot](../../glossary.md#per-pilot) | [🗃️ Payload](../../glossary.md#ent-payload) | ✏️ Mock-up | [![UC-024 KO: Payload refused](../../screens/UC-024/ko.png)](../../screens/UC-024/ko.png) [![UC-024 KO: Payload refused (dark)](../../screens/UC-024/ko.dark.png)](../../screens/UC-024/ko.dark.png) |

## <a id="alternative-flows"></a>↪️ Alternative and error flows

| # | At step | Condition | What happens |
| --- | --- | --- | --- |
| A1 | 4 | The Pilot mounts the LiDAR of the Field kit on Delta, and it does not fit the ANAFI USA | Refused: Ground control names the Drone, the Payload and the reason ([📏 BR-022](../business-rules/BR-022-payload-compatibility.md)). Delta keeps its zoom camera. |
| A2 | 4 | A Payload would take a Drone over the weight limit of its Drone model | Refused with the excess weight ([📏 BR-025](../business-rules/BR-025-on-site-changes-are-checked-again.md)). |

## <a id="business-rules"></a>📏 Business rules applied

| Rule | Where it applies |
| --- | --- |
| [📏 BR-025: On-site changes are checked again](../business-rules/BR-025-on-site-changes-are-checked-again.md) | Steps 5 to 7: the Mission is checked again, the changes are told to the Mission planner and recorded, the Pre-flight check is signed again |
| [📏 BR-022: Payload compatibility](../business-rules/BR-022-payload-compatibility.md) | Step 4: each Payload fits its Drone model and can perform its task |
| [📏 BR-011: Drone readiness](../business-rules/BR-011-drone-readiness.md) | Steps 3 and 4: Charlie Grounded, Echo Ready, the new Battery above the health threshold |

## <a id="postconditions"></a>🏁 Postconditions

- ✅ **Success:** the Squad is Alpha, Bravo with its new Battery, Echo and Delta; the Mission passed its checks again and is Verified with a new signed Pre-flight check. Léa Martin knows of the changes, and the Flight log records them.
- ❌ **Failure:** a change that breaks a rule is refused with its reason, the Squad keeps its former setting, and the Mission stays as it was until the Pilot makes a valid change.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-020: Ground control Workspace and configuration](../features/FS-020-ground-control-workspace-and-configuration.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ UC-023: Configure the Workspace of Ground control](UC-023-configure-the-workspace-of-ground-control.md) · 📄 **Page 50 / 109** · [UC-025: Monitor a Mission in Ground control ▶️](UC-025-monitor-a-mission-in-ground-control.md)
<!-- /spec:nav-bottom -->
