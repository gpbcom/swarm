# 🔐 Security

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ API layer](05-api.md) · 📄 **Page 101 / 120** · [Scalability and performance ▶️](07-scalability.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> Who can do what, how Operators stay apart, how Outside agents are held to a person's decision, and how the links to Drones and the supply chain are protected. Decisions T17 to T20.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🔑 Identity](#identity)
2. [👥 Roles and Operator isolation](#authorisation)
3. [🛡️ The human gate for AI agents](#human-gate)
4. [📡 Links to Drones, Docks and the edge](#links)
5. [🔑 Secrets and keys](#secrets)
6. [🛡️ Supply chain and testing](#supply-chain)
7. [🛡️ Privacy and compliance](#privacy)
8. [🔗 Features implemented](#features)
<!-- /spec:summary -->

## <a id="identity"></a>🔑 Identity

- **Keycloak** (OpenID Connect), the same product in the cloud and on premises; one realm per deployment, each [🗃️ Operator](../glossary.md#ent-operator) an organisation; single sign-on with the Operator's own identity provider (OIDC or SAML) on request.
- **Multi-factor authentication** required for Pilots, Mission planners, Fleet maintainers, Instructors and Swarm administrators; optional for Clients and Site agents.
- **Tokens:** short-lived access tokens (5 minutes) carrying the person, the Operator, the roles and, for Clients and Site agents, their Sites; refresh tokens rotated. Desktop and web use the authorisation code flow with PKCE.
- **Pre-flight PIN:** a separate secret per Pilot, hashed with Argon2id, locked after five failures.

## <a id="authorisation"></a>👥 Roles and Operator isolation

| Role (persona) | Main rights |
| --- | --- |
| Pilot | Run Pre-flight checks, sign, launch, supervise, approve Re-plans, manual control, abort, debrief |
| Mission planner | Design and simulate Missions, record Authorisations, review Defects and Deliverables, publish, invite Clients |
| Fleet maintainer | Register and maintain Drones, Payloads, Batteries, Docks; run compatibility tests |
| Instructor | Run training sessions and inject failures in the Simulator only |
| Client | Order Missions, follow them read-only, download published Deliverables, verify evidence (own Sites) |
| Site agent | Request Patrols, receive Alarm outcomes (own Sites) |
| Swarm administrator | Create Operators and their first accounts; no access to Operators' data |

- **Checks in two places:** the gateway checks the role and the Operator of every call; PostgreSQL row-level security enforces the Operator on every row ([🗄️ Storage](03-storage.md#postgresql)).
- **NATS accounts per Operator:** a service acting for one Operator can only publish and subscribe on `op.<operator_id>.…`.
- **Object storage:** one bucket per Operator, access through signed URLs only.

## <a id="human-gate"></a>🛡️ The human gate for AI agents

Every act of an AI agent (the [⚙️ Assistant](../glossary.md#sys-assistant), its specialists, or an [🔤 Outside agent](../glossary.md#term-outside-agent) connected through MCP or A2A) names the person it acts for, and runs only within the [🗃️ Assistant permission](../glossary.md#ent-assistant-permission) of that action for that person ([📏 BR-021](../functional/business-rules/BR-021-ai-agents-propose-people-decide.md), [📏 BR-028](../functional/business-rules/BR-028-assistant-permissions-are-layered.md)). An Outside agent holds a token naming that person and the agent itself.

| Assistant permission | What the gateway and the services do |
| --- | --- |
| Off | Refuse, and say who sets the permission |
| Read | Read only what the person may read ([📏 BR-032](../functional/business-rules/BR-032-the-assistant-reaches-only-what-its-person-may-reach.md)) |
| Propose | Create a `Proposal`; it takes effect when a person accepts it, recorded with their name |
| Act | Do it and record it with the person it acted for; ask the person to confirm first where the Operator set it; a Flight-critical act only while a Pilot is on duty for the Squad and sees it in Ground control, announced with a countdown the Pilot can cancel ([📏 BR-029](../functional/business-rules/BR-029-flight-critical-acts-need-a-pilot-on-duty.md)) |

- **Outside agents:** signing the Pre-flight check and launching always wait for the person's confirmation on their own device (push Notification, then their PIN), whatever the Assistant permission.
- **Layers:** the Swarm administrator sets a ceiling per Operator, the Operator sets each role within it, each person may only lower their own levels; a new Operator starts at Propose everywhere ([📏 BR-028](../functional/business-rules/BR-028-assistant-permissions-are-layered.md)).
- **Before the Assistant permissions (milestone M5):** the fixed gate of P5 applies. Read, propose and drafts are allowed; approving a Re-plan, publishing a Deliverable or Scorecard and inviting a Client are allowed as the person's delegate, recorded with both names; signing the Pre-flight check and launching wait for the person's confirmation on their own device (push Notification, then their PIN); abort, manual control and Hold stay in Ground control.

The gate is enforced in the gateway and the services, never trusted to the agent. Every act of an AI agent is recorded in the `AssistantActivity` and in the evidence ledger.

## <a id="links"></a>📡 Links to Drones, Docks and the edge

- **MAVLink 2 signing** on every MAVLink link, one key per Drone, rotated per Mission by the flight engine.
- **Cellular and mesh links:** WireGuard tunnels from Drones and Docks to the edge.
- **Edge to cell:** NATS leaf node over mTLS, credentials per edge node, revocable from the Back office.
- **Vendor links** (Parrot, DJI, Skydio): the vendors' own encryption, wrapped by the adapter.
- **Simulator:** separate credentials that cannot reach a real Drone ([📏 BR-014](../functional/business-rules/BR-014-simulation-isolation.md)).

## <a id="secrets"></a>🔑 Secrets and keys

- **Vault** (HashiCorp Vault or OpenBao) per cell for database credentials (dynamic), signing keys, LLM provider keys of each Operator, webhook secrets; cloud KMS for envelope encryption where available.
- **Configuration holds names, never secrets** (AGENT.md: fields ending in `_key` name a vault entry).
- **Evidence signing keys** (Ed25519) never leave the vault; signatures are made through its transit engine.

## <a id="supply-chain"></a>🛡️ Supply chain and testing

- Dependency, secret and container scans in CI (OSV-Scanner, Trivy), static analysis (ruff, mypy, Semgrep, cargo-audit, eslint).
- Images built from minimal bases, signed with cosign, with an SBOM; Kubernetes admission accepts only signed images.
- The edge appliance and on-premises bundle are signed; updates are verified before install.
- A penetration test every year and before each new Activity goes live.

## <a id="privacy"></a>🛡️ Privacy and compliance

- **GDPR:** video and images can show people. Raw images and video kept 90 days by default; faces blurred in Client-visible video on request; a data processing register per Operator; data subject requests handled per Operator.
- **Residency:** EU Operators in EU cells (OVHcloud, Scaleway or self-hosted in the EU), US Operators in US self-hosted cells; data never crosses regions, only fingerprints reach Anchoring services.
- **Encryption at rest:** databases, object storage, NATS streams, edge SQLite (SQLCipher); in transit everywhere (TLS 1.3, including NATS and HTTP between services inside a cell).
- **Audit:** every write and every agent call in the evidence ledger ([📘 FS-009](../functional/features/FS-009-evidence-ledger-and-anchoring.md)).

## <a id="features"></a>🔗 Features implemented

[📘 FS-002](../functional/features/FS-002-pre-flight-check-and-launch.md), [📘 FS-009](../functional/features/FS-009-evidence-ledger-and-anchoring.md), [📘 FS-012](../functional/features/FS-012-operators-deployment-and-languages.md), [📘 FS-015](../functional/features/FS-015-patrol.md), [📘 FS-017](../functional/features/FS-017-mission-assistant.md), [📘 FS-023](../functional/features/FS-023-ai-assistant.md).

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ API layer](05-api.md) · 📄 **Page 101 / 120** · [Scalability and performance ▶️](07-scalability.md)
<!-- /spec:nav-bottom -->
