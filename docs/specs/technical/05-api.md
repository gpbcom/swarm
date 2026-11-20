# 🔌 API layer

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ Engine and services](04-engine.md) · 📄 **Page 100 / 120** · [Security ▶️](06-security.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> How the front ends, Operators' systems and AI agents talk to Swarm: REST for resources, WebSocket for live data, WebRTC and LL-HLS for video, webhooks, and MCP and A2A for agents. Inside a cell, services talk over NATS. Decisions T13 to T16, T19, T23.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🔭 Overview](#overview)
2. [🔌 REST](#rest)
3. [📨 Live data over WebSocket](#live)
4. [🎥 Video](#video)
5. [🔁 Webhooks](#webhooks)
6. [💬 MCP and A2A](#mcp-a2a)
7. [🔌 Connectors and the ERP port](#connectors)
8. [🔁 Internal calls](#internal)
9. [🔗 Features implemented](#features)
<!-- /spec:summary -->

## <a id="overview"></a>🔭 Overview

| Interface | Used by | Technology | Served by |
| --- | --- | --- | --- |
| REST `/v1` | Front ends, Operators' integrations | FastAPI, OpenAPI 3.1, JSON | gateway → services |
| Live `/v1/live` | Ground control (remote), Client portal, dashboards | WebSocket, MessagePack | gateway |
| Local live | Ground control at the edge | WebSocket to the local flight engine | flight-engine |
| Video | Pilots; Clients when enabled | WebRTC (SFU), LL-HLS | video-relay, SFU, CDN |
| Webhooks out | Operators' systems | HTTPS POST, HMAC-signed | notifier |
| Webhooks in | Site security systems | HTTPS POST; SIA DC-09 through an adapter | gateway |
| MCP | Outside AI clients | MCP over Streamable HTTP, OAuth 2.1 | agents |
| A2A | Outside agents | A2A protocol, Agent Cards | agents |
| Internal | Services in a cell | NATS request-reply and JetStream events | every service |

## <a id="rest"></a>🔌 REST

- **Resources** follow the glossary: `/v1/missions`, `/v1/missions/{id}/squad`, `/v1/missions/{id}/replans`, `/v1/drones`, `/v1/drone-models`, `/v1/payloads`, `/v1/authorisations`, `/v1/deliverables`, `/v1/defects`, `/v1/scorecards`, `/v1/evidence/{id}/verify`, `/v1/proposals/{id}:accept`.
- **Conventions:** cursor pagination (`?after=`), `ETag` and `If-Match` on updates, `Idempotency-Key` on every POST, errors as `application/problem+json` with the message rules of AGENT.md, field selection (`?fields=`) for heavy lists.
- **Performance:** responses serialised by Pydantic in Rust (`model_dump_json`), gzip or Brotli, read endpoints on replicas, short-lived cache in Valkey for lists that many people read (Fleet, Missions of the day).
- **Budget:** p95 under 100 ms for reads and under 250 ms for writes inside a cell.
- **Contract:** the OpenAPI document is generated and published; the TypeScript client in `packages/ts/api-client` is generated from it in CI.

## <a id="live"></a>📨 Live data over WebSocket

One socket per client, many subscriptions:

```text
client → {"op": "subscribe", "topic": "mission/<id>/squad", "rate": "full"}
client → {"op": "subscribe", "topic": "mission/<id>/alerts"}
server → SquadFrame | Alert | ReplanProposed | AlarmRaised | Notification   (MessagePack)
```

- **Fan-out:** the gateway subscribes once per Mission to NATS and fans out to every client watching it; a cell's gateways share the work by consistent hashing of Mission ids.
- **Per-client rate and fields** (decision T15): Pilot full rate with all Telemetry; Client portal 2 Hz positions only; dashboards 1 Hz aggregates. Rights decide the ceiling, the client may ask for less.
- **Frames:** delta-encoded `SquadFrame`, batched every 50 ms, `permessage-deflate`.
- **Backpressure:** each client has a one-slot mailbox per topic holding the latest state; a slow client skips intermediate frames instead of growing a queue.
- **At the edge** Ground control connects straight to the flight engine with the same protocol, so the same front end works locally and remotely.

## <a id="video"></a>🎥 Video

- **Pilots:** WebRTC through a self-hostable SFU (LiveKit) in each cell and at the edge; each Payload stream is sent in simulcast (three layers), so the Mosaic takes the small layer and the Focus view the full one; budget under 300 ms glass to glass.
- **Clients:** LL-HLS (2 to 5 s), produced from the SFU and served by the CDN, only when the Operator enabled it for the Mission.
- **Recording:** segments to object storage, fingerprinted for Patrol evidence.

## <a id="webhooks"></a>🔁 Webhooks

- **Out:** Mission events, Deliverables published, Scorecards published, Alarm outcomes; signed with HMAC-SHA256, retried with exponential back-off for 24 hours, visible in the Back office.
- **In:** Site security systems post Alarms to `/v1/sites/{id}/alarms` with a per-Site secret; alarm panels speaking SIA DC-09 connect to a small receiver that converts to the same call ([📘 FS-015](../functional/features/FS-015-patrol.md)).

## <a id="mcp-a2a"></a>💬 MCP and A2A

- **MCP server** per Operator: tools mirror the REST resources and the Proposal flow; OAuth 2.1 with Keycloak; the token names the person and the Outside agent.
- **A2A:** Agent Cards for the Mission assistant, the Co-pilot and the Report writer at `/.well-known/agent.json` per Operator; tasks, streaming updates and artefacts per the A2A protocol.
- **Rights:** an Outside agent has the rights of its person, within the Assistant permissions of that person ([📏 BR-021](../functional/business-rules/BR-021-ai-agents-propose-people-decide.md), [📏 BR-028](../functional/business-rules/BR-028-assistant-permissions-are-layered.md)); acts that need the person (signing the Pre-flight check, launching) return `202 Accepted` with a pending confirmation, which completes only when the person confirms on their device ([🔐 the human gate](06-security.md#human-gate)). Abort and manual control are not exposed outside Ground control.
- **Limits:** separate rate limits for agents, every call recorded in the evidence ledger.
- **Serving:** the MCP server and the A2A agents run behind their own Kubernetes Services (`agents-mcp`, `agents-a2a`) and are scaled by KEDA; long runs go to `agents-worker`, scaled by KEDA on the JetStream queue ([🔩 Engine and services](04-engine.md#agents)).

## <a id="connectors"></a>🔌 Connectors and the ERP port

- **ERP port** ([📘 FS-024: ERP and Squad shortfall](../functional/features/FS-024-erp-and-squad-shortfall.md)): one contract in Swarm for every ERP. Its operations: read and keep in step Clients and Sites; create a quote from a Mission request and an invoice from a delivered Mission, with its Deliverables as proof; register Drones, Payloads and Batteries as assets with their purchase, maintenance and repair costs; send staff time per Mission; read stock, bills of materials, suppliers and lead times; place Manufacturing orders and Purchase orders and follow them ([📏 BR-031](../functional/business-rules/BR-031-a-squad-shortfall-is-covered-through-the-erp.md)).
- **Simple-ERP** (`gpbcom/simple-erp`) is the first adapter of the port. It is reached through its API once that API exists, an external prerequisite ([🤝 P-10](../roadmap/11-hardware-and-partners.md#p-10)), and also through MCP and A2A.
- **Connectors the Operator adds:** MCP servers and A2A agents registered in the Back office, and REST APIs and webhooks described by their URL, their authentication and the actions they allow. Each becomes tools of the action catalogue with its own Assistant permissions ([🔩 Engine and services](04-engine.md#agents)).
- **Office tools:** the person's e-mail, calendar and documents in Microsoft 365 or Google Workspace, after that person's consent (OAuth), with that person's rights only.
- **Chat tools:** Slack and Microsoft Teams apps, to talk to the Assistant and for it to post.
- **GIS, payments, assets:** GIS and map servers, invoicing and payment services, asset registers and IoT platforms, each reached as a Connector of its own.
- **Secrets:** every Connector credential is kept in Vault, never in configuration ([🔑 Secrets and keys](06-security.md#secrets)).

## <a id="internal"></a>🔁 Internal calls

- **Request-reply** over NATS for commands and queries between services, with Pydantic payloads, deadlines and idempotency keys; one layer owns each retry.
- **Events** on JetStream subjects `op.<operator_id>.…`; consumers are durable and idempotent.
- **No shared database:** a service never reads another's schema.

## <a id="features"></a>🔗 Features implemented

[📘 FS-008](../functional/features/FS-008-client-portal.md), [📘 FS-015](../functional/features/FS-015-patrol.md), [📘 FS-017](../functional/features/FS-017-mission-assistant.md), [📘 FS-021](../functional/features/FS-021-ground-control-monitoring.md), and every feature with a screen.

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ Engine and services](04-engine.md) · 📄 **Page 100 / 120** · [Security ▶️](06-security.md)
<!-- /spec:nav-bottom -->
