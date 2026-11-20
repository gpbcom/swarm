# T0.19: Simulated Squad on the Ground control map

**Status:** 🟡 Planned

## Roadmap

- **Ticket:** [T0.19](../../specs/roadmap/01-p0-foundations.md#s04) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Phase:** [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md)
- **Sprint:** [S04](../../specs/roadmap/01-p0-foundations.md#s04), 15 to 26 February 2027: first use case and M0
- **Epic:** [E0.6](../../specs/roadmap/01-p0-foundations.md#epics): Simulator and live path. [📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md) and the M0 proof.

## What it delivers

- The first screen of `ground-control` in the browser, in `frontends/ground-control`, as [🖥️ GUI and WebUI: apps and shared packages](../../specs/technical/10-frontends.md#apps).
- MapLibre with self-hosted PMTiles, in `packages/ts/maps`, as [🗺️ GUI and WebUI: maps and 3D](../../specs/technical/10-frontends.md#maps).
- A deck.gl layer of Drones, in `packages/ts/maps`, with binary attribute updates for moving Drones, as [🗺️ GUI and WebUI: maps and 3D](../../specs/technical/10-frontends.md#maps).
- The live client in `packages/ts/live`: MessagePack decoded in a Web Worker into typed arrays, as [📨 GUI and WebUI: live data in the browser](../../specs/technical/10-frontends.md#live-data) and [📨 API layer: live data over WebSocket](../../specs/technical/05-api.md#live).
- The frame of Ground control with ✋ Hold the Squad and 🛑 Abort shown but not yet wired, as [🎨 GUI and WebUI: design system](../../specs/technical/10-frontends.md#design-system) and [📏 BR-023](../../specs/functional/business-rules/BR-023-fixed-safety-controls.md).
- The measure of the Telemetry latency from Drone to screen through the cell, shown in Grafana, as [🩺 Observability: signals](../../specs/technical/08-observability.md#signals).

## Features, use cases and business rules

- [📏 BR-014: Simulation isolation](../../specs/functional/business-rules/BR-014-simulation-isolation.md)
- [📏 BR-023: Fixed safety controls](../../specs/functional/business-rules/BR-023-fixed-safety-controls.md)
- [🎬 UC-025: Monitor a Mission in Ground control](../../specs/functional/use-cases/UC-025-monitor-a-mission-in-ground-control.md)

## Technical pages it builds on

- [🗂️ GUI and WebUI: apps and shared packages](../../specs/technical/10-frontends.md#apps): `ground-control` is the app of the Pilot and Instructor; `live` holds the "WebSocket client, MessagePack decoder in a Web Worker" and `maps` the "MapLibre and deck.gl layers".
- [📨 GUI and WebUI: live data in the browser](../../specs/technical/10-frontends.md#live-data): "The main thread never decodes frames"; the Web Worker does the MessagePack decode and typed arrays, and deck.gl attributes are updated in place.
- [🗺️ GUI and WebUI: maps and 3D](../../specs/technical/10-frontends.md#maps): "MapLibre GL JS with self-hosted vector tiles from OpenStreetMap (PMTiles files ...)" and "deck.gl GPU layers for Drones".
- [🎨 GUI and WebUI: design system](../../specs/technical/10-frontends.md#design-system): the frame of each part of Swarm is made of layout components that use the tokens only.
- [⏱️ GUI and WebUI: front-end budgets](../../specs/technical/10-frontends.md#performance): "Live frame to pixels < 50 ms inside the browser".
- [📨 API layer: live data over WebSocket](../../specs/technical/05-api.md#live): one socket per client, subscriptions per Mission topic, frames in MessagePack.
- [🩺 Observability: signals](../../specs/technical/08-observability.md#signals): the signals of the dev cell that Grafana shows.

## Screens touched

- [🖼️ UC-025 A1](../../specs/functional/use-cases/UC-025-monitor-a-mission-in-ground-control.md#screen-a1): the first screen of Ground control, with the map and the Squad.

## Budgets touched

- [⏱️ Telemetry, Drone to Pilot's screen](../../specs/technical/07-scalability.md#budgets): p95 < 150 ms at the edge, < 400 ms through the cell.

## Acceptance criteria

The "done when" of the roadmap row. The roadmap names no Given, when, then criterion of a feature for this ticket.

1. **Given** 10 simulated Drones flying in the dev cell, **when** Ground control is open in a browser, **then** the 10 Drones move on the map. ([📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md), [🎬 UC-025](../../specs/functional/use-cases/UC-025-monitor-a-mission-in-ground-control.md))
2. **Given** simulated Drones flying through the cell, **when** the Telemetry latency from Drone to screen is measured, **then** it is shown in Grafana. ([📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md), [🎬 UC-025](../../specs/functional/use-cases/UC-025-monitor-a-mission-in-ground-control.md))
3. **Given** the frame of Ground control, **when** it is shown, **then** ✋ Hold the Squad and 🛑 Abort are visible in the title bar and not yet wired. ([📏 BR-023](../../specs/functional/business-rules/BR-023-fixed-safety-controls.md), [🎬 UC-025](../../specs/functional/use-cases/UC-025-monitor-a-mission-in-ground-control.md))

## Out of scope

- The flight engine and the gateway `/v1/live` WebSocket, see [T0.18](../../specs/roadmap/01-p0-foundations.md#s04).
- The Simulator and its synthetic Drones, see [T0.13](../../specs/roadmap/01-p0-foundations.md#s03).
- Wiring ✋ Hold the Squad and 🛑 Abort, which the roadmap row says are shown but not yet wired.
- Screenshot pipeline and visual tests, see [T0.20](../../specs/roadmap/01-p0-foundations.md#s04).

## Assumptions

- The roadmap row names no feature, use case or business rule. [📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md) is linked because the epic E0.6 names it, [📏 BR-023](../../specs/functional/business-rules/BR-023-fixed-safety-controls.md) because the technical page ties Hold the Squad and abort to fixed controls, and [🎬 UC-025](../../specs/functional/use-cases/UC-025-monitor-a-mission-in-ground-control.md) because it is the use case of the Ground control Flight view.
- The row names no screen. The ticket is a front-end ticket, so it links the A1 screen of UC-025 as the most conservative match, to be captured as 📸 Screenshot (TKT-21).
- The row names no budget row. The Telemetry budget is linked because the row measures that latency.
- The row gives no latency value for the done-when, so the criteria assert none beyond the budget row.
