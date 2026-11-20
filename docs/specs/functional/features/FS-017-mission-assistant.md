# 📘 FS-017: Mission assistant

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-016: Inspection](FS-016-inspection.md) · 📄 **Page 21 / 120** · [FS-018: Live Co-pilot ▶️](FS-018-live-co-pilot.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> The [⚙️ Mission assistant](../../glossary.md#sys-mission-assistant) turns the [👤 Mission planner](../../glossary.md#per-mission-planner)'s description into a proposed [🗃️ Mission](../../glossary.md#ent-mission), checked against every rule.

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

Save design time. The Mission planner describes the need in their own words; the Mission assistant proposes the area, the [🗃️ Squad](../../glossary.md#ent-squad) with a [🗃️ Payload](../../glossary.md#ent-payload) per [🗃️ Drone](../../glossary.md#ent-drone), the routes and the time slot, explains each choice and the rules it checked. The Mission planner edits and accepts.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Mission planner](../../glossary.md#per-mission-planner) | Persona | Describes and accepts |
| [🗃️ Mission](../../glossary.md#ent-mission) | Entity | Proposed as Draft |
| [⚙️ Mission assistant](../../glossary.md#sys-mission-assistant) | System | Proposes |
| [🔤 LLM provider](../../glossary.md#term-llm-provider) | Term | Chosen by the Operator |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-021: AI agents propose, people decide](../business-rules/BR-021-ai-agents-propose-people-decide.md) | AI agents propose, people decide |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-021: Plan a Mission with the Mission assistant](../use-cases/UC-021-plan-a-mission-with-the-mission-assistant.md) | [👤 Mission planner](../../glossary.md#per-mission-planner) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a description of an Inspection **when** the Mission assistant answers **then** it proposes a Draft Mission that the Mission planner must accept | [📏 BR-021](../business-rules/BR-021-ai-agents-propose-people-decide.md) | [🎬 UC-021](../use-cases/UC-021-plan-a-mission-with-the-mission-assistant.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| LLM provider | Swarm is provider-agnostic: each Operator chooses its [🔤 LLM provider](../../glossary.md#term-llm-provider) and models. Cloud default: Claude models. On premises: an open-weight model on the Operator's own servers; no data leaves the site |
| Outside agents | Swarm exposes an MCP server and its agents through the A2A protocol; an [🔤 Outside agent](../../glossary.md#term-outside-agent) is the delegate of a person, with that person's rights, behind the human gate of [📏 BR-021](../business-rules/BR-021-ai-agents-propose-people-decide.md) |

## <a id="out-of-scope"></a>🚫 Out of scope

- Talking to the Client directly

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

> [🏠 Index](../../README.md) · [◀️ FS-016: Inspection](FS-016-inspection.md) · 📄 **Page 21 / 120** · [FS-018: Live Co-pilot ▶️](FS-018-live-co-pilot.md)
<!-- /spec:nav-bottom -->
