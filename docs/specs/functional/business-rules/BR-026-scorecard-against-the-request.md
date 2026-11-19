# 📏 BR-026: Scorecard against the request

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-025: On-site changes are checked again](BR-025-on-site-changes-are-checked-again.md) · 📄 **Page 82 / 109** · [BR-027: The Pilot's attention is preserved ▶️](BR-027-the-pilot-s-attention-is-preserved.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Type:** Computation · **Updated:** 2026-11-18

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
> The [🗃️ Scorecard](../../glossary.md#ent-scorecard) of a [🗃️ Mission](../../glossary.md#ent-mission) MUST assess each acceptance criterion of the [👤 Client](../../glossary.md#per-client)'s request as passed or failed from the [🗃️ Flight log](../../glossary.md#ent-flight-log), the [🔤 Quality checks](../../glossary.md#term-quality-check) and the [🗃️ Deliverables](../../glossary.md#ent-deliverable), and is Passed only when every criterion passes. It MUST be published to the Client only after a [👤 Mission planner](../../glossary.md#per-mission-planner) has reviewed it. A re-fly is a new Mission linked to the original, and the original Scorecard is assessed again with both. A Flight log whose Evidence record shows Altered MUST NOT give Scorecard: Passed.

## <a id="rationale"></a>💡 Rationale

The Client asked for a result, not for a flight. The Scorecard shows, criterion by criterion, whether the result was delivered, and triggers a re-fly when it was not.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | Request: 100 % of Les Vignes covered, image overlap 75 %; actual: 100 %, 78 % | Scorecard: Passed |
| 2 | ❌ Refused | Coverage 96 %: two rows missed after a Drone was lost | Scorecard: Failed; the Debrief proposes a re-fly of the gaps |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-022: Debrief and assessment](../features/FS-022-debrief-and-assessment.md)
- [🎬 UC-011: Follow a Mission and download its Deliverables](../use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md)
- [🎬 UC-027: Debrief a Mission](../use-cases/UC-027-debrief-a-mission.md)
- [🎬 UC-028: Assess a Mission against the request](../use-cases/UC-028-assess-a-mission-against-the-request.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-025: On-site changes are checked again](BR-025-on-site-changes-are-checked-again.md) · 📄 **Page 82 / 109** · [BR-027: The Pilot's attention is preserved ▶️](BR-027-the-pilot-s-attention-is-preserved.md)
<!-- /spec:nav-bottom -->
