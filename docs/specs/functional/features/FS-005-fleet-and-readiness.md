# 📘 FS-005: Fleet and readiness

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-004: Fail-safes and emergencies](FS-004-fail-safes-and-emergencies.md) · 📄 **Page 9 / 109** · [FS-006: Authorisations and compliance ▶️](FS-006-authorisations-and-compliance.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> In the [⚙️ Back office](../../glossary.md#sys-back-office), the [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) registers [🗃️ Drones](../../glossary.md#ent-drone), [🗃️ Payloads](../../glossary.md#ent-payload), each [🗃️ Battery](../../glossary.md#ent-battery) and [🗃️ Docks](../../glossary.md#ent-dock), and keeps them ready.

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

Know at any time which Drones can fly, with which Payloads. The Fleet maintainer registers each Drone with its [🗃️ Drone model](../../glossary.md#ent-drone-model), the Payloads it can carry and its Batteries, records maintenance, and grounds a Drone that is not airworthy. Swarm counts flight hours and Battery cycles from the [🗃️ Flight logs](../../glossary.md#ent-flight-log).

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) | Persona | Registers and maintains the Fleet |
| [🗃️ Drone](../../glossary.md#ent-drone) | Entity | Ready or Grounded |
| [🗃️ Payload](../../glossary.md#ent-payload) | Entity | Registered with the Drone models it fits |
| [🗃️ Battery](../../glossary.md#ent-battery) | Entity | Cycles and health |
| [🗃️ Dock](../../glossary.md#ent-dock) | Entity | Registered at a Site |
| [⚙️ Back office](../../glossary.md#sys-back-office) | System | Holds the Fleet |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-011: Drone readiness](../business-rules/BR-011-drone-readiness.md) | Only Ready Drones join a Squad |
| [📏 BR-015: Approved Drone models only](../business-rules/BR-015-approved-drone-models-only.md) | Only approved Drone models fly |
| [📏 BR-022: Payload compatibility](../business-rules/BR-022-payload-compatibility.md) | Payloads are registered with the Drone models they fit |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-007: Register a Drone and track its readiness](../use-cases/UC-007-register-a-drone-and-track-its-readiness.md) | [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a Drone with overdue maintenance **when** the Fleet maintainer opens it **then** it shows Grounded and cannot join a Squad | [📏 BR-011](../business-rules/BR-011-drone-readiness.md) | [🎬 UC-007](../use-cases/UC-007-register-a-drone-and-track-its-readiness.md) |
| AC-2 | **Given** a new thermal camera Payload **when** the Fleet maintainer registers it **then** they choose the Drone models it fits | [📏 BR-022](../business-rules/BR-022-payload-compatibility.md) | [🎬 UC-007](../use-cases/UC-007-register-a-drone-and-track-its-readiness.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Maintenance intervals | Imported from the maker of each Drone model; the [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) may make them shorter, never longer |
| Drone model approval | [🔄 Drone model: Approved](../../glossary.md#st-drone-model-approved) or [🔄 Drone model: Not approved](../../glossary.md#st-drone-model-not-approved) (see [📘 FS-011: Drone adapters](FS-011-drone-adapters.md)) |

## <a id="out-of-scope"></a>🚫 Out of scope

- Spare parts and purchasing

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

> [🏠 Index](../../README.md) · [◀️ FS-004: Fail-safes and emergencies](FS-004-fail-safes-and-emergencies.md) · 📄 **Page 9 / 109** · [FS-006: Authorisations and compliance ▶️](FS-006-authorisations-and-compliance.md)
<!-- /spec:nav-bottom -->
