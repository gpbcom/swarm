# 📘 FS-016: Inspection

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-015: Patrol](FS-015-patrol.md) · 📄 **Page 20 / 109** · [FS-017: Mission assistant ▶️](FS-017-mission-assistant.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> Swarm maps [🗃️ Sites](../../glossary.md#ent-site) and inspects solar farms, wind turbines, power lines, buildings and bridges, and finds [🗃️ Defects](../../glossary.md#ent-defect) for a person to confirm.

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

Inspect large structures quickly with a mixed [🗃️ Squad](../../glossary.md#ent-squad): thermal and RGB [🗃️ Payloads](../../glossary.md#ent-payload) together, sharing the area under Supervised autonomy. Detection marks Suspected Defects; the [👤 Mission planner](../../glossary.md#per-mission-planner) confirms or dismisses them before the [👤 Client](../../glossary.md#per-client) sees them.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Mission planner](../../glossary.md#per-mission-planner) | Persona | Reviews Defects |
| [🗃️ Defect](../../glossary.md#ent-defect) | Entity | Suspected, Confirmed, Dismissed |
| [🗃️ Deliverable](../../glossary.md#ent-deliverable) | Entity | Orthomosaic, 3D model, defect list |
| [🗃️ Payload](../../glossary.md#ent-payload) | Entity | Thermal, RGB, zoom, LiDAR |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-020: Defects confirmed by a person](../business-rules/BR-020-defects-confirmed-by-a-person.md) | Defects are confirmed by a person |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-020: Review the Defects of an Inspection](../use-cases/UC-020-review-the-defects-of-an-inspection.md) | [👤 Mission planner](../../glossary.md#per-mission-planner) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** 12 Suspected Defects **when** the Mission planner confirms 9 and dismisses 3 **then** only the 9 appear in the Client's defect list | [📏 BR-020](../business-rules/BR-020-defects-confirmed-by-a-person.md) | [🎬 UC-020](../use-cases/UC-020-review-the-defects-of-an-inspection.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Detection models | Swarm ships them, solar farms first, then wind turbines, power lines, buildings and bridges, trained by the Swarm team on labelled data from Operators who consent. Operators may also train their own models on their data |
| Dismissing a Defect | A reason from a fixed list is required; the reviewer's name and the time are recorded |
| Dismissal reasons | Not a Defect, duplicate, already known to the Client, image quality too low, other (comment required) |
| Reviewer recorded | The reviewer's name and the time are recorded for confirmations and dismissals alike |
| Model quality gate | A detection model is used for Clients only with recall of at least 90 % and precision of at least 80 % on the Operator's validation set |

## <a id="out-of-scope"></a>🚫 Out of scope

- Repair planning

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

> [🏠 Index](../../README.md) · [◀️ FS-015: Patrol](FS-015-patrol.md) · 📄 **Page 20 / 109** · [FS-017: Mission assistant ▶️](FS-017-mission-assistant.md)
<!-- /spec:nav-bottom -->
