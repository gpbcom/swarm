# 📏 BR-022: Payload compatibility

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-021: AI agents propose, people decide](BR-021-ai-agents-propose-people-decide.md) · 📄 **Page 84 / 120** · [BR-023: Fixed safety controls ▶️](BR-023-fixed-safety-controls.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Type:** Validation · **Updated:** 2026-11-18

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
> Each [🗃️ Drone](../../glossary.md#ent-drone) of a [🗃️ Squad](../../glossary.md#ent-squad) MAY carry its own [🗃️ Payload](../../glossary.md#ent-payload) and role, and a Drone MUST be assigned to a task of the [🗃️ Mission](../../glossary.md#ent-mission) only when its Payload can perform that task, fits its [🗃️ Drone model](../../glossary.md#ent-drone-model), and keeps the Drone within the weight limit of its Drone model.

## <a id="rationale"></a>💡 Rationale

Mixed Squads are the strength of a swarm: in an Inspection, a thermal camera and a zoom camera fly together; in a Patrol, one Drone carries a spotlight and another a loudspeaker. Each pairing must still be safe and able to do its part.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | Inspection of Les Vignes: Alpha with a thermal camera on the panels, Bravo with an RGB camera for the orthomosaic | Both tasks are covered |
| 2 | ❌ Refused | A sprayer tank assigned to a Drone model that cannot lift it | The Mission cannot become Planned; the Mission studio names the Drone and the excess weight |
| 3 | ❌ Refused | A thermal inspection task assigned to a Drone with an RGB camera only | The assignment is refused |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-001: Mission design](../features/FS-001-mission-design.md)
- [📘 FS-005: Fleet and readiness](../features/FS-005-fleet-and-readiness.md)
- [🎬 UC-001: Design a Mission](../use-cases/UC-001-design-a-mission.md)
- [🎬 UC-007: Register a Drone and track its readiness](../use-cases/UC-007-register-a-drone-and-track-its-readiness.md)
- [🎬 UC-024: Configure each Drone of the Squad on the Site](../use-cases/UC-024-configure-each-drone-of-the-squad-on-the-site.md)
- [🎬 UC-033: Cover a Squad shortfall through the ERP](../use-cases/UC-033-cover-a-squad-shortfall-through-the-erp.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-021: AI agents propose, people decide](BR-021-ai-agents-propose-people-decide.md) · 📄 **Page 84 / 120** · [BR-023: Fixed safety controls ▶️](BR-023-fixed-safety-controls.md)
<!-- /spec:nav-bottom -->
