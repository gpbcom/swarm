# 📏 BR-006: Fail-safe per Activity

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-005: Autonomy level per Activity](BR-005-autonomy-level-per-activity.md) · 📄 **Page 62 / 108** · [BR-007: Launch only after a passed Pre-flight check ▶️](BR-007-launch-only-after-a-passed-pre-flight-check.md)
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
> When a [🗃️ Drone](../../glossary.md#ent-drone) fails or is lost: in a [🔤 Light show](../../glossary.md#term-light-show) the whole [🗃️ Squad](../../glossary.md#ent-squad) MUST [🔤 Hold](../../glossary.md#term-hold), then land or [🔤 Return home](../../glossary.md#term-return-home), and the Mission becomes Aborted once every Drone has landed; in every other [🔤 Activity](../../glossary.md#term-activity) the failing Drone MUST Return home or land, the others MUST share its work, and the [🗃️ Mission](../../glossary.md#ent-mission) MUST be Held when fewer Drones remain than the minimum the [👤 Mission planner](../../glossary.md#per-mission-planner) set, or when the [👤 Pilot](../../glossary.md#per-pilot) loses the [🔤 Link](../../glossary.md#term-link) to the Squad.

## <a id="rationale"></a>💡 Rationale

Above an audience, any surprise is a danger: stopping everything is the safe answer. Elsewhere, the value of a Squad is that it can finish the work without one of its Drones.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | Inspection, 4 Drones, minimum 2; one Drone is lost | The 3 others share its area after the Pilot approves the Re-plan |
| 2 | ❌ Refused | Light show, one Drone of 200 has a motor fault | The whole Squad Holds, then lands at its landing positions |
| 3 | ❌ Refused | Patrol, 2 Drones, minimum 2; one Returns home | The Mission is Held and the Pilot decides |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> A [🗃️ Drone](../../glossary.md#ent-drone) that is lost cannot receive orders: it follows the Fail-safe programmed on board, which Swarm sets before take-off to Return home.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-004: Fail-safes and emergencies](../features/FS-004-fail-safes-and-emergencies.md)
- [📘 FS-013: Light shows](../features/FS-013-light-shows.md)
- [🎬 UC-005: Lose a Drone in flight](../use-cases/UC-005-lose-a-drone-in-flight.md)
- [🎬 UC-016: Import and fly a Light show](../use-cases/UC-016-import-and-fly-a-light-show.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-005: Autonomy level per Activity](BR-005-autonomy-level-per-activity.md) · 📄 **Page 62 / 108** · [BR-007: Launch only after a passed Pre-flight check ▶️](BR-007-launch-only-after-a-passed-pre-flight-check.md)
<!-- /spec:nav-bottom -->
