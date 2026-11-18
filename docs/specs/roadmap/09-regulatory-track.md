# 🏛️ Regulatory track

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ P7: Scale and reach](08-p7-scale-and-reach.md) · 📄 **Page 104 / 108** · [Flight test campaigns ▶️](10-flight-test-campaigns.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Sprints:** S02 to S52 · **Dates:** 18 Jan 2027 to 29 Dec 2028

> [!NOTE]
> Every regulatory step the roadmap depends on, with the sprint it must be done by: the person's Pilot qualifications, the Operator's registration and Specific category Authorisation, airspace checks per Site, Agriculture and event rules, and the US study before the US cell.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🔭 Overview](#overview)
2. [🏛️ Steps](#steps)
3. [⛓️ How the track drives the roadmap](#dependencies)
4. [🎲 Risks](#risks)
<!-- /spec:summary -->

## <a id="overview"></a>🔭 Overview

Swarm is built and tested in France, under EU rules (EASA), by one person who is also the [👤 Pilot](../glossary.md#per-pilot) of the test flights. Until the Specific category [🗃️ Authorisation](../glossary.md#ent-authorisation) is granted, real flights stay in the Open category: visual line of sight, Drones within its weight classes, one Pilot per Drone flown at a time by hand or with Squads kept within what the category allows. The Specific category Authorisation, applied for through SORA 2.5, is what lets one Pilot supervise a Squad, fly over a partner's Site and later fly [🔤 BVLOS](../glossary.md#term-bvlos).

Swarm itself records every step below in the Back office ([📘 FS-006](../functional/features/FS-006-authorisations-and-compliance.md)) as soon as P1 delivers it, so the roadmap is also its first real data.

## <a id="steps"></a>🏛️ Steps

| ID | Step | Sprint | Date due | Needed for |
| --- | --- | --- | --- | --- |
| <a id="g-01"></a>G-01 | Register the person's company as an operator with the French civil aviation authority, get the operator number | S02 | 29 Jan 2027 | Any real flight; Drone registration labels |
| <a id="g-02"></a>G-02 | Pass the EU A2 certificate of competency (online exam and self-practical training) | S06 | 26 Mar 2027 | Open category flights close to people, first campaign [🛫 C-01](10-flight-test-campaigns.md#c-01) |
| <a id="g-03"></a>G-03 | Complete the STS theoretical exam and practical training (STS-01 and STS-02 scenarios) | S08 to S10 | 21 May 2027 | The SORA application and Specific category flights |
| <a id="g-04"></a>G-04 | Submit the SORA 2.5 application: concept of operations for Squads with one Pilot, ground and air risk, mitigations (Geofence on board, edge safety loop, Fail-safes, landing reserve, evidence ledger) | S09 | 7 May 2027 | [🏛️ G-05](#g-05) |
| <a id="g-05"></a>G-05 | Specific category Authorisation granted: Inspection with Squads up to the Pilot ratio it grants, in visual line of sight first, extended to BVLOS on request | S20 | 8 Oct 2027 | Campaign [🛫 C-02](10-flight-test-campaigns.md#c-02), the Inspection beta (M2) |
| <a id="g-06"></a>G-06 | Airspace and U-space checks for each partner Site: restricted areas, local authorisations, U-space service where it exists | Before each campaign | 2 sprints before | Every campaign from C-02 on |
| <a id="g-07"></a>G-07 | Agriculture: rules for applying products by Drone on the partner farm, applicator licence of the person or partner (recorded in Swarm; a missing or expired licence fails the Pre-flight check), Prescription map formats agreed with the farm | S30 | 25 Feb 2028 | Campaigns [🛫 C-04](10-flight-test-campaigns.md#c-04) and [🛫 C-05](10-flight-test-campaigns.md#c-05) |
| <a id="g-08"></a>G-08 | Light show: event authorisation, safety perimeter with the event organiser and the prefecture, insurance for flights above an audience | S44 | 8 Sep 2028 | Campaign [🛫 C-06](10-flight-test-campaigns.md#c-06), milestone M6 |
| <a id="g-09"></a>G-09 | US rules study for the US cell: Part 107, waivers and exemptions for one Pilot and several Drones, Part 137 for Agriculture, LAANC | S47 | 20 Oct 2028 | US self-hosted cell in P7; selling to US Operators after general availability |

## <a id="dependencies"></a>⛓️ How the track drives the roadmap

- **P1** flies in the Open category only: one real Drone at a time through the whole Squad pipeline, while the 4-Drone Squad is proven in the Simulator (M1).
- **The first real Squad flight** (4 Drones, one Pilot) waits for [🏛️ G-05](#g-05) and happens in [🛫 C-02](10-flight-test-campaigns.md#c-02).
- **P2** depends on [🏛️ G-05](#g-05): if it is late, the Inspection beta flies in the Open category on the partner's Site, smaller and in visual line of sight ([🎲 R-02](12-risks.md#r-02)).
- **P4** cannot spray before [🏛️ G-07](#g-07); seeding cover crops (no product) is the fallback for the autumn beta.
- **P6** cannot fly above an audience before [🏛️ G-08](#g-08); the fallback is a show without spectators, filmed.
- **P7** opens the US cell for testing only; US Operators fly under their own Authorisations, which Swarm records like EU ones.

## <a id="risks"></a>🎲 Risks

[🎲 R-02](12-risks.md#r-02) (Authorisation late), [🎲 R-15](12-risks.md#r-15) (rules change, such as the proposed U-space light), [🎲 R-16](12-risks.md#r-16) (show permissions).

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ P7: Scale and reach](08-p7-scale-and-reach.md) · 📄 **Page 104 / 108** · [Flight test campaigns ▶️](10-flight-test-campaigns.md)
<!-- /spec:nav-bottom -->
