# T0.13: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🎯 Constraints

- A Command to a Drone outside the adapter registry is refused and logged, and every Flight log is marked simulated (acceptance criteria 2 and 3 of [TICKET.md](TICKET.md), [📏 BR-014](../../specs/functional/business-rules/BR-014-simulation-isolation.md)).
- Simulated Squads use separate NATS credentials, and PX4 SITL gives fidelity while Rust synthetic Drones give volume ([🕹️ Engine and services: simulator](../../specs/technical/04-engine.md#simulator)).
- 10 synthetic Drones and one PX4 Drone fly a square route (criterion 1); the crate has a `step` benchmark under the 5 % gate (assumption on budgets).
- The AGENT.md rules hold: layers call downwards only, one class per file, no raw strings, every branch logs, an `AsyncRunnable` yields its status ([`AGENT.md`](../../../AGENT.md)).
- The NATS credentials are issued by T0.09, which is out of scope here.

## ⚖️ Choices at a glance

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | How a Drone is addressed | Adapter registry with a host allowlist, the only path | Address any host a Command names | Allowlist to maintain, `localhost` shipped in it |
| [D2](#d2) | How credentials are proved simulated | Guard reads the `simulated` tag of the JWT payload | Verify the signature in the service | Trusts the NATS server for the signature |
| [D3](#d3) | Where the simulated flag is enforced | Model default, store check and SQLite `CHECK` | One check only | Three places to keep in step |
| [D4](#d4) | Operator isolation of the responder | Subject must sit under `op.<operator_id>.` | Rely on the NATS account alone | Config for `fly` needs NATS values |
| [D5](#d5) | Volume of synthetic Drones | One Rust process, one thread, bounded reads | One process per Drone | One slow Drone shares the tick |
| [D6](#d6) | Deployment | Sub-chart off by default, with a NetworkPolicy | Always on | PX4 image default is not yet the ticket's own |

## <a id="d1"></a>D1: How a Drone is addressed

**Chosen:** an `AdapterRegistry` refusing any host outside `simulated_hosts`, with the client taking host and port from the registered Drone only · **Where:** [`adapter_registry.py:47`](../../../services/simulator/src/simulator/service/registry/adapter_registry.py#L47) · **Source:** PLAN, read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ Registry with allowlist | Meets "cannot address a real Drone" of the technical page; the refusal is logged ([`simulated_command_service.py:188`](../../../services/simulator/src/simulator/service/commands/simulated_command_service.py#L188)) | The list of hosts must be kept right; `127.0.0.1` and `localhost` are in the shipped [`app.yaml`](../../../services/simulator/conf/app.yaml#L25-L29) |
| Address the host a Command names | Fewer moving parts | Breaks criterion 2 and BR-014 |

**Trade-off:** a configured list in exchange for a hard guarantee in code.

**Revisit when:** the loopback entries are moved to the test configuration (follow-up of the review).

## <a id="d2"></a>D2: How credentials are proved simulated

**Chosen:** the guard decodes only the JWT payload and requires the `simulated` tag, before anything connects · **Where:** [`simulated_credentials_guard.py:149`](../../../services/simulator/src/simulator/service/credentials/simulated_credentials_guard.py#L149) and [`serve_command.py:143`](../../../services/simulator/src/simulator/api/cli/commands/serve_command.py#L143) · **Source:** PLAN, review

| Option | For | Against |
| --- | --- | --- |
| ✅ Read the tag, exit 3 before connecting | A service credential never reaches NATS; the guard logs only the path and the error type (no secret) | It does not prove the JWT is authentic |
| Verify the signature too | Stronger proof | Needs the operator key, which T0.09 owns and this ticket does not use; the NATS server already checks the signature |

**Trade-off:** authenticity is left to NATS, as the reviewer accepted.

**Revisit when:** a service needs to trust a credentials file without connecting.

## <a id="d3"></a>D3: Where the simulated flag is enforced

**Chosen:** three levels: the model default and validator, the store's check and the SQLite `CHECK (simulated = 1)` · **Where:** [`flight_log_entry.py:184`](../../../services/simulator/src/simulator/models/flight_logs/flight_log_entry.py#L184), [`flight_log_store.py:115`](../../../services/simulator/src/simulator/storage/edge/flight_log_store.py#L115), [`flight_log_store.py:43`](../../../services/simulator/src/simulator/storage/edge/flight_log_store.py#L43) · **Source:** read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ Three levels | The database refuses a row whatever writes to it, tested by `test_a_row_that_is_not_simulated_is_refused_by_the_database` | Three places to change together |
| Model only | Simplest | A writer that bypasses the model is not stopped |

**Trade-off:** duplication for a rule that BR-014 states as MUST.

**Revisit when:** the Flight log moves to a shared store (a later ticket); the reason for exactly three levels is not recorded.

## <a id="d4"></a>D4: Operator isolation of the responder

**Chosen:** `validate_deployment` refuses a subject outside `op.<operator_id>.`, and the deployment values have no default · **Where:** [`simulator_config.py:154`](../../../services/simulator/src/simulator/models/config/simulator_config.py#L154) · **Source:** reviewer note

| Option | For | Against |
| --- | --- | --- |
| ✅ Check in the configuration | `Command` carries no `operator_id`, so this check and the NATS account are the whole isolation | `fly` also needs NATS values, so the documented command fails with the shipped [`app.yaml`](../../../services/simulator/conf/app.yaml) |
| NATS account alone | No code | A wrong subject would only be caught by the server |

**Trade-off:** safer defaults, at the cost of a `fly` that needs values it does not use (follow-up).

**Revisit when:** the check moves to `serve` only.

## <a id="d5"></a>D5: Volume of synthetic Drones

**Chosen:** one process flying up to 255 Drones on one thread, with at most 64 datagrams per Drone per tick and at most 5 catch-up ticks · **Where:** [`link.rs:66`](../../../packages/rust/swarm-synthetic-drones/src/link.rs#L66), [`link.rs:361`](../../../packages/rust/swarm-synthetic-drones/src/link.rs#L361) · **Source:** PLAN, read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ One thread, bounded reads | A flood to one Drone cannot starve the others; the `step` benchmark ([`step.rs:22`](../../../packages/rust/swarm-synthetic-drones/benches/step.rs#L22)) is under the 5 % gate | All Drones share one tick |
| One process per Drone | Isolation | Not a "volume" answer at 255 Drones |

**Trade-off:** a single tick budget in exchange for bounded work.

**Revisit when:** the benchmark shows a tick close to the tick period at 255 Drones. No measurement is recorded here.

## <a id="d6"></a>D6: Deployment

**Chosen:** the `simulator` sub-chart is a condition of the cell chart, off by default, with a NetworkPolicy allowing only the simulator pod to reach the Drone pods · **Where:** [`Chart.yaml:24-26`](../../../deploy/charts/cell/Chart.yaml#L24-L26), [`values.yaml:14-15`](../../../deploy/charts/cell/values.yaml#L14-L15), [`networkpolicy.yaml:1-21`](../../../deploy/charts/simulator/templates/networkpolicy.yaml#L1-L21) · **Source:** read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ Optional, isolated | A cell without simulation runs no simulated Drone; the policy backs D1 at the network | PX4 image default is still `px4io/px4-sitl` ([`values.yaml`](../../../deploy/charts/simulator/values.yaml)); nothing publishes `deploy/images/*` |
| Always on | Criterion 1 "given the dev cell" is met without a flag | A Simulator in every cell |

**Trade-off:** an explicit switch and an image to set, at enabling time.

**Revisit when:** `deploy/images/*` is published from CI.

## 📝 Assumptions behind the choices

- Simulated NATS credentials come from T0.09: supports [D2](#d2).
- "Refused and logged" is taken as written: supports [D1](#d1).
- No budget is touched, the crate keeping its `step` benchmark: supports [D5](#d5).
