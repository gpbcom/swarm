# 📘 FS-007: Data processing and Deliverables

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-006: Authorisations and compliance](FS-006-authorisations-and-compliance.md) · 📄 **Page 11 / 108** · [FS-008: Client portal ▶️](FS-008-client-portal.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> After a [🗃️ Mission](../../glossary.md#ent-mission), Swarm turns the data of the [🗃️ Squad](../../glossary.md#ent-squad) into [🗃️ Deliverables](../../glossary.md#ent-deliverable): orthomosaics, 3D models, defect lists, spray maps, patrol clips.

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

Deliver finished products, not raw files. Swarm collects the images, video and logs of every [🗃️ Drone](../../glossary.md#ent-drone), tags them with Drone, [🗃️ Payload](../../glossary.md#ent-payload), position and time, and processes them per [🔤 Activity](../../glossary.md#term-activity). The [👤 Mission planner](../../glossary.md#per-mission-planner) reviews and publishes the Deliverables to the [👤 Client](../../glossary.md#per-client).

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Mission planner](../../glossary.md#per-mission-planner) | Persona | Reviews and publishes |
| [🗃️ Deliverable](../../glossary.md#ent-deliverable) | Entity | Processing, then Published |
| [🗃️ Flight log](../../glossary.md#ent-flight-log) | Entity | Source of the data |
| [⚙️ Back office](../../glossary.md#sys-back-office) | System | Runs the processing |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-009: Evidence integrity](../business-rules/BR-009-evidence-integrity.md) | Each Deliverable gets its Evidence record |
| [📏 BR-008: Operator isolation](../business-rules/BR-008-operator-isolation.md) | Deliverables stay inside their Operator |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-009: Process flight data into Deliverables](../use-cases/UC-009-process-flight-data-into-deliverables.md) | [👤 Mission planner](../../glossary.md#per-mission-planner) |
| [🎬 UC-020: Review the Defects of an Inspection](../use-cases/UC-020-review-the-defects-of-an-inspection.md) | [👤 Mission planner](../../glossary.md#per-mission-planner) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a completed Inspection **when** its data is uploaded **then** the orthomosaic shows Deliverable: Processing, then Published once the Mission planner publishes it | [📏 BR-009](../business-rules/BR-009-evidence-integrity.md) | [🎬 UC-009](../use-cases/UC-009-process-flight-data-into-deliverables.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Where processing runs | In the cloud, and on premises for on-premise Operators, on their own GPU server |
| Review | A built Deliverable is [🔄 Deliverable: In review](../../glossary.md#st-deliverable-in-review) until a person publishes it |

## <a id="out-of-scope"></a>🚫 Out of scope

- Editing the 3D models

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

> [🏠 Index](../../README.md) · [◀️ FS-006: Authorisations and compliance](FS-006-authorisations-and-compliance.md) · 📄 **Page 11 / 108** · [FS-008: Client portal ▶️](FS-008-client-portal.md)
<!-- /spec:nav-bottom -->
