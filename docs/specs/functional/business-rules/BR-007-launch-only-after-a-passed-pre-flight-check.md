# 📏 BR-007: Launch only after a passed Pre-flight check

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-006: Fail-safe per Activity](BR-006-fail-safe-per-activity.md) · 📄 **Page 63 / 109** · [BR-008: Operator isolation ▶️](BR-008-operator-isolation.md)
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
> A [🗃️ Mission](../../glossary.md#ent-mission) MUST NOT launch until every automatic check of the [🗃️ Pre-flight check](../../glossary.md#ent-pre-flight-check) has passed and the [👤 Pilot](../../glossary.md#per-pilot) has signed it: [🗃️ Geofence](../../glossary.md#ent-geofence), weather ([📏 BR-003](BR-003-weather-limits.md)), [🗃️ Authorisation](../../glossary.md#ent-authorisation) ([📏 BR-010](BR-010-valid-authorisation-for-the-jurisdiction.md)), [🔤 Pilot ratio](../../glossary.md#term-pilot-ratio) ([📏 BR-004](BR-004-pilot-ratio.md)), readiness of every [🗃️ Drone](../../glossary.md#ent-drone) ([📏 BR-011](BR-011-drone-readiness.md)), [🔤 Links](../../glossary.md#term-link), and the airspace grant of the [⚙️ U-space service](../../glossary.md#sys-u-space-service) where the [🔤 Jurisdiction](../../glossary.md#term-jurisdiction) requires it. The Pilot signs with a personal PIN, after ticking every item of the checklist the [🗃️ Operator](../../glossary.md#ent-operator) set for the Activity; a signed Pre-flight check stays valid 30 minutes. For an Agriculture Mission, the Pilot's and the Operator's licences MUST be present and valid.

## <a id="rationale"></a>💡 Rationale

Swarm verifies what a machine can verify better than a person; the Pilot remains responsible and signs. Both are recorded in the [🗃️ Flight log](../../glossary.md#ent-flight-log).

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | All checks pass, the Pilot signs | The Mission becomes Verified and can launch |
| 2 | ❌ Refused | One Drone of the Squad is Grounded | The check fails on readiness; the Pilot cannot sign |
| 3 | ❌ Refused | The U-space service has not granted the airspace | The check fails on airspace |
| 4 | ❌ Refused | The Pre-flight check was signed 40 minutes ago | The automatic checks run again and the Pilot signs again |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-002: Pre-flight check and launch](../features/FS-002-pre-flight-check-and-launch.md)
- [🎬 UC-003: Run the Pre-flight check and launch](../use-cases/UC-003-run-the-pre-flight-check-and-launch.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-006: Fail-safe per Activity](BR-006-fail-safe-per-activity.md) · 📄 **Page 63 / 109** · [BR-008: Operator isolation ▶️](BR-008-operator-isolation.md)
<!-- /spec:nav-bottom -->
