# 🎲 Risks

<!-- spec:nav-top -->
> [🏠 Index](../README.md) · [◀️ Hardware and partners](11-hardware-and-partners.md) · 📄 **Page 107 / 109** · [Traceability ▶️](13-traceability.md)
<!-- /spec:nav-top -->

**Status:** 🟢 Approved · **Sprints:** S01 to S52 · **Dates:** 4 Jan 2027 to 29 Dec 2028

> [!NOTE]
> The risks register of the roadmap: each risk with how likely and how serious it is, the signal that shows it coming, the response planned, and the phases it threatens. The person reviews it at the end of every sprint.

<!-- spec:summary -->
## <a id="summary"></a>📑 Summary

1. [🎲 How risks are rated](#scale)
2. [🎲 Register](#register)
3. [🗓️ Review](#review)
<!-- /spec:summary -->

## <a id="scale"></a>🎲 How risks are rated

| Rating | Likelihood | Impact |
| --- | --- | --- |
| 🟥 High | More likely than not within the phases it threatens | A milestone moves by more than a month, or safety is at stake |
| 🟨 Medium | Plausible | A milestone moves by up to a month, or a feature ships smaller |
| 🟩 Low | Unlikely | Absorbed within a sprint |

## <a id="register"></a>🎲 Register

| ID | Risk | Likelihood | Impact | Signal | Response | Phases |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="r-01"></a>R-01 | One person's review is the bottleneck: tickets wait, agents idle | 🟥 High | 🟥 High | More than 8 tickets waiting for review at the end of a sprint | Smaller tickets; agents write the tests and the review notes first; automated checks before review; cut scope of the phase rather than skip reviews | All |
| <a id="r-02"></a>R-02 | The Specific category Authorisation comes late | 🟨 Medium | 🟥 High | No answer 3 months after [🏛️ G-04](09-regulatory-track.md#g-04) | Inspection beta in the Open category on the partner Site, one real Drone at a time, the Squad in the Simulator; keep BVLOS for after M2 | P2, P3 |
| <a id="r-03"></a>R-03 | The safety tick misses its budget once the Rust core runs inside the Python flight engine | 🟨 Medium | 🟥 High | Benchmarks above 5 ms for 500 Drones in a pull request | Move more of the tick into Rust, cut allocations, run the tick in a dedicated thread; no real flight with a missed budget | P1, P6 |
| <a id="r-04"></a>R-04 | A vendor restricts SDK access (Parrot, DJI, Skydio) or changes terms | 🟨 Medium | 🟨 Medium | SDK licence refused or changed | MAVLink stays the core path; delay that vendor's adapter; tell partners which Drone models are supported | P3, P7 |
| <a id="r-05"></a>R-05 | The design-partner Operator is not signed, or leaves | 🟨 Medium | 🟥 High | No signature by S12; feedback stops for two sprints | Two candidates in talks from P1; the person flies the beta Missions with a partner Site directly | P1, P2 |
| <a id="r-06"></a>R-06 | OpenDroneMap quality or speed is not good enough for paying Clients | 🟨 Medium | 🟨 Medium | Orthomosaic of 1,000 images above 30 minutes, or artefacts the partner rejects | Tune and split large Sites; keep the processing interface open for a commercial engine later | P2 |
| <a id="r-07"></a>R-07 | Weather and seasons block campaigns (wind, rain, the Agriculture season) | 🟥 High | 🟨 Medium | Forecast beyond the Drone model limits in the campaign window | Two spare weeks per campaign; Simulator rehearsals; Agriculture beta on autumn seeding if spring is lost | P1, P2, P3, P4, P6 |
| <a id="r-08"></a>R-08 | The full scope does not fit 24 months for one person | 🟥 High | 🟥 High | Phase exit criteria not met by the phase's last sprint | Overlap phases with agents; protect M2, M3 and M7 first; move what slips in P6 and P7 to after general availability, decided at each phase end | All |
| <a id="r-09"></a>R-09 | LLM cost, latency or quality makes an agent unusable | 🟨 Medium | 🟨 Medium | Evaluations below threshold; cost per Mission above plan | Smaller models for tools, caching, provider switch (provider-agnostic); agents stay optional | P5 |
| <a id="r-10"></a>R-10 | Security incident: an Operator's data exposed, or an evidence signing key compromised | 🟩 Low | 🟥 High | Alerts from scans, unusual access in the evidence ledger | Row-level security tests in CI, key rotation procedure, incident runbook, penetration test before M2 and M7 | All |
| <a id="r-11"></a>R-11 | A Drone crashes or is lost in a test | 🟨 Medium | 🟨 Medium | Fail-safe drill failures; Link quality alerts | Simulator first, drills at each campaign start, spare Drones, insurance | All campaigns |
| <a id="r-12"></a>R-12 | A cell cannot ingest 100,000 frames per second into TimescaleDB | 🟨 Medium | 🟨 Medium | Nightly load test below target | Larger batches, more partitions, an extra writer; if still short, smaller cells (more of them) | P7 |
| <a id="r-13"></a>R-13 | Browser gaps block the full web Ground control (Window Management API, Gamepad API) | 🟨 Medium | 🟩 Low | A supported browser lacks the API | Fallback of one window per panel with `BroadcastChannel`; the desktop app covers the rest | P1 |
| <a id="r-14"></a>R-14 | A GDPR complaint about video of people | 🟩 Low | 🟨 Medium | A request or complaint from a person filmed | Retention of 90 days, face blurring for Client-visible video, data processing register ready by M2 | P3 |
| <a id="r-15"></a>R-15 | Rules change during the roadmap (EU U-space light, US rules for several Drones per Pilot) | 🟨 Medium | 🟨 Medium | Published proposals adopted | Authorisations are data in Swarm, not code; the regulatory track is reviewed each phase | All |
| <a id="r-16"></a>R-16 | Show permissions for an event are refused or late | 🟨 Medium | 🟨 Medium | No answer 8 weeks before the event | A show without spectators, filmed, for M6 | P6 |

## <a id="review"></a>🗓️ Review

- At the end of every sprint, the person updates likelihood and impact, and adds new risks with the next free ID.
- A risk that becomes an issue gets a ticket the same day; the phase page records the response taken.
- Risks closed stay in the table, marked closed, so their IDs are never reused.

<!-- spec:nav-bottom -->
---

> [🏠 Index](../README.md) · [◀️ Hardware and partners](11-hardware-and-partners.md) · 📄 **Page 107 / 109** · [Traceability ▶️](13-traceability.md)
<!-- /spec:nav-bottom -->
