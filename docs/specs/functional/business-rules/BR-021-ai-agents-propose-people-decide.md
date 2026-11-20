# 📏 BR-021: AI agents propose, people decide

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-020: Defects confirmed by a person](BR-020-defects-confirmed-by-a-person.md) · 📄 **Page 83 / 120** · [BR-022: Payload compatibility ▶️](BR-022-payload-compatibility.md)
<!-- /spec:nav-top -->

**Status:** 🟡 Draft · **Type:** Authorisation · **Updated:** 2026-11-20

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
> An AI agent ([⚙️ Assistant](../../glossary.md#sys-assistant), [⚙️ Mission assistant](../../glossary.md#sys-mission-assistant), [⚙️ Co-pilot](../../glossary.md#sys-co-pilot), [⚙️ Report writer](../../glossary.md#sys-report-writer)) or an [🔤 Outside agent](../../glossary.md#term-outside-agent) MAY do an action only within the [🗃️ Assistant permission](../../glossary.md#ent-assistant-permission) people set for it ([📏 BR-028: Assistant permissions are layered](BR-028-assistant-permissions-are-layered.md)): at Propose, the action MUST take effect only when a person accepts it; at Act, it MAY take effect without that acceptance, after the person's confirmation where the Operator asked for it, and a [🔤 Flight-critical act](../../glossary.md#term-flight-critical-act) only as [📏 BR-029: Flight-critical acts need a Pilot on duty](BR-029-flight-critical-acts-need-a-pilot-on-duty.md) allows; an Outside agent MUST NOT sign the Pre-flight check or launch without the person's confirmation on their own device with their PIN, whatever the permission; Swarm MUST record the person it acted for and, at Propose, the person who accepted.

## <a id="rationale"></a>💡 Rationale

The Pilot and the Operator are accountable to the authorities and to the Client. AI agents speed up their work; people decide how far each one may go, action by action, and accept what they keep for themselves. Every act names the person behind it.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | The Co-pilot proposes a Re-plan; "Approve a Re-plan" is at Propose; the Pilot approves | Applied, with the Pilot's name in the Flight log |
| 2 | ❌ Refused | The Report writer drafts a report; "Publish a Deliverable" is at Propose | It stays a draft until the Mission planner publishes it |
| 3 | ✅ Allowed | "Place a Purchase order" is at Act for Fleet maintainers; a Fleet maintainer asks the Assistant to order two spare Batteries | The Assistant places the Purchase order in the ERP and reports it; the Assistant activity names the Fleet maintainer |
| 4 | ❌ Refused | An Outside agent acting for a Pilot asks to launch, and "Launch" is at Propose | Nothing happens until the Pilot accepts it |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-017: Mission assistant](../features/FS-017-mission-assistant.md)
- [📘 FS-018: Live Co-pilot](../features/FS-018-live-co-pilot.md)
- [📘 FS-019: Mission reports](../features/FS-019-mission-reports.md)
- [📘 FS-022: Debrief and assessment](../features/FS-022-debrief-and-assessment.md)
- [📘 FS-023: AI Assistant](../features/FS-023-ai-assistant.md)
- [📘 FS-024: ERP and Squad shortfall](../features/FS-024-erp-and-squad-shortfall.md)
- [🎬 UC-004: Supervise a Squad and approve a Re-plan](../use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md)
- [🎬 UC-021: Plan a Mission with the Mission assistant](../use-cases/UC-021-plan-a-mission-with-the-mission-assistant.md)
- [🎬 UC-022: Receive the Mission report](../use-cases/UC-022-receive-the-mission-report.md)
- [🎬 UC-026: Handle an Alert](../use-cases/UC-026-handle-an-alert.md)
- [🎬 UC-028: Assess a Mission against the request](../use-cases/UC-028-assess-a-mission-against-the-request.md)
- [🎬 UC-031: Ask the Assistant](../use-cases/UC-031-ask-the-assistant.md)
- [🎬 UC-033: Cover a Squad shortfall through the ERP](../use-cases/UC-033-cover-a-squad-shortfall-through-the-erp.md)
- [🎬 UC-034: Let the Assistant hold a Squad](../use-cases/UC-034-let-the-assistant-hold-a-squad.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-020: Defects confirmed by a person](BR-020-defects-confirmed-by-a-person.md) · 📄 **Page 83 / 120** · [BR-022: Payload compatibility ▶️](BR-022-payload-compatibility.md)
<!-- /spec:nav-bottom -->
