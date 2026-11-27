# T0.19: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md)

The workers reported no decisions. Every choice below comes from [PLAN.md](PLAN.md) or is read from the diff. Where a plan assumption states no alternative, the alternative is the one the plan or the specifications imply, and the reason beyond the plan is an open point.

## 🎯 Constraints

- The 10 Drones must move on the map, and the Drone to screen latency must be measured and shown (criteria of [TICKET.md](TICKET.md)).
- Hold the Squad and Abort are visible and not wired (BR-023, [TICKET.md](TICKET.md)).
- The first route stays under 300 kB of JavaScript, and frame to pixels stays under 50 ms ([`10-frontends`](../../specs/technical/10-frontends.md#performance)).
- The map is self-hosted ([`10-frontends`](../../specs/technical/10-frontends.md#maps)), and colours come from the tokens only.
- Every on-screen text is translated in four languages (BR-017).
- The gateway, `infra/charts` and the other tickets' areas are outside this ticket (PLAN.md).

## ⚖️ Choices at a glance

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | Where the socket is read | A Web Worker | The main thread | A worker protocol to maintain |
| [D2](#d2) | What the worker sends | Throttled full snapshots in transferable typed arrays | One message per frame | Up to 33 ms of added delay |
| [D3](#d3) | Where Ground control connects | The live URL of `config.json`, edge flight engine by default | The gateway with a token | No Operator check at the edge |
| [D4](#d4) | How latency reaches Grafana | OTLP/HTTP JSON built by hand | The OpenTelemetry SDK | Names assumed until T0.17 |
| [D5](#d5) | How the Squad is drawn | deck.gl layer with binary attributes, one draw per animation frame | React state per frame | Less idiomatic React |
| [D6](#d6) | The base map | PMTiles from a volume, style without labels | A hosted tile service | No labels or place names |
| [D7](#d7) | Loading the map | `React.lazy` | A static import | A loading state |
| [D8](#d8) | Verifying criterion 1 | Playwright on the image with a stand-in socket | Running in the dev cell | Not the literal wording |
| [D9](#d9) | Runtime configuration | `config.json` beside `index.html` | Build-time variables | A fetch at start |
| [D10](#d10) | The UC-025 A1 screen | Update the mock-up | Take screenshots | The reference screen drifts from UC-025 |

## <a id="d1"></a>D1: Where the socket is read

**Chosen:** a Web Worker · **Where:** [`frontend/packages/live/src/worker/live-worker-core.ts:30`](../../../frontend/packages/live/src/worker/live-worker-core.ts#L30) · **Source:** PLAN.md

| Option | For | Against |
| --- | --- | --- |
| ✅ Worker | The main thread never decodes a frame; the core takes the socket, post function and clock as arguments, so a fake socket tests it ([`frontend/packages/live/test/worker/fake-socket.ts`](../../../frontend/packages/live/test/worker/fake-socket.ts)) | A message protocol ([`live-worker-messages.ts`](../../../frontend/packages/live/src/worker/live-worker-messages.ts)) and a second entry point |
| Main thread | Simpler | Decoding competes with drawing, against the 50 ms budget |

**Trade-off:** more code for a main thread that only draws.

**Revisit when:** measured frame to pixels stays far under budget with a larger Squad on the main thread (no such measure exists yet).

## <a id="d2"></a>D2: What the worker sends

**Chosen:** a snapshot at most 30 times a second, buffers transferred · **Where:** [`live-worker-core.ts:92`](../../../frontend/packages/live/src/worker/live-worker-core.ts#L92), [`frontend/packages/live/src/snapshot/squad-store.ts:69`](../../../frontend/packages/live/src/snapshot/squad-store.ts#L69) · **Source:** PLAN.md

| Option | For | Against |
| --- | --- | --- |
| ✅ Throttled snapshot | Bounded work per second whatever the frame rate; no copy on transfer; frames are full, so merging by `drone_id` and `seq` is safe ([`squad-store.ts:38`](../../../frontend/packages/live/src/snapshot/squad-store.ts#L38)) | A frame may wait up to one interval |
| One message per frame | No added delay | One structured clone and one redraw request per frame |

**Trade-off:** a small delay against a steady load. The 30 per second default is in the constructor ([`live-worker-core.ts:39`](../../../frontend/packages/live/src/worker/live-worker-core.ts#L39)); the reason for 30 is an open point.

**Revisit when:** Drone to screen latency nears the 150 ms edge budget.

## <a id="d3"></a>D3: Where Ground control connects

**Chosen:** the `liveUrl` of the config, by default the edge flight engine · **Where:** [`frontend/apps/ground-control/src/config/app-config.ts:13`](../../../frontend/apps/ground-control/src/config/app-config.ts#L13) · **Source:** PLAN.md, reviewer

| Option | For | Against |
| --- | --- | --- |
| ✅ Config URL, edge default | 05-api#live says that at the edge Ground control connects straight to the flight engine | That endpoint checks no Operator |
| Gateway `/v1/live` | Checks the Operator | It reads the token from the handshake header, which a browser cannot set; the gateway is outside this ticket |

**Trade-off:** no Operator isolation on this path until the gateway settles how a browser sends its token. The reviewer flagged this to read first.

**Revisit when:** the gateway accepts a browser token.

## <a id="d4"></a>D4: How latency reaches Grafana

**Chosen:** an OTLP/HTTP JSON body written by hand, to an optional `metricsUrl` · **Where:** [`frontend/packages/live/src/latency/otlp-metrics-body.ts:31`](../../../frontend/packages/live/src/latency/otlp-metrics-body.ts#L31) · **Source:** PLAN.md

| Option | For | Against |
| --- | --- | --- |
| ✅ Hand-built body | Keeps the bundle small (300 kB budget) | Prometheus names assume the collector's default translation |
| OpenTelemetry SDK | Standard | Bundle size; T0.17, which brings the SDK, depends on this ticket |

**Trade-off:** the dashboard queries ([`telemetry-latency.json:26`](../../../infra/charts/observability/dashboards/telemetry-latency.json#L26)) may need renaming.

**Revisit when:** T0.17 lands.

## <a id="d5"></a>D5: How the Squad is drawn

**Chosen:** a deck.gl layer on binary attributes, redrawn once per animation frame · **Where:** [`frontend/packages/maps/src/drones/drone-layer.ts:41`](../../../frontend/packages/maps/src/drones/drone-layer.ts#L41), [`SquadMap.tsx:119`](../../../frontend/packages/maps/src/map/SquadMap.tsx#L119) · **Source:** PLAN.md

| Option | For | Against |
| --- | --- | --- |
| ✅ Binary layer, no React state per frame | No per-frame React render or object allocation; the snapshot arrays feed the GPU directly | Imperative code in an effect |
| React state per snapshot | Idiomatic | A render per snapshot, against the 50 ms budget |

**Trade-off:** harder code for a cheap draw path.

**Revisit when:** the budget is measured with the Squad sizes of later phases.

## <a id="d6"></a>D6: The base map

**Chosen:** PMTiles served from a mounted volume, no glyphs, sprite or labels · **Where:** [`frontend/packages/maps/src/style/base-style.ts:21`](../../../frontend/packages/maps/src/style/base-style.ts#L21) · **Source:** PLAN.md

| Option | For | Against |
| --- | --- | --- |
| ✅ Self-hosted PMTiles | "Self-hosted" in 10-frontends#maps; nothing fetched from a third party | No file committed, so the deployment must mount one; no place names |
| Hosted tiles | Labels and tiles for free | Contradicts 10-frontends#maps |

**Trade-off:** a map with colours only.

**Revisit when:** a later ticket supplies a tile file and fonts.

## <a id="d7"></a>D7: Loading the map

**Chosen:** `React.lazy` · **Where:** [`FlightView.tsx:40`](../../../frontend/apps/ground-control/src/flight/FlightView.tsx#L40) · **Source:** PLAN.md

| Option | For | Against |
| --- | --- | --- |
| ✅ Lazy | MapLibre and deck.gl stay out of the first route's 300 kB | A moment of loading |
| Static import | Simpler | Risks the 300 kB budget; no bundle measure was made, an open point |

**Trade-off:** the Suspense fallback.

**Revisit when:** a bundle measure shows room.

## <a id="d8"></a>D8: Verifying criterion 1

**Chosen:** Playwright on the real image with a stand-in socket · **Where:** [`frontend/apps/ground-control/e2e/live-stand-in-server.ts`](../../../frontend/apps/ground-control/e2e/live-stand-in-server.ts) · **Source:** PLAN.md, reviewer

| Option | For | Against |
| --- | --- | --- |
| ✅ Stand-in, in CI | Tests what ships ([AGENT.md](../../../AGENT.md) front-end tests rule); runs without the cell | Not 10 Simulator Drones |
| Dev cell | The literal criterion | No chart deploys the three services; `infra/charts` is outside the ticket |

**Trade-off:** the literal wording is unproven; the e2e has not run locally.

**Revisit when:** the cell deploys Ground control.

## <a id="d9"></a>D9: Runtime configuration

**Chosen:** `config.json` loaded at start · **Where:** [`app-config.ts:78`](../../../frontend/apps/ground-control/src/config/app-config.ts#L78) · **Source:** read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ `config.json` | One image for every cell; the compose test can set it | If it fails to load nothing renders (a follow-up) |
| Build-time variables | No fetch | One image per cell |

The reason beyond this is an open point: no worker or specification states it.

**Trade-off:** a failure path to fix.

**Revisit when:** the follow-up on unreadable config is done.

## <a id="d10"></a>D10: The UC-025 A1 screen

**Chosen:** update the mock-up · **Where:** [`docs/specs/screens/mockups/UC-025/a1.html`](../../../docs/specs/screens/mockups/UC-025/a1.html) · **Source:** PLAN.md

| Option | For | Against |
| --- | --- | --- |
| ✅ Update mock-up | T0.20 is not merged, so TKT-21's screenshot pipeline is not available | The screen now drops the Geofence and work-done zones that UC-025 step 2 specifies |
| Screenshots | Real window | Not possible yet |

**Trade-off:** the reference screen contradicts its use case until the follow-up.

**Revisit when:** T0.20 merges.

## 📝 Assumptions behind the choices

- The edge flight engine checks no Operator: supports [D3](#d3).
- Clocks are NTP-synchronised, and the collector's default naming applies: supports [D4](#d4).
- Full SquadFrames per tick: supports [D2](#d2).
- No PMTiles file committed: supports [D6](#d6).
- The dev cell does not deploy these services yet: supports [D8](#d8).
- T0.20 is not merged: supports [D10](#d10).
