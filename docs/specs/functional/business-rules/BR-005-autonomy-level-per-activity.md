# 📏 BR-005: Autonomy level per Activity

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-004: Pilot ratio](BR-004-pilot-ratio.md) · 📄 **Page 67 / 120** · [BR-006: Fail-safe per Activity ▶️](BR-006-fail-safe-per-activity.md)
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
> Each [🗃️ Mission](../../glossary.md#ent-mission) MUST fly at the [🔤 Autonomy level](../../glossary.md#term-autonomy-level) of its [🔤 Activity](../../glossary.md#term-activity): [🔤 Light show](../../glossary.md#term-light-show) Pre-planned; [🔤 Inspection](../../glossary.md#term-inspection) and [🔤 Patrol](../../glossary.md#term-patrol) Supervised autonomy; [🔤 Agriculture](../../glossary.md#term-agriculture) Pre-planned routes, with Supervised autonomy only for refills and failures.

## <a id="rationale"></a>💡 Rationale

A pre-planned Light show is predictable above an audience and easier to authorise. Inspection and Patrol gain from re-planning live, when a Drone drops out or an Alarm moves. Agriculture follows its Field plan but must react to refills and failures.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | A Light show flies its Choreography and only Fail-safes act in flight | Pre-planned |
| 2 | ✅ Allowed | An Inspection Squad shares the area of a returning Drone | Supervised autonomy, the Pilot approves (see BR-013) |
| 3 | ❌ Refused | A Light show Drone proposes a new path to avoid another | Not allowed: the Drone Holds and the Fail-safe of BR-006 applies |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-001: Mission design](../features/FS-001-mission-design.md)
- [📘 FS-003: Live supervision](../features/FS-003-live-supervision.md)
- [📘 FS-013: Light shows](../features/FS-013-light-shows.md)
- [📘 FS-014: Agriculture](../features/FS-014-agriculture.md)
- [📘 FS-015: Patrol](../features/FS-015-patrol.md)
- [🎬 UC-001: Design a Mission](../use-cases/UC-001-design-a-mission.md)
- [🎬 UC-016: Import and fly a Light show](../use-cases/UC-016-import-and-fly-a-light-show.md)
- [🎬 UC-017: Spray a Field with refills](../use-cases/UC-017-spray-a-field-with-refills.md)
- [🎬 UC-018: Respond to a Site Alarm](../use-cases/UC-018-respond-to-a-site-alarm.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-004: Pilot ratio](BR-004-pilot-ratio.md) · 📄 **Page 67 / 120** · [BR-006: Fail-safe per Activity ▶️](BR-006-fail-safe-per-activity.md)
<!-- /spec:nav-bottom -->
