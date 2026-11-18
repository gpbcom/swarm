# 📘 FS-019: Mission reports

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-018: Live Co-pilot](FS-018-live-co-pilot.md) · 📄 **Page 23 / 108** · [FS-020: Ground control Workspace and configuration ▶️](FS-020-ground-control-workspace-and-configuration.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> After a [🗃️ Mission](../../glossary.md#ent-mission), the [⚙️ Report writer](../../glossary.md#sys-report-writer) drafts the Mission report and the compliance evidence; a person publishes them.

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

Close each Mission with a clear report for the [👤 Client](../../glossary.md#per-client) and the evidence the [🗃️ Operator](../../glossary.md#ent-operator) keeps for authorities and insurers. The report summarises the flight, the work done, the [🗃️ Deliverables](../../glossary.md#ent-deliverable) and the Confirmed [🗃️ Defects](../../glossary.md#ent-defect), in the Client's language.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Client](../../glossary.md#per-client) | Persona | Receives the report |
| [🗃️ Deliverable](../../glossary.md#ent-deliverable) | Entity | The Mission report |
| [⚙️ Report writer](../../glossary.md#sys-report-writer) | System | Drafts the report |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-021: AI agents propose, people decide](../business-rules/BR-021-ai-agents-propose-people-decide.md) | The report stays a draft until a person publishes it |
| [📏 BR-020: Defects confirmed by a person](../business-rules/BR-020-defects-confirmed-by-a-person.md) | Only Confirmed Defects are reported |
| [📏 BR-009: Evidence integrity](../business-rules/BR-009-evidence-integrity.md) | The report gets its Evidence record |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-022: Receive the Mission report](../use-cases/UC-022-receive-the-mission-report.md) | [👤 Client](../../glossary.md#per-client) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a completed Inspection **when** the Mission planner publishes the drafted report **then** the Client receives it with its Evidence record | [📏 BR-021](../business-rules/BR-021-ai-agents-propose-people-decide.md) | [🎬 UC-022](../use-cases/UC-022-receive-the-mission-report.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Common skeleton | Summary, Mission, Squad, work done against the request, Scorecard, Deliverables, incidents, Evidence records |
| Per Activity | Inspection: Confirmed Defects with pictures. Agriculture: dose map, products, area treated. Patrol: timeline of events and Alarms. Light show: show log and incidents |
| Changes to a draft | The Mission planner may ask the Report writer for changes in a conversation; every version stays a draft until a person publishes it |

## <a id="out-of-scope"></a>🚫 Out of scope

- Reports for the authorities in their own forms

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

> [🏠 Index](../../README.md) · [◀️ FS-018: Live Co-pilot](FS-018-live-co-pilot.md) · 📄 **Page 23 / 108** · [FS-020: Ground control Workspace and configuration ▶️](FS-020-ground-control-workspace-and-configuration.md)
<!-- /spec:nav-bottom -->
