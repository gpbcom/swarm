# 📏 BR-002: Separation distance

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-001: Geofence and Altitude ceiling](BR-001-geofence-and-altitude-ceiling.md) · 📄 **Page 58 / 109** · [BR-003: Weather limits ▶️](BR-003-weather-limits.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Type:** Constraint · **Updated:** 2026-11-18

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [📌 Statement](#statement)
2. [💡 Rationale](#rationale)
3. [🧪 Examples](#examples)
4. [⚠️ Exceptions](#exceptions)
5. [🔗 Referenced by](#referenced-by)
<!-- /spec:summary -->

## <a id="statement"></a>📌 Statement

> [!IMPORTANT]
> Two [🗃️ Drones](../../glossary.md#ent-drone) of a [🗃️ Squad](../../glossary.md#ent-squad) MUST always be at least the [🔤 Separation distance](../../glossary.md#term-separation-distance) of the [🗃️ Mission](../../glossary.md#ent-mission) apart, and no Drone MUST come closer than that distance to the people and obstacles declared on the [🗃️ Site](../../glossary.md#ent-site). The Separation distance MUST NOT be smaller than the largest minimum of the [🗃️ Drone models](../../glossary.md#ent-drone-model) in the Squad.

## <a id="rationale"></a>💡 Rationale

A collision inside the Squad is the risk that a single Drone does not have. In a [🔤 Light show](../../glossary.md#term-light-show), the Squad flies close together above an audience.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | Separation distance 3 m, two Drones 5 m apart | The Squad flies on |
| 2 | ❌ Refused | A Choreography places two Drones 1.5 m apart at 02:14 | The import is refused and names the frame and the two Drones |
| 3 | ❌ Refused | In flight, two Drones converge after a gust | Both Hold; Swarm proposes a Re-plan |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-001: Mission design](../features/FS-001-mission-design.md)
- [📘 FS-013: Light shows](../features/FS-013-light-shows.md)
- [🎬 UC-001: Design a Mission](../use-cases/UC-001-design-a-mission.md)
- [🎬 UC-002: Simulate a Mission](../use-cases/UC-002-simulate-a-mission.md)
- [🎬 UC-016: Import and fly a Light show](../use-cases/UC-016-import-and-fly-a-light-show.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-001: Geofence and Altitude ceiling](BR-001-geofence-and-altitude-ceiling.md) · 📄 **Page 58 / 109** · [BR-003: Weather limits ▶️](BR-003-weather-limits.md)
<!-- /spec:nav-bottom -->
