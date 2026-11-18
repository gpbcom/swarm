# 📏 BR-008: Operator isolation

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-007: Launch only after a passed Pre-flight check](BR-007-launch-only-after-a-passed-pre-flight-check.md) · 📄 **Page 64 / 108** · [BR-009: Evidence integrity ▶️](BR-009-evidence-integrity.md)
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
> A person MUST see and change only the data of their own [🗃️ Operator](../../glossary.md#ent-operator): no [🗃️ Mission](../../glossary.md#ent-mission), [🗃️ Drone](../../glossary.md#ent-drone), [🗃️ Flight log](../../glossary.md#ent-flight-log), [🗃️ Deliverable](../../glossary.md#ent-deliverable) or [👤 Client](../../glossary.md#per-client) of one Operator is visible to another, in the cloud as on premises.

## <a id="rationale"></a>💡 Rationale

Operators are competitors sharing one cloud service, and their Clients' Sites can be sensitive (energy, logistics, events).

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | A Pilot of Aerowing Services opens a Mission of Aerowing Services | The Mission opens |
| 2 | ❌ Refused | A Pilot of another Operator opens the link to that Mission | Not found; the attempt is logged |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-007: Data processing and Deliverables](../features/FS-007-data-processing-and-deliverables.md)
- [📘 FS-008: Client portal](../features/FS-008-client-portal.md)
- [📘 FS-012: Operators, deployment and languages](../features/FS-012-operators-deployment-and-languages.md)
- [🎬 UC-009: Process flight data into Deliverables](../use-cases/UC-009-process-flight-data-into-deliverables.md)
- [🎬 UC-015: Invite a Client to the Client portal](../use-cases/UC-015-invite-a-client-to-the-client-portal.md)
- [🎬 UC-020: Review the Defects of an Inspection](../use-cases/UC-020-review-the-defects-of-an-inspection.md)
- [🎬 UC-029: Create an Operator](../use-cases/UC-029-create-an-operator.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-007: Launch only after a passed Pre-flight check](BR-007-launch-only-after-a-passed-pre-flight-check.md) · 📄 **Page 64 / 108** · [BR-009: Evidence integrity ▶️](BR-009-evidence-integrity.md)
<!-- /spec:nav-bottom -->
