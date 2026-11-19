# 📘 FS-008: Client portal

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-007: Data processing and Deliverables](FS-007-data-processing-and-deliverables.md) · 📄 **Page 12 / 109** · [FS-009: Evidence ledger and Anchoring ▶️](FS-009-evidence-ledger-and-anchoring.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> In the [⚙️ Client portal](../../glossary.md#sys-client-portal), the [👤 Client](../../glossary.md#per-client) orders [🗃️ Missions](../../glossary.md#ent-mission), follows them live and downloads their [🗃️ Deliverables](../../glossary.md#ent-deliverable).

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

Give each Client a window on its own Missions. The Client orders a Mission for a [🗃️ Site](../../glossary.md#ent-site), follows the [🗃️ Squad](../../glossary.md#ent-squad) on a map during the flight (read only), and downloads the published Deliverables and reports. Other modes (results by e-mail only, no live view) can be configured per Client.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Client](../../glossary.md#per-client) | Persona | Orders, follows, downloads |
| [🗃️ Mission](../../glossary.md#ent-mission) | Entity | Requested, then Flying, then Completed |
| [🗃️ Deliverable](../../glossary.md#ent-deliverable) | Entity | Published to the Client |
| [⚙️ Client portal](../../glossary.md#sys-client-portal) | System | The Client's interface |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-016: Clients see only their own Missions](../business-rules/BR-016-clients-see-only-their-own-missions.md) | Clients see only their own Missions |
| [📏 BR-008: Operator isolation](../business-rules/BR-008-operator-isolation.md) | Operators never see each other's Clients |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-010: Order a Mission in the Client portal](../use-cases/UC-010-order-a-mission-in-the-client-portal.md) | [👤 Client](../../glossary.md#per-client) |
| [🎬 UC-011: Follow a Mission and download its Deliverables](../use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md) | [👤 Client](../../glossary.md#per-client) |
| [🎬 UC-015: Invite a Client to the Client portal](../use-cases/UC-015-invite-a-client-to-the-client-portal.md) | [👤 Mission planner](../../glossary.md#per-mission-planner), [👤 Client](../../glossary.md#per-client) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** a Client of Helio Energy **when** they order an Inspection of Les Vignes **then** the Mission is Requested for the Operator | [📏 BR-016](../business-rules/BR-016-clients-see-only-their-own-missions.md) | [🎬 UC-010](../use-cases/UC-010-order-a-mission-in-the-client-portal.md) |
| AC-2 | **Given** a Mission Flying **when** the Client opens it **then** they see the Squad on the map but no command | [📏 BR-016](../business-rules/BR-016-clients-see-only-their-own-missions.md) | [🎬 UC-011](../use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Live view | The Client sees Drone positions live; live video only when the Operator enables it for the Mission (off by default, for privacy) |
| Ordering | An order needs at least one acceptance criterion |

## <a id="out-of-scope"></a>🚫 Out of scope

- Invoicing and payment

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

> [🏠 Index](../../README.md) · [◀️ FS-007: Data processing and Deliverables](FS-007-data-processing-and-deliverables.md) · 📄 **Page 12 / 109** · [FS-009: Evidence ledger and Anchoring ▶️](FS-009-evidence-ledger-and-anchoring.md)
<!-- /spec:nav-bottom -->
