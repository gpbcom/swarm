# 📘 FS-014: Agriculture

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-013: Light shows](FS-013-light-shows.md) · 📄 **Page 18 / 108** · [FS-015: Patrol ▶️](FS-015-patrol.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> Swarm splits a [🗃️ Field](../../glossary.md#ent-field) between the [🗃️ Drones](../../glossary.md#ent-drone) of a [🗃️ Squad](../../glossary.md#ent-squad), applies a uniform dose or the [🗃️ Prescription map](../../glossary.md#ent-prescription-map), and plans refills.

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

Spray or seed a Field faster with several Drones and one crew. Swarm imports the Field boundary and the Prescription map (Shapefile, ISOXML), divides the Field, plans refill and battery swaps, and records what was applied where. Routes are Pre-planned; refills and failures are re-planned under supervision.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Supervises spraying and refills |
| [🗃️ Field](../../glossary.md#ent-field) | Entity | Boundary |
| [🗃️ Prescription map](../../glossary.md#ent-prescription-map) | Entity | Dose per zone |
| [🗃️ Payload](../../glossary.md#ent-payload) | Entity | Sprayer tank or spreader |
| [🗃️ Squad](../../glossary.md#ent-squad) | Entity | Sprays together |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-018: Dose follows the Prescription map](../business-rules/BR-018-dose-follows-the-prescription-map.md) | Dose follows the Prescription map, nothing outside the Field |
| [📏 BR-001: Geofence and Altitude ceiling](../business-rules/BR-001-geofence-and-altitude-ceiling.md) | The Field sets the Geofence |
| [📏 BR-005: Autonomy level per Activity](../business-rules/BR-005-autonomy-level-per-activity.md) | Pre-planned routes, supervised refills |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-017: Spray a Field with refills](../use-cases/UC-017-spray-a-field-with-refills.md) | [👤 Pilot](../../glossary.md#per-pilot) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a Prescription map with two zones **when** the Squad sprays **then** each zone receives its dose and the spray map shows it | [📏 BR-018](../business-rules/BR-018-dose-follows-the-prescription-map.md) | [🎬 UC-017](../use-cases/UC-017-spray-a-field-with-refills.md) |
| AC-2 | **Given** a Drone with an empty tank **when** it needs a refill **then** Swarm proposes a refill Re-plan to the Pilot | [📏 BR-005](../business-rules/BR-005-autonomy-level-per-activity.md) | [🎬 UC-017](../use-cases/UC-017-spray-a-field-with-refills.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Licences per Pilot | Drone qualification per Jurisdiction (EU A2 or STS, US Part 107) and pesticide applicator licence |
| Licences per Operator | Part 137 certificate in the US |
| Refill | Proposed at 10 % of the tank left (Operator setting) |
| Missing licence | A missing or expired licence of the Pilot or the Operator fails the Pre-flight check of an Agriculture Mission |
| Seeding | Seed and granule doses in kg/ha, liquids in L/ha |

## <a id="out-of-scope"></a>🚫 Out of scope

- Choosing the products and doses (agronomy)

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

> [🏠 Index](../../README.md) · [◀️ FS-013: Light shows](FS-013-light-shows.md) · 📄 **Page 18 / 108** · [FS-015: Patrol ▶️](FS-015-patrol.md)
<!-- /spec:nav-bottom -->
