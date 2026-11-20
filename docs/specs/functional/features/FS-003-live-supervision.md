# 📘 FS-003: Live supervision

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-002: Pre-flight check and launch](FS-002-pre-flight-check-and-launch.md) · 📄 **Page 7 / 120** · [FS-004: Fail-safes and emergencies ▶️](FS-004-fail-safes-and-emergencies.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> In [⚙️ Ground control](../../glossary.md#sys-ground-control), the [👤 Pilot](../../glossary.md#per-pilot) supervises the [🗃️ Squad](../../glossary.md#ent-squad) in flight, approves or rejects [🗃️ Re-plans](../../glossary.md#ent-re-plan), and can intervene at any time.

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

Let one Pilot keep a correct picture of a whole Squad. Ground control shows each [🗃️ Drone](../../glossary.md#ent-drone) on the map with its state, [🗃️ Payload](../../glossary.md#ent-payload) and [🔤 Telemetry](../../glossary.md#term-telemetry), the progress of the [🗃️ Mission](../../glossary.md#ent-mission), and the [🔤 Alerts](../../glossary.md#term-alert). Under Supervised autonomy the Squad re-plans by itself; major Re-plans wait for the Pilot.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Supervising, approves Re-plans |
| [🗃️ Squad](../../glossary.md#ent-squad) | Entity | Flies the Mission |
| [🗃️ Re-plan](../../glossary.md#ent-re-plan) | Entity | Proposed, then Applied or Rejected |
| [⚙️ Ground control](../../glossary.md#sys-ground-control) | System | Shows the Squad and takes commands |
| [⚙️ Co-pilot](../../glossary.md#sys-co-pilot) | System | Explains Alerts and proposes Re-plans |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-012: Pilot override always available](../business-rules/BR-012-pilot-override-always-available.md) | The Pilot can always Hold, take control, Return home or land |
| [📏 BR-013: Re-plan approval](../business-rules/BR-013-re-plan-approval.md) | Major Re-plans need the Pilot's approval |
| [📏 BR-005: Autonomy level per Activity](../business-rules/BR-005-autonomy-level-per-activity.md) | Only Supervised autonomy Missions re-plan in flight |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-004: Supervise a Squad and approve a Re-plan](../use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md) | [👤 Pilot](../../glossary.md#per-pilot) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a Drone Returning home in an Inspection **when** the Squad proposes to share its area **then** the Re-plan waits for the Pilot's approval | [📏 BR-013](../business-rules/BR-013-re-plan-approval.md) | [🎬 UC-004](../use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md) |
| AC-2 | **Given** any Mission in flight **when** the Pilot presses Hold the Squad **then** every Drone Holds | [📏 BR-012](../business-rules/BR-012-pilot-override-always-available.md) | [🎬 UC-004](../use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Always visible per Drone | State, battery %, Link quality, altitude, [🗃️ Payload](../../glossary.md#ent-payload) |
| On demand | Speed, heading, GNSS accuracy, motor and Battery temperatures, Payload status |
| Re-plan answer time | 60 seconds (Operator setting); without an answer the Re-plan is Rejected, the Squad keeps its plan and the Alert stays open |

## <a id="out-of-scope"></a>🚫 Out of scope

- Failures and aborts ([📘 FS-004: Fail-safes and emergencies](FS-004-fail-safes-and-emergencies.md))
- The AI part of the proposals ([📘 FS-018: Live Co-pilot](FS-018-live-co-pilot.md))

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

> [🏠 Index](../../README.md) · [◀️ FS-002: Pre-flight check and launch](FS-002-pre-flight-check-and-launch.md) · 📄 **Page 7 / 120** · [FS-004: Fail-safes and emergencies ▶️](FS-004-fail-safes-and-emergencies.md)
<!-- /spec:nav-bottom -->
