# 📘 FS-011: Drone adapters

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-010: Simulator and training](FS-010-simulator-and-training.md) · 📄 **Page 15 / 109** · [FS-012: Operators, deployment and languages ▶️](FS-012-operators-deployment-and-languages.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> [⚙️ Drone adapters](../../glossary.md#sys-drone-adapter) let Swarm fly any [🗃️ Drone model](../../glossary.md#ent-drone-model) that passes its compatibility test: MAVLink (PX4, ArduPilot), DJI, Skydio and Parrot.

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

Avoid lock-in to one maker. Each Drone adapter translates the commands of Swarm (take off, follow a route, [🔤 Hold](../../glossary.md#term-hold), [🔤 Return home](../../glossary.md#term-return-home), land, [🗃️ Geofence](../../glossary.md#ent-geofence), [🗃️ Payload](../../glossary.md#ent-payload) control) for one family of Drones and its [🔤 Link](../../glossary.md#term-link). A new Drone model flies only after its compatibility test.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) | Persona | Connects a new Drone model |
| [🗃️ Drone model](../../glossary.md#ent-drone-model) | Entity | Approved or not |
| [⚙️ Drone adapter](../../glossary.md#sys-drone-adapter) | System | One per family of Drones |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-015: Approved Drone models only](../business-rules/BR-015-approved-drone-models-only.md) | Only approved Drone models fly |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-014: Connect a new Drone model](../use-cases/UC-014-connect-a-new-drone-model.md) | [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a new Drone model **when** its compatibility test fails on Return home **then** its Drones stay Grounded | [📏 BR-015](../business-rules/BR-015-approved-drone-models-only.md) | [🎬 UC-014](../use-cases/UC-014-connect-a-new-drone-model.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Order of adapters | MAVLink (PX4, ArduPilot) first, then Parrot, then the other vendor SDKs |
| Compatibility test | First in the Simulator where the Drone model allows it, then one real flight in a test area flown by a Pilot |
| Firmware | A new firmware version makes the Drone model Not approved until it passes the test again |

## <a id="out-of-scope"></a>🚫 Out of scope

- Writing firmware for the Drones

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

> [🏠 Index](../../README.md) · [◀️ FS-010: Simulator and training](FS-010-simulator-and-training.md) · 📄 **Page 15 / 109** · [FS-012: Operators, deployment and languages ▶️](FS-012-operators-deployment-and-languages.md)
<!-- /spec:nav-bottom -->
