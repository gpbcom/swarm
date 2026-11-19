# 📘 FS-002: Pre-flight check and launch

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-001: Mission design](FS-001-mission-design.md) · 📄 **Page 6 / 109** · [FS-003: Live supervision ▶️](FS-003-live-supervision.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> Before take-off, Swarm runs every automatic check and the [👤 Pilot](../../glossary.md#per-pilot) signs the [🗃️ Pre-flight check](../../glossary.md#ent-pre-flight-check); only then can the [🗃️ Mission](../../glossary.md#ent-mission) launch.

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

Make launching safe and fast on the [🗃️ Site](../../glossary.md#ent-site). [⚙️ Ground control](../../glossary.md#sys-ground-control) checks the [🗃️ Geofence](../../glossary.md#ent-geofence), the weather, the [🗃️ Authorisation](../../glossary.md#ent-authorisation), the [🔤 Pilot ratio](../../glossary.md#term-pilot-ratio), the readiness of every [🗃️ Drone](../../glossary.md#ent-drone) and [🗃️ Payload](../../glossary.md#ent-payload), the [🔤 Links](../../glossary.md#term-link) and the airspace grant of the [⚙️ U-space service](../../glossary.md#sys-u-space-service). The Pilot sees what passed and what failed, signs, and launches the [🗃️ Squad](../../glossary.md#ent-squad).

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Reads the checks, signs, launches |
| [🗃️ Mission](../../glossary.md#ent-mission) | Entity | From Planned to Verified, then Flying |
| [🗃️ Drone](../../glossary.md#ent-drone) | Entity | From Ready to Airborne |
| [🗃️ Pre-flight check](../../glossary.md#ent-pre-flight-check) | Entity | Automatic checks and signed checklist |
| [⚙️ Ground control](../../glossary.md#sys-ground-control) | System | Runs the checks |
| [⚙️ Weather service](../../glossary.md#sys-weather-service) | System | Gives the weather at the Site |
| [⚙️ U-space service](../../glossary.md#sys-u-space-service) | System | Grants the airspace |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-007: Launch only after a passed Pre-flight check](../business-rules/BR-007-launch-only-after-a-passed-pre-flight-check.md) | No launch without every check passed and the Pilot's signature |
| [📏 BR-003: Weather limits](../business-rules/BR-003-weather-limits.md) | Weather inside the limits of every Drone model |
| [📏 BR-004: Pilot ratio](../business-rules/BR-004-pilot-ratio.md) | No more Drones than the Pilot ratio |
| [📏 BR-010: Valid Authorisation for the Jurisdiction](../business-rules/BR-010-valid-authorisation-for-the-jurisdiction.md) | A Valid Authorisation covers the Mission |
| [📏 BR-011: Drone readiness](../business-rules/BR-011-drone-readiness.md) | Every Drone of the Squad is Ready |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-003: Run the Pre-flight check and launch](../use-cases/UC-003-run-the-pre-flight-check-and-launch.md) | [👤 Pilot](../../glossary.md#per-pilot) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** every check passed **when** the Pilot signs **then** the Mission is Verified and the launch button is enabled | [📏 BR-007](../business-rules/BR-007-launch-only-after-a-passed-pre-flight-check.md) | [🎬 UC-003](../use-cases/UC-003-run-the-pre-flight-check-and-launch.md) |
| AC-2 | **Given** gusts above the limit of one Drone model **when** the checks run **then** the weather check fails and the launch stays disabled | [📏 BR-003](../business-rules/BR-003-weather-limits.md) | [🎬 UC-003](../use-cases/UC-003-run-the-pre-flight-check-and-launch.md) |
| AC-3 | **Given** a Squad of 6 under a Pilot ratio of 3 **when** the checks run **then** the Pilot ratio check fails | [📏 BR-004](../business-rules/BR-004-pilot-ratio.md) | [🎬 UC-003](../use-cases/UC-003-run-the-pre-flight-check-and-launch.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Validity | A signed [🗃️ Pre-flight check](../../glossary.md#ent-pre-flight-check) stays valid 30 minutes; after that the automatic checks run again |
| Signature | The [👤 Pilot](../../glossary.md#per-pilot) enters a personal PIN |
| Manual items | The Operator defines a checklist per [🔤 Activity](../../glossary.md#term-activity) (propellers, Payload fixed, area clear); every item must be ticked |

## <a id="out-of-scope"></a>🚫 Out of scope

- Recording Authorisations ([📘 FS-006: Authorisations and compliance](FS-006-authorisations-and-compliance.md))
- Maintenance of Drones ([📘 FS-005: Fleet and readiness](FS-005-fleet-and-readiness.md))

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

> [🏠 Index](../../README.md) · [◀️ FS-001: Mission design](FS-001-mission-design.md) · 📄 **Page 6 / 109** · [FS-003: Live supervision ▶️](FS-003-live-supervision.md)
<!-- /spec:nav-bottom -->
