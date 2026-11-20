# 📏 BR-028: Assistant permissions are layered

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-027: The Pilot's attention is preserved](BR-027-the-pilot-s-attention-is-preserved.md) · 📄 **Page 90 / 120** · [BR-029: Flight-critical acts need a Pilot on duty ▶️](BR-029-flight-critical-acts-need-a-pilot-on-duty.md)
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
> The [🗃️ Assistant permission](../../glossary.md#ent-assistant-permission) of an action MUST NOT be set higher for a role than the ceiling the [👤 Swarm administrator](../../glossary.md#per-swarm-administrator) set for the [🗃️ Operator](../../glossary.md#ent-operator), nor higher for a person than the level of their role; each person MAY lower their own levels, and a new Operator MUST start at Propose for every action its people may do.

## <a id="rationale"></a>💡 Rationale

The Operator answers to the authorities and to its Clients for every act done in its name, so it decides how far the [⚙️ Assistant](../../glossary.md#sys-assistant) may go, inside a ceiling the Swarm administrator keeps per Operator. A person who wants more control may keep the Assistant on a shorter leash for themselves, but never give it more than their role allows.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | The Swarm administrator set Act as the ceiling of "Place a Purchase order" for Aerowing Services, and the Operator sets Act for its Fleet maintainers | Fleet maintainers' Assistant places Purchase orders and reports them |
| 2 | ✅ Allowed | The Mission planner Léa Martin lowers "Publish a Deliverable" from Act to Propose for herself | Applied to Léa Martin only: her Assistant now proposes, she publishes |
| 3 | ❌ Refused | The Operator sets Act for "Launch" for its Pilots while the ceiling is Propose | Refused: the level stays Propose, and the screen shows the ceiling |
| 4 | ❌ Refused | A Pilot raises "Abort" above the level of the Pilot role for himself | Refused: a person may only lower their own levels |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-023: AI Assistant](../features/FS-023-ai-assistant.md)
- [📘 FS-024: ERP and Squad shortfall](../features/FS-024-erp-and-squad-shortfall.md)
- [🎬 UC-031: Ask the Assistant](../use-cases/UC-031-ask-the-assistant.md)
- [🎬 UC-032: Set the Assistant permissions](../use-cases/UC-032-set-the-assistant-permissions.md)
- [🎬 UC-033: Cover a Squad shortfall through the ERP](../use-cases/UC-033-cover-a-squad-shortfall-through-the-erp.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-027: The Pilot's attention is preserved](BR-027-the-pilot-s-attention-is-preserved.md) · 📄 **Page 90 / 120** · [BR-029: Flight-critical acts need a Pilot on duty ▶️](BR-029-flight-critical-acts-need-a-pilot-on-duty.md)
<!-- /spec:nav-bottom -->
