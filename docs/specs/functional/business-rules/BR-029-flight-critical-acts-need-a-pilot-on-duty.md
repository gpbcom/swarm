# 📏 BR-029: Flight-critical acts need a Pilot on duty

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-028: Assistant permissions are layered](BR-028-assistant-permissions-are-layered.md) · 📄 **Page 91 / 120** · [BR-030: The Assistant stays within its budget ▶️](BR-030-the-assistant-stays-within-its-budget.md)
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
> The [⚙️ Assistant](../../glossary.md#sys-assistant) MAY do a [🔤 Flight-critical act](../../glossary.md#term-flight-critical-act) at Act only while a named [👤 Pilot](../../glossary.md#per-pilot) is on duty for that [🗃️ Squad](../../glossary.md#ent-squad) and sees it in [⚙️ Ground control](../../glossary.md#sys-ground-control); it MUST announce the act with a countdown the Pilot can cancel, and Swarm MUST record that Pilot as the accountable person in the [🗃️ Flight log](../../glossary.md#ent-flight-log).

## <a id="rationale"></a>💡 Rationale

The remote pilot in command answers for the flight under every Jurisdiction. The Operator may let the Assistant act fast, for example hold a Squad when the wind rises beyond the limits, but only under the eyes of a Pilot who can stop it and who stays accountable.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | "Hold" is at Act for the Pilot role; the wind rises beyond the limits while Sam Carter is on duty with the Squad open in Ground control | The Assistant announces the Hold with its countdown; Sam Carter does not cancel; the Squad holds and the Flight log names Sam Carter as accountable |
| 2 | ✅ Allowed | Same case; Sam Carter cancels during the countdown | Nothing is done; the cancelled act is recorded in the Assistant activity |
| 3 | ❌ Refused | "Launch" is at Act, but no Pilot is on duty for the Squad | Not done: the launch becomes a proposal to the Pilots of the Operator, with a Notification |
| 4 | ❌ Refused | A Pilot is on duty but does not have the Squad open in Ground control | Not done: the Assistant asks the Pilot to open the Squad, or proposes the act instead |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> The Fail-safes of the Squad ([📏 BR-006: Fail-safe per Activity](BR-006-fail-safe-per-activity.md)) act by themselves, without the Assistant and without a countdown, and the Pilot can always take over ([📏 BR-012: Pilot override always available](BR-012-pilot-override-always-available.md)).

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-023: AI Assistant](../features/FS-023-ai-assistant.md)
- [🎬 UC-032: Set the Assistant permissions](../use-cases/UC-032-set-the-assistant-permissions.md)
- [🎬 UC-034: Let the Assistant hold a Squad](../use-cases/UC-034-let-the-assistant-hold-a-squad.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-028: Assistant permissions are layered](BR-028-assistant-permissions-are-layered.md) · 📄 **Page 91 / 120** · [BR-030: The Assistant stays within its budget ▶️](BR-030-the-assistant-stays-within-its-budget.md)
<!-- /spec:nav-bottom -->
