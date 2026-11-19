# 📏 BR-024: Alert thresholds within the Operator limits

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-023: Fixed safety controls](BR-023-fixed-safety-controls.md) · 📄 **Page 80 / 109** · [BR-025: On-site changes are checked again ▶️](BR-025-on-site-changes-are-checked-again.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Type:** Validation · **Updated:** 2026-11-18

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
> A [👤 Pilot](../../glossary.md#per-pilot) MAY change an [🔤 Alert threshold](../../glossary.md#term-alert-threshold) only within the limits the [🗃️ Operator](../../glossary.md#ent-operator) sets, and the threshold MUST NOT be less safe than the limits of the [🗃️ Drone models](../../glossary.md#ent-drone-model) in use.

## <a id="rationale"></a>💡 Rationale

Pilots differ in experience and prefer earlier or later warnings, but the Operator is accountable for safety margins.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | Operator range for the low battery warning: 25 % to 40 %; the Pilot sets 30 % | Saved |
| 2 | ❌ Refused | The Pilot sets the low battery warning at 15 % | Refused: below the Operator's limit |
| 3 | ✅ Allowed | Default Operator limits: Link warning 30 % to 70 %, wind warning 60 % to 90 % of the Drone model limit | The Pilot sets the wind warning at 70 % |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-020: Ground control Workspace and configuration](../features/FS-020-ground-control-workspace-and-configuration.md)
- [🎬 UC-023: Configure the Workspace of Ground control](../use-cases/UC-023-configure-the-workspace-of-ground-control.md)
- [🎬 UC-026: Handle an Alert](../use-cases/UC-026-handle-an-alert.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-023: Fixed safety controls](BR-023-fixed-safety-controls.md) · 📄 **Page 80 / 109** · [BR-025: On-site changes are checked again ▶️](BR-025-on-site-changes-are-checked-again.md)
<!-- /spec:nav-bottom -->
