# 📘 FS-010: Simulator and training

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-009: Evidence ledger and Anchoring](FS-009-evidence-ledger-and-anchoring.md) · 📄 **Page 14 / 120** · [FS-011: Drone adapters ▶️](FS-011-drone-adapters.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> The [⚙️ Simulator](../../glossary.md#sys-simulator) flies a virtual [🗃️ Squad](../../glossary.md#ent-squad) with the real flight software of each [🗃️ Drone model](../../glossary.md#ent-drone-model), to test [🗃️ Missions](../../glossary.md#ent-mission) and train [👤 Pilots](../../glossary.md#per-pilot).

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🎯 Goal](#goal)
2. [👤 Personas and entities](#personas)
3. [📏 Business rules](#business-rules)
4. [🎬 Use cases](#use-cases)
5. [✅ Acceptance criteria](#acceptance)
6. [🗒️ Details](#details)
7. [🚫 Out of scope](#out-of-scope)
8. [❓ Open questions](#open-questions)
9. [🔗 References](#references)
<!-- /spec:summary -->

## <a id="goal"></a>🎯 Goal

Test before flying and train without risk. The Mission planner simulates a Planned Mission to see coverage, timing, battery use and conflicts. The Pilot trains in [⚙️ Ground control](../../glossary.md#sys-ground-control) on simulated Squads, including failures injected by an [👤 Instructor](../../glossary.md#per-instructor).

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Trains |
| [👤 Instructor](../../glossary.md#per-instructor) | Persona | Injects failures during training |
| [👤 Mission planner](../../glossary.md#per-mission-planner) | Persona | Tests Missions |
| [🗃️ Squad](../../glossary.md#ent-squad) | Entity | Virtual |
| [⚙️ Simulator](../../glossary.md#sys-simulator) | System | Flies virtual Drones |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-014: Simulation isolation](../business-rules/BR-014-simulation-isolation.md) | A simulated Squad never commands a real Drone |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-002: Simulate a Mission](../use-cases/UC-002-simulate-a-mission.md) | [👤 Mission planner](../../glossary.md#per-mission-planner) |
| [🎬 UC-013: Train on the Simulator](../use-cases/UC-013-train-on-the-simulator.md) | [👤 Pilot](../../glossary.md#per-pilot) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a training session **when** the Pilot launches **then** no real Drone receives a command and the Flight log is marked simulated | [📏 BR-014](../business-rules/BR-014-simulation-isolation.md) | [🎬 UC-013](../use-cases/UC-013-train-on-the-simulator.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Failures in training | Injected by an [👤 Instructor](../../glossary.md#per-instructor), from a second Ground control on the same training session |

## <a id="out-of-scope"></a>🚫 Out of scope

- Photorealistic rendering of the Payload images

## <a id="open-questions"></a>❓ Open questions

> [!WARNING]
> None.

## <a id="references"></a>🔗 References

- 🧭 [Functional overview](../README.md)
- 📖 [Glossary](../../glossary.md)
- 🎤 [Interview decisions](../../../research/interview.md)
- 🔭 [Market landscape](../../../research/landscape.md)

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ FS-009: Evidence ledger and Anchoring](FS-009-evidence-ledger-and-anchoring.md) · 📄 **Page 14 / 120** · [FS-011: Drone adapters ▶️](FS-011-drone-adapters.md)
<!-- /spec:nav-bottom -->
