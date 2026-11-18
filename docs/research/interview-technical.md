# 🛠️ Technical specification interview

**Date:** 2026-11-18. **Interviewee:** the product owner. **Input:** the approved functional specification
([docs/specs/](../specs/README.md)) and its [decisions](interview.md). Goal: a mono-repo for backend and frontend,
optimised for performance and scalability. These answers are the source of the technical pages in
[docs/specs/technical/](../specs/technical/README.md).

| # | Topic | Decision |
| --- | --- | --- |
| T1 | Topology | Edge and core: the flight engine runs at the edge (field laptop, operations centre, Dock site) and keeps flying without network; everything else runs in the core |
| T2 | Languages | Python 3.12 by default; Rust (PyO3 crates) for the hot path: safety loop, coverage planning, Choreography checks, MAVLink parsing; TypeScript for the frontends |
| T3 | Data models | Pydantic everywhere: one source of truth for every model; TypeScript types generated from OpenAPI |
| T4 | Messaging | NATS JetStream from edge to core, leaf nodes at the edge, subjects per Operator and Mission |
| T5 | Main database | PostgreSQL 16 with PostGIS; Operator isolation by row-level security; PgBouncer; read replicas |
| T6 | Telemetry store | TimescaleDB hypertables, compression, continuous aggregates; Parquet archive in object storage |
| T7 | Files | S3-compatible object storage (provider service, MinIO on premises), object lock for evidence |
| T8 | Cache and edge store | Valkey in the core; SQLite at the edge, synced through NATS |
| T9 | Services | flight-engine and video-relay at the edge; gateway, missions, fleet, planner, processing, agents, evidence, notifier, simulator in the core |
| T10 | Safety loop | Two layers: Geofence and Fail-safes uploaded to each autopilot; a deterministic tick per Mission at the edge (20 Hz, 50 Hz for Light shows) |
| T11 | Processing | OpenDroneMap on GPU workers; own detection models (PyTorch, ONNX Runtime); Operators may train their own |
| T12 | AI agents | LangGraph and typed tools, LLM provider-agnostic; plus an MCP server and the A2A protocol |
| T13 | Public API | REST (FastAPI, OpenAPI 3.1, /v1) and WebSocket for live data; webhooks in and out |
| T14 | Internal calls | NATS request-reply; no service reads another's database |
| T15 | Live data | Per-client rate and fields, delta encoding, batching, backpressure keeping the latest state |
| T16 | Video | WebRTC through a self-hostable SFU for Pilots (simulcast), LL-HLS for the Client portal |
| T17 | Identity | Keycloak (OIDC), Operators as organisations, MFA, roles per persona, row-level security |
| T18 | Links | MAVLink 2 signing, WireGuard for cellular and mesh, NATS over mTLS, secrets in a vault |
| T19 | MCP and A2A | Full access for outside agents as delegates of a person, behind a human gate: signing the Pre-flight check and launch need the person's confirmation; abort and manual control stay in Ground control; BR-021 amended |
| T20 | Compliance | GDPR retention and blurring, EU and US data residency, encryption at rest, audit in the evidence ledger, scans, SBOM, yearly penetration test |
| T21 | Scale targets | Large: 10,000 Operators, 2,000 Missions in flight, 50,000 Drones, Light shows up to 5,000 Drones, about 1 million telemetry messages per second |
| T22 | Budgets | Command to Drone p99 < 50 ms; Hold or abort to every Drone < 100 ms; safety tick < 5 ms for 500 Drones; telemetry to screen p95 < 150 ms local, < 400 ms remote; REST p95 < 100 ms reads, < 250 ms writes; video < 300 ms |
| T23 | Encoding | MessagePack for telemetry and WebSocket frames (same Pydantic models); JSON for REST |
| T24 | Scale-out | Cells: independent copies of the flight-facing core, about 200 Missions each; a thin global layer for identity and routing |
| T25 | Big shows | Partitioned edge: sectors of up to 1,000 Drones per edge node, one show coordinator |
| T26 | Observability | OpenTelemetry, Prometheus or Mimir, Loki, Tempo, Grafana, self-hosted; SLOs; system telemetry kept apart from Drone Telemetry |
| T27 | Load tests | Simulated fleets (PX4 SITL and synthetic Rust Drones), k6, nightly full-cell load with budgets as assertions, Rust benchmarks per pull request, chaos tests |
| T28 | Cloud | Sovereign EU providers first, OVHcloud and Scaleway, plus self-hosted k3s cells (US Operators included) |
| T29 | On premises and edge | One cell on k3s from a signed offline bundle; edge appliance with over-the-air updates, never during a Mission |
| T30 | Mono-repo | uv workspace, pnpm workspace with Turborepo, Cargo workspace (maturin); GitHub Actions with change detection; signed images on GHCR; Argo CD; GitFlow |
| T31 | Environments | Ephemeral dev cells per branch, staging, production cells per region, an always-on simulation environment |
| T32 | Frontends | One React and TypeScript codebase for the four parts of Swarm, Tauri 2 desktop shell; PyQt6 dropped |
| T33 | Maps | MapLibre GL with self-hosted vector tiles (offline at the edge) and deck.gl GPU layers |
| T34 | Front state | TanStack Query, a Web Worker for live frames with typed arrays, Zustand, tokens from the visual identity, Radix primitives, FormatJS, Playwright and visual tests |
| T35 | Inputs | Desktop and web browser both full: gamepads, joysticks, manual control, multi-screen; tablet as decided in the functional specification |
| T36 | Retention | Full-rate telemetry 90 days, then Parquet for the Evidence record lifetime (default 5 years); raw images and video 90 days; Deliverables and evidence 5 years |
| T37 | Disaster recovery | Per cell: RPO 5 minutes, RTO 1 hour; replicated streams and storage; monthly restore drills |
| T38 | GPU | Pooled per cell, scaled on queue depth, priority queues; at least one GPU server on premises |
| T39 | MCP and A2A serving | Every MCP server and A2A agent sits behind a Kubernetes Service and is scaled by KEDA: `agents-mcp` and `agents-a2a` on in-flight requests (2 to 40 pods in production, scale to zero in dev), `agents-worker` on JetStream queue lag (0 to 100 pods); stateless pods with session and task state in Valkey and JetStream |
| T40 | Derived details | Confirmed: 13 cells at full target; 50,000 people connected, 5,000 on video; big shows send Telemetry to the cell at 5 Hz; tokens 5 min; PIN locked after 5 failures; encrypted edge store; signal retention and SLOs; global layer in two EU regions; edge update rings; on-premises sizing; front-end budgets |
| T41 | Roadmap | `docs/specs/roadmap/` added to the specification layout as a page kind (🛣️), with its overview page |
| T42 | Layers and repositories | Every service has `api/` (all endpoints), `service/` (all business logic, using storage and clients), `storage/` (all storage classes), `clients/` (other services and external systems) and `models/`; one repository per entity stored in PostgreSQL, a shared base class, a unit of work with an outbox |
| T43 | Infrastructure as code | Terraform provisions every cell and the global layer (clusters, node pools, networks, object storage, DNS, vault) for OVHcloud, Scaleway and self-hosted k3s; Helm and Argo CD deploy on top |
| T44 | Cells before general availability | An OVHcloud cell for the design partner from S24 and a self-hosted beta cell as the second cell |
