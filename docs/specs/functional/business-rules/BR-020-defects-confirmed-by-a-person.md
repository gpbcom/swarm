# 📏 BR-020: Defects confirmed by a person

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-019: Site agents request, never pilot](BR-019-site-agents-request-never-pilot.md) · 📄 **Page 76 / 109** · [BR-021: AI agents propose, people decide ▶️](BR-021-ai-agents-propose-people-decide.md)
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
> A [🗃️ Defect](../../glossary.md#ent-defect) found by detection MUST stay Suspected until a person confirms or dismisses it, and only Confirmed Defects MUST be reported to the [👤 Client](../../glossary.md#per-client). Dismissing a Defect MUST give a reason from a fixed list (not a Defect, duplicate, already known to the Client, image quality too low, other with a comment), and Swarm MUST record the name of the reviewer and the time of every confirmation and dismissal.

## <a id="rationale"></a>💡 Rationale

Detection models make mistakes. A false Defect sent to a Client costs a site visit and trust.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | The Mission planner confirms a hot spot on panel row 14 | Defect: Confirmed, in the Deliverables |
| 2 | ❌ Refused | A Suspected Defect nobody reviewed | Not in the report sent to the Client |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-016: Inspection](../features/FS-016-inspection.md)
- [📘 FS-019: Mission reports](../features/FS-019-mission-reports.md)
- [🎬 UC-020: Review the Defects of an Inspection](../use-cases/UC-020-review-the-defects-of-an-inspection.md)
- [🎬 UC-022: Receive the Mission report](../use-cases/UC-022-receive-the-mission-report.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-019: Site agents request, never pilot](BR-019-site-agents-request-never-pilot.md) · 📄 **Page 76 / 109** · [BR-021: AI agents propose, people decide ▶️](BR-021-ai-agents-propose-people-decide.md)
<!-- /spec:nav-bottom -->
