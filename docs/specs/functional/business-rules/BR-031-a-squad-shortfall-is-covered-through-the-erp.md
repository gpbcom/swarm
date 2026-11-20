# 📏 BR-031: A Squad shortfall is covered through the ERP

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-030: The Assistant stays within its budget](BR-030-the-assistant-stays-within-its-budget.md) · 📄 **Page 93 / 120** · [BR-032: The Assistant reaches only what its person may reach ▶️](BR-032-the-assistant-reaches-only-what-its-person-may-reach.md)
<!-- /spec:nav-top -->

**Status:** 🟡 Draft · **Type:** Inference · **Updated:** 2026-11-20

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
> When a planned [🗃️ Squad](../../glossary.md#ent-squad) needs more [🗃️ Drones](../../glossary.md#ent-drone), [🗃️ Payloads](../../glossary.md#ent-payload) or [🗃️ Battery](../../glossary.md#ent-battery) units than the [🗃️ Fleet](../../glossary.md#ent-fleet) has ready on the Mission date, Swarm MUST show the [🔤 Squad shortfall](../../glossary.md#term-squad-shortfall) and MAY propose a [🗃️ Manufacturing order](../../glossary.md#ent-manufacturing-order) for a [🗃️ Drone model](../../glossary.md#ent-drone-model) built in-house, a [🗃️ Purchase order](../../glossary.md#ent-purchase-order) for what is bought, the earliest date the Squad can be complete, or a smaller Squad with its trade-off; an order MUST reach the [⚙️ ERP](../../glossary.md#sys-erp) only within the [🗃️ Assistant permission](../../glossary.md#ent-assistant-permission) of that action.

## <a id="rationale"></a>💡 Rationale

The Mission planner sizes the Squad from the work to do, not from what happens to be ready that day. Some Drone models the Operator builds itself, others it buys: the ERP knows the stock, the bills of materials and the lead times, so it is where a shortfall is covered.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | The Mission M-2026-0412 needs three Drones with a thermal camera on 3 December 2026; the Fleet has two Ready | Swarm shows a shortfall of one; the Assistant proposes a Manufacturing order for one X500 built in-house, ready on the date the ERP gives; Léa Martin accepts and the order reaches the ERP |
| 2 | ✅ Allowed | Same shortfall; Léa Martin prefers to fly with the Drones available | The Assistant proposes a Squad of two Drones and shows the trade-off: one hour forty minutes instead of one hour |
| 3 | ❌ Refused | "Place a Manufacturing order" is at Propose for the Mission planner; the Assistant would send the order by itself | Refused: the order waits for Léa Martin to accept it |
| 4 | ❌ Refused | The Operator has no ERP connected | The shortfall is shown, but no order and no earliest date can be proposed; the Assistant says why |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-024: ERP and Squad shortfall](../features/FS-024-erp-and-squad-shortfall.md)
- [🎬 UC-033: Cover a Squad shortfall through the ERP](../use-cases/UC-033-cover-a-squad-shortfall-through-the-erp.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-030: The Assistant stays within its budget](BR-030-the-assistant-stays-within-its-budget.md) · 📄 **Page 93 / 120** · [BR-032: The Assistant reaches only what its person may reach ▶️](BR-032-the-assistant-reaches-only-what-its-person-may-reach.md)
<!-- /spec:nav-bottom -->
