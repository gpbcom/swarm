# T0.19: Review note

**Verdict:** ✅ Approved · **Branch:** `feature/tickets`

## What changed

- Ground control now opens on a Flight view. A MapLibre map on self-hosted PMTiles is loaded on demand, and a deck.gl layer draws the Squad from binary typed arrays, coloured only from the tokens.
- `@swarm/live` gains a Web Worker that owns the socket, sends the `mission/<id>/squad` subscription, decodes MessagePack, merges by Drone and posts transferable snapshots at most 30 times a second. The main thread never decodes a frame.
- The latency of what is drawn (frame time to draw time, and worker receipt to draw time) is recorded in histograms. When `metricsUrl` is set, they are exported as OTLP/HTTP JSON. A Grafana dashboard shows the p95 against the 150, 400 and 50 ms budgets.
- Ground control gets its own image (unprivileged nginx, runtime `config.json`, `/tiles/` from a volume), a compose service on port 8180, and its Playwright suite in the images.yml e2e job.
- ✋ Hold the Squad and 🛑 Abort stay visible in the title bar and are still no-ops.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. Given 10 simulated Drones flying in the dev cell, when Ground control is open in a browser, then the 10 Drones move on the map | `flight view › shows the number of Drones of the latest snapshot`, `SquadMap › sets the Drone layer at most once per animation frame` (tests-evidences/test.txt). The Playwright tests `shows the ten Drones of the Squad on the map` and `moves the Drones: two screenshots one second apart differ` first run in CI's images.yml, against a stand-in socket | ✅ Pass (unit). The e2e has not run locally, and the dev cell is not deployed yet (assumption) |
| 2. Given simulated Drones flying through the cell, when the Telemetry latency from Drone to screen is measured, then it is shown in Grafana | `flight view › records one drone to screen sample per Drone drawn and reports it`, the latency tests of @swarm/live (test.txt), `TestTelemetryLatencyDashboard` (pytest.txt) | ✅ Pass for the measure, the export and the dashboard. Grafana itself arrives with T0.17 (assumption) |
| 3. Given the frame of Ground control, when it is shown, then ✋ Hold the Squad and 🛑 Abort are visible in the title bar and not yet wired | `shows Hold the Squad and Abort in the title bar`, `does nothing yet when Hold the Squad and Abort are clicked` (test.txt). Playwright: `sends nothing but the subscription when Hold and Abort are clicked` | ✅ Pass |

All checks pass in the clean tree: pnpm install with the T0.19 lock, lint, typecheck, test, ruff, mypy, pytest (4936 passed) and specs.py check.

## Look at first

- **Where the live socket points (Operator isolation):** Ground control connects to `config.liveUrl`, by default the edge flight engine, which checks no Operator. This follows 05-api#live ("at the edge Ground control connects straight to the flight engine"). How a browser carries its token to the gateway is still open. Read `frontend/apps/ground-control/src/config/app-config.ts`, `frontend/apps/ground-control/public/config.json` and `frontend/packages/live/src/worker/live-worker-core.ts` line by line.
- **Simulator isolation:** nothing here talks to the Simulator. Criterion 1 is proven against a stand-in socket (`frontend/apps/ground-control/e2e/live-stand-in-server.ts`), not against the Simulator through the cell.
- **The draw path at display rate (budget < 50 ms frame to pixels):** the worker throttles snapshots (`frontend/packages/live/src/worker/live-worker-core.ts`, `frontend/packages/live/src/snapshot/squad-store.ts`). SquadMap redraws at most once per animation frame, with no React state per frame (`frontend/packages/maps/src/map/SquadMap.tsx`, `frontend/packages/maps/src/drones/drone-layer.ts`, `frontend/apps/ground-control/src/flight/squad-feed.ts`).
- **The latency measure and the dashboard names:** `frontend/packages/live/src/latency/otlp-metrics-body.ts` and `infra/charts/observability/dashboards/telemetry-latency.json`. The Prometheus names assume the collector's default translation, and T0.17 confirms them.
- **The UC-025 A1 mock-up:** the Geofence and the work-done zones were removed, against UC-025 step 2 (see the follow-ups). Read `docs/specs/screens/mockups/UC-025/a1.html`.

## Assumptions accepted

- The default live URL is the edge flight engine, with no token: accepted, because the spec routes Ground control straight to the flight engine at the edge.
- Criterion 1 is proven by Playwright on the real image with a stand-in socket of 10 Drones: accepted, because no chart deploys these services in the dev cell yet.
- Criterion 2 ships as an OTLP export plus a dashboard ahead of Grafana: accepted, because T0.17 depends on T0.19 in the ticket graph.
- The latency uses t_us and NTP-synchronised clocks, and skips negative samples: accepted, with a follow-up.
- Full SquadFrames are merged by drone_id and seq: accepted, consistent with live_codec.py.
- No PMTiles file is committed, and the style needs nothing from a third party: accepted.
- Dots in the entity colour, Lost in the failure colour, no labels: accepted.
- Hold and Abort are shown but not wired, and there is no reconnection policy: accepted, as the roadmap row and the specifications say.
- The map is loaded lazily for the 300 kB budget, and the only new on-screen text is `flight.map.label` in four languages: accepted.
- The mock-up is updated instead of captured while T0.20 is not merged: accepted under TKT-21.

## Follow-ups

- Put the Geofence and work-done zones, and the Mission name, back in the UC-025 A1 mock-up, then render again (K23).
- When `config.json` fails to load, still render the frame with Hold the Squad and Abort (BR-023) (K22).
- `LiveClient.connect()` called twice leaks the first worker (K19).
- Remove the Dockerfile's `config.json` fallback, which never runs and has a different default URL (K17).
- Note that the measured latency starts when the flight engine receives the datagram, not at the Drone (K22).
- Run criterion 1 against 10 Simulator Drones in the dev cell once Ground control is deployed there, and keep a Playwright run in tests-evidences (K06).
- In AGENT.md, say that the dashboards folder waits for T0.17's observability chart (K18).
