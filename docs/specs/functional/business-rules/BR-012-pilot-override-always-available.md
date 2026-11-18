# 📏 BR-012: Pilot override always available

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-011: Drone readiness](BR-011-drone-readiness.md) · 📄 **Page 68 / 108** · [BR-013: Re-plan approval ▶️](BR-013-re-plan-approval.md)
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
> At any time and at any [🔤 Autonomy level](../../glossary.md#term-autonomy-level), the [👤 Pilot](../../glossary.md#per-pilot) MUST be able to [🔤 Hold](../../glossary.md#term-hold), take manual control of, [🔤 Return home](../../glossary.md#term-return-home) or land any [🗃️ Drone](../../glossary.md#ent-drone) or the whole [🗃️ Squad](../../glossary.md#ent-squad), and Swarm MUST carry out the command as fast as the [🔤 Link](../../glossary.md#term-link) allows.

## <a id="rationale"></a>💡 Rationale

The Pilot is the remote pilot in command in both Jurisdictions. Autonomy helps the Pilot; it never takes the last word away.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | A Squad under Supervised autonomy is re-planning | The Pilot presses Hold the Squad; every Drone Holds |
| 2 | ✅ Allowed | A Light show is running | The Pilot lands the Squad; the Choreography stops |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> A Drone that is Lost cannot receive the command: it follows its on-board Fail-safe (see [📏 BR-006: Fail-safe per Activity](BR-006-fail-safe-per-activity.md)). Every Drone also keeps a landing reserve of at least 20 % battery (Operator setting, never below the Drone model minimum): Swarm sends it home in time.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-003: Live supervision](../features/FS-003-live-supervision.md)
- [📘 FS-004: Fail-safes and emergencies](../features/FS-004-fail-safes-and-emergencies.md)
- [📘 FS-021: Ground control monitoring](../features/FS-021-ground-control-monitoring.md)
- [🎬 UC-004: Supervise a Squad and approve a Re-plan](../use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md)
- [🎬 UC-005: Lose a Drone in flight](../use-cases/UC-005-lose-a-drone-in-flight.md)
- [🎬 UC-006: Take manual control or abort](../use-cases/UC-006-take-manual-control-or-abort.md)
- [🎬 UC-025: Monitor a Mission in Ground control](../use-cases/UC-025-monitor-a-mission-in-ground-control.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-011: Drone readiness](BR-011-drone-readiness.md) · 📄 **Page 68 / 108** · [BR-013: Re-plan approval ▶️](BR-013-re-plan-approval.md)
<!-- /spec:nav-bottom -->
