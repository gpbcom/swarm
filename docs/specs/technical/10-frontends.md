# 🖥️ GUI and WebUI

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ Deployment](09-deployment.md) · 📄 **Page 94 / 109** · [Roadmap ▶️](../roadmap/README.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Updated:** 2026-11-18

> [!NOTE]
> One React and TypeScript codebase for the four parts of Swarm, a Tauri desktop shell, live data decoded off the main thread, GPU-rendered maps, low-latency video, and the visual identity turned into code. Decisions T32 to T35.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🗂️ Apps and shared packages](#apps)
2. [🖥️ Desktop shell and inputs](#desktop)
3. [📨 Live data in the browser](#live-data)
4. [🗺️ Maps and 3D](#maps)
5. [🎥 Video](#video)
6. [🎨 Design system](#design-system)
7. [⏱️ Front-end budgets](#performance)
8. [🔗 Features implemented](#features)
<!-- /spec:summary -->

## <a id="apps"></a>🗂️ Apps and shared packages

| App (`frontends/`) | Persona | Platforms |
| --- | --- | --- |
| `ground-control` | Pilot, Instructor | Desktop (Tauri), web browser, tablet, laptop |
| `mission-studio` | Mission planner | Desktop (Tauri), web browser |
| `back-office` | Fleet maintainer, Mission planner, Swarm administrator | Web browser |
| `client-portal` | Client, Site agent | Web browser, mobile (installable web app with push) |
| `desktop` | Shell for Ground control and Mission studio | Windows, macOS, Linux |

| Package (`packages/ts/`) | Holds |
| --- | --- |
| `ui` | Components on Radix primitives, styled only with the design tokens |
| `tokens` | CSS variables generated from [🎨 the visual identity](../visual-identity.md) |
| `live` | WebSocket client, MessagePack decoder in a Web Worker, WebRTC helpers |
| `api-client` | Generated REST client and types |
| `maps` | MapLibre and deck.gl layers: Drones, routes, coverage, Geofences, Defects, Choreographies |
| `i18n` | FormatJS messages in English, French, German and Spanish |

Stack: React 19, Vite, TanStack Query for server data, Zustand for UI state, Vitest and Playwright for tests.

## <a id="desktop"></a>🖥️ Desktop shell and inputs

- **Tauri 2** wraps Ground control and Mission studio: native windows on several screens (one Workspace screen per window), auto-update, local connection to the edge flight engine.
- **Gamepads and joysticks:** read natively through Rust (SDL2) in the desktop shell, through the Gamepad API in the browser.
- **Web browser is full too** (decision T35): manual control, gamepads and multi-screen Workspaces. Where the browser supports the Window Management API, Ground control places its windows on each screen; elsewhere, each panel opens in its own browser window, kept in sync through a `BroadcastChannel`.
- **Tablet:** everything except manual control and multi-screen Workspaces, as the functional specification decided ([📘 FS-020](../functional/features/FS-020-ground-control-workspace-and-configuration.md)).
- **Fixed inputs** on every platform that has them: H or both bumpers for Hold the Squad, Ctrl+Shift+A or Back and Start for abort, held 1 second ([📏 BR-023](../functional/business-rules/BR-023-fixed-safety-controls.md)).

## <a id="live-data"></a>📨 Live data in the browser

```text
WebSocket ──► Web Worker: MessagePack decode, delta merge, typed arrays (positions, states, battery)
                 │  transferable snapshot, at most 30 per second
                 ▼
            Main thread: deck.gl attributes updated in place, React only for panels and Alerts
```

- The main thread never decodes frames; React re-renders panels at most a few times per second, the map at the display rate.
- **Target:** 5,000 moving Drones at 60 frames per second on a recent laptop GPU; the Squad panel is virtualised.
- **Alerts and safety controls** are rendered outside the virtualised areas, so they are never delayed by heavy panels ([📏 BR-027](../functional/business-rules/BR-027-the-pilot-s-attention-is-preserved.md)).

## <a id="maps"></a>🗺️ Maps and 3D

- **MapLibre GL JS** with self-hosted vector tiles from OpenStreetMap (PMTiles files, also cached at the edge for offline use), and the Operator's licensed satellite layer.
- **deck.gl** GPU layers for Drones, routes, coverage, Geofences, Prescription map zones and Defects; binary attribute updates for moving Drones.
- **3D:** Choreographies and point clouds through deck.gl (3D Tiles); orthomosaics as Cloud Optimized GeoTIFF tiles.

## <a id="video"></a>🎥 Video

- **WebRTC** from the SFU, with simulcast: the Mosaic subscribes to the smallest layer of each Drone, the Focus view to the full one; streams beyond the Operator's maximum are not subscribed.
- **LL-HLS** in the Client portal, only when the Operator enabled it.

## <a id="design-system"></a>🎨 Design system

- Tokens in [🎨 the visual identity](../visual-identity.md) are generated into `packages/ts/tokens` (CSS variables with light and dark values), by the same pipeline that writes the mock-ups' `visual-identity.css`.
- Components in `packages/ts/ui` use the tokens only, like `components.css` does for the mock-ups; the frames of each part of Swarm are layout components.
- **Visual tests:** Playwright renders each screen of the use cases with the specification's sample data and compares it with the mock-up PNG, in light and dark mode; a large difference fails the build. Once a screen matches, its row becomes 📸 Screenshot in the use case.

## <a id="performance"></a>⏱️ Front-end budgets

| Measure | Budget |
| --- | --- |
| First load of an app (web, 4G) | < 2.5 s to interactive; JavaScript < 300 kB compressed for the first route |
| Map with 5,000 moving Drones | 60 frames per second on a recent laptop |
| Live frame to pixels | < 50 ms inside the browser |
| Switching to the Focus view | < 200 ms |

Routes and heavy libraries (3D, video) are split and loaded on demand; the apps are installable and cache their shell.

## <a id="features"></a>🔗 Features implemented

[📘 FS-001](../functional/features/FS-001-mission-design.md), [📘 FS-008](../functional/features/FS-008-client-portal.md), [📘 FS-020](../functional/features/FS-020-ground-control-workspace-and-configuration.md), [📘 FS-021](../functional/features/FS-021-ground-control-monitoring.md), [📘 FS-022](../functional/features/FS-022-debrief-and-assessment.md), and every screen of the use cases.

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ Deployment](09-deployment.md) · 📄 **Page 94 / 109** · [Roadmap ▶️](../roadmap/README.md)
<!-- /spec:nav-bottom -->
