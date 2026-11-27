# T0.19: Simulated Squad on the map

**Status:** ✅ Done · **Ticket:** [TICKET.md](TICKET.md) · **Choices and trade-offs:** [IMPLEMENTATION.md](IMPLEMENTATION.md)

## 🔭 What it does

- Ground control opens on a Flight view: a MapLibre map on self-hosted PMTiles, with the Squad drawn by deck.gl as dots.
- A Web Worker owns the live socket, decodes MessagePack, merges frames by Drone and hands the main thread a snapshot at most 30 times a second.
- The latency of what is drawn is recorded in histograms, exported as OTLP/HTTP when `metricsUrl` is set, and shown by a Grafana dashboard with the 150, 400 and 50 ms budgets as thresholds.
- Ground control has its own image, a compose service on port 8180 and a Playwright suite in the images workflow. Hold the Squad and Abort stay visible and still do nothing.

## ⚙️ How it works

1. **Runtime config:** `config.json` is read and validated at start-up, in [`frontend/apps/ground-control/src/config/app-config.ts:78`](../../../frontend/apps/ground-control/src/config/app-config.ts#L78); [`frontend/apps/ground-control/src/main.tsx:18`](../../../frontend/apps/ground-control/src/main.tsx#L18) renders the app only once it is loaded.
2. **Flight view:** [`frontend/apps/ground-control/src/flight/FlightView.tsx:43`](../../../frontend/apps/ground-control/src/flight/FlightView.tsx#L43) builds the feed, two latency histograms and loads the map on demand ([`FlightView.tsx:40`](../../../frontend/apps/ground-control/src/flight/FlightView.tsx#L40)).
3. **Connect:** the effect at [`FlightView.tsx:62`](../../../frontend/apps/ground-control/src/flight/FlightView.tsx#L62) starts the feed, which calls `LiveClient.connect` in [`frontend/packages/live/src/client/live-client.ts:29`](../../../frontend/packages/live/src/client/live-client.ts#L29); this creates the worker ([`frontend/packages/live/src/worker/live.worker.ts`](../../../frontend/packages/live/src/worker/live.worker.ts)).
4. **Socket in the worker:** [`frontend/packages/live/src/worker/live-worker-core.ts:56`](../../../frontend/packages/live/src/worker/live-worker-core.ts#L56) opens the socket, sends the `mission/<id>/squad` subscription on open and reports statuses.
5. **Decode and merge:** each message is decoded by [`frontend/packages/live/src/protocol/squad-frame-decoder.ts:63`](../../../frontend/packages/live/src/protocol/squad-frame-decoder.ts#L63) and merged by `drone_id` into typed arrays in [`frontend/packages/live/src/snapshot/squad-store.ts:38`](../../../frontend/packages/live/src/snapshot/squad-store.ts#L38); a frame whose `seq` is not newer is skipped.
6. **Throttled snapshot:** [`live-worker-core.ts:92`](../../../frontend/packages/live/src/worker/live-worker-core.ts#L92) arms one timer when the store is dirty, then posts a snapshot whose buffers are transferred, not copied.
7. **Draw once per frame:** [`frontend/packages/maps/src/map/SquadMap.tsx:103`](../../../frontend/packages/maps/src/map/SquadMap.tsx#L103) schedules at most one `requestAnimationFrame`, builds the layer with [`frontend/packages/maps/src/drones/drone-layer.ts:41`](../../../frontend/packages/maps/src/drones/drone-layer.ts#L41) (binary attributes, colours from the tokens) and fits the Squad's bounds once.
8. **Base map:** the style is built from the palette in [`frontend/packages/maps/src/style/base-style.ts:21`](../../../frontend/packages/maps/src/style/base-style.ts#L21) and reads PMTiles through the protocol registered at [`frontend/packages/maps/src/style/pmtiles-protocol.ts:12`](../../../frontend/packages/maps/src/style/pmtiles-protocol.ts#L12).
9. **Measure:** after the render, [`SquadMap.tsx:119`](../../../frontend/packages/maps/src/map/SquadMap.tsx#L119) reports the drawn snapshot; [`frontend/apps/ground-control/src/flight/squad-feed.ts:62`](../../../frontend/apps/ground-control/src/flight/squad-feed.ts#L62) records draw time minus `t_us` per updated Drone, and worker receipt to draw time once.
10. **Export:** when `metricsUrl` is set, [`FlightView.tsx:81`](../../../frontend/apps/ground-control/src/flight/FlightView.tsx#L81) starts a reporter whose flush ([`frontend/packages/live/src/latency/latency-reporter.ts:78`](../../../frontend/packages/live/src/latency/latency-reporter.ts#L78)) posts the body built by [`frontend/packages/live/src/latency/otlp-metrics-body.ts:31`](../../../frontend/packages/live/src/latency/otlp-metrics-body.ts#L31).
11. **Dashboard:** the p95 queries and thresholds are in [`infra/charts/observability/dashboards/telemetry-latency.json:26`](../../../infra/charts/observability/dashboards/telemetry-latency.json#L26) (cell, 400 ms), [`:49`](../../../infra/charts/observability/dashboards/telemetry-latency.json#L49) (edge, 150 ms) and [`:72`](../../../infra/charts/observability/dashboards/telemetry-latency.json#L72) (frame to pixels, 50 ms).
12. **Image:** [`frontend/apps/ground-control/Dockerfile`](../../../frontend/apps/ground-control/Dockerfile) builds the app and serves it with unprivileged nginx; [`infra/compose/e2e.yaml:8`](../../../infra/compose/e2e.yaml#L8) publishes it on 8180 for the Playwright suite.

## 🧱 Files and lines changed

<!-- changes -->
| File | Change | Lines in the new version | Added | Removed |
| --- | --- | --- | --- | --- |
| [`.github/workflows/images.yml`](../../../.github/workflows/images.yml) | Modified | [168-169](../../../.github/workflows/images.yml#L168), [175-177](../../../.github/workflows/images.yml#L175) | +5 | −1 |
| [`AGENT.md`](../../../AGENT.md) | Modified | [67-78](../../../AGENT.md#L67), [253-257](../../../AGENT.md#L253) | +17 | −0 |
| [`docs/specs/screens/UC-025/a1.dark.png`](../../../docs/specs/screens/UC-025/a1.dark.png) | Modified | binary | +- | −- |
| [`docs/specs/screens/UC-025/a1.png`](../../../docs/specs/screens/UC-025/a1.png) | Modified | binary | +- | −- |
| [`docs/specs/screens/mockups/UC-025/a1.html`](../../../docs/specs/screens/mockups/UC-025/a1.html) | Modified | [11](../../../docs/specs/screens/mockups/UC-025/a1.html#L11), [removed after 24](../../../docs/specs/screens/mockups/UC-025/a1.html#L24), [removed after 28](../../../docs/specs/screens/mockups/UC-025/a1.html#L28) | +1 | −7 |
| [`frontend/apps/ground-control/Dockerfile`](../../../frontend/apps/ground-control/Dockerfile) | Added | [1-19](../../../frontend/apps/ground-control/Dockerfile#L1) | +19 | −0 |
| [`frontend/apps/ground-control/e2e/flight-view.spec.ts`](../../../frontend/apps/ground-control/e2e/flight-view.spec.ts) | Added | [1-71](../../../frontend/apps/ground-control/e2e/flight-view.spec.ts#L1) | +71 | −0 |
| [`frontend/apps/ground-control/e2e/global-setup.ts`](../../../frontend/apps/ground-control/e2e/global-setup.ts) | Added | [1-51](../../../frontend/apps/ground-control/e2e/global-setup.ts#L1) | +51 | −0 |
| [`frontend/apps/ground-control/e2e/live-stand-in-server.ts`](../../../frontend/apps/ground-control/e2e/live-stand-in-server.ts) | Added | [1-94](../../../frontend/apps/ground-control/e2e/live-stand-in-server.ts#L1) | +94 | −0 |
| [`frontend/apps/ground-control/e2e/squad-route.ts`](../../../frontend/apps/ground-control/e2e/squad-route.ts) | Added | [1-43](../../../frontend/apps/ground-control/e2e/squad-route.ts#L1) | +43 | −0 |
| [`frontend/apps/ground-control/eslint.config.js`](../../../frontend/apps/ground-control/eslint.config.js) | Modified | [4](../../../frontend/apps/ground-control/eslint.config.js#L4) | +1 | −1 |
| [`frontend/apps/ground-control/nginx.conf`](../../../frontend/apps/ground-control/nginx.conf) | Added | [1-53](../../../frontend/apps/ground-control/nginx.conf#L1) | +53 | −0 |
| [`frontend/apps/ground-control/package.json`](../../../frontend/apps/ground-control/package.json) | Modified | [9-10](../../../frontend/apps/ground-control/package.json#L9), [14-15](../../../frontend/apps/ground-control/package.json#L14), [24-25](../../../frontend/apps/ground-control/package.json#L24), [27](../../../frontend/apps/ground-control/package.json#L27), [34](../../../frontend/apps/ground-control/package.json#L34), [41-42](../../../frontend/apps/ground-control/package.json#L41) | +10 | −2 |
| [`frontend/apps/ground-control/playwright.config.ts`](../../../frontend/apps/ground-control/playwright.config.ts) | Added | [1-11](../../../frontend/apps/ground-control/playwright.config.ts#L1) | +11 | −0 |
| [`frontend/apps/ground-control/public/config.json`](../../../frontend/apps/ground-control/public/config.json) | Added | [1-9](../../../frontend/apps/ground-control/public/config.json#L1) | +9 | −0 |
| [`frontend/apps/ground-control/src/App.tsx`](../../../frontend/apps/ground-control/src/App.tsx) | Modified | [6-17](../../../frontend/apps/ground-control/src/App.tsx#L6), [23-31](../../../frontend/apps/ground-control/src/App.tsx#L23) | +21 | −2 |
| [`frontend/apps/ground-control/src/config/app-config.ts`](../../../frontend/apps/ground-control/src/config/app-config.ts) | Added | [1-97](../../../frontend/apps/ground-control/src/config/app-config.ts#L1) | +97 | −0 |
| [`frontend/apps/ground-control/src/config/load-app-config.ts`](../../../frontend/apps/ground-control/src/config/load-app-config.ts) | Added | [1-28](../../../frontend/apps/ground-control/src/config/load-app-config.ts#L1) | +28 | −0 |
| [`frontend/apps/ground-control/src/flight/FlightView.tsx`](../../../frontend/apps/ground-control/src/flight/FlightView.tsx) | Added | [1-124](../../../frontend/apps/ground-control/src/flight/FlightView.tsx#L1) | +124 | −0 |
| [`frontend/apps/ground-control/src/flight/flight-view.css`](../../../frontend/apps/ground-control/src/flight/flight-view.css) | Added | [1-12](../../../frontend/apps/ground-control/src/flight/flight-view.css#L1) | +12 | −0 |
| [`frontend/apps/ground-control/src/flight/squad-feed.ts`](../../../frontend/apps/ground-control/src/flight/squad-feed.ts) | Added | [1-71](../../../frontend/apps/ground-control/src/flight/squad-feed.ts#L1) | +71 | −0 |
| [`frontend/apps/ground-control/src/main.tsx`](../../../frontend/apps/ground-control/src/main.tsx) | Modified | [10](../../../frontend/apps/ground-control/src/main.tsx#L10), [16](../../../frontend/apps/ground-control/src/main.tsx#L16), [18-30](../../../frontend/apps/ground-control/src/main.tsx#L18) | +15 | −7 |
| [`frontend/apps/ground-control/test/app.test.tsx`](../../../frontend/apps/ground-control/test/app.test.tsx) | Modified | [4](../../../frontend/apps/ground-control/test/app.test.tsx#L4), [12-13](../../../frontend/apps/ground-control/test/app.test.tsx#L12), [19-26](../../../frontend/apps/ground-control/test/app.test.tsx#L19), [39](../../../frontend/apps/ground-control/test/app.test.tsx#L39), [46](../../../frontend/apps/ground-control/test/app.test.tsx#L46), [51](../../../frontend/apps/ground-control/test/app.test.tsx#L51), [58](../../../frontend/apps/ground-control/test/app.test.tsx#L58), [63](../../../frontend/apps/ground-control/test/app.test.tsx#L63), [69](../../../frontend/apps/ground-control/test/app.test.tsx#L69), [74-77](../../../frontend/apps/ground-control/test/app.test.tsx#L74), [79-100](../../../frontend/apps/ground-control/test/app.test.tsx#L79) | +43 | −12 |
| [`frontend/apps/ground-control/test/config/app-config.test.ts`](../../../frontend/apps/ground-control/test/config/app-config.test.ts) | Added | [1-95](../../../frontend/apps/ground-control/test/config/app-config.test.ts#L1) | +95 | −0 |
| [`frontend/apps/ground-control/test/flight/fakes.tsx`](../../../frontend/apps/ground-control/test/flight/fakes.tsx) | Added | [1-100](../../../frontend/apps/ground-control/test/flight/fakes.tsx#L1) | +100 | −0 |
| [`frontend/apps/ground-control/test/flight/flight-view.test.tsx`](../../../frontend/apps/ground-control/test/flight/flight-view.test.tsx) | Added | [1-148](../../../frontend/apps/ground-control/test/flight/flight-view.test.tsx#L1) | +148 | −0 |
| [`frontend/apps/ground-control/test/flight/squad-feed.test.ts`](../../../frontend/apps/ground-control/test/flight/squad-feed.test.ts) | Added | [1-103](../../../frontend/apps/ground-control/test/flight/squad-feed.test.ts#L1) | +103 | −0 |
| [`frontend/apps/ground-control/tsconfig.json`](../../../frontend/apps/ground-control/tsconfig.json) | Modified | [22](../../../frontend/apps/ground-control/tsconfig.json#L22), [24-25](../../../frontend/apps/ground-control/tsconfig.json#L24) | +3 | −1 |
| [`frontend/apps/ground-control/vite.config.ts`](../../../frontend/apps/ground-control/vite.config.ts) | Modified | [7](../../../frontend/apps/ground-control/vite.config.ts#L7), [11](../../../frontend/apps/ground-control/vite.config.ts#L11) | +2 | −1 |
| [`frontend/packages/i18n/src/messages/de.json`](../../../frontend/packages/i18n/src/messages/de.json) | Modified | [23-24](../../../frontend/packages/i18n/src/messages/de.json#L23) | +2 | −1 |
| [`frontend/packages/i18n/src/messages/en.json`](../../../frontend/packages/i18n/src/messages/en.json) | Modified | [23-24](../../../frontend/packages/i18n/src/messages/en.json#L23) | +2 | −1 |
| [`frontend/packages/i18n/src/messages/es.json`](../../../frontend/packages/i18n/src/messages/es.json) | Modified | [23-24](../../../frontend/packages/i18n/src/messages/es.json#L23) | +2 | −1 |
| [`frontend/packages/i18n/src/messages/fr.json`](../../../frontend/packages/i18n/src/messages/fr.json) | Modified | [23-24](../../../frontend/packages/i18n/src/messages/fr.json#L23) | +2 | −1 |
| [`frontend/packages/live/package.json`](../../../frontend/packages/live/package.json) | Modified | [11](../../../frontend/packages/live/package.json#L11), [14-16](../../../frontend/packages/live/package.json#L14) | +4 | −1 |
| [`frontend/packages/live/src/client/live-client.ts`](../../../frontend/packages/live/src/client/live-client.ts) | Added | [1-68](../../../frontend/packages/live/src/client/live-client.ts#L1) | +68 | −0 |
| [`frontend/packages/live/src/index.ts`](../../../frontend/packages/live/src/index.ts) | Modified | [2-14](../../../frontend/packages/live/src/index.ts#L2) | +13 | −0 |
| [`frontend/packages/live/src/latency/latency-histogram.ts`](../../../frontend/packages/live/src/latency/latency-histogram.ts) | Added | [1-37](../../../frontend/packages/live/src/latency/latency-histogram.ts#L1) | +37 | −0 |
| [`frontend/packages/live/src/latency/latency-reporter.ts`](../../../frontend/packages/live/src/latency/latency-reporter.ts) | Added | [1-113](../../../frontend/packages/live/src/latency/latency-reporter.ts#L1) | +113 | −0 |
| [`frontend/packages/live/src/latency/otlp-metrics-body.ts`](../../../frontend/packages/live/src/latency/otlp-metrics-body.ts) | Added | [1-64](../../../frontend/packages/live/src/latency/otlp-metrics-body.ts#L1) | +64 | −0 |
| [`frontend/packages/live/src/protocol/live-protocol-errors.ts`](../../../frontend/packages/live/src/protocol/live-protocol-errors.ts) | Added | [1-15](../../../frontend/packages/live/src/protocol/live-protocol-errors.ts#L1) | +15 | −0 |
| [`frontend/packages/live/src/protocol/squad-frame-decoder.ts`](../../../frontend/packages/live/src/protocol/squad-frame-decoder.ts) | Added | [1-80](../../../frontend/packages/live/src/protocol/squad-frame-decoder.ts#L1) | +80 | −0 |
| [`frontend/packages/live/src/protocol/topics.ts`](../../../frontend/packages/live/src/protocol/topics.ts) | Added | [1-20](../../../frontend/packages/live/src/protocol/topics.ts#L1) | +20 | −0 |
| [`frontend/packages/live/src/snapshot/squad-snapshot.ts`](../../../frontend/packages/live/src/snapshot/squad-snapshot.ts) | Added | [1-23](../../../frontend/packages/live/src/snapshot/squad-snapshot.ts#L1) | +23 | −0 |
| [`frontend/packages/live/src/snapshot/squad-store.ts`](../../../frontend/packages/live/src/snapshot/squad-store.ts) | Added | [1-125](../../../frontend/packages/live/src/snapshot/squad-store.ts#L1) | +125 | −0 |
| [`frontend/packages/live/src/worker/live-worker-core.ts`](../../../frontend/packages/live/src/worker/live-worker-core.ts) | Added | [1-125](../../../frontend/packages/live/src/worker/live-worker-core.ts#L1) | +125 | −0 |
| [`frontend/packages/live/src/worker/live-worker-messages.ts`](../../../frontend/packages/live/src/worker/live-worker-messages.ts) | Added | [1-10](../../../frontend/packages/live/src/worker/live-worker-messages.ts#L1) | +10 | −0 |
| [`frontend/packages/live/src/worker/live.worker.ts`](../../../frontend/packages/live/src/worker/live.worker.ts) | Added | [1-25](../../../frontend/packages/live/src/worker/live.worker.ts#L1) | +25 | −0 |
| [`frontend/packages/live/test/client/fake-worker.ts`](../../../frontend/packages/live/test/client/fake-worker.ts) | Added | [1-20](../../../frontend/packages/live/test/client/fake-worker.ts#L1) | +20 | −0 |
| [`frontend/packages/live/test/client/live-client.test.ts`](../../../frontend/packages/live/test/client/live-client.test.ts) | Added | [1-126](../../../frontend/packages/live/test/client/live-client.test.ts#L1) | +126 | −0 |
| [`frontend/packages/live/test/latency/latency-histogram.test.ts`](../../../frontend/packages/live/test/latency/latency-histogram.test.ts) | Added | [1-86](../../../frontend/packages/live/test/latency/latency-histogram.test.ts#L1) | +86 | −0 |
| [`frontend/packages/live/test/latency/latency-reporter.test.ts`](../../../frontend/packages/live/test/latency/latency-reporter.test.ts) | Added | [1-137](../../../frontend/packages/live/test/latency/latency-reporter.test.ts#L1) | +137 | −0 |
| [`frontend/packages/live/test/latency/otlp-metrics-body.test.ts`](../../../frontend/packages/live/test/latency/otlp-metrics-body.test.ts) | Added | [1-126](../../../frontend/packages/live/test/latency/otlp-metrics-body.test.ts#L1) | +126 | −0 |
| [`frontend/packages/live/test/protocol/frames.ts`](../../../frontend/packages/live/test/protocol/frames.ts) | Added | [1-46](../../../frontend/packages/live/test/protocol/frames.ts#L1) | +46 | −0 |
| [`frontend/packages/live/test/protocol/squad-frame-decoder.test.ts`](../../../frontend/packages/live/test/protocol/squad-frame-decoder.test.ts) | Added | [1-73](../../../frontend/packages/live/test/protocol/squad-frame-decoder.test.ts#L1) | +73 | −0 |
| [`frontend/packages/live/test/protocol/topics.test.ts`](../../../frontend/packages/live/test/protocol/topics.test.ts) | Added | [1-33](../../../frontend/packages/live/test/protocol/topics.test.ts#L1) | +33 | −0 |
| [`frontend/packages/live/test/snapshot/squad-store.test.ts`](../../../frontend/packages/live/test/snapshot/squad-store.test.ts) | Added | [1-176](../../../frontend/packages/live/test/snapshot/squad-store.test.ts#L1) | +176 | −0 |
| [`frontend/packages/live/test/worker/fake-clock.ts`](../../../frontend/packages/live/test/worker/fake-clock.ts) | Added | [1-43](../../../frontend/packages/live/test/worker/fake-clock.ts#L1) | +43 | −0 |
| [`frontend/packages/live/test/worker/fake-socket.ts`](../../../frontend/packages/live/test/worker/fake-socket.ts) | Added | [1-41](../../../frontend/packages/live/test/worker/fake-socket.ts#L1) | +41 | −0 |
| [`frontend/packages/live/test/worker/live-worker-core.test.ts`](../../../frontend/packages/live/test/worker/live-worker-core.test.ts) | Added | [1-227](../../../frontend/packages/live/test/worker/live-worker-core.test.ts#L1) | +227 | −0 |
| [`frontend/packages/live/tsconfig.json`](../../../frontend/packages/live/tsconfig.json) | Modified | [8-15](../../../frontend/packages/live/tsconfig.json#L8), [17-22](../../../frontend/packages/live/tsconfig.json#L17) | +14 | −2 |
| [`frontend/packages/maps/eslint.config.js`](../../../frontend/packages/maps/eslint.config.js) | Added | [1-11](../../../frontend/packages/maps/eslint.config.js#L1) | +11 | −0 |
| [`frontend/packages/maps/package.json`](../../../frontend/packages/maps/package.json) | Added | [1-44](../../../frontend/packages/maps/package.json#L1) | +44 | −0 |
| [`frontend/packages/maps/src/drones/drone-layer.ts`](../../../frontend/packages/maps/src/drones/drone-layer.ts) | Added | [1-60](../../../frontend/packages/maps/src/drones/drone-layer.ts#L1) | +60 | −0 |
| [`frontend/packages/maps/src/drones/fit-squad.ts`](../../../frontend/packages/maps/src/drones/fit-squad.ts) | Added | [1-26](../../../frontend/packages/maps/src/drones/fit-squad.ts#L1) | +26 | −0 |
| [`frontend/packages/maps/src/index.ts`](../../../frontend/packages/maps/src/index.ts) | Added | [1-9](../../../frontend/packages/maps/src/index.ts#L1) | +9 | −0 |
| [`frontend/packages/maps/src/map/SquadMap.tsx`](../../../frontend/packages/maps/src/map/SquadMap.tsx) | Added | [1-152](../../../frontend/packages/maps/src/map/SquadMap.tsx#L1) | +152 | −0 |
| [`frontend/packages/maps/src/palette/map-palette.ts`](../../../frontend/packages/maps/src/palette/map-palette.ts) | Added | [1-59](../../../frontend/packages/maps/src/palette/map-palette.ts#L1) | +59 | −0 |
| [`frontend/packages/maps/src/style/base-style.ts`](../../../frontend/packages/maps/src/style/base-style.ts) | Added | [1-68](../../../frontend/packages/maps/src/style/base-style.ts#L1) | +68 | −0 |
| [`frontend/packages/maps/src/style/pmtiles-protocol.ts`](../../../frontend/packages/maps/src/style/pmtiles-protocol.ts) | Added | [1-19](../../../frontend/packages/maps/src/style/pmtiles-protocol.ts#L1) | +19 | −0 |
| [`frontend/packages/maps/src/styles.css`](../../../frontend/packages/maps/src/styles.css) | Added | [1-6](../../../frontend/packages/maps/src/styles.css#L1) | +6 | −0 |
| [`frontend/packages/maps/test/drones/drone-layer.test.ts`](../../../frontend/packages/maps/test/drones/drone-layer.test.ts) | Added | [1-82](../../../frontend/packages/maps/test/drones/drone-layer.test.ts#L1) | +82 | −0 |
| [`frontend/packages/maps/test/drones/fit-squad.test.ts`](../../../frontend/packages/maps/test/drones/fit-squad.test.ts) | Added | [1-35](../../../frontend/packages/maps/test/drones/fit-squad.test.ts#L1) | +35 | −0 |
| [`frontend/packages/maps/test/map/squad-map.test.tsx`](../../../frontend/packages/maps/test/map/squad-map.test.tsx) | Added | [1-175](../../../frontend/packages/maps/test/map/squad-map.test.tsx#L1) | +175 | −0 |
| [`frontend/packages/maps/test/palette/map-palette.test.ts`](../../../frontend/packages/maps/test/palette/map-palette.test.ts) | Added | [1-56](../../../frontend/packages/maps/test/palette/map-palette.test.ts#L1) | +56 | −0 |
| [`frontend/packages/maps/test/style/base-style.test.ts`](../../../frontend/packages/maps/test/style/base-style.test.ts) | Added | [1-117](../../../frontend/packages/maps/test/style/base-style.test.ts#L1) | +117 | −0 |
| [`frontend/packages/maps/test/style/pmtiles-protocol.test.ts`](../../../frontend/packages/maps/test/style/pmtiles-protocol.test.ts) | Added | [1-44](../../../frontend/packages/maps/test/style/pmtiles-protocol.test.ts#L1) | +44 | −0 |
| [`frontend/packages/maps/tsconfig.json`](../../../frontend/packages/maps/tsconfig.json) | Added | [1-25](../../../frontend/packages/maps/tsconfig.json#L1) | +25 | −0 |
| [`frontend/packages/maps/vitest.config.ts`](../../../frontend/packages/maps/vitest.config.ts) | Added | [1-11](../../../frontend/packages/maps/vitest.config.ts#L1) | +11 | −0 |
| [`infra/charts/observability/dashboards/telemetry-latency.json`](../../../infra/charts/observability/dashboards/telemetry-latency.json) | Added | [1-86](../../../infra/charts/observability/dashboards/telemetry-latency.json#L1) | +86 | −0 |
| [`infra/compose/e2e.yaml`](../../../infra/compose/e2e.yaml) | Modified | [8-13](../../../infra/compose/e2e.yaml#L8) | +6 | −0 |
| [`pnpm-lock.yaml`](../../../pnpm-lock.yaml) | Modified | [345-350](../../../pnpm-lock.yaml#L345), [370-375](../../../pnpm-lock.yaml#L370), [379-381](../../../pnpm-lock.yaml#L379), [400-402](../../../pnpm-lock.yaml#L400), [424-426](../../../pnpm-lock.yaml#L424), [588-591](../../../pnpm-lock.yaml#L588), [615-684](../../../pnpm-lock.yaml#L615), [818-835](../../../pnpm-lock.yaml#L818), [961-1065](../../../pnpm-lock.yaml#L961), [1081-1089](../../../pnpm-lock.yaml#L1081), [1624-1626](../../../pnpm-lock.yaml#L1624), [1641-1646](../../../pnpm-lock.yaml#L1641), [1655-1657](../../../pnpm-lock.yaml#L1655), [1751-1753](../../../pnpm-lock.yaml#L1751), [1783-1786](../../../pnpm-lock.yaml#L1783), [1817-1819](../../../pnpm-lock.yaml#L1817), [1880-1885](../../../pnpm-lock.yaml#L1880), [1964-1966](../../../pnpm-lock.yaml#L1964), [1977-1979](../../../pnpm-lock.yaml#L1977), [1992-1994](../../../pnpm-lock.yaml#L1992), [2100-2108](../../../pnpm-lock.yaml#L2100), [2208-2211](../../../pnpm-lock.yaml#L2208), [2223-2225](../../../pnpm-lock.yaml#L2223), [2229-2231](../../../pnpm-lock.yaml#L2229), [2286-2289](../../../pnpm-lock.yaml#L2286), [2311-2313](../../../pnpm-lock.yaml#L2311), [2318-2320](../../../pnpm-lock.yaml#L2318), [2334-2336](../../../pnpm-lock.yaml#L2334), [2345-2347](../../../pnpm-lock.yaml#L2345), [2455-2457](../../../pnpm-lock.yaml#L2455), [2509-2511](../../../pnpm-lock.yaml#L2509), [2656-2667](../../../pnpm-lock.yaml#L2656), [2686-2703](../../../pnpm-lock.yaml#L2686), [2734-2777](../../../pnpm-lock.yaml#L2734), [2904-3044](../../../pnpm-lock.yaml#L2904), [3058-3065](../../../pnpm-lock.yaml#L3058), [3497-3498](../../../pnpm-lock.yaml#L3497), [3512-3517](../../../pnpm-lock.yaml#L3512), [3526-3529](../../../pnpm-lock.yaml#L3526), [3641-3642](../../../pnpm-lock.yaml#L3641), [3664-3670](../../../pnpm-lock.yaml#L3664), [3697-3700](../../../pnpm-lock.yaml#L3697), [3756-3759](../../../pnpm-lock.yaml#L3756), [3846-3847](../../../pnpm-lock.yaml#L3846), [3863-3864](../../../pnpm-lock.yaml#L3863), [3872-3873](../../../pnpm-lock.yaml#L3872), [3989-3994](../../../pnpm-lock.yaml#L3989), [4067-4093](../../../pnpm-lock.yaml#L4067), [4105-4106](../../../pnpm-lock.yaml#L4105), [4109-4110](../../../pnpm-lock.yaml#L4109), [4168-4171](../../../pnpm-lock.yaml#L4168), [4184-4187](../../../pnpm-lock.yaml#L4184), [4194-4195](../../../pnpm-lock.yaml#L4194), [4206-4207](../../../pnpm-lock.yaml#L4206), [4214-4215](../../../pnpm-lock.yaml#L4214), [4321-4322](../../../pnpm-lock.yaml#L4321), [4374-4375](../../../pnpm-lock.yaml#L4374), [4456-4457](../../../pnpm-lock.yaml#L4456), [4467-4471](../../../pnpm-lock.yaml#L4467) | +625 | −0 |
| [`tests/ci/e2e/test_compose_e2e.py`](../../../tests/ci/e2e/test_compose_e2e.py) | Modified | [25-27](../../../tests/ci/e2e/test_compose_e2e.py#L25), [88-94](../../../tests/ci/e2e/test_compose_e2e.py#L88) | +10 | −0 |
| [`tests/ci/images/test_images_workflow.py`](../../../tests/ci/images/test_images_workflow.py) | Modified | [206-221](../../../tests/ci/images/test_images_workflow.py#L206) | +16 | −0 |
| [`tests/conventions/mono_repo/frontend/test_frontend_workspace.py`](../../../tests/conventions/mono_repo/frontend/test_frontend_workspace.py) | Modified | [20-30](../../../tests/conventions/mono_repo/frontend/test_frontend_workspace.py#L20), [41-42](../../../tests/conventions/mono_repo/frontend/test_frontend_workspace.py#L41), [179-221](../../../tests/conventions/mono_repo/frontend/test_frontend_workspace.py#L179) | +56 | −0 |
| [`tests/infra/charts/observability/test_telemetry_latency_dashboard.py`](../../../tests/infra/charts/observability/test_telemetry_latency_dashboard.py) | Added | [1-132](../../../tests/infra/charts/observability/test_telemetry_latency_dashboard.py#L1) | +132 | −0 |
| **85 files** | | | **+5055** | **−41** |
<!-- /changes -->

- [`frontend/packages/live`](../../../frontend/packages/live/src/index.ts): the protocol, snapshot, worker, client and latency code (new files under `src/`), with their tests under `test/`.
- [`frontend/packages/maps`](../../../frontend/packages/maps/src/index.ts): new package with the base style, token palette, Drone layer and `SquadMap`.
- [`frontend/apps/ground-control`](../../../frontend/apps/ground-control/src/App.tsx): config, Flight view, squad feed, Dockerfile, nginx, Playwright e2e with a stand-in socket of 10 Drones ([`e2e/live-stand-in-server.ts`](../../../frontend/apps/ground-control/e2e/live-stand-in-server.ts)).
- [`frontend/packages/i18n/src/messages/en.json`](../../../frontend/packages/i18n/src/messages/en.json) and the fr, de and es files: the `flight.map.label` message.
- [`infra/charts/observability/dashboards/telemetry-latency.json`](../../../infra/charts/observability/dashboards/telemetry-latency.json): the Grafana dashboard.
- [`infra/compose/e2e.yaml`](../../../infra/compose/e2e.yaml), [`.github/workflows/images.yml`](../../../.github/workflows/images.yml), [`pnpm-lock.yaml`](../../../pnpm-lock.yaml): the service, the front-end e2e step and the new dependencies.
- [`docs/specs/screens/mockups/UC-025/a1.html`](../../../docs/specs/screens/mockups/UC-025/a1.html) and its two PNGs ([`a1.png`](../../../docs/specs/screens/UC-025/a1.png), [`a1.dark.png`](../../../docs/specs/screens/UC-025/a1.dark.png)): the mock-up updated to what the app shows (TKT-21).
- [`AGENT.md`](../../../AGENT.md): the new packages, the ground-control image and the dashboards folder.
- [`tests/ci/e2e/test_compose_e2e.py`](../../../tests/ci/e2e/test_compose_e2e.py), [`tests/ci/images/test_images_workflow.py`](../../../tests/ci/images/test_images_workflow.py), [`tests/conventions/mono_repo/frontend/test_frontend_workspace.py`](../../../tests/conventions/mono_repo/frontend/test_frontend_workspace.py), [`tests/infra/charts/observability/test_telemetry_latency_dashboard.py`](../../../tests/infra/charts/observability/test_telemetry_latency_dashboard.py): convention, compose, workflow and dashboard tests.

## 🧪 How to test it

```bash
pnpm --filter @swarm/live test
pnpm --filter @swarm/maps test
pnpm --filter @swarm/ground-control test
uv run pytest tests/infra/charts/observability tests/ci/e2e tests/ci/images -n 2
SWARM_IMAGE_TAG=<tag> pnpm --filter @swarm/ground-control run e2e
```

The first four run the unit and convention tests. The last runs the Playwright suite against the real image.

## 🔗 Evidence

- [Front-end tests](tests-evidences/test.txt), [lint](tests-evidences/lint.txt), [typecheck](tests-evidences/typecheck.txt): pass.
- [pytest](tests-evidences/pytest.txt) (4936 passed), [ruff check](tests-evidences/ruff-check.txt), [ruff format](tests-evidences/ruff-format.txt), [mypy](tests-evidences/mypy.txt): pass.
- [specs check](tests-evidences/specs-check.txt), [ticket refs](tests-evidences/ticket-refs.txt), [plan view](tests-evidences/plan-view.txt): clean.
- [pnpm install](tests-evidences/pnpm-install.txt), [swarm_core wheel](tests-evidences/swarm-core-wheel.txt), [swarm_core install](tests-evidences/swarm-core-install.txt): environment set-up.
- The Playwright e2e has no local run: it first runs in CI.

## 📝 Assumptions accepted

- Ground control connects to the live URL of `config.json`, by default the edge flight engine, which checks no Operator (05-api#live). How a browser sends its token to the gateway is left to the gateway.
- Criterion 1 is proven by Playwright on the real image with a stand-in socket of 10 moving Drones, because no chart deploys these services in the dev cell.
- Criterion 2 is an OTLP/HTTP export plus a dashboard, ahead of T0.17 which brings Grafana.
- Prometheus names follow the collector's default naming (`swarm_telemetry_drone_to_screen_milliseconds_bucket`, label `swarm_live_path`); T0.17 confirms them.
- Latency is draw time minus `t_us`, with NTP-synchronised clocks; negative samples are skipped.
- Full SquadFrames are merged by `drone_id`, ignoring frames whose `seq` is not newer.
- No PMTiles file is committed; `/tiles/` comes from a volume; no glyphs, sprite or labels; attribution reads "© OpenStreetMap contributors".
- Drones are dots in the entity colour, a lost Drone in the failure colour, with no labels.
- Hold the Squad and Abort stay shown and enabled as no-ops.
- No reconnection when the socket closes.
- The only new text is `flight.map.label`, in four languages (BR-017).
- The map loads lazily (`React.lazy`) for the 300 kB budget.
- The UC-025 A1 mock-up was updated, not captured, as T0.20 is not merged (TKT-21).
- The telemetry export uses no OpenTelemetry SDK; T0.17 may move it onto it.

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| [`docs/specs/screens/mockups/UC-025/a1.html`](../../../docs/specs/screens/mockups/UC-025/a1.html), [`docs/specs/screens/UC-025/a1.png`](../../../docs/specs/screens/UC-025/a1.png), [`docs/specs/screens/UC-025/a1.dark.png`](../../../docs/specs/screens/UC-025/a1.dark.png) | The Geofence zone, work-done zones and Pilot marker were removed, and the Mission name from the title. UC-025 step 2 specifies the Geofence and the work done. Put them back (and the Mission name, unless the visual identity decides otherwise), then run `specs.py render` again. |
| [`frontend/apps/ground-control/src/main.tsx`](../../../frontend/apps/ground-control/src/main.tsx), [`frontend/apps/ground-control/test/app.test.tsx`](../../../frontend/apps/ground-control/test/app.test.tsx) | When `config.json` is unreadable, only `console.error` runs and nothing renders, so Hold the Squad and Abort are missing. Render the frame with the defaults or an error state, and add a test (BR-023). |
| [`frontend/packages/live/src/client/live-client.ts`](../../../frontend/packages/live/src/client/live-client.ts), [`frontend/packages/live/test/client/live-client.test.ts`](../../../frontend/packages/live/test/client/live-client.test.ts) | A second `connect()` replaces the worker without terminating the first. Close the current worker first, and test it. |
| [`frontend/apps/ground-control/Dockerfile`](../../../frontend/apps/ground-control/Dockerfile) | The `config.json` fallback never runs, and its `liveUrl` differs from the default of `DEFAULT_APP_CONFIG`. Remove it. |
| [`frontend/apps/ground-control/src/flight/squad-feed.ts`](../../../frontend/apps/ground-control/src/flight/squad-feed.ts), [`frontend/apps/ground-control/test/flight/squad-feed.test.ts`](../../../frontend/apps/ground-control/test/flight/squad-feed.test.ts) | "Drone to screen" starts at `t_us`, stamped when the flight engine receives the datagram, so the Drone to flight engine leg is left out. Say so in the dashboard or metric description, and revisit when frames carry the Drone's own time. |
| [`frontend/apps/ground-control/e2e/flight-view.spec.ts`](../../../frontend/apps/ground-control/e2e/flight-view.spec.ts) | No Playwright run is in tests-evidences. Once the dev cell deploys Ground control, add a run against 10 Simulator Drones. |
| [`AGENT.md`](../../../AGENT.md) | It describes the dashboards folder as present, but the observability chart that provisions it arrives with T0.17. Say it waits for T0.17. |
