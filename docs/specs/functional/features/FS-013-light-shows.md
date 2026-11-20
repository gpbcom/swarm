# 📘 FS-013: Light shows

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-012: Operators, deployment and languages](FS-012-operators-deployment-and-languages.md) · 📄 **Page 17 / 120** · [FS-014: Agriculture ▶️](FS-014-agriculture.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> Swarm designs or imports a [🗃️ Choreography](../../glossary.md#ent-choreography) and flies it as a [🔤 Light show](../../glossary.md#term-light-show), Pre-planned, with music by time code.

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

Fly safe, precise Light shows. The [👤 Mission planner](../../glossary.md#per-mission-planner) builds simple shows on a timeline or imports complex ones from Blender or Skybrush Studio; Swarm checks [🔤 Separation distance](../../glossary.md#term-separation-distance), speeds and battery for every frame. In flight, any failure stops the whole [🗃️ Squad](../../glossary.md#ent-squad).

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Mission planner](../../glossary.md#per-mission-planner) | Persona | Designs or imports the show |
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Flies the show |
| [🗃️ Choreography](../../glossary.md#ent-choreography) | Entity | Timed positions and colours |
| [🗃️ Payload](../../glossary.md#ent-payload) | Entity | Show lights |
| [🗃️ Squad](../../glossary.md#ent-squad) | Entity | Many identical Drones |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-006: Fail-safe per Activity](../business-rules/BR-006-fail-safe-per-activity.md) | Any failure stops the whole Squad |
| [📏 BR-002: Separation distance](../business-rules/BR-002-separation-distance.md) | Separation distance in every frame and from the audience |
| [📏 BR-005: Autonomy level per Activity](../business-rules/BR-005-autonomy-level-per-activity.md) | Light shows are Pre-planned |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-016: Import and fly a Light show](../use-cases/UC-016-import-and-fly-a-light-show.md) | [👤 Mission planner](../../glossary.md#per-mission-planner), [👤 Pilot](../../glossary.md#per-pilot) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a Choreography with two Drones too close at one frame **when** it is imported **then** it is refused and the frame is named | [📏 BR-002](../business-rules/BR-002-separation-distance.md) | [🎬 UC-016](../use-cases/UC-016-import-and-fly-a-light-show.md) |
| AC-2 | **Given** a show in flight **when** one Drone fails **then** every Drone Holds, then lands | [📏 BR-006](../business-rules/BR-006-fail-safe-per-activity.md) | [🎬 UC-016](../use-cases/UC-016-import-and-fly-a-light-show.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Music | Swarm sends a standard time code (SMPTE LTC or MIDI time code) to the show's audio desk, or plays the music itself |
| After a fault | The Squad Holds and lands; once every Drone has landed, the Mission is Aborted |

## <a id="out-of-scope"></a>🚫 Out of scope

- Pyrotechnics on Drones

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

> [🏠 Index](../../README.md) · [◀️ FS-012: Operators, deployment and languages](FS-012-operators-deployment-and-languages.md) · 📄 **Page 17 / 120** · [FS-014: Agriculture ▶️](FS-014-agriculture.md)
<!-- /spec:nav-bottom -->
