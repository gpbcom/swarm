# 🤝 Hardware and partners

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ Flight test campaigns](10-flight-test-campaigns.md) · 📄 **Page 106 / 109** · [Risks ▶️](12-risks.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Sprints:** S01 to S52 · **Dates:** 4 Jan 2027 to 29 Dec 2028

> [!NOTE]
> What must be bought, rented or signed, and by when: the test fleet, Payloads, the edge box, a Dock, rented Drones for Agriculture and the show, the on-premises GPU server, and the partners who give Swarm real Sites, real Clients and its hosting.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🤝 Hardware](#hardware)
2. [🤝 Partners](#partners)
3. [📉 Ordering lead times](#budget)
<!-- /spec:summary -->

## <a id="hardware"></a>🤝 Hardware

| ID | Item | Sprint | Date needed | Bought or rented | For |
| --- | --- | --- | --- | --- | --- |
| <a id="h-01"></a>H-01 | 4 X500 Drones on PX4 with RTK GNSS, telemetry radios, spare Batteries | S06 | 26 Mar 2027 | Bought | P1 integration, [🛫 C-01](10-flight-test-campaigns.md#c-01), [🛫 C-02](10-flight-test-campaigns.md#c-02) |
| <a id="h-02"></a>H-02 | Payloads: 2 thermal cameras, 2 RGB cameras with gimbals | S08 | 23 Apr 2027 | Bought | Inspection, mixed Squads ([📏 BR-022](../functional/business-rules/BR-022-payload-compatibility.md)) |
| <a id="h-03"></a>H-03 | Rugged edge box (GPU-less, 16 cores) and a sunlight-readable laptop | S12 | 18 Jun 2027 | Bought | Edge appliance, field Ground control |
| <a id="h-04"></a>H-04 | 2 Parrot ANAFI USA | S24 | 3 Dec 2027 | Bought | Parrot adapter, Patrol ([🛫 C-03](10-flight-test-campaigns.md#c-03)) |
| <a id="h-05"></a>H-05 | One Dock (vendor chosen in S22 among Docks that work with the test fleet, delivered by S26) | S22 to S26 | 31 Dec 2027 | Bought | Patrol, Dock launches and recharges |
| <a id="h-06"></a>H-06 | Spray Drones with tanks and spreaders | S34 | 21 Apr 2028 | Rented per campaign | Agriculture ([🛫 C-04](10-flight-test-campaigns.md#c-04), [🛫 C-05](10-flight-test-campaigns.md#c-05)) |
| <a id="h-07"></a>H-07 | About 50 show Drones with lights and their radios | S45 | 22 Sep 2028 | Rented | Light show ([🛫 C-06](10-flight-test-campaigns.md#c-06)) |
| <a id="h-08"></a>H-08 | GPU server for the on-premises test install | S46 | 6 Oct 2028 | Bought or rented | On-premises bundle, open-weight model, processing |
| <a id="h-09"></a>H-09 | A DJI Drone | S47 | 20 Oct 2028 | Rented | The DJI adapter's compatibility flight ([📏 BR-015](../functional/business-rules/BR-015-approved-drone-models-only.md)) |
| <a id="h-10"></a>H-10 | A Skydio Drone | S47 | 20 Oct 2028 | Rented | The Skydio adapter's compatibility flight |

## <a id="partners"></a>🤝 Partners

| ID | Partner | Sprint | Date | Gives Swarm |
| --- | --- | --- | --- | --- |
| <a id="p-01"></a>P-01 | Design-partner Operator: a drone service company doing solar Inspection (sample name in the screens: Aerowing Services) | S12 | 18 Jun 2027 | Real Missions, feedback every sprint from P2, the Inspection beta (M2) |
| <a id="p-02"></a>P-02 | A solar farm Client of the design partner (sample: Les Vignes of Helio Energy) | S18 | 10 Sep 2027 | A real Site for [🛫 C-02](10-flight-test-campaigns.md#c-02) and real Deliverables |
| <a id="p-03"></a>P-03 | A Dock site: a warehouse that wants patrols (sample: Northgate warehouse) | S28 | 28 Jan 2028 | A Site for the Dock, Alarms from its security system, Site agents |
| <a id="p-04"></a>P-04 | A partner farm (sample: Domaine des Trois Chênes) | S30 | 25 Feb 2028 | Fields, Prescription maps, two seasons of campaigns |
| <a id="p-05"></a>P-05 | An event hosting the show (sample: Riverside Festival) | S44 | 8 Sep 2028 | An audience, a show slot, the event authorisation work |
| <a id="p-06"></a>P-06 | Hosting providers: self-hosted k3s for dev, staging and the beta cell from S01; an OVHcloud cell for the design partner from S24; OVHcloud and Scaleway production cells at target size from S46 | S01, S24, S46 | 4 Jan 2027, 3 Dec 2027, 25 Sep 2028 | The cells of [🚢 Deployment](../technical/09-deployment.md#providers) |
| <a id="p-07"></a>P-07 | A qualified timestamping authority (eIDAS) | S20 | 8 Oct 2027 | Default Anchoring of Evidence records |
| <a id="p-08"></a>P-08 | LLM provider accounts (Claude by default; others for the provider-agnostic tests) | S36 | 19 May 2028 | The AI agents of P5 |
| <a id="p-09"></a>P-09 | A blockchain aggregator account | S47 | 20 Oct 2028 | The blockchain Anchoring option of P7 |

## <a id="budget"></a>📉 Ordering lead times

- Order each item **two sprints before** the date needed; Drones and Docks can take longer, so H-01 is ordered in S02 and H-05 in S22.
- Rented Drones (H-06, H-07) are booked when the matching campaign date is fixed with the partner.
- A partner is "signed" when a written agreement covers Site access, data use (including for detection models, with consent) and insurance.

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ Flight test campaigns](10-flight-test-campaigns.md) · 📄 **Page 106 / 109** · [Risks ▶️](12-risks.md)
<!-- /spec:nav-bottom -->
