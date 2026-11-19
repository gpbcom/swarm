# 📏 BR-027: The Pilot's attention is preserved

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-026: Scorecard against the request](BR-026-scorecard-against-the-request.md) · 📄 **Page 83 / 109** · [Technical specifications ▶️](../../technical/README.md)
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
> [⚙️ Ground control](../../glossary.md#sys-ground-control) MUST keep the [👤 Pilot](../../glossary.md#per-pilot)'s attention on what matters: at most the number of video streams the [🗃️ Operator](../../glossary.md#ent-operator) allows on the platform, one [🔤 Focus view](../../glossary.md#term-focus-view) at a time, new events queued without replacing the open Focus view, the map and the [🗃️ Squad](../../glossary.md#ent-squad) always visible, critical [🔤 Alerts](../../glossary.md#term-alert), Hold the Squad and abort never covered, and the previous view one action away. An event a Drone detects opens the Focus view by itself only at or above the Pilot's severity setting (Information, Warning, Critical; default Warning and above).

## <a id="rationale"></a>💡 Rationale

One Pilot supervises several Drones. A screen that changes by itself, or too many videos at once, makes the Pilot miss the Alert that matters.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | Alpha detects a hot spot above the Pilot's severity setting, no Focus view open | The Focus view of Alpha opens; the map and the Squad stay visible, smaller |
| 2 | ❌ Refused | Charlie detects a person while the Focus view of Alpha is open | No switch: Charlie's event queues with a badge until the Pilot clicks it |
| 3 | ❌ Refused | The Pilot asks for 6 streams on a laptop limited to 2 | Refused: 2 at most |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-021: Ground control monitoring](../features/FS-021-ground-control-monitoring.md)
- [🎬 UC-023: Configure the Workspace of Ground control](../use-cases/UC-023-configure-the-workspace-of-ground-control.md)
- [🎬 UC-025: Monitor a Mission in Ground control](../use-cases/UC-025-monitor-a-mission-in-ground-control.md)
- [🎬 UC-030: Focus on a Drone](../use-cases/UC-030-focus-on-a-drone.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-026: Scorecard against the request](BR-026-scorecard-against-the-request.md) · 📄 **Page 83 / 109** · [Technical specifications ▶️](../../technical/README.md)
<!-- /spec:nav-bottom -->
