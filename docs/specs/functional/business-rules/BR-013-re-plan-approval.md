# 📏 BR-013: Re-plan approval

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-012: Pilot override always available](BR-012-pilot-override-always-available.md) · 📄 **Page 69 / 109** · [BR-014: Simulation isolation ▶️](BR-014-simulation-isolation.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Type:** Authorisation · **Updated:** 2026-11-18

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
> Under Supervised autonomy, a [🗃️ Re-plan](../../glossary.md#ent-re-plan) that changes the area covered, adds or removes a [🗃️ Drone](../../glossary.md#ent-drone), or extends the duration of the [🗃️ Mission](../../glossary.md#ent-mission) MUST be approved by the [👤 Pilot](../../glossary.md#per-pilot) before it applies. Smaller corrections inside the [🗃️ Geofence](../../glossary.md#ent-geofence) (a path around an obstacle, a change of spacing) MAY apply without approval and are logged. The Pilot has 60 seconds (Operator setting) to answer; without an answer the Re-plan is Rejected and the Squad keeps its plan.

## <a id="rationale"></a>💡 Rationale

The Pilot must keep a correct picture of what the Squad does, without being asked about every small correction.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | A Drone steps around a crane inside the Geofence | Applied without approval, logged |
| 2 | ✅ Allowed | The Pilot approves sharing the area of a returning Drone | Re-plan: Applied |
| 3 | ❌ Refused | The Pilot rejects the proposal to extend the Mission by 10 minutes | Re-plan: Rejected; the Squad keeps its plan |
| 4 | ❌ Refused | The Pilot does not answer a proposed Re-plan within 60 seconds | Re-plan: Rejected; the Alert stays open |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> Pre-planned Missions have no Re-plan in flight, only Fail-safes (see [📏 BR-005: Autonomy level per Activity](BR-005-autonomy-level-per-activity.md)).

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-003: Live supervision](../features/FS-003-live-supervision.md)
- [📘 FS-018: Live Co-pilot](../features/FS-018-live-co-pilot.md)
- [📘 FS-021: Ground control monitoring](../features/FS-021-ground-control-monitoring.md)
- [🎬 UC-004: Supervise a Squad and approve a Re-plan](../use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md)
- [🎬 UC-006: Take manual control or abort](../use-cases/UC-006-take-manual-control-or-abort.md)
- [🎬 UC-017: Spray a Field with refills](../use-cases/UC-017-spray-a-field-with-refills.md)
- [🎬 UC-026: Handle an Alert](../use-cases/UC-026-handle-an-alert.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-012: Pilot override always available](BR-012-pilot-override-always-available.md) · 📄 **Page 69 / 109** · [BR-014: Simulation isolation ▶️](BR-014-simulation-isolation.md)
<!-- /spec:nav-bottom -->
