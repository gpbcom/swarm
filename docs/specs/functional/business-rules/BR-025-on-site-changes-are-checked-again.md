# 📏 BR-025: On-site changes are checked again

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-024: Alert thresholds within the Operator limits](BR-024-alert-thresholds-within-the-operator-limits.md) · 📄 **Page 87 / 120** · [BR-026: Scorecard against the request ▶️](BR-026-scorecard-against-the-request.md)
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
> When the [👤 Pilot](../../glossary.md#per-pilot) changes a [🗃️ Drone](../../glossary.md#ent-drone), a [🗃️ Payload](../../glossary.md#ent-payload) or a [🗃️ Battery](../../glossary.md#ent-battery) of the [🗃️ Squad](../../glossary.md#ent-squad) on the [🗃️ Site](../../glossary.md#ent-site), Swarm MUST check the [🗃️ Mission](../../glossary.md#ent-mission) again against [📏 BR-011](BR-011-drone-readiness.md) and [📏 BR-022](BR-022-payload-compatibility.md), and the [🗃️ Pre-flight check](../../glossary.md#ent-pre-flight-check) MUST be run and signed again.

## <a id="rationale"></a>💡 Rationale

On-site changes are normal (a spare Drone, a fresh Battery, another camera) but each one can break a rule the Mission planner had checked.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | The Pilot replaces Charlie by the spare Echo, same Drone model and Payload | Checks pass; the Pilot signs a new Pre-flight check |
| 2 | ❌ Refused | The Pilot mounts a sprayer tank on a Drone model that cannot lift it | Refused, with the excess weight |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-020: Ground control Workspace and configuration](../features/FS-020-ground-control-workspace-and-configuration.md)
- [🎬 UC-024: Configure each Drone of the Squad on the Site](../use-cases/UC-024-configure-each-drone-of-the-squad-on-the-site.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-024: Alert thresholds within the Operator limits](BR-024-alert-thresholds-within-the-operator-limits.md) · 📄 **Page 87 / 120** · [BR-026: Scorecard against the request ▶️](BR-026-scorecard-against-the-request.md)
<!-- /spec:nav-bottom -->
