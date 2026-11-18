# 📘 FS-021: Ground control monitoring

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-020: Ground control Workspace and configuration](FS-020-ground-control-workspace-and-configuration.md) · 📄 **Page 25 / 108** · [FS-022: Debrief and assessment ▶️](FS-022-debrief-and-assessment.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> During a [🗃️ Mission](../../glossary.md#ent-mission), [⚙️ Ground control](../../glossary.md#sys-ground-control) shows the [👤 Pilot](../../glossary.md#per-pilot) the map and the [🗃️ Squad](../../glossary.md#ent-squad), live video, [🔤 Alerts](../../glossary.md#term-alert) with the [⚙️ Co-pilot](../../glossary.md#sys-co-pilot), and the progress against the plan, and takes their commands.

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

Let one Pilot understand a whole Squad at a glance and act in one move. Four things are always visible; the rest is one click away.

| Always visible | Shows |
| --- | --- |
| 🗺️ Map and Squad | Every Drone with its state, Payload, battery and Link; the Geofence; the work done and left |
| 🎥 Live video | The video of one Drone's Payload, or a mosaic of several |
| ⚠️ Alerts and Co-pilot | Alerts by severity, the Co-pilot's explanation, proposed Re-plans to approve or reject |
| 📈 Progress | Against the plan: area covered, dose applied, show timeline, time and battery left |

The Pilot commands with the mouse or touch, keyboard shortcuts, a gamepad or joystick, or hands one Drone over to its vendor remote.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Supervising, acts on Alerts |
| [🗃️ Squad](../../glossary.md#ent-squad) | Entity | Shown Drone by Drone |
| [🗃️ Drone](../../glossary.md#ent-drone) | Entity | State, Payload, battery, Link |
| [⚙️ Ground control](../../glossary.md#sys-ground-control) | System | Shows and commands |
| [⚙️ Co-pilot](../../glossary.md#sys-co-pilot) | System | Explains Alerts |
| [🔤 Focus view](../../glossary.md#term-focus-view) | Term | One Drone large |
| [🔤 Mosaic](../../glossary.md#term-mosaic) | Term | Video tiles |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-012: Pilot override always available](../business-rules/BR-012-pilot-override-always-available.md) | The Pilot can always take over |
| [📏 BR-023: Fixed safety controls](../business-rules/BR-023-fixed-safety-controls.md) | Hold the Squad and abort one action away |
| [📏 BR-013: Re-plan approval](../business-rules/BR-013-re-plan-approval.md) | Major Re-plans wait for the Pilot |
| [📏 BR-027: The Pilot's attention is preserved](../business-rules/BR-027-the-pilot-s-attention-is-preserved.md) | The Pilot's attention is preserved |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-025: Monitor a Mission in Ground control](../use-cases/UC-025-monitor-a-mission-in-ground-control.md) | [👤 Pilot](../../glossary.md#per-pilot) |
| [🎬 UC-026: Handle an Alert](../use-cases/UC-026-handle-an-alert.md) | [👤 Pilot](../../glossary.md#per-pilot) |
| [🎬 UC-004: Supervise a Squad and approve a Re-plan](../use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md) | [👤 Pilot](../../glossary.md#per-pilot) |
| [🎬 UC-006: Take manual control or abort](../use-cases/UC-006-take-manual-control-or-abort.md) | [👤 Pilot](../../glossary.md#per-pilot) |
| [🎬 UC-030: Focus on a Drone](../use-cases/UC-030-focus-on-a-drone.md) | [👤 Pilot](../../glossary.md#per-pilot) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a Mission Flying **when** the Pilot looks at the Workspace **then** the map, the video, the Alerts and the progress are visible across its screens, and every screen shows Hold the Squad and abort | [📏 BR-023](../business-rules/BR-023-fixed-safety-controls.md) | [🎬 UC-025](../use-cases/UC-025-monitor-a-mission-in-ground-control.md) |
| AC-2 | **Given** a Link weakening on one Drone **when** the Alert threshold is crossed **then** an Alert appears with the Co-pilot's explanation and the actions available | [📏 BR-013](../business-rules/BR-013-re-plan-approval.md) | [🎬 UC-026](../use-cases/UC-026-handle-an-alert.md) |
| AC-3 | **Given** a gamepad connected **when** the Pilot takes manual control of Bravo **then** Bravo follows the gamepad and the others continue | [📏 BR-012](../business-rules/BR-012-pilot-override-always-available.md) | [🎬 UC-006](../use-cases/UC-006-take-manual-control-or-abort.md) |
| AC-4 | **Given** a Focus view open on Alpha **when** Charlie detects a person **then** the event queues with a badge and does not replace the Focus view until the Pilot clicks it | [📏 BR-027](../business-rules/BR-027-the-pilot-s-attention-is-preserved.md) | [🎬 UC-030](../use-cases/UC-030-focus-on-a-drone.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Video streams | The Operator sets a maximum per platform; the Pilot chooses up to it (defaults: desktop 4, laptop 2, tablet 1, web browser 2) |
| Focus view | One Drone large, opened by an event the Drone detects (person, fire, hot spot, obstacle) at or above the Pilot's severity setting, by a click on the Drone on the map, or by a click on its tile in the [🔤 Mosaic](../../glossary.md#term-mosaic) |
| Attention | See [📏 BR-027: The Pilot's attention is preserved](../business-rules/BR-027-the-pilot-s-attention-is-preserved.md): one [🔤 Focus view](../../glossary.md#term-focus-view) at a time, events queue, critical Alerts and the fixed controls never covered |
| Severity | Events a Drone detects use the severities of the Alerts: Information, Warning, Critical. Default Pilot setting: Warning and above opens the Focus view; an event below is listed in the Alerts area and one click opens its Focus view |

## <a id="out-of-scope"></a>🚫 Out of scope

- Recording the video for the Client (it is a Deliverable, [📘 FS-007: Data processing and Deliverables](FS-007-data-processing-and-deliverables.md))

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

> [🏠 Index](../../README.md) · [◀️ FS-020: Ground control Workspace and configuration](FS-020-ground-control-workspace-and-configuration.md) · 📄 **Page 25 / 108** · [FS-022: Debrief and assessment ▶️](FS-022-debrief-and-assessment.md)
<!-- /spec:nav-bottom -->
