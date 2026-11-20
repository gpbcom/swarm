# 📏 BR-019: Site agents request, never pilot

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-018: Dose follows the Prescription map](BR-018-dose-follows-the-prescription-map.md) · 📄 **Page 81 / 120** · [BR-020: Defects confirmed by a person ▶️](BR-020-defects-confirmed-by-a-person.md)
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
> A [👤 Site agent](../../glossary.md#per-site-agent) MAY request a [🗃️ Mission](../../glossary.md#ent-mission) on demand and MUST NOT launch, command or change a [🗃️ Squad](../../glossary.md#ent-squad). The request becomes a Mission only when a [👤 Pilot](../../glossary.md#per-pilot) accepts it. A request waits 10 minutes (Operator setting); without a Pilot's answer it is Declined, and the Site agent and every Pilot on duty are told.

## <a id="rationale"></a>💡 Rationale

Site agents know the Site but are not qualified Pilots. The Pilot remains responsible for every flight.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | Inès Garcia requests a look at gate 3 | Mission: Requested, sent to the Pilot |
| 2 | ❌ Refused | Inès Garcia tries to send the Squad elsewhere during the flight | Not possible from the Client portal |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-015: Patrol](../features/FS-015-patrol.md)
- [🎬 UC-018: Respond to a Site Alarm](../use-cases/UC-018-respond-to-a-site-alarm.md)
- [🎬 UC-019: Request a Patrol on demand](../use-cases/UC-019-request-a-patrol-on-demand.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-018: Dose follows the Prescription map](BR-018-dose-follows-the-prescription-map.md) · 📄 **Page 81 / 120** · [BR-020: Defects confirmed by a person ▶️](BR-020-defects-confirmed-by-a-person.md)
<!-- /spec:nav-bottom -->
