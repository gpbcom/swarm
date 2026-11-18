# 📏 BR-016: Clients see only their own Missions

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-015: Approved Drone models only](BR-015-approved-drone-models-only.md) · 📄 **Page 72 / 108** · [BR-017: Every screen in four languages ▶️](BR-017-every-screen-in-four-languages.md)
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
> A [👤 Client](../../glossary.md#per-client) and its [👤 Site agents](../../glossary.md#per-site-agent) MUST see only the [🗃️ Missions](../../glossary.md#ent-mission), [🗃️ Flight logs](../../glossary.md#ent-flight-log) and [🗃️ Deliverables](../../glossary.md#ent-deliverable) of their own Client account, and only what the [🗃️ Operator](../../glossary.md#ent-operator) has published to them.

## <a id="rationale"></a>💡 Rationale

Several Clients of one Operator use the same Client portal. Sites and Defects are confidential.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | Priya Shah of Helio Energy opens the Deliverables of Les Vignes | They open |
| 2 | ❌ Refused | Priya Shah opens a Mission of Northgate Logistics | Not found |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-008: Client portal](../features/FS-008-client-portal.md)
- [🎬 UC-010: Order a Mission in the Client portal](../use-cases/UC-010-order-a-mission-in-the-client-portal.md)
- [🎬 UC-011: Follow a Mission and download its Deliverables](../use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md)
- [🎬 UC-015: Invite a Client to the Client portal](../use-cases/UC-015-invite-a-client-to-the-client-portal.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-015: Approved Drone models only](BR-015-approved-drone-models-only.md) · 📄 **Page 72 / 108** · [BR-017: Every screen in four languages ▶️](BR-017-every-screen-in-four-languages.md)
<!-- /spec:nav-bottom -->
