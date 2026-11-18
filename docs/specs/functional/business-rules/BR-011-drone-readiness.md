# 📏 BR-011: Drone readiness

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-010: Valid Authorisation for the Jurisdiction](BR-010-valid-authorisation-for-the-jurisdiction.md) · 📄 **Page 67 / 108** · [BR-012: Pilot override always available ▶️](BR-012-pilot-override-always-available.md)
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
> A [🗃️ Drone](../../glossary.md#ent-drone) MUST be Ready to join a [🗃️ Squad](../../glossary.md#ent-squad): no maintenance due, no open fault, every [🗃️ Battery](../../glossary.md#ent-battery) it uses above the health threshold of its [🗃️ Drone model](../../glossary.md#ent-drone-model), and an approved Drone model ([📏 BR-015](BR-015-approved-drone-models-only.md)). Otherwise it is Grounded.

## <a id="rationale"></a>💡 Rationale

One weak Drone endangers the whole Squad and, under BR-006, can stop a Light show. Maintenance intervals come from the maker of the Drone model; the Fleet maintainer may make them shorter, never longer.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | Maintenance due in 12 flight hours, no fault | Ready |
| 2 | ❌ Refused | Maintenance overdue by 2 flight hours | Grounded until the Fleet maintainer closes the maintenance |
| 3 | ❌ Refused | Battery health below the threshold of the Drone model | The Battery cannot be assigned; the Drone needs another Battery |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-002: Pre-flight check and launch](../features/FS-002-pre-flight-check-and-launch.md)
- [📘 FS-005: Fleet and readiness](../features/FS-005-fleet-and-readiness.md)
- [🎬 UC-003: Run the Pre-flight check and launch](../use-cases/UC-003-run-the-pre-flight-check-and-launch.md)
- [🎬 UC-007: Register a Drone and track its readiness](../use-cases/UC-007-register-a-drone-and-track-its-readiness.md)
- [🎬 UC-014: Connect a new Drone model](../use-cases/UC-014-connect-a-new-drone-model.md)
- [🎬 UC-024: Configure each Drone of the Squad on the Site](../use-cases/UC-024-configure-each-drone-of-the-squad-on-the-site.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-010: Valid Authorisation for the Jurisdiction](BR-010-valid-authorisation-for-the-jurisdiction.md) · 📄 **Page 67 / 108** · [BR-012: Pilot override always available ▶️](BR-012-pilot-override-always-available.md)
<!-- /spec:nav-bottom -->
