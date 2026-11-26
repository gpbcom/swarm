# T0.18: Review note

**Verdict:** ✅ Approved · **Branch:** `feature/tickets` (checked and shipped with T0.11 and T0.15)

## What changed

- MAVLink 2 frames are decoded in Rust. `swarm-core-mavlink` provides `decode` and `LatestFrames`, and the `swarm_core` wheel exposes them with the GIL released. Malformed bytes never panic and are counted as rejected.
- New service `services/flight-engine`: one uvloop process with one `MissionActor` per Mission. On a monotonic 50 ms schedule, each actor builds one `SquadFrame` and publishes it first to the local hub (edge `/v1/live`), then to the leaf node on `op.<operator>.mission.<mission>.squad`. A failure on the leaf side is logged and the ticks go on.
- New shared package `swarm-live`: the one-slot mailbox, the hub, the MessagePack codec and the `LiveSession` AsyncRunnable. The gateway and the flight engine speak the same protocol. `LiveSubscription` is a shared model, and the generated schema, Rust and TypeScript files are regenerated.
- Gateway `/v1/live`: the Operator comes only from the verified token (`LiveOperator`, using T0.11's access service), and the code is 1008 otherwise. NATS is subscribed once per Operator and Mission subject, on the first watcher, and unsubscribed on the last.
- CI: the services job installs the pinned nats-server and builds the wheel for services that import `swarm_core`. The repository job builds the wheel for `tests/live`.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. Given 10 simulated Drones flying in the cell, when a WebSocket client subscribes to their Mission on `/v1/live`, then the client receives their frames through the cell | `tests/live/test_live_path.py::TestLivePath::test_a_client_of_the_gateway_receives_the_squad_through_the_cell` (leaf node, then cell, then gateway), plus `test_a_client_of_the_flight_engine_receives_the_squad_locally`; `tests-evidences/pytest.txt` (4548 passed, 79 skipped). The report does not say whether this test ran or skipped: see follow-ups | ✅ Pass |
| 2. Given a slow WebSocket client, when frames arrive faster than it reads, then it skips frames instead of growing a queue | `packages/python/swarm-live/tests/api/live/test_live_session.py::test_a_slow_client_skips_frames_and_ends_on_the_latest`, `test_live_mailbox.py::test_fifty_puts_never_leave_more_than_one_frame`, `services/gateway/tests/service/live/test_live_fan_out.py::test_a_client_that_does_not_take_its_mailbox_holds_only_the_last_frame` | ✅ Pass |

## Look at first

- **Identity and Operator isolation (gateway), read line by line:**
  - `services/gateway/src/gateway/api/live/live_operator.py`: token only, and administrators and callers without an Operator are refused.
  - `services/gateway/src/gateway/service/live/live_fan_out.py` (`_subject`) and `operator_live_source.py`: the subject is built from the connection's Operator, never from the message.
  - `services/gateway/src/gateway/api/rest/gateway_rest_app.py`: live router, lifespan, then `AccessInstaller`.
  - Tests: `test_live_operator.py`, `test_live_fan_out.py::test_a_client_of_one_operator_gets_nothing_of_another_operator`, `test_operator_live_source.py`.
- **Edge socket has no Operator check:** `services/flight-engine/src/flight_engine/api/live/live_endpoint.py`, with `conf/app.yaml` (`live.host: 127.0.0.1`). The hub key is the topic alone. This is acceptable for one Operator per edge, but `MissionCatalog` does not enforce it (follow-up).
- **Session clean-up:** `packages/python/swarm-live/src/swarm_live/api/live/live_session.py` (`close`, `_send_loop`). A sender that dies with an error other than cancellation stops `close` before every topic is left (follow-up).
- **Simulator isolation (BR-014):** `services/flight-engine/src/flight_engine/clients/mavlink/mavlink_listener.py` and `packages/rust/swarm-core/mavlink/src/frame.rs` only read and send no command. MAVLink signatures are not verified yet (follow-up).
- **Tick loop:** `services/flight-engine/src/flight_engine/service/missions/mission_actor.py` (`run`, `_tick`). Missed ticks are skipped, not run in a burst, and the hub is served before the leaf node.
- **Test seam:** `tests/live/conftest.py` overrides `LiveRouter.operator` with a query parameter. The end-to-end isolation test therefore proves the fan-out, and the token is proven by the gateway unit tests.

## Assumptions accepted

- BR-014 is linked through epic E0.6: accepted, because the path only reads MAVLink and sends no command.
- No budget is touched and no latency is asserted: accepted, because the roadmap row names none.
- No screen is touched: accepted, because there is no front-end change and TKT-21 does not apply.
- Only "10 simulated Drones" is quantified: accepted, because tests/live uses exactly 10.
- The workers reported no assumption and no decision.

## Follow-ups

- `live_session.py` `close`: catch and log each sender's failure, and always run `leave` (K18).
- Close the socket cleanly when `source.join` or `source_for` fails after `accept` (K18, K25).
- Cap the topics per live session through configuration (K18).
- Edge `/v1/live`: enforce one Operator per edge catalogue, or key the hub by Operator (K26, K19).
- MAVLink: verify signatures, check the CRC of every message, check the sender's address (K14, K22).
- An unknown battery or heading is shown as 0.0. Make it distinguishable before T0.19 shows it (K24).
- `tests/live`: remove the nested `consume` coroutine, catch the specific error, and use `# isort: skip` per line instead of the file-level `noqa` (K11).
- Keep evidence that `tests/live` actually ran (pytest `-rs`) (K11 and the verifier).
- `LiveRouter.operator`: name it in UPPER_CASE or make it an instance attribute (K25).
- Measure the per-frame DEBUG logging on the Telemetry path (T0.17).
