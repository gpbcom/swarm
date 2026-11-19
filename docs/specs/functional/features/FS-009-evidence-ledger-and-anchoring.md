# 📘 FS-009: Evidence ledger and Anchoring

<!-- spec:nav-top -->
> [🏠 Index](../../README.md) · [◀️ FS-008: Client portal](FS-008-client-portal.md) · 📄 **Page 13 / 109** · [FS-010: Simulator and training ▶️](FS-010-simulator-and-training.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> Swarm signs and chains an [🗃️ Evidence record](../../glossary.md#ent-evidence-record) for every [🗃️ Flight log](../../glossary.md#ent-flight-log) and [🗃️ Deliverable](../../glossary.md#ent-deliverable), and anchors it with the [⚙️ Anchoring service](../../glossary.md#sys-anchoring-service) the [🗃️ Operator](../../glossary.md#ent-operator) chooses: none, a timestamping authority or a blockchain.

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

Prove, months later, that a Flight log, a spray map or a patrol clip was not altered. Each record is signed and chained to the previous one; its fingerprint is anchored as the Operator chooses. Anyone with the file and its record can verify it, and only fingerprints leave Swarm.

## <a id="personas"></a>👤 Personas and entities

| Name | Kind | Role in this feature |
| --- | --- | --- |
| [👤 Client](../../glossary.md#per-client) | Persona | Verifies the evidence of a flight |
| [🗃️ Evidence record](../../glossary.md#ent-evidence-record) | Entity | Verified or Altered |
| [⚙️ Anchoring service](../../glossary.md#sys-anchoring-service) | System | Timestamping authority or blockchain |

## <a id="business-rules"></a>📏 Business rules

| Rule | Why it matters here |
| --- | --- |
| [📏 BR-009: Evidence integrity](../business-rules/BR-009-evidence-integrity.md) | Evidence integrity |

## <a id="use-cases"></a>🎬 Use cases

| Use case | Personas |
| --- | --- |
| [🎬 UC-012: Verify the Evidence record of a flight](../use-cases/UC-012-verify-the-evidence-record-of-a-flight.md) | [👤 Client](../../glossary.md#per-client) |

## <a id="acceptance"></a>✅ Acceptance criteria

| # | Given, when, then | Rule | Use case |
| --- | --- | --- | --- |
| AC-1 | **Given** an unchanged Flight log **when** it is verified **then** it shows Evidence record: Verified with its Anchoring date | [📏 BR-009](../business-rules/BR-009-evidence-integrity.md) | [🎬 UC-012](../use-cases/UC-012-verify-the-evidence-record-of-a-flight.md) |
| AC-2 | **Given** a Flight log edited after closing **when** it is verified **then** it shows Evidence record: Altered | [📏 BR-009](../business-rules/BR-009-evidence-integrity.md) | [🎬 UC-012](../use-cases/UC-012-verify-the-evidence-record-of-a-flight.md) |

## <a id="details"></a>🗒️ Details

Settled with the product owner ([interview](../../../research/interview.md)).

| Topic | Decision |
| --- | --- |
| Default Anchoring | A qualified timestamping authority (eIDAS, RFC 3161) |
| Blockchain option | A public blockchain, through an aggregator that batches fingerprints: low cost, no consortium to run |
| When a record shows Altered | The Operator is told at once; the person who verified sees the result; the Client is told when the record concerns them |

## <a id="out-of-scope"></a>🚫 Out of scope

- Coordinating Drones through a blockchain (rejected in the interview)
- Payments by smart contract

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

> [🏠 Index](../../README.md) · [◀️ FS-008: Client portal](FS-008-client-portal.md) · 📄 **Page 13 / 109** · [FS-010: Simulator and training ▶️](FS-010-simulator-and-training.md)
<!-- /spec:nav-bottom -->
