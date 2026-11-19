# 📏 BR-023: Fixed safety controls

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-022: Payload compatibility](BR-022-payload-compatibility.md) · 📄 **Page 79 / 109** · [BR-024: Alert thresholds within the Operator limits ▶️](BR-024-alert-thresholds-within-the-operator-limits.md)
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
> On every platform of [⚙️ Ground control](../../glossary.md#sys-ground-control), Hold the [🗃️ Squad](../../glossary.md#ent-squad) and abort the [🗃️ Mission](../../glossary.md#ent-mission) MUST always be one action away, visible on every screen, and their keyboard and gamepad inputs MUST NOT be changed by any [🔤 Control mapping](../../glossary.md#term-control-mapping). Both act when held for 1 second, without a dialog: Hold the Squad with the key H or both gamepad bumpers, abort with Ctrl+Shift+A or the gamepad Back and Start buttons.

## <a id="rationale"></a>💡 Rationale

In an emergency the Pilot acts by reflex. Those two commands must be where the hand expects them, whatever Workspace or controller the Pilot uses.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | The Pilot moves the video panel to the second screen | Hold the Squad and abort stay in the title bar of every screen |
| 2 | ❌ Refused | The Pilot maps the abort key to another command | Refused: the input is fixed |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-020: Ground control Workspace and configuration](../features/FS-020-ground-control-workspace-and-configuration.md)
- [📘 FS-021: Ground control monitoring](../features/FS-021-ground-control-monitoring.md)
- [🎬 UC-006: Take manual control or abort](../use-cases/UC-006-take-manual-control-or-abort.md)
- [🎬 UC-023: Configure the Workspace of Ground control](../use-cases/UC-023-configure-the-workspace-of-ground-control.md)
- [🎬 UC-025: Monitor a Mission in Ground control](../use-cases/UC-025-monitor-a-mission-in-ground-control.md)
- [🎬 UC-030: Focus on a Drone](../use-cases/UC-030-focus-on-a-drone.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-022: Payload compatibility](BR-022-payload-compatibility.md) · 📄 **Page 79 / 109** · [BR-024: Alert thresholds within the Operator limits ▶️](BR-024-alert-thresholds-within-the-operator-limits.md)
<!-- /spec:nav-bottom -->
