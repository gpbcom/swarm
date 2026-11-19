# 📘 FS-015: Patrol

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-014: Agriculture](FS-014-agriculture.md) · 📄 **Page 19 / 109** · [FS-016: Inspection ▶️](FS-016-inspection.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> Swarm patrols a [🗃️ Site](../../glossary.md#ent-site) on a schedule, on an [🗃️ Alarm](../../glossary.md#ent-alarm) of the [⚙️ Site security system](../../glossary.md#sys-site-security-system), or on demand of a [👤 Site agent](../../glossary.md#per-site-agent), often from [🗃️ Docks](../../glossary.md#ent-dock).

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

Watch Sites with less staff. Scheduled patrols fly their [🗃️ Patrol route](../../glossary.md#ent-patrol-route); an Alarm sends the nearest Drones to its position; a Site agent can request a look. The [👤 Pilot](../../glossary.md#per-pilot) supervises, closes each Alarm with its outcome, and every clip has its [🗃️ Evidence record](../../glossary.md#ent-evidence-record).

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Site agent](../../glossary.md#per-site-agent) | Persona | Requests patrols, receives outcomes |
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Supervises and closes Alarms |
| [🗃️ Alarm](../../glossary.md#ent-alarm) | Entity | Raised, then Closed |
| [🗃️ Patrol route](../../glossary.md#ent-patrol-route) | Entity | Path and points to watch |
| [🗃️ Dock](../../glossary.md#ent-dock) | Entity | Launches and recharges |
| [⚙️ Site security system](../../glossary.md#sys-site-security-system) | System | Sends Alarms |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-019: Site agents request, never pilot](../business-rules/BR-019-site-agents-request-never-pilot.md) | Site agents request, never pilot |
| [📏 BR-005: Autonomy level per Activity](../business-rules/BR-005-autonomy-level-per-activity.md) | Patrols fly under Supervised autonomy |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-018: Respond to a Site Alarm](../use-cases/UC-018-respond-to-a-site-alarm.md) | [👤 Site agent](../../glossary.md#per-site-agent), [👤 Pilot](../../glossary.md#per-pilot) |
| [🎬 UC-019: Request a Patrol on demand](../use-cases/UC-019-request-a-patrol-on-demand.md) | [👤 Site agent](../../glossary.md#per-site-agent) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** an Alarm at gate 3 **when** the Site security system sends it **then** the Pilot sees it and the nearest Drones are proposed | [📏 BR-005](../business-rules/BR-005-autonomy-level-per-activity.md) | [🎬 UC-018](../use-cases/UC-018-respond-to-a-site-alarm.md) |
| AC-2 | **Given** a Site agent **when** they request a look at the car park **then** the request waits for a Pilot to accept it | [📏 BR-019](../business-rules/BR-019-site-agents-request-never-pilot.md) | [🎬 UC-019](../use-cases/UC-019-request-a-patrol-on-demand.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Launch on Alarm | Drones in Docks launch by themselves towards the Alarm only if the Operator enabled it for the Site and a Pilot is on duty; otherwise the Pilot sends them |
| No Drone Ready | The Alarm stays Raised; the Pilot and the Site agent are told at once that no Drone can fly |
| Closing an Alarm | Outcome from a fixed list (false alarm, intrusion confirmed, fire confirmed, other) and an optional comment |
| Integrations | A generic web API (webhook) first, then alarm panels through SIA DC-09 |
| Requests | A request waits 10 minutes for a Pilot (Operator setting); then it is [🔄 Mission: Declined](../../glossary.md#st-mission-declined), and the Site agent and every Pilot on duty are told. An accepted request becomes Mission: Planned on its Patrol route |

## <a id="out-of-scope"></a>🚫 Out of scope

- Recognising people in the video

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

> [🏠 Index](../../README.md) · [◀️ FS-014: Agriculture](FS-014-agriculture.md) · 📄 **Page 19 / 109** · [FS-016: Inspection ▶️](FS-016-inspection.md)
<!-- /spec:nav-bottom -->
