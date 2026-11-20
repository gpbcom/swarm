# 📏 BR-015: Approved Drone models only

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ BR-014: Simulation isolation](BR-014-simulation-isolation.md) · 📄 **Page 77 / 120** · [BR-016: Clients see only their own Missions ▶️](BR-016-clients-see-only-their-own-missions.md)
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
> A [🗃️ Drone](../../glossary.md#ent-drone) MUST NOT fly unless its [🗃️ Drone model](../../glossary.md#ent-drone-model) has a [⚙️ Drone adapter](../../glossary.md#sys-drone-adapter) that has passed the compatibility test of Swarm for that model. The test runs first in the [⚙️ Simulator](../../glossary.md#sys-simulator) where the Drone model allows it, then in one real flight in a test area flown by a [👤 Pilot](../../glossary.md#per-pilot); a new firmware version makes the Drone model Not approved until it passes again.

## <a id="rationale"></a>💡 Rationale

Swarm talks to many families of Drones (MAVLink, DJI, Skydio, Parrot). Each Drone model must prove that it obeys Hold, Return home, Geofence and manual control as Swarm expects.

## <a id="examples"></a>🧪 Examples

| # | Case | Given | Expected |
| --- | --- | --- | --- |
| 1 | ✅ Allowed | X500 (PX4) with the MAVLink Drone adapter, test passed | The Drone model is approved |
| 2 | ❌ Refused | A new Drone model whose test failed on Return home | Its Drones stay Grounded |

## <a id="exceptions"></a>⚠️ Exceptions

> [!WARNING]
> None.

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
- [📘 FS-005: Fleet and readiness](../features/FS-005-fleet-and-readiness.md)
- [📘 FS-011: Drone adapters](../features/FS-011-drone-adapters.md)
- [🎬 UC-007: Register a Drone and track its readiness](../use-cases/UC-007-register-a-drone-and-track-its-readiness.md)
- [🎬 UC-014: Connect a new Drone model](../use-cases/UC-014-connect-a-new-drone-model.md)
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ BR-014: Simulation isolation](BR-014-simulation-isolation.md) · 📄 **Page 77 / 120** · [BR-016: Clients see only their own Missions ▶️](BR-016-clients-see-only-their-own-missions.md)
<!-- /spec:nav-bottom -->
