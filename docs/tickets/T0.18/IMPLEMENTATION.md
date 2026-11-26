# T0.18: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🎯 Constraints

- One asyncio process on uvloop, one actor per Mission; one `SquadFrame` per tick to the local WebSocket and the leaf node ([TICKET.md](TICKET.md)).
- MAVLink is read through `swarm-core`, the Rust package ([TICKET.md](TICKET.md)).
- A slow client skips frames instead of growing a queue (acceptance criterion 2 of [TICKET.md](TICKET.md)).
- The Operator of a live connection comes only from the verified token, never from a message (the plan's brief of the gateway router, using T0.11's access service).
- The live path only reads MAVLink and sends no command ([📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md)).
- AGENT.md: one class per file, an `AsyncRunnable` yielding its status for long async work, a log in every branch, and no logger handed on ([AGENT.md](../../../AGENT.md)).
- The gateway and the flight engine must not import each other: shared code goes in `packages/` ([AGENT.md](../../../AGENT.md)).

## ⚖️ Choices at a glance

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | Where the live protocol lives | New shared package `swarm-live` | Duplicate it in each service | One more package to version |
| [D2](#d2) | What a slow client gets | One-slot mailbox that replaces the unread frame | A bounded queue | The client sees only the latest frame |
| [D3](#d3) | Where MAVLink is decoded | In Rust, GIL released | In Python | A Rust wheel in CI |
| [D4](#d4) | Tick scheduling | Monotonic slots, missed ones skipped | A fixed sleep of 50 ms | A skipped tick is lost, not caught up |
| [D5](#d5) | Order of publication | Local hub first, then the leaf node, whose failure is logged | Fail the tick when the leaf fails | A frame can reach the edge and not the cell |
| [D6](#d6) | Operator of a live socket | Verified token only | Operator in the subscribe message | The end-to-end test needs a seam |
| [D7](#d7) | NATS subscriptions in the gateway | One per subject, on the first watcher | One per client | Reference counting in the fan-out |
| [D8](#d8) | Client message format | MessagePack | JSON | The specification's JSON is read as notation |
| [D9](#d9) | CI for the live path | Pinned nats-server and wheel in the workflow | Skip those tests in CI | Longer service jobs |

## <a id="d1"></a>D1: Where the live protocol lives

**Chosen:** package `swarm-live` · **Where:** [`pyproject.toml`](https://github.com/gpbcom/swarm/blob/a2e43f7e74d65cc12a43507ec33f673fd2bc62e3/packages/python/swarm-live/pyproject.toml) · **Source:** read from the diff and the plan

| Option | For | Against |
| --- | --- | --- |
| ✅ Shared package | The gateway and the flight engine speak the same protocol; AGENT.md forbids a service importing another | One more workspace member |
| Copy in each service | No new package | Two codecs that can drift; breaks the single-source idea of the shared models |

**Trade-off:** a new package for one source of truth.

**Revisit when:** the two sides need different protocols.

## <a id="d2"></a>D2: What a slow client gets

**Chosen:** one-slot mailbox · **Where:** [`live_mailbox.py:40`](../../../backend/swarm-service/src/swarm_service/shared/live/hub/live_mailbox.py#L40) · **Source:** the technical page, "a slow client skips intermediate frames"

| Option | For | Against |
| --- | --- | --- |
| ✅ One slot | Memory is constant; the criterion is met by construction | Older frames are lost |
| Bounded queue | Keeps a short history | Still grows to its bound, and the client reads stale frames first |

**Trade-off:** latest frame only, which is what a map needs.

**Revisit when:** a topic needs every frame, such as alerts (out of this ticket).

## <a id="d3"></a>D3: Where MAVLink is decoded

**Chosen:** Rust in `swarm-core-mavlink`, exposed with the GIL released · **Where:** [`frame.rs:101`](../../../rust/swarm-core/mavlink/src/frame.rs#L101), [`lib.rs:111`](../../../rust/swarm-core/python/src/lib.rs#L111) · **Source:** [TICKET.md](TICKET.md), read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ Rust | The ticket asks for it; the engine's event loop is not blocked while decoding | CI must build the wheel ([`python.yml`](../../../.github/workflows/python.yml#L49)) |
| Python | No wheel | Contradicts the ticket; decoding runs on the event loop |

**Trade-off:** a build step in CI. No timing was measured by this ticket.

**Revisit when:** T0.17 measures the Telemetry path.

## <a id="d4"></a>D4: Tick scheduling

**Chosen:** monotonic slots · **Where:** [`mission_actor.py:114`](../../../backend/swarm-service/src/swarm_service/flight/missions/mission_actor.py#L114) · **Source:** read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ Slots from a start time, late ones skipped | No drift; no burst after a stall | A skipped tick is not replayed |
| Sleep 50 ms after each tick | Simpler | Drifts by the work time of every tick |

**Trade-off:** frames are dropped under load rather than bursting.

**Revisit when:** a consumer needs every tick.

## <a id="d5"></a>D5: Order of publication

**Chosen:** hub first, leaf second, leaf failure logged · **Where:** [`mission_actor.py:90`](../../../backend/swarm-service/src/swarm_service/flight/missions/mission_actor.py#L90) · **Source:** read from the diff, review note

| Option | For | Against |
| --- | --- | --- |
| ✅ Local first, leaf failure logged | The edge screen keeps working when the leaf node is down | The cell can miss frames the edge saw |
| Fail the tick | Both sides always agree | An edge outage would stop local display |

**Trade-off:** edge availability over agreement.

**Revisit when:** an open point: no source states the required behaviour on a leaf outage.

## <a id="d6"></a>D6: Operator of a live socket

**Chosen:** verified token only · **Where:** [`live_operator.py:71`](../../../backend/swarm-api/src/swarm_api/dependencies/live_operator.py#L71) · **Source:** plan, reviewer

| Option | For | Against |
| --- | --- | --- |
| ✅ Token | Isolation cannot be forged by a message | [`tests/swarm_flight_engine/main/conftest.py`](../../../tests/swarm_flight_engine/main/conftest.py#L121) overrides the dependency, so the end-to-end test proves the fan-out, not the token |
| Operator in the message | Easy to test | A client could name another Operator |

**Trade-off:** token checks are proven by unit tests, not end to end.

**Revisit when:** a test environment can issue real tokens.

## <a id="d7"></a>D7: NATS subscriptions in the gateway

**Chosen:** one per subject on the first watcher · **Where:** [`live_fan_out.py:95`](../../../backend/swarm-service/src/swarm_service/gateway/live/live_fan_out.py#L95) · **Source:** the technical page "subscribes once per Mission"

| Option | For | Against |
| --- | --- | --- |
| ✅ Shared subscription | NATS load does not grow with clients | The last-watcher leave must be right (see follow-up on `close`) |
| One per client | Simple | Load grows with clients |

**Trade-off:** reference counting for a flat NATS load.

**Revisit when:** consistent hashing across gateways arrives.

## <a id="d8"></a>D8: Client message format

**Chosen:** MessagePack · **Where:** [`live_codec.py:118`](../../../backend/swarm-service/src/swarm_service/shared/live/live_codec.py#L118) · **Source:** [PLAN.md](PLAN.md) (decision T23)

| Option | For | Against |
| --- | --- | --- |
| ✅ MessagePack | Same as frames; decision T23 | The specification shows JSON |
| JSON | Matches the specification text | Two formats on one socket |

**Trade-off:** the JSON in the specification is read as notation.

**Revisit when:** the specification is clarified.

## <a id="d9"></a>D9: CI for the live path

**Chosen:** install the pinned nats-server and the wheel · **Where:** [`python.yml:38`](../../../.github/workflows/python.yml#L38) · **Source:** read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ Install them | The live tests run in CI instead of skipping | Longer jobs; the wheel step runs only when the service imports `swarm_core` |
| Let them skip | Faster | Criterion 1 would never be checked in CI |

**Trade-off:** CI time for real evidence. The reviewer notes the local pytest report does not show whether `tests/live` ran.

**Revisit when:** CI time becomes a problem.

## 📝 Assumptions behind the choices

- BR-014 holds because the path only reads MAVLink: supports [D3](#d3) and [D5](#d5).
- No latency is asserted, as the roadmap gives no figure: supports [D3](#d3) and [D4](#d4).
