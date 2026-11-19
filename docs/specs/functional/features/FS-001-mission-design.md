# 📘 FS-001: Mission design

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ Functional specifications](../README.md) · 📄 **Page 5 / 109** · [FS-002: Pre-flight check and launch ▶️](FS-002-pre-flight-check-and-launch.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> The [👤 Mission planner](../../glossary.md#per-mission-planner) designs a [🗃️ Mission](../../glossary.md#ent-mission) for any [🔤 Activity](../../glossary.md#term-activity) in the [⚙️ Mission studio](../../glossary.md#sys-mission-studio): area, routes or [🗃️ Choreography](../../glossary.md#ent-choreography), [🗃️ Squad](../../glossary.md#ent-squad), [🗃️ Payload](../../glossary.md#ent-payload) and role of each [🗃️ Drone](../../glossary.md#ent-drone), and rules.

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

Turn a Client need into a complete Mission that breaks no rule before anyone goes to the [🗃️ Site](../../glossary.md#ent-site). The Mission planner draws the [🗃️ Geofence](../../glossary.md#ent-geofence), picks the Activity, builds a Squad in which each Drone can have its own [🗃️ Drone model](../../glossary.md#ent-drone-model), Payload and task, and sees at once any rule the Mission breaks. A Mission becomes Planned only when it is complete and valid, and can then be simulated.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Mission planner](../../glossary.md#per-mission-planner) | Persona | Designs the Mission |
| [🗃️ Mission](../../glossary.md#ent-mission) | Entity | From Draft to Planned |
| [🗃️ Squad](../../glossary.md#ent-squad) | Entity | Built from Ready Drones, mixed Drone models and Payloads |
| [🗃️ Payload](../../glossary.md#ent-payload) | Entity | Chosen per Drone for its task |
| [🗃️ Geofence](../../glossary.md#ent-geofence) | Entity | Drawn inside the Authorisation |
| [⚙️ Mission studio](../../glossary.md#sys-mission-studio) | System | Where the Mission is designed and checked |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-001: Geofence and Altitude ceiling](../business-rules/BR-001-geofence-and-altitude-ceiling.md) | Every route stays inside the Geofence and under the Altitude ceiling |
| [📏 BR-002: Separation distance](../business-rules/BR-002-separation-distance.md) | Routes and formations keep the Separation distance |
| [📏 BR-005: Autonomy level per Activity](../business-rules/BR-005-autonomy-level-per-activity.md) | The Activity sets the Autonomy level of the Mission |
| [📏 BR-010: Valid Authorisation for the Jurisdiction](../business-rules/BR-010-valid-authorisation-for-the-jurisdiction.md) | The Mission is designed under a covering Authorisation |
| [📏 BR-022: Payload compatibility](../business-rules/BR-022-payload-compatibility.md) | Each Drone gets a Payload that can do its task |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-001: Design a Mission](../use-cases/UC-001-design-a-mission.md) | [👤 Mission planner](../../glossary.md#per-mission-planner) |
| [🎬 UC-002: Simulate a Mission](../use-cases/UC-002-simulate-a-mission.md) | [👤 Mission planner](../../glossary.md#per-mission-planner) |
| [🎬 UC-021: Plan a Mission with the Mission assistant](../use-cases/UC-021-plan-a-mission-with-the-mission-assistant.md) | [👤 Mission planner](../../glossary.md#per-mission-planner) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a route above the Altitude ceiling **when** the Mission planner saves the Mission **then** it stays Draft and the leg at fault is shown | [📏 BR-001](../business-rules/BR-001-geofence-and-altitude-ceiling.md) | [🎬 UC-001](../use-cases/UC-001-design-a-mission.md) |
| AC-2 | **Given** a Squad of a thermal and an RGB Drone **when** the Mission planner assigns the thermal task to the RGB Drone **then** the assignment is refused | [📏 BR-022](../business-rules/BR-022-payload-compatibility.md) | [🎬 UC-001](../use-cases/UC-001-design-a-mission.md) |
| AC-3 | **Given** a complete Mission that breaks no rule **when** the Mission planner saves it **then** it becomes Planned | [📏 BR-010](../business-rules/BR-010-valid-authorisation-for-the-jurisdiction.md) | [🎬 UC-001](../use-cases/UC-001-design-a-mission.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Map background | Open map data (OpenStreetMap) by default; satellite imagery from a provider the [🗃️ Operator](../../glossary.md#ent-operator) licenses; maps cached for use without network |

## <a id="out-of-scope"></a>🚫 Out of scope

- Flying the Mission ([📘 FS-002: Pre-flight check and launch](FS-002-pre-flight-check-and-launch.md), [📘 FS-003: Live supervision](FS-003-live-supervision.md))
- The design of Choreographies, covered by [📘 FS-013: Light shows](FS-013-light-shows.md)

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

> [🏠 Index](../../README.md) · [◀️ Functional specifications](../README.md) · 📄 **Page 5 / 109** · [FS-002: Pre-flight check and launch ▶️](FS-002-pre-flight-check-and-launch.md)
<!-- /spec:nav-bottom -->
