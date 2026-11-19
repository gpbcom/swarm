# 📘 FS-004: Fail-safes and emergencies

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-003: Live supervision](FS-003-live-supervision.md) · 📄 **Page 8 / 109** · [FS-005: Fleet and readiness ▶️](FS-005-fleet-and-readiness.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> When a [🗃️ Drone](../../glossary.md#ent-drone) fails or is lost, Swarm applies the [🔤 Fail-safe](../../glossary.md#term-fail-safe) of the [🔤 Activity](../../glossary.md#term-activity); the [👤 Pilot](../../glossary.md#per-pilot) can take manual control or abort.

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

Keep people safe and save the [🗃️ Mission](../../glossary.md#ent-mission) when possible. In a [🔤 Light show](../../glossary.md#term-light-show), any failure stops the whole [🗃️ Squad](../../glossary.md#ent-squad). In the other Activities, the failing Drone applies [🔤 Return home](../../glossary.md#term-return-home) and the others share its work, until too few Drones remain. The Pilot can take manual control of one Drone or abort the Mission at any time.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | In manual control, aborts |
| [🗃️ Drone](../../glossary.md#ent-drone) | Entity | Lost, Returning |
| [🗃️ Mission](../../glossary.md#ent-mission) | Entity | Held, Aborted |
| [⚙️ Ground control](../../glossary.md#sys-ground-control) | System | Raises Alerts and applies Fail-safes |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-006: Fail-safe per Activity](../business-rules/BR-006-fail-safe-per-activity.md) | Fail-safe per Activity |
| [📏 BR-012: Pilot override always available](../business-rules/BR-012-pilot-override-always-available.md) | The Pilot's override always works |
| [📏 BR-001: Geofence and Altitude ceiling](../business-rules/BR-001-geofence-and-altitude-ceiling.md) | A Drone at the Geofence edge Holds and Returns home |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-005: Lose a Drone in flight](../use-cases/UC-005-lose-a-drone-in-flight.md) | [👤 Pilot](../../glossary.md#per-pilot) |
| [🎬 UC-006: Take manual control or abort](../use-cases/UC-006-take-manual-control-or-abort.md) | [👤 Pilot](../../glossary.md#per-pilot) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** an Inspection with 4 Drones and a minimum of 2 **when** one Drone is Lost **then** it follows its on-board Fail-safe and the others propose to share its area | [📏 BR-006](../business-rules/BR-006-fail-safe-per-activity.md) | [🎬 UC-005](../use-cases/UC-005-lose-a-drone-in-flight.md) |
| AC-2 | **Given** a Light show **when** one Drone fails **then** the whole Squad Holds and lands | [📏 BR-006](../business-rules/BR-006-fail-safe-per-activity.md) | [🎬 UC-005](../use-cases/UC-005-lose-a-drone-in-flight.md) |
| AC-3 | **Given** a Mission Flying **when** the Pilot aborts **then** every Drone Returns home and the Mission is Aborted | [📏 BR-012](../business-rules/BR-012-pilot-override-always-available.md) | [🎬 UC-006](../use-cases/UC-006-take-manual-control-or-abort.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Drone: Lost | After 5 seconds without any Link path (Operator setting, never below the minimum of the Drone model) |
| Abort | Press and hold 1 second (button, key or gamepad), no dialog: one action, no accident |
| Give a Drone back | Return to Squad: Swarm checks the Separation distance, the Drone flies back to its planned position and the Squad resumes |
| From Mission: Held | Resume (the automatic checks run again), Return home for every Drone, or abort |
| After a flight | A Drone on the ground is [🔄 Drone: Landed](../../glossary.md#st-drone-landed) |
| Return to Squad refused | When the Separation distance check fails, the Drone stays in manual control, an Alert says why, and Swarm proposes a safe path as a Re-plan for the Pilot to approve |
| Abort released early | Released before 1 second, nothing is sent; a hint says to hold 1 second |
| Landing reserve | A Drone must land with at least 20 % battery (Operator setting, never below the Drone model minimum); Swarm sends it home in time |

## <a id="out-of-scope"></a>🚫 Out of scope

- Collision avoidance with manned aviation (detect and avoid), left to the Drone models and the U-space service

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

> [🏠 Index](../../README.md) · [◀️ FS-003: Live supervision](FS-003-live-supervision.md) · 📄 **Page 8 / 109** · [FS-005: Fleet and readiness ▶️](FS-005-fleet-and-readiness.md)
<!-- /spec:nav-bottom -->
