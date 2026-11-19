# 🎬 UC-011: Follow a Mission and download its Deliverables

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ UC-010: Order a Mission in the Client portal](UC-010-order-a-mission-in-the-client-portal.md) · 📄 **Page 37 / 109** · [UC-012: Verify the Evidence record of a flight ▶️](UC-012-verify-the-evidence-record-of-a-flight.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> The [👤 Client](../../glossary.md#per-client) follows its [🗃️ Mission](../../glossary.md#ent-mission) live in the [⚙️ Client portal](../../glossary.md#sys-client-portal), without any command, then reads its published [🗃️ Scorecard](../../glossary.md#ent-scorecard) and downloads its [🗃️ Deliverables](../../glossary.md#ent-deliverable).

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
| [👤 Client](../../glossary.md#per-client) | Persona | Priya Shah of Helio Energy: follows the Mission, reads the Scorecard, downloads the Deliverables |
| [🗃️ Mission](../../glossary.md#ent-mission) | Entity | M-2026-0412 Inspection of Les Vignes: Mission: Flying, then Mission: Completed |
| [🗃️ Squad](../../glossary.md#ent-squad) | Entity | Alpha, Bravo, Charlie and Delta, shown on the map, read only |
| [🗃️ Scorecard](../../glossary.md#ent-scorecard) | Entity | Published by the Operator after review, read by the Client |
| [🗃️ Deliverable](../../glossary.md#ent-deliverable) | Entity | Orthomosaic, 3D model, defect list and Mission report, downloaded once published |
| [⚙️ Client portal](../../glossary.md#sys-client-portal) | System | Shows the Mission, the Scorecard and the Deliverables of the Client only |

## <a id="preconditions"></a>🚦 Preconditions

1. The Client Priya Shah ordered M-2026-0412 ([🎬 UC-010: Order a Mission in the Client portal](UC-010-order-a-mission-in-the-client-portal.md)), and the [🗃️ Operator](../../glossary.md#ent-operator) Aerowing Services planned it.
2. The live view is on for Helio Energy. The Operator can configure other modes per Client, such as results by e-mail only. Live video is off for M-2026-0412: it is off by default ([📘 FS-008: Client portal](../features/FS-008-client-portal.md#details)).

## <a id="trigger"></a>⚡ Trigger

The Squad takes off on 3 December 2026 and the Mission is Flying. The Client opens the Mission in **🗺️ Missions**.

## <a id="main-flow"></a>➡️ Main flow

1. The Client opens M-2026-0412. The Client portal shows the Drone positions of the Squad live on the map, the area covered and the state Mission: Flying, read only: there is no command ([📏 BR-016](../business-rules/BR-016-clients-see-only-their-own-missions.md)).
2. Every Drone lands and the work is done. The Client sees the state Mission: Completed, and the Deliverables in the state Deliverable: Processing, then Deliverable: In review while the Operator reviews them.
3. Once a [👤 Mission planner](../../glossary.md#per-mission-planner) of the Operator has reviewed and published the Scorecard ([🎬 UC-028: Assess a Mission against the request](UC-028-assess-a-mission-against-the-request.md)), the Client reads it in **🧾 Scorecards**: each acceptance criterion of the order, requested and actual, passed or failed ([📏 BR-026](../business-rules/BR-026-scorecard-against-the-request.md)).
4. The Client opens **📦 Deliverables**. The Client portal lists the Deliverables of the Mission in the state Deliverable: Published.
5. The Client downloads the Deliverables.

## <a id="flowchart"></a>🔀 Flow chart

```mermaid
flowchart LR
    P1(["👤 Client"]):::persona
    S1[["⚙️ Client portal"]]:::system
    E1[("🗃️ Mission")]:::entity
    E2[("🗃️ Squad")]:::entity
    E3[("🗃️ Scorecard")]:::entity
    E4[("🗃️ Deliverable")]:::entity
    A1["Follow the Squad on the map"]:::action
    A2["See the Mission completed"]:::action
    A3["Read the Scorecard"]:::action
    D1{"❓ Deliverables published?"}:::decision
    OK(["✅ Deliverables downloaded"]):::success
    KO(["❌ Deliverables not published yet"]):::failure

    P1 -- "opens the Mission in" --> S1
    S1 -- "shows, read only" --> A1
    A1 -- "reads the positions of" --> E2
    A1 -- "reads the state of" --> E1
    A1 -- "every Drone lands" --> A2
    A2 -- "reads" --> E1
    P1 -- "opens Scorecards" --> A3
    A3 -- "reads" --> E3
    A3 --> D1
    P1 -- "opens Deliverables" --> D1
    D1 -- "yes" --> OK
    D1 -- "no" --> KO
    OK -- "downloads" --> E4
    KO -- "waits for" --> E4

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
| <a id="screen-a1"></a>A1: Follow the Squad on the map | [👤 Client](../../glossary.md#per-client) | [🔄 Mission: Flying](../../glossary.md#st-mission-flying) | ✏️ Mock-up | [![UC-011 A1: Follow the Squad on the map](../../screens/UC-011/a1.png)](../../screens/UC-011/a1.png) [![UC-011 A1: Follow the Squad on the map (dark)](../../screens/UC-011/a1.dark.png)](../../screens/UC-011/a1.dark.png) |
| <a id="screen-a2"></a>A2: See the Mission completed | [👤 Client](../../glossary.md#per-client) | [🔄 Mission: Completed](../../glossary.md#st-mission-completed)<br>[🔄 Deliverable: Processing](../../glossary.md#st-deliverable-processing) | ✏️ Mock-up | [![UC-011 A2: See the Mission completed](../../screens/UC-011/a2.png)](../../screens/UC-011/a2.png) [![UC-011 A2: See the Mission completed (dark)](../../screens/UC-011/a2.dark.png)](../../screens/UC-011/a2.dark.png) |
| <a id="screen-a3"></a>A3: Read the Scorecard | [👤 Client](../../glossary.md#per-client) | [🔄 Scorecard: Passed](../../glossary.md#st-scorecard-passed) | ✏️ Mock-up | [![UC-011 A3: Read the Scorecard](../../screens/UC-011/a3.png)](../../screens/UC-011/a3.png) [![UC-011 A3: Read the Scorecard (dark)](../../screens/UC-011/a3.dark.png)](../../screens/UC-011/a3.dark.png) |
| <a id="screen-ok"></a>OK: Deliverables downloaded | [👤 Client](../../glossary.md#per-client) | [🔄 Deliverable: Published](../../glossary.md#st-deliverable-published) | ✏️ Mock-up | [![UC-011 OK: Deliverables downloaded](../../screens/UC-011/ok.png)](../../screens/UC-011/ok.png) [![UC-011 OK: Deliverables downloaded (dark)](../../screens/UC-011/ok.dark.png)](../../screens/UC-011/ok.dark.png) |
| <a id="screen-ko"></a>KO: Deliverables not published yet | [👤 Client](../../glossary.md#per-client) | [🔄 Deliverable: In review](../../glossary.md#st-deliverable-in-review)<br>[🔄 Deliverable: Processing](../../glossary.md#st-deliverable-processing) | ✏️ Mock-up | [![UC-011 KO: Deliverables not published yet](../../screens/UC-011/ko.png)](../../screens/UC-011/ko.png) [![UC-011 KO: Deliverables not published yet (dark)](../../screens/UC-011/ko.dark.png)](../../screens/UC-011/ko.dark.png) |

## <a id="alternative-flows"></a>↪️ Alternative and error flows

| # | At step | Condition | What happens |
| --- | --- | --- | --- |
| A1 | 1 | The Operator has enabled live video for this Mission | The Client also sees the live video of the Drones, read only |
| A2 | 1 | The Operator has turned the live view off for this Client | The Client portal shows the state of the Mission only, with no map |
| A3 | 1 | The Client opens a link to a Mission of another Client | ❌ Not found ([📏 BR-016](../business-rules/BR-016-clients-see-only-their-own-missions.md)) |
| A4 | 3 | The Scorecard is not published yet | **🧾 Scorecards** does not show it: only a reviewed Scorecard reaches the Client ([📏 BR-026](../business-rules/BR-026-scorecard-against-the-request.md)) |
| A5 | 3 | The Scorecard is Scorecard: Failed | The Client reads which criterion failed. The Operator explains, or re-flies the gaps as a new Mission linked to M-2026-0412, and the Scorecard is assessed again with both ([🎬 UC-028: Assess a Mission against the request](UC-028-assess-a-mission-against-the-request.md)) |
| A6 | 4 | The Deliverables are still Deliverable: Processing or Deliverable: In review | ❌ The Client portal lists them without a download; the Client comes back once they are Published |

## <a id="business-rules"></a>📏 Business rules applied

| Rule | Where it applies |
| --- | --- |
| [📏 BR-016: Clients see only their own Missions](../business-rules/BR-016-clients-see-only-their-own-missions.md) | Steps 1 to 5: only the Missions, Scorecards and Deliverables of Helio Energy, only what the Operator published, and no command |
| [📏 BR-026: Scorecard against the request](../business-rules/BR-026-scorecard-against-the-request.md) | Step 3: the Scorecard assesses each acceptance criterion of the order and reaches the Client only after review |

## <a id="postconditions"></a>🏁 Postconditions

- ✅ **Success:** the Client has followed the Mission until Mission: Completed, read its Scorecard and downloaded its published Deliverables. Nothing in the Mission was changed by the Client.
- ❌ **Failure:** the Deliverables are not published yet. The Client sees them as Processing or In review, without a download.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-008: Client portal](../features/FS-008-client-portal.md)
- [📘 FS-022: Debrief and assessment](../features/FS-022-debrief-and-assessment.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ UC-010: Order a Mission in the Client portal](UC-010-order-a-mission-in-the-client-portal.md) · 📄 **Page 37 / 109** · [UC-012: Verify the Evidence record of a flight ▶️](UC-012-verify-the-evidence-record-of-a-flight.md)
<!-- /spec:nav-bottom -->
