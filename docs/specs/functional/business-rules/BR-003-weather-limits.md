# 📏 BR-003: Weather limits

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-002: Separation distance](BR-002-separation-distance.md) · 📄 **Page 65 / 120** · [BR-004: Pilot ratio ▶️](BR-004-pilot-ratio.md)
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
> A [🗃️ Mission](../../glossary.md#ent-mission) MUST NOT launch, and a [🗃️ Squad](../../glossary.md#ent-squad) in flight MUST [🔤 Return home](../../glossary.md#term-return-home), when the wind, rain, temperature or visibility at the [🗃️ Site](../../glossary.md#ent-site) given by the [⚙️ Weather service](../../glossary.md#sys-weather-service) is outside the limits of any [🗃️ Drone model](../../glossary.md#ent-drone-model) of the Squad.

## <a id="rationale"></a>💡 Rationale

Each Drone model is built for a weather envelope. The weakest Drone of the Squad sets the limit, because the Squad shares one plan.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | Wind 8 m/s, lowest Drone model limit 12 m/s | The weather check passes |
| 2 | ❌ Refused | Forecast gusts 15 m/s during the time slot, limit 12 m/s | The Pre-flight check fails on weather |
| 3 | ❌ Refused | In flight, the wind rises above the limit | The Squad Returns home; the Pilot gets an Alert |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-002: Pre-flight check and launch](../features/FS-002-pre-flight-check-and-launch.md)
- [🎬 UC-003: Run the Pre-flight check and launch](../use-cases/UC-003-run-the-pre-flight-check-and-launch.md)
- [🎬 UC-034: Let the Assistant hold a Squad](../use-cases/UC-034-let-the-assistant-hold-a-squad.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-002: Separation distance](BR-002-separation-distance.md) · 📄 **Page 65 / 120** · [BR-004: Pilot ratio ▶️](BR-004-pilot-ratio.md)
<!-- /spec:nav-bottom -->
