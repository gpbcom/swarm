# 📘 FS-023: AI Assistant

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-022: Debrief and assessment](FS-022-debrief-and-assessment.md) · 📄 **Page 27 / 120** · [FS-024: ERP and Squad shortfall ▶️](FS-024-erp-and-squad-shortfall.md)
<!-- /spec:nav-top -->

**Status:** 🟡 Draft · **Updated:** 2026-11-20

> [!NOTE]
> Every person of Swarm talks to one [⚙️ Assistant](../../glossary.md#sys-assistant), in every part of Swarm, by voice, on a mobile phone or from a chat tool; it can use every feature, action and [🔤 Connector](../../glossary.md#term-connector) of Swarm, as far as the [🗃️ Assistant permission](../../glossary.md#ent-assistant-permission)s people set allow.

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

People should not have to know which screen, which agent or which outside system holds what they need. The Assistant is the front door: it answers from everything the person may see, hands design, flight and report work to the [⚙️ Mission assistant](../../glossary.md#sys-mission-assistant), the [⚙️ Co-pilot](../../glossary.md#sys-co-pilot) and the [⚙️ Report writer](../../glossary.md#sys-report-writer), and does any action of Swarm, flight-critical ones included. How far it goes is decided action by action, in layers, by the Swarm administrator, the [🗃️ Operator](../../glossary.md#ent-operator) and each person; by default it only proposes, and people decide.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Pilot](../../glossary.md#per-pilot) | Persona | Asks, gets help in flight, and stays accountable for the Flight-critical acts it lets the Assistant do |
| [👤 Mission planner](../../glossary.md#per-mission-planner) | Persona | Asks, and sets the Assistant permissions of each role of the Operator |
| [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) | Persona | Asks and gets the Fleet work done |
| [👤 Client](../../glossary.md#per-client) | Persona | Asks about their own Missions and Deliverables in the Client portal |
| [👤 Site agent](../../glossary.md#per-site-agent) | Persona | Asks for and follows Missions of their Site, including from a mobile phone |
| [👤 Instructor](../../glossary.md#per-instructor) | Persona | Uses it in training sessions in the Simulator |
| [👤 Swarm administrator](../../glossary.md#per-swarm-administrator) | Persona | Sets the ceiling of the Assistant permissions of each Operator |
| [⚙️ Assistant](../../glossary.md#sys-assistant) | System | The front door |
| [⚙️ Mission assistant](../../glossary.md#sys-mission-assistant) | System | Specialist for designing Missions |
| [⚙️ Co-pilot](../../glossary.md#sys-co-pilot) | System | Specialist for flights |
| [⚙️ Report writer](../../glossary.md#sys-report-writer) | System | Specialist for Mission reports |
| [🗃️ Assistant permission](../../glossary.md#ent-assistant-permission) | Entity | Off, Read, Propose or Act, per action, in layers |
| [🗃️ Assistant activity](../../glossary.md#ent-assistant-activity) | Entity | Every act and proposal, explained and undone where possible |
| [🗃️ Trigger](../../glossary.md#ent-trigger) | Entity | Events and schedules that start the Assistant |
| [🗃️ Conversation](../../glossary.md#ent-conversation) | Entity | Kept per person |
| [🗃️ Knowledge document](../../glossary.md#ent-knowledge-document) | Entity | The Operator's documents it cites |
| [🔤 Connector](../../glossary.md#term-connector) | Term | The outside systems it reaches |
| [🔤 Assistant budget](../../glossary.md#term-assistant-budget) | Term | The monthly spend of the Operator and of each person |
| [🔤 Flight-critical act](../../glossary.md#term-flight-critical-act) | Term | Acts it may do only under a Pilot on duty |
| [🔤 LLM provider](../../glossary.md#term-llm-provider) | Term | Chosen by the Operator |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-021: AI agents propose, people decide](../business-rules/BR-021-ai-agents-propose-people-decide.md) | Every act stays within an Assistant permission and names the person behind it |
| [📏 BR-028: Assistant permissions are layered](../business-rules/BR-028-assistant-permissions-are-layered.md) | Who may set what, and the default of Propose |
| [📏 BR-029: Flight-critical acts need a Pilot on duty](../business-rules/BR-029-flight-critical-acts-need-a-pilot-on-duty.md) | The safety net of every Flight-critical act |
| [📏 BR-030: The Assistant stays within its budget](../business-rules/BR-030-the-assistant-stays-within-its-budget.md) | The cost stays under control without leaving a Pilot alone in the air |
| [📏 BR-032: The Assistant reaches only what its person may reach](../business-rules/BR-032-the-assistant-reaches-only-what-its-person-may-reach.md) | The Assistant never opens a way around a person's access |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-031: Ask the Assistant](../use-cases/UC-031-ask-the-assistant.md) | [👤 Fleet maintainer](../../glossary.md#per-fleet-maintainer) |
| [🎬 UC-032: Set the Assistant permissions](../use-cases/UC-032-set-the-assistant-permissions.md) | [👤 Swarm administrator](../../glossary.md#per-swarm-administrator), [👤 Mission planner](../../glossary.md#per-mission-planner), [👤 Pilot](../../glossary.md#per-pilot) |
| [🎬 UC-034: Let the Assistant hold a Squad](../use-cases/UC-034-let-the-assistant-hold-a-squad.md) | [👤 Pilot](../../glossary.md#per-pilot) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** "Schedule a maintenance" at Propose for the Fleet maintainer **when** the Fleet maintainer asks the Assistant to schedule one **then** the Assistant shows what it will change and nothing takes effect until the Fleet maintainer accepts | [📏 BR-021](../business-rules/BR-021-ai-agents-propose-people-decide.md) | [🎬 UC-031](../use-cases/UC-031-ask-the-assistant.md) |
| AC-2 | **Given** the same action at Act **when** the Fleet maintainer asks for it **then** the Assistant does it, reports it with **Undo**, and the Assistant activity names the Fleet maintainer | [📏 BR-021](../business-rules/BR-021-ai-agents-propose-people-decide.md) | [🎬 UC-031](../use-cases/UC-031-ask-the-assistant.md) |
| AC-3 | **Given** the same action Off for this person **when** the Fleet maintainer asks for it **then** the Assistant refuses and says who sets its permissions | [📏 BR-028](../business-rules/BR-028-assistant-permissions-are-layered.md) | [🎬 UC-031](../use-cases/UC-031-ask-the-assistant.md) |
| AC-4 | **Given** a request for a Mission design, an Alert explanation or a report **when** a person asks the Assistant **then** it hands the work to the Mission assistant, the Co-pilot or the Report writer in the same Conversation | [📏 BR-021](../business-rules/BR-021-ai-agents-propose-people-decide.md) | [🎬 UC-031](../use-cases/UC-031-ask-the-assistant.md) |
| AC-5 | **Given** a ceiling of Propose for "Launch" **when** the Mission planner sets "Launch" to Act for the Pilots **then** the level is refused and stays at the ceiling | [📏 BR-028](../business-rules/BR-028-assistant-permissions-are-layered.md) | [🎬 UC-032](../use-cases/UC-032-set-the-assistant-permissions.md) |
| AC-6 | **Given** "Hold" at Act for the Pilot role **when** a Pilot lowers it to Propose for himself **then** the Assistant only proposes a Hold to that Pilot, and nothing changes for the other Pilots | [📏 BR-028](../business-rules/BR-028-assistant-permissions-are-layered.md) | [🎬 UC-032](../use-cases/UC-032-set-the-assistant-permissions.md) |
| AC-7 | **Given** "Hold" at Act and a Pilot on duty who sees the Squad in Ground control **when** the wind rises beyond the limits **then** the Assistant announces the Hold with a countdown the Pilot can cancel, and the Flight log names the Pilot as accountable | [📏 BR-029](../business-rules/BR-029-flight-critical-acts-need-a-pilot-on-duty.md) | [🎬 UC-034](../use-cases/UC-034-let-the-assistant-hold-a-squad.md) |
| AC-8 | **Given** "Hold" at Act and no Pilot on duty for the Squad **when** the wind rises beyond the limits **then** no Hold is done by the Assistant; it becomes a proposal with a Notification to the Pilots | [📏 BR-029](../business-rules/BR-029-flight-critical-acts-need-a-pilot-on-duty.md) | [🎬 UC-034](../use-cases/UC-034-let-the-assistant-hold-a-squad.md) |
| AC-9 | **Given** an Operator at 100 % of its Assistant budget **when** a person asks for a report draft **then** the Assistant answers in read-only mode, and during a flight it keeps helping | [📏 BR-030](../business-rules/BR-030-the-assistant-stays-within-its-budget.md) | [🎬 UC-031](../use-cases/UC-031-ask-the-assistant.md) |
| AC-10 | **Given** a Client of Aerowing Services **when** they ask about a Mission of another Client **then** the Assistant says it cannot see it | [📏 BR-032](../business-rules/BR-032-the-assistant-reaches-only-what-its-person-may-reach.md) | [🎬 UC-031](../use-cases/UC-031-ask-the-assistant.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Front door | One Assistant for every person; the Mission assistant, the Co-pilot and the Report writer stay as its specialists |
| Where | A panel in the Mission studio, Ground control, the Back office and the Client portal, aware of the screen the person is on; by voice; from a mobile phone; from Slack, Microsoft Teams and e-mail |
| Reach | Every action of Swarm can be opened to it, flight-critical ones included |
| Assistant permissions | Off, Read, Propose or Act per action or group of actions; Act may ask the person to confirm first. Layered: the Swarm administrator sets a ceiling per Operator, the Operator sets each role within it, each person may only narrow their own. A new Operator starts at Propose everywhere |
| Flight-critical acts | At Act only while a Pilot is on duty for the Squad and sees it in Ground control, announced with a countdown the Pilot can cancel; the Pilot stays accountable ([📏 BR-029](../business-rules/BR-029-flight-critical-acts-need-a-pilot-on-duty.md)) |
| Triggers | When a person asks; on events (an Alarm, an Alert, a Mission request, a failed check, a weather change); on schedules a person sets up; always within its permissions |
| Connectors | Swarm's own systems; MCP servers and A2A agents the Operator registers; REST APIs and webhooks; the person's e-mail, calendar and documents (Microsoft 365 or Google Workspace) with their consent; Slack and Microsoft Teams; GIS and maps; invoicing and payments; asset registers and IoT platforms; the [⚙️ ERP](../../glossary.md#sys-erp) ([📘 FS-024: ERP and Squad shortfall](FS-024-erp-and-squad-shortfall.md)); each with its own Assistant permissions |
| Memory and knowledge | Each person's Conversations, kept 12 months by default (the Operator sets it from 30 days to forever, and a person may delete their own); the Operator's Knowledge documents, cited; Swarm's user guide and the regulations of each Jurisdiction; preferences it learns per person, which the person can see and erase |
| Oversight | The Assistant activity of every act and proposal; **Undo** for a set time where an act can be reversed; a daily digest; on any act, the person can ask why |
| Cost | A monthly Assistant budget per Operator, optionally per person, with usage and cost in the Back office; a warning at 80 %, read-only answers at 100 %; help during a flight never stops |
| Offline | Online by default; it may also work offline with open-weight models |
| Languages | The four languages of Swarm, by text and by voice, answering in the person's language |
| LLM provider | The one the Operator chose, as for its specialists |
| Who sets the roles' permissions | The Mission planner, who manages the Operator's people, within the ceiling of the Swarm administrator |
| Countdown and Undo | Operator settings: a 10-second countdown before a Flight-critical act and **Undo** for 5 minutes by default |
| Irreversible acts | Messages sent, orders received by the ERP or a supplier, Flight-critical acts and publications to the Client cannot be undone; the Assistant says so before acting |
| Outside agents | Signing the Pre-flight check and launching always wait for the person's confirmation on their own device with their PIN, whatever the Assistant permission |
| Conversations | Kept 12 months by default; each Operator sets it from 30 days to forever; a person may delete their own |

## <a id="out-of-scope"></a>🚫 Out of scope

- The ERP and the Squad shortfall: [📘 FS-024: ERP and Squad shortfall](FS-024-erp-and-squad-shortfall.md)
- The Fail-safes of the Squad, which act by themselves, without the Assistant ([📏 BR-006: Fail-safe per Activity](../business-rules/BR-006-fail-safe-per-activity.md))

## <a id="open-questions"></a>❓ Open questions

> [!WARNING]
> None.

## <a id="references"></a>🔗 References

- 🧭 [Functional overview](../README.md)
- 📖 [Glossary](../../glossary.md)

<!-- spec:nav-bottom -->
---

> [🏠 Index](../../README.md) · [◀️ FS-022: Debrief and assessment](FS-022-debrief-and-assessment.md) · 📄 **Page 27 / 120** · [FS-024: ERP and Squad shortfall ▶️](FS-024-erp-and-squad-shortfall.md)
<!-- /spec:nav-bottom -->
