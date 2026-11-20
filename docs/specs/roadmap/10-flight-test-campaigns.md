# 🛫 Flight test campaigns

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ Regulatory track](09-regulatory-track.md) · 📄 **Page 116 / 120** · [Hardware and partners ▶️](11-hardware-and-partners.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Sprints:** S10 to S52 · **Dates:** 10 May 2027 to 29 Dec 2028

> [!NOTE]
> Every real flight of the roadmap: where it happens, with which Drones, under which rules, and what it proves. Everything else is proven in the Simulator; a campaign proves what only real Drones, real wind and real Links can.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🔭 Overview](#overview)
2. [🛫 Rules for every campaign](#rules)
3. [🧬 What each campaign covers](#coverage)
<!-- /spec:summary -->

## <a id="overview"></a>🔭 Overview

| ID | Sprints | Dates | Activity | Drones | Rules | Proves |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="c-01"></a>C-01 | S10 to S12 | 10 May to 18 Jun 2027 | Inspection of a test area | 4 X500 (PX4) with RTK, RGB and thermal Payloads ([🤝 H-01](11-hardware-and-partners.md#h-01), [🤝 H-02](11-hardware-and-partners.md#h-02)) | Open category, visual line of sight, model flying club field in France; one real Drone at a time | Milestone M1: the whole Squad pipeline, the safety loop, Fail-safes and manual control on a real Drone; the 4-Drone Squad in the Simulator with the same Mission |
| <a id="c-02"></a>C-02 | S20 to S24 | 27 Sep to 3 Dec 2027 | Inspection of a solar farm | The 4 X500 | Specific category Authorisation ([🏛️ G-05](09-regulatory-track.md#g-05)), partner Site ([🤝 P-02](11-hardware-and-partners.md#p-02)) | The first real Squad flights (4 Drones, one Pilot); milestone M2: Deliverables, Defects and a Scorecard from a real Client Site |
| <a id="c-03"></a>C-03 | S30 to S33 | 14 Feb to 7 Apr 2028 | Patrol of a warehouse | 2 Parrot ANAFI USA and one Dock ([🤝 H-04](11-hardware-and-partners.md#h-04), [🤝 H-05](11-hardware-and-partners.md#h-05)) | Specific category, Dock site of a partner ([🤝 P-03](11-hardware-and-partners.md#p-03)) | The Parrot adapter, Dock launches, Alarms, night video, Site agents |
| <a id="c-04"></a>C-04 | S34 to S38 | 10 Apr to 16 Jun 2028 | Agriculture, spring spraying | Rented spray Drones ([🤝 H-06](11-hardware-and-partners.md#h-06)) | Specific category and Agriculture rules ([🏛️ G-07](09-regulatory-track.md#g-07)), partner farm ([🤝 P-04](11-hardware-and-partners.md#p-04)) | Prescription maps, dose per zone, refills, the pump stopping at the Field boundary |
| <a id="c-05"></a>C-05 | S44 to S46 | 28 Aug to 6 Oct 2028 | Agriculture, autumn seeding (beta) | Rented spray Drones with spreaders | Same as C-04 | Milestone M4: a full season task with the partner farm |
| <a id="c-06"></a>C-06 | S46 to S48 | 25 Sep to 3 Nov 2028 | Light show | About 50 rented show Drones ([🤝 H-07](11-hardware-and-partners.md#h-07)) | Event authorisation ([🏛️ G-08](09-regulatory-track.md#g-08)), partner event ([🤝 P-05](11-hardware-and-partners.md#p-05)) | Milestone M6: a real show, the whole Squad stopping on a fault |
| <a id="c-07"></a>C-07 | S50 to S52 | 20 Nov to 29 Dec 2028 | Every Activity | The whole test fleet | As for each Activity | Milestone M7: the release candidate on real Drones before general availability |

## <a id="rules"></a>🛫 Rules for every campaign

1. **Simulator first:** every Mission of a campaign is flown in the Simulator the week before, with the same Squad, Geofence and weather limits; a failure there cancels the real flight.
2. **Pre-flight check:** every real flight passes the Pre-flight check of Swarm itself ([📏 BR-007](../functional/business-rules/BR-007-launch-only-after-a-passed-pre-flight-check.md)); from C-01 on, Swarm is its own flight tool.
3. **Fail-safe drills:** each campaign starts with a drill: Link cut, Geofence edge, Hold the Squad, abort, manual control; the results go to the campaign report.
4. **Evidence:** every Flight log of a campaign has its Evidence record; campaign reports are written from the Debrief ([📘 FS-022](../functional/features/FS-022-debrief-and-assessment.md)).
5. **Screens:** each campaign captures the real screens of the use cases it covers, in light and dark mode, to replace their ✏️ Mock-ups with 📸 Screenshots.
6. **Weather windows:** each campaign holds two spare weeks for weather ([🎲 R-07](12-risks.md#r-07)).
7. **Safety and insurance:** insurance for each campaign, a visual observer when the rules ask for one, a written emergency procedure on Site.

## <a id="coverage"></a>🧬 What each campaign covers

| Campaign | Use cases flown for real |
| --- | --- |
| C-01 | [🎬 UC-003](../functional/use-cases/UC-003-run-the-pre-flight-check-and-launch.md), [🎬 UC-004](../functional/use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md), [🎬 UC-005](../functional/use-cases/UC-005-lose-a-drone-in-flight.md), [🎬 UC-006](../functional/use-cases/UC-006-take-manual-control-or-abort.md), [🎬 UC-024](../functional/use-cases/UC-024-configure-each-drone-of-the-squad-on-the-site.md), [🎬 UC-025](../functional/use-cases/UC-025-monitor-a-mission-in-ground-control.md), [🎬 UC-026](../functional/use-cases/UC-026-handle-an-alert.md), [🎬 UC-030](../functional/use-cases/UC-030-focus-on-a-drone.md) |
| C-02 | [🎬 UC-009](../functional/use-cases/UC-009-process-flight-data-into-deliverables.md), [🎬 UC-011](../functional/use-cases/UC-011-follow-a-mission-and-download-its-deliverables.md), [🎬 UC-020](../functional/use-cases/UC-020-review-the-defects-of-an-inspection.md), [🎬 UC-027](../functional/use-cases/UC-027-debrief-a-mission.md), [🎬 UC-028](../functional/use-cases/UC-028-assess-a-mission-against-the-request.md) |
| C-03 | [🎬 UC-014](../functional/use-cases/UC-014-connect-a-new-drone-model.md) (Parrot), [🎬 UC-018](../functional/use-cases/UC-018-respond-to-a-site-alarm.md), [🎬 UC-019](../functional/use-cases/UC-019-request-a-patrol-on-demand.md) |
| C-04, C-05 | [🎬 UC-017](../functional/use-cases/UC-017-spray-a-field-with-refills.md) |
| C-06 | [🎬 UC-016](../functional/use-cases/UC-016-import-and-fly-a-light-show.md) |
| C-07 | One Mission per Activity, end to end, with the Co-pilot on ([🎬 UC-004](../functional/use-cases/UC-004-supervise-a-squad-and-approve-a-re-plan.md)) |

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ Regulatory track](09-regulatory-track.md) · 📄 **Page 116 / 120** · [Hardware and partners ▶️](11-hardware-and-partners.md)
<!-- /spec:nav-bottom -->
