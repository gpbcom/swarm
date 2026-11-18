# 📏 BR-021: AI agents propose, people decide

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-020: Defects confirmed by a person](BR-020-defects-confirmed-by-a-person.md) · 📄 **Page 77 / 108** · [BR-022: Payload compatibility ▶️](BR-022-payload-compatibility.md)
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
> An AI agent ([⚙️ Mission assistant](../../glossary.md#sys-mission-assistant), [⚙️ Co-pilot](../../glossary.md#sys-co-pilot), [⚙️ Report writer](../../glossary.md#sys-report-writer)) MUST NOT launch, command, approve or publish anything by itself: each of its proposals takes effect only when a person accepts it, and Swarm MUST record who accepted it. An [🔤 Outside agent](../../glossary.md#term-outside-agent) acts as the delegate of the person whose access it holds and MAY do what that person may do, except that signing the Pre-flight check and launching MUST be confirmed by the person on their own device with their PIN, and abort and manual control MUST stay in Ground control; Swarm MUST record both the delegate and the person.

## <a id="rationale"></a>💡 Rationale

The Pilot and the Operator are accountable to the authorities and to the Client. AI agents speed up their work; they do not take decisions.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | The Co-pilot proposes a Re-plan; the Pilot approves | Applied, with the Pilot's name in the Flight log |
| 2 | ❌ Refused | The Report writer drafts a report | It stays a draft until the Mission planner publishes it |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-017: Mission assistant](../features/FS-017-mission-assistant.md)
- [📘 FS-018: Live Co-pilot](../features/FS-018-live-co-pilot.md)
- [📘 FS-019: Mission reports](../features/FS-019-mission-reports.md)
- [📘 FS-022: Debrief and assessment](../features/FS-022-debrief-and-assessment.md)
- [🎬 UC-004: Supervise a Squad and approve a Re-plan](../use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md)
- [🎬 UC-021: Plan a Mission with the Mission assistant](../use-cases/UC-021-plan-a-mission-with-the-mission-assistant.md)
- [🎬 UC-022: Receive the Mission report](../use-cases/UC-022-receive-the-mission-report.md)
- [🎬 UC-026: Handle an Alert](../use-cases/UC-026-handle-an-alert.md)
- [🎬 UC-028: Assess a Mission against the request](../use-cases/UC-028-assess-a-mission-against-the-request.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-020: Defects confirmed by a person](BR-020-defects-confirmed-by-a-person.md) · 📄 **Page 77 / 108** · [BR-022: Payload compatibility ▶️](BR-022-payload-compatibility.md)
<!-- /spec:nav-bottom -->
