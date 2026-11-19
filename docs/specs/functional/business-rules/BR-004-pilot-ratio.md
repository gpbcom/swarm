# 📏 BR-004: Pilot ratio

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-003: Weather limits](BR-003-weather-limits.md) · 📄 **Page 60 / 109** · [BR-005: Autonomy level per Activity ▶️](BR-005-autonomy-level-per-activity.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Type:** Constraint · **Updated:** 2026-11-18

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
> Swarm MUST NOT launch a [🗃️ Squad](../../glossary.md#ent-squad) with more [🗃️ Drones](../../glossary.md#ent-drone) than the [🔤 Pilot ratio](../../glossary.md#term-pilot-ratio) of the [🗃️ Authorisation](../../glossary.md#ent-authorisation) allows for one [👤 Pilot](../../glossary.md#per-pilot).

## <a id="rationale"></a>💡 Rationale

In the EU and in the US, one Pilot for several Drones is allowed only within the limits of a specific Authorisation, exemption or waiver.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | Pilot ratio 5, Squad of 4 Drones | The check passes |
| 2 | ❌ Refused | Pilot ratio 3, Squad of 6 Drones | The launch is refused; the Mission planner can split the Mission into two Squads with two Pilots |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> Flights in the [⚙️ Simulator](../../glossary.md#sys-simulator) are not limited (see [📏 BR-014: Simulation isolation](BR-014-simulation-isolation.md)).

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-002: Pre-flight check and launch](../features/FS-002-pre-flight-check-and-launch.md)
- [📘 FS-006: Authorisations and compliance](../features/FS-006-authorisations-and-compliance.md)
- [🎬 UC-003: Run the Pre-flight check and launch](../use-cases/UC-003-run-the-pre-flight-check-and-launch.md)
- [🎬 UC-008: Record an Authorisation](../use-cases/UC-008-record-an-authorisation.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-003: Weather limits](BR-003-weather-limits.md) · 📄 **Page 60 / 109** · [BR-005: Autonomy level per Activity ▶️](BR-005-autonomy-level-per-activity.md)
<!-- /spec:nav-bottom -->
