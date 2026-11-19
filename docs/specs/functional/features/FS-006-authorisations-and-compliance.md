# 📘 FS-006: Authorisations and compliance

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-005: Fleet and readiness](FS-005-fleet-and-readiness.md) · 📄 **Page 10 / 109** · [FS-007: Data processing and Deliverables ▶️](FS-007-data-processing-and-deliverables.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> The [👤 Mission planner](../../glossary.md#per-mission-planner) records the [🗃️ Authorisations](../../glossary.md#ent-authorisation) of the [🗃️ Operator](../../glossary.md#ent-operator) for each [🔤 Jurisdiction](../../glossary.md#term-jurisdiction), and Swarm checks every [🗃️ Mission](../../glossary.md#ent-mission) against them.

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

Fly only what is authorised, in the EU and in the US. Each Authorisation holds its Jurisdiction, area, [🔤 Altitude ceiling](../../glossary.md#term-altitude-ceiling), [🔤 Pilot ratio](../../glossary.md#term-pilot-ratio), [🔤 BVLOS](../../glossary.md#term-bvlos) permission, Activities and validity dates. Swarm warns before an Authorisation expires, refuses Missions it does not cover, and keeps the evidence an authority may ask for.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Mission planner](../../glossary.md#per-mission-planner) | Persona | Records Authorisations |
| [🗃️ Authorisation](../../glossary.md#ent-authorisation) | Entity | Valid or Expired |
| [🗃️ Operator](../../glossary.md#ent-operator) | Entity | Holds the Authorisations |
| [⚙️ Back office](../../glossary.md#sys-back-office) | System | Stores Authorisations |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-010: Valid Authorisation for the Jurisdiction](../business-rules/BR-010-valid-authorisation-for-the-jurisdiction.md) | A Valid Authorisation covers each Mission |
| [📏 BR-004: Pilot ratio](../business-rules/BR-004-pilot-ratio.md) | The Pilot ratio comes from the Authorisation |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-008: Record an Authorisation](../use-cases/UC-008-record-an-authorisation.md) | [👤 Mission planner](../../glossary.md#per-mission-planner) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** an Authorisation past its end date **when** a Mission under it is checked **then** it is refused with Authorisation: Expired | [📏 BR-010](../business-rules/BR-010-valid-authorisation-for-the-jurisdiction.md) | [🎬 UC-008](../use-cases/UC-008-record-an-authorisation.md) |
| AC-2 | **Given** a new Authorisation with a Pilot ratio of 3 **when** it is saved **then** Squads under it are limited to 3 Drones per Pilot | [📏 BR-004](../business-rules/BR-004-pilot-ratio.md) | [🎬 UC-008](../use-cases/UC-008-record-an-authorisation.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Expiry warnings | 30 days and 7 days before the end date |
| Documents | The Authorisation PDF is required; the operations manual and the SORA or ConOps file are optional |
| On expiry | Planned Missions under the Authorisation go back to Draft and the Mission planner is told |

## <a id="out-of-scope"></a>🚫 Out of scope

- Writing the SORA application itself
- Submitting applications to the authorities

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

> [🏠 Index](../../README.md) · [◀️ FS-005: Fleet and readiness](FS-005-fleet-and-readiness.md) · 📄 **Page 10 / 109** · [FS-007: Data processing and Deliverables ▶️](FS-007-data-processing-and-deliverables.md)
<!-- /spec:nav-bottom -->
