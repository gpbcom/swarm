# 📏 BR-001: Geofence and Altitude ceiling

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ UC-034: Let the Assistant hold a Squad](../use-cases/UC-034-let-the-assistant-hold-a-squad.md) · 📄 **Page 63 / 120** · [BR-002: Separation distance ▶️](BR-002-separation-distance.md)
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
> A [🗃️ Drone](../../glossary.md#ent-drone) MUST NOT leave the [🗃️ Geofence](../../glossary.md#ent-geofence) of its [🗃️ Mission](../../glossary.md#ent-mission) nor fly above its [🔤 Altitude ceiling](../../glossary.md#term-altitude-ceiling). A Drone that reaches the edge of the Geofence MUST [🔤 Hold](../../glossary.md#term-hold), then [🔤 Return home](../../glossary.md#term-return-home).

## <a id="rationale"></a>💡 Rationale

The [🗃️ Authorisation](../../glossary.md#ent-authorisation) covers only that volume. Leaving it puts manned aviation and people on the ground at risk, and breaks the Authorisation the [🗃️ Operator](../../glossary.md#ent-operator) depends on. The rule applies at design time in the [⚙️ Mission studio](../../glossary.md#sys-mission-studio) and in flight, whoever flies the Drone.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | Altitude ceiling 120 m, a route at 100 m inside the area | The Mission can become Planned |
| 2 | ❌ Refused | A route drawn at 150 m under a 120 m Altitude ceiling | The Mission studio refuses to mark the Mission Planned and shows the leg at fault |
| 3 | ❌ Refused | In flight, wind pushes a Drone to the edge of the Geofence | The Drone Holds, then Returns home; the Pilot gets an Alert |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None. A [👤 Pilot](../../glossary.md#per-pilot) in manual control is held to the same Geofence.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-001: Mission design](../features/FS-001-mission-design.md)
- [📘 FS-004: Fail-safes and emergencies](../features/FS-004-fail-safes-and-emergencies.md)
- [📘 FS-014: Agriculture](../features/FS-014-agriculture.md)
- [🎬 UC-001: Design a Mission](../use-cases/UC-001-design-a-mission.md)
- [🎬 UC-017: Spray a Field with refills](../use-cases/UC-017-spray-a-field-with-refills.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ UC-034: Let the Assistant hold a Squad](../use-cases/UC-034-let-the-assistant-hold-a-squad.md) · 📄 **Page 63 / 120** · [BR-002: Separation distance ▶️](BR-002-separation-distance.md)
<!-- /spec:nav-bottom -->
