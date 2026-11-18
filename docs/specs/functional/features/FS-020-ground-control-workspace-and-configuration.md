# 📘 FS-020: Ground control Workspace and configuration

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-019: Mission reports](FS-019-mission-reports.md) · 📄 **Page 24 / 108** · [FS-021: Ground control monitoring ▶️](FS-021-ground-control-monitoring.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> The [👤 Pilot](../../glossary.md#per-pilot) arranges [⚙️ Ground control](../../glossary.md#sys-ground-control) on any platform (desktop with several screens, laptop, tablet, web browser), sets units, language, light or dark mode, [🔤 Alert thresholds](../../glossary.md#term-alert-threshold) and [🔤 Control mapping](../../glossary.md#term-control-mapping), and adjusts each [🗃️ Drone](../../glossary.md#ent-drone) of the [🗃️ Squad](../../glossary.md#ent-squad) on the [🗃️ Site](../../glossary.md#ent-site).

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

Ground control adapts to the Pilot and to the place, never the reverse. The same Mission can be flown from an operations centre with three screens, from a laptop on a Field kit table, or supervised from a tablet or a web browser. Each Pilot saves a [🗃️ Workspace](../../glossary.md#ent-workspace) per platform. Before launch, the Pilot can swap a Drone, a [🗃️ Payload](../../glossary.md#ent-payload) or a [🗃️ Battery](../../glossary.md#ent-battery); Swarm checks the Mission again.

| Setting | Who sets it | Bounds |
| --- | --- | --- |
| Workspace: panels per screen | Pilot, per platform | Hold the Squad and abort visible on every screen |
| Alert thresholds (battery, Link, wind) | Pilot | Within the Operator's limits |
| Units, language, light or dark mode | Pilot | Metric or imperial; English, French, German, Spanish |
| Control mapping (gamepad, joystick, keys) | Pilot | Hold the Squad and abort fixed |
| Manual control device | Pilot | Gamepad or joystick, vendor remote, on-screen commands, keyboard |
| Drone, Payload, Battery of each Squad member | Pilot, on the Site | Checked again before the Pre-flight check |

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Configures Ground control and the Squad |
| [🗃️ Workspace](../../glossary.md#ent-workspace) | Entity | Saved per Pilot and platform |
| [🗃️ Squad](../../glossary.md#ent-squad) | Entity | Each Drone with its own Payload and Battery |
| [🗃️ Payload](../../glossary.md#ent-payload) | Entity | Swapped on the Site |
| [🗃️ Operator](../../glossary.md#ent-operator) | Entity | Sets the limits of the Alert thresholds |
| [⚙️ Ground control](../../glossary.md#sys-ground-control) | System | Desktop, laptop, tablet and web |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-023: Fixed safety controls](../business-rules/BR-023-fixed-safety-controls.md) | Hold the Squad and abort stay fixed and visible |
| [📏 BR-024: Alert thresholds within the Operator limits](../business-rules/BR-024-alert-thresholds-within-the-operator-limits.md) | Alert thresholds stay within the Operator's limits |
| [📏 BR-025: On-site changes are checked again](../business-rules/BR-025-on-site-changes-are-checked-again.md) | On-site changes are checked again |
| [📏 BR-017: Every screen in four languages](../business-rules/BR-017-every-screen-in-four-languages.md) | Every screen in four languages |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-023: Configure the Workspace of Ground control](../use-cases/UC-023-configure-the-workspace-of-ground-control.md) | [👤 Pilot](../../glossary.md#per-pilot) |
| [🎬 UC-024: Configure each Drone of the Squad on the Site](../use-cases/UC-024-configure-each-drone-of-the-squad-on-the-site.md) | [👤 Pilot](../../glossary.md#per-pilot) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a Pilot with two screens **when** they move the video panel to the second screen and save **then** the Workspace opens the same way next time on that desktop | [📏 BR-023](../business-rules/BR-023-fixed-safety-controls.md) | [🎬 UC-023](../use-cases/UC-023-configure-the-workspace-of-ground-control.md) |
| AC-2 | **Given** an Operator range of 25 % to 40 % **when** the Pilot sets the low battery Alert threshold to 15 % **then** it is refused | [📏 BR-024](../business-rules/BR-024-alert-thresholds-within-the-operator-limits.md) | [🎬 UC-023](../use-cases/UC-023-configure-the-workspace-of-ground-control.md) |
| AC-3 | **Given** a Verified Mission **when** the Pilot replaces a Drone by a spare **then** the Mission is checked again and the Pre-flight check must be signed again | [📏 BR-025](../business-rules/BR-025-on-site-changes-are-checked-again.md) | [🎬 UC-024](../use-cases/UC-024-configure-each-drone-of-the-squad-on-the-site.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Tablet | Everything except manual control and multi-screen Workspaces: it can Hold, abort, approve Re-plans and close Alarms |
| Controllers | XInput gamepads first, then generic USB joysticks |
| Operator limits | Link warning 30 % to 70 % quality (default 50 %); wind warning 60 % to 90 % of the Drone model limit (default 80 %); low battery 25 % to 40 % (default 30 %) |
| Fixed inputs, held 1 second | Hold the Squad: key H or both gamepad bumpers. Abort: Ctrl+Shift+A or gamepad Back and Start |
| On-site changes | The Mission planner is told; the change is recorded in the Flight log |
| Thresholds in flight | The Pilot may change an Alert threshold from the Alert itself, within the Operator limits; recorded in the Flight log |

## <a id="out-of-scope"></a>🚫 Out of scope

- Designing the Mission ([📘 FS-001: Mission design](FS-001-mission-design.md))
- Registering Drones and Payloads ([📘 FS-005: Fleet and readiness](FS-005-fleet-and-readiness.md))

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

> [🏠 Index](../../README.md) · [◀️ FS-019: Mission reports](FS-019-mission-reports.md) · 📄 **Page 24 / 108** · [FS-021: Ground control monitoring ▶️](FS-021-ground-control-monitoring.md)
<!-- /spec:nav-bottom -->
