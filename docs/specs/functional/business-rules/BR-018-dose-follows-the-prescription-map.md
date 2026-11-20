# 📏 BR-018: Dose follows the Prescription map

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-017: Every screen in four languages](BR-017-every-screen-in-four-languages.md) · 📄 **Page 80 / 120** · [BR-019: Site agents request, never pilot ▶️](BR-019-site-agents-request-never-pilot.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Type:** Computation · **Updated:** 2026-11-18

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
> In [🔤 Agriculture](../../glossary.md#term-agriculture), the dose applied in each zone of a [🗃️ Field](../../glossary.md#ent-field) MUST be the dose the [🗃️ Prescription map](../../glossary.md#ent-prescription-map) gives for that zone, or the uniform dose of the [🗃️ Mission](../../glossary.md#ent-mission) when there is no Prescription map, and nothing MUST be sprayed outside the Field.

## <a id="rationale"></a>💡 Rationale

Overdosing harms crops and the environment and breaks product regulations; spraying outside the Field can reach neighbours and water.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | Zone A 2 L/ha, zone B 1 L/ha in the Prescription map | Each zone receives its dose |
| 2 | ✅ Allowed | No Prescription map, uniform dose 1.5 L/ha | The whole Field receives 1.5 L/ha |
| 3 | ❌ Refused | A Drone reaches the Field boundary with the pump on | The pump stops at the boundary |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-014: Agriculture](../features/FS-014-agriculture.md)
- [🎬 UC-017: Spray a Field with refills](../use-cases/UC-017-spray-a-field-with-refills.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-017: Every screen in four languages](BR-017-every-screen-in-four-languages.md) · 📄 **Page 80 / 120** · [BR-019: Site agents request, never pilot ▶️](BR-019-site-agents-request-never-pilot.md)
<!-- /spec:nav-bottom -->
