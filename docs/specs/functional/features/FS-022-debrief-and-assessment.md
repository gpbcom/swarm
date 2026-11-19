# 📘 FS-022: Debrief and assessment

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-021: Ground control monitoring](FS-021-ground-control-monitoring.md) · 📄 **Page 26 / 109** · [UC-001: Design a Mission ▶️](../use-cases/UC-001-design-a-mission.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> After landing, the [🗃️ Debrief](../../glossary.md#ent-debrief) lets the [👤 Pilot](../../glossary.md#per-pilot) and the [👤 Mission planner](../../glossary.md#per-mission-planner) replay the [🗃️ Mission](../../glossary.md#ent-mission), compare plan and actual, run [🔤 Quality checks](../../glossary.md#term-quality-check) and score the result against the [👤 Client](../../glossary.md#per-client)'s request.

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

Know whether the Client got what they asked for, before telling them. The Debrief brings four views together:

| View | Answers |
| --- | --- |
| 📼 Replay | What happened, when, and what did the Pilot decide? |
| 📊 Plan against actual | Coverage and gaps, dose, timing, Drones lost, Re-plans |
| 🔬 Quality checks | Is the data good enough for the Deliverables? |
| 🧾 Scorecard | Is each acceptance criterion of the request met? |

The Pilot sees it in Ground control right after landing; the Mission planner decides on a re-fly and publishes the Scorecard to the Client; the [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) sees how each Drone and Battery behaved.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Debriefs right after landing |
| [👤 Mission planner](../../glossary.md#per-mission-planner) | Persona | Reviews, re-flies, publishes |
| [👤 Client](../../glossary.md#per-client) | Persona | Sees the published Scorecard |
| [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) | Persona | Sees Drone and Battery behaviour |
| [🗃️ Debrief](../../glossary.md#ent-debrief) | Entity | Replay, plan against actual, Quality checks |
| [🗃️ Scorecard](../../glossary.md#ent-scorecard) | Entity | Passed or Failed |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-026: Scorecard against the request](../business-rules/BR-026-scorecard-against-the-request.md) | The Scorecard assesses every acceptance criterion |
| [📏 BR-021: AI agents propose, people decide](../business-rules/BR-021-ai-agents-propose-people-decide.md) | The Scorecard is published by a person |
| [📏 BR-009: Evidence integrity](../business-rules/BR-009-evidence-integrity.md) | The Debrief relies on the Evidence record of the Flight log |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-027: Debrief a Mission](../use-cases/UC-027-debrief-a-mission.md) | [👤 Pilot](../../glossary.md#per-pilot) |
| [🎬 UC-028: Assess a Mission against the request](../use-cases/UC-028-assess-a-mission-against-the-request.md) | [👤 Mission planner](../../glossary.md#per-mission-planner), [👤 Client](../../glossary.md#per-client) |
| [🎬 UC-011: Follow a Mission and download its Deliverables](../use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md) | [👤 Client](../../glossary.md#per-client) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a completed Inspection **when** the Pilot opens the Debrief **then** the Replay, the plan against actual and the Quality checks are available | [📏 BR-009](../business-rules/BR-009-evidence-integrity.md) | [🎬 UC-027](../use-cases/UC-027-debrief-a-mission.md) |
| AC-2 | **Given** coverage of 96 % against a request of 100 % **when** the Scorecard is computed **then** it is Failed and the gaps are proposed for a re-fly | [📏 BR-026](../business-rules/BR-026-scorecard-against-the-request.md) | [🎬 UC-028](../use-cases/UC-028-assess-a-mission-against-the-request.md) |
| AC-3 | **Given** a reviewed Scorecard **when** the Mission planner publishes it **then** the Client sees it in the Client portal | [📏 BR-021](../business-rules/BR-021-ai-agents-propose-people-decide.md) | [🎬 UC-028](../use-cases/UC-028-assess-a-mission-against-the-request.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Criteria per Activity | Inspection: coverage %, image overlap %, ground resolution (cm per pixel), thermal calibration. Agriculture: area treated %, dose tolerance %. Patrol: route completed, points checked, time to reach an Alarm. Light show: show completed, no Drone landed outside its zone |
| Re-fly | A new Mission linked to the original; the original Scorecard is assessed again with both |
| Quality pass levels | Swarm defaults per Activity; the Operator may make them stricter; a stricter Client criterion wins |
| Altered Flight log | The Operator is told at once; the Debrief stays readable, marked Altered, and cannot give Scorecard: Passed |

## <a id="out-of-scope"></a>🚫 Out of scope

- Invoicing on the Scorecard

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

> [🏠 Index](../../README.md) · [◀️ FS-021: Ground control monitoring](FS-021-ground-control-monitoring.md) · 📄 **Page 26 / 109** · [UC-001: Design a Mission ▶️](../use-cases/UC-001-design-a-mission.md)
<!-- /spec:nav-bottom -->
