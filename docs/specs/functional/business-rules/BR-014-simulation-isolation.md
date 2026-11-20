# 📏 BR-014: Simulation isolation

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-013: Re-plan approval](BR-013-re-plan-approval.md) · 📄 **Page 76 / 120** · [BR-015: Approved Drone models only ▶️](BR-015-approved-drone-models-only.md)
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
> A [🗃️ Squad](../../glossary.md#ent-squad) flown in the [⚙️ Simulator](../../glossary.md#sys-simulator) MUST NOT send any command to a real [🗃️ Drone](../../glossary.md#ent-drone), and its [🗃️ Flight log](../../glossary.md#ent-flight-log) MUST be marked as simulated.

## <a id="rationale"></a>💡 Rationale

The same Ground control flies real and simulated Squads, for training and testing. A mix-up must be impossible.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | A Pilot trains with a simulated Squad of 6 | No real Drone receives a command; the Flight log reads Simulated |
| 2 | ❌ Refused | A simulated Mission tries to address the real Drone Alpha | Refused and logged |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-010: Simulator and training](../features/FS-010-simulator-and-training.md)
- [🎬 UC-002: Simulate a Mission](../use-cases/UC-002-simulate-a-mission.md)
- [🎬 UC-013: Train on the Simulator](../use-cases/UC-013-train-on-the-simulator.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-013: Re-plan approval](BR-013-re-plan-approval.md) · 📄 **Page 76 / 120** · [BR-015: Approved Drone models only ▶️](BR-015-approved-drone-models-only.md)
<!-- /spec:nav-bottom -->
