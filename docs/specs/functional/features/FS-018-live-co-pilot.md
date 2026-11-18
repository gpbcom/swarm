# 📘 FS-018: Live Co-pilot

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-017: Mission assistant](FS-017-mission-assistant.md) · 📄 **Page 22 / 108** · [FS-019: Mission reports ▶️](FS-019-mission-reports.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> In flight, the [⚙️ Co-pilot](../../glossary.md#sys-co-pilot) watches the [🔤 Telemetry](../../glossary.md#term-telemetry), explains [🔤 Alerts](../../glossary.md#term-alert) in plain words and proposes [🗃️ Re-plans](../../glossary.md#ent-re-plan) to the [👤 Pilot](../../glossary.md#per-pilot).

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

Reduce the load on a Pilot supervising several [🗃️ Drones](../../glossary.md#ent-drone). The Co-pilot spots trends (a Battery draining faster, a [🔤 Link](../../glossary.md#term-link) weakening, wind rising), explains them, and proposes a Re-plan with its reasons. The Pilot approves or rejects.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Approves or rejects |
| [🗃️ Re-plan](../../glossary.md#ent-re-plan) | Entity | Proposed by the Co-pilot |
| [⚙️ Co-pilot](../../glossary.md#sys-co-pilot) | System | Watches and proposes |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-021: AI agents propose, people decide](../business-rules/BR-021-ai-agents-propose-people-decide.md) | The Co-pilot never commands the Squad |
| [📏 BR-013: Re-plan approval](../business-rules/BR-013-re-plan-approval.md) | Major Re-plans need the Pilot's approval |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-004: Supervise a Squad and approve a Re-plan](../use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md) | [👤 Pilot](../../glossary.md#per-pilot) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a Battery draining faster than planned **when** the Co-pilot notices **then** it proposes a Re-plan with its reason, which waits for the Pilot | [📏 BR-021](../business-rules/BR-021-ai-agents-propose-people-decide.md) | [🎬 UC-004](../use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Speech | The Co-pilot speaks critical Alerts aloud (Drone Lost, Geofence, weather beyond limits); the Pilot can mute the others |
| Muting | Critical Alerts are always spoken and can never be muted; the Pilot may mute the others |

## <a id="out-of-scope"></a>🚫 Out of scope

- Voice interaction

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

> [🏠 Index](../../README.md) · [◀️ FS-017: Mission assistant](FS-017-mission-assistant.md) · 📄 **Page 22 / 108** · [FS-019: Mission reports ▶️](FS-019-mission-reports.md)
<!-- /spec:nav-bottom -->
