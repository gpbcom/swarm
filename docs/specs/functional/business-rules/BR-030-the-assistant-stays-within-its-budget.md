# 📏 BR-030: The Assistant stays within its budget

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-029: Flight-critical acts need a Pilot on duty](BR-029-flight-critical-acts-need-a-pilot-on-duty.md) · 📄 **Page 92 / 120** · [BR-031: A Squad shortfall is covered through the ERP ▶️](BR-031-a-squad-shortfall-is-covered-through-the-erp.md)
<!-- /spec:nav-top -->

**Status:** 🟡 Draft · **Type:** Constraint · **Updated:** 2026-11-20

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
> When the [🔤 Assistant budget](../../glossary.md#term-assistant-budget) of an [🗃️ Operator](../../glossary.md#ent-operator) or of a person reaches 80 %, the [⚙️ Assistant](../../glossary.md#sys-assistant) MUST warn; at 100 % it MUST only answer in read-only mode until the budget is raised, except during a flight, where its help MUST NOT stop.

## <a id="rationale"></a>💡 Rationale

The LLM provider charges for every answer. The Operator must see what it spends before the bill arrives, and a spent budget must never leave a Pilot without help in the air.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | Aerowing Services has used 80 % of its monthly Assistant budget | Every person of the Operator sees the warning, and the Back office shows the usage and the cost |
| 2 | ✅ Allowed | The budget is spent while Sam Carter flies a Squad | The Co-pilot keeps explaining Alerts and proposing Re-plans until the flight ends |
| 3 | ❌ Refused | The budget is spent; Léa Martin asks the Assistant to draft a Mission report | Refused: the Assistant says the budget is reached, answers what it can read, and offers to tell the person who sets the budget |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None, beyond the help during a flight that the statement keeps.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-023: AI Assistant](../features/FS-023-ai-assistant.md)
- [🎬 UC-031: Ask the Assistant](../use-cases/UC-031-ask-the-assistant.md)
- [🎬 UC-034: Let the Assistant hold a Squad](../use-cases/UC-034-let-the-assistant-hold-a-squad.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-029: Flight-critical acts need a Pilot on duty](BR-029-flight-critical-acts-need-a-pilot-on-duty.md) · 📄 **Page 92 / 120** · [BR-031: A Squad shortfall is covered through the ERP ▶️](BR-031-a-squad-shortfall-is-covered-through-the-erp.md)
<!-- /spec:nav-bottom -->
