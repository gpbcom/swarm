# 📏 BR-032: The Assistant reaches only what its person may reach

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-031: A Squad shortfall is covered through the ERP](BR-031-a-squad-shortfall-is-covered-through-the-erp.md) · 📄 **Page 94 / 120** · [Technical specifications ▶️](../../technical/README.md)
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
> The [⚙️ Assistant](../../glossary.md#sys-assistant) MUST read and act only on what the person it acts for may read and do: within that person's [🗃️ Operator](../../glossary.md#ent-operator) ([📏 BR-008: Operator isolation](BR-008-operator-isolation.md)) and, for a [👤 Client](../../glossary.md#per-client) or a [👤 Site agent](../../glossary.md#per-site-agent), within that Client's own Missions and [🗃️ Sites](../../glossary.md#ent-site) ([📏 BR-016: Clients see only their own Missions](BR-016-clients-see-only-their-own-missions.md)), whatever its [🗃️ Assistant permission](../../glossary.md#ent-assistant-permission) and its [🔤 Connectors](../../glossary.md#term-connector).

## <a id="rationale"></a>💡 Rationale

An AI that sees everything would leak one Client's data to another, or one Operator's to a competitor, through a single well-worded question. The Assistant is a way to use a person's access, never a way around it.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | The Client Priya Shah of Helio Energy asks for her Deliverables | The Assistant lists the Deliverables of Helio Energy's Missions only |
| 2 | ❌ Refused | Priya Shah asks about a Mission of another Client of Aerowing Services | Refused: the Assistant says it cannot see that Mission |
| 3 | ❌ Refused | A Knowledge document of another Operator would answer a question | Never searched: the Assistant searches the person's own Operator only |
| 4 | ❌ Refused | A Trigger set up by a person whose access has been removed fires | Nothing runs: the Trigger stops with the person's access |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-023: AI Assistant](../features/FS-023-ai-assistant.md)
- [🎬 UC-031: Ask the Assistant](../use-cases/UC-031-ask-the-assistant.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-031: A Squad shortfall is covered through the ERP](BR-031-a-squad-shortfall-is-covered-through-the-erp.md) · 📄 **Page 94 / 120** · [Technical specifications ▶️](../../technical/README.md)
<!-- /spec:nav-bottom -->
