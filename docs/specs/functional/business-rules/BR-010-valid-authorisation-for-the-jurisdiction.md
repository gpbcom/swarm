# 📏 BR-010: Valid Authorisation for the Jurisdiction

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-009: Evidence integrity](BR-009-evidence-integrity.md) · 📄 **Page 66 / 108** · [BR-011: Drone readiness ▶️](BR-011-drone-readiness.md)
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
> A [🗃️ Mission](../../glossary.md#ent-mission) MUST fly under an [🗃️ Authorisation](../../glossary.md#ent-authorisation) that is Valid on the day, for its [🔤 Jurisdiction](../../glossary.md#term-jurisdiction), and that covers its [🔤 Activity](../../glossary.md#term-activity), its area, its [🔤 Altitude ceiling](../../glossary.md#term-altitude-ceiling) and, when the Mission is [🔤 BVLOS](../../glossary.md#term-bvlos), BVLOS operations. When an Authorisation expires, the Planned Missions under it go back to Draft and the [👤 Mission planner](../../glossary.md#per-mission-planner) is told.

## <a id="rationale"></a>💡 Rationale

Flights with several Drones per Pilot, or BVLOS, are in the Specific category in the EU (SORA 2.5, standard scenarios) and need an exemption or waiver in the US. Without a covering Authorisation, the Operator flies illegally.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | EU Authorisation valid to 2027-06-30, Inspection, BVLOS covered | The check passes |
| 2 | ❌ Refused | Authorisation expired on 2026-11-30, Mission on 2026-12-03 | The check fails: Authorisation: Expired |
| 3 | ❌ Refused | BVLOS Mission under an Authorisation without BVLOS | The check fails and names the missing condition |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> Flights in the [⚙️ Simulator](../../glossary.md#sys-simulator) need no Authorisation.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-001: Mission design](../features/FS-001-mission-design.md)
- [📘 FS-002: Pre-flight check and launch](../features/FS-002-pre-flight-check-and-launch.md)
- [📘 FS-006: Authorisations and compliance](../features/FS-006-authorisations-and-compliance.md)
- [🎬 UC-001: Design a Mission](../use-cases/UC-001-design-a-mission.md)
- [🎬 UC-003: Run the Pre-flight check and launch](../use-cases/UC-003-run-the-pre-flight-check-and-launch.md)
- [🎬 UC-008: Record an Authorisation](../use-cases/UC-008-record-an-authorisation.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-009: Evidence integrity](BR-009-evidence-integrity.md) · 📄 **Page 66 / 108** · [BR-011: Drone readiness ▶️](BR-011-drone-readiness.md)
<!-- /spec:nav-bottom -->
