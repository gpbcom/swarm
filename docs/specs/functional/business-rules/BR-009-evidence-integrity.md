# 📏 BR-009: Evidence integrity

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-008: Operator isolation](BR-008-operator-isolation.md) · 📄 **Page 65 / 109** · [BR-010: Valid Authorisation for the Jurisdiction ▶️](BR-010-valid-authorisation-for-the-jurisdiction.md)
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
> When a [🗃️ Flight log](../../glossary.md#ent-flight-log) or a [🗃️ Deliverable](../../glossary.md#ent-deliverable) is closed, Swarm MUST create its [🗃️ Evidence record](../../glossary.md#ent-evidence-record), signed and chained to the previous one, and MUST anchor it with the [⚙️ Anchoring service](../../glossary.md#sys-anchoring-service) the [🗃️ Operator](../../glossary.md#ent-operator) chose, if any. Only fingerprints MAY leave Swarm, never the data.

## <a id="rationale"></a>💡 Rationale

Authorities, insurers, Clients and courts need to trust that a Flight log, a spray map or a patrol clip was not changed after the fact. The interview kept blockchain as one Anchoring option among others, never for flight coordination. By default the Operator anchors with a qualified timestamping authority (eIDAS, RFC 3161); the blockchain option uses a public blockchain through an aggregator. When a record shows Altered, the Operator is told at once.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | A Mission completes; the Operator chose a timestamping authority | The Evidence record is created and anchored with a timestamp token |
| 2 | ✅ Allowed | The Operator chose no Anchoring | The Evidence record is signed and chained, not anchored |
| 3 | ❌ Refused | Someone edits a Flight log after it was closed | Verification shows Evidence record: Altered |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-007: Data processing and Deliverables](../features/FS-007-data-processing-and-deliverables.md)
- [📘 FS-009: Evidence ledger and Anchoring](../features/FS-009-evidence-ledger-and-anchoring.md)
- [📘 FS-019: Mission reports](../features/FS-019-mission-reports.md)
- [📘 FS-022: Debrief and assessment](../features/FS-022-debrief-and-assessment.md)
- [🎬 UC-009: Process flight data into Deliverables](../use-cases/UC-009-process-flight-data-into-deliverables.md)
- [🎬 UC-012: Verify the Evidence record of a flight](../use-cases/UC-012-verify-the-evidence-record-of-a-flight.md)
- [🎬 UC-018: Respond to a Site Alarm](../use-cases/UC-018-respond-to-a-site-alarm.md)
- [🎬 UC-020: Review the Defects of an Inspection](../use-cases/UC-020-review-the-defects-of-an-inspection.md)
- [🎬 UC-022: Receive the Mission report](../use-cases/UC-022-receive-the-mission-report.md)
- [🎬 UC-027: Debrief a Mission](../use-cases/UC-027-debrief-a-mission.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-008: Operator isolation](BR-008-operator-isolation.md) · 📄 **Page 65 / 109** · [BR-010: Valid Authorisation for the Jurisdiction ▶️](BR-010-valid-authorisation-for-the-jurisdiction.md)
<!-- /spec:nav-bottom -->
