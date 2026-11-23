# T0.13: Review note

**Verdict:** ✅ Approved · **Branch:** `feature/tickets`

Both blocking findings of the previous run are fixed. Nothing blocking is left. Before you approve the push, run the PX4 test yourself (see Look at first).

## What changed

- A new Simulator service has two commands. `swarm-simulator fly` flies the simulated Squad (10 synthetic Drones and one PX4 SITL Drone) on a square route. `swarm-simulator serve` answers Commands on NATS, and only with credentials tagged `simulated`.
- Simulator isolation has three locks: an adapter registry that holds only `synthetic` or `px4_sitl` Drones on an allowed host; a credentials guard that runs before anything connects; and a responder subject that must sit under `op.<operator_id>.`.
- Every Flight log entry is marked simulated at three levels: the model's default, a check in the store, and a SQLite `CHECK (simulated = 1)`.
- A Rust crate, `swarm-synthetic-drones`, runs up to 255 MAVLink 2 Drones per process on one thread, with bounded reads per tick and the `step` benchmark. There is also a PX4 SITL image with headless Gazebo Harmonic.
- A `simulator` Helm sub-chart, off by default in the cell chart. Its NetworkPolicy lets only the simulator pod reach the Drone pods.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. Given the dev cell, when 10 synthetic Drones and one PX4 SITL Drone fly a square route, then all of them complete it | `tests-evidences/acceptance.txt`: `test_ten_synthetic_drones_complete_a_square_route` passed; `test_ten_synthetic_drones_and_one_px4_sitl_drone_all_complete_it` was skipped (Docker unreachable); no dev cell run | ⚠️ Synthetic Drones pass. PX4 and the dev cell are left to you (environment) |
| 2. Given simulated credentials, when a command is sent to a Drone outside the adapter registry, then it is refused and logged | `tests/simulator/test_command_isolation.py::test_a_command_to_a_drone_outside_the_registry_is_refused_and_logged`, `::test_a_serve_started_with_a_service_credential_exits_and_never_connects` | ✅ Pass |
| 3. Given a flight of the Simulator, when its Flight log is produced, then it is marked simulated | `tests/simulator/test_simulated_flight_log.py` (3 tests) | ✅ Pass |

Latest verifier run (`tests-evidences/pytest.txt`): 3112 passed, 1 skipped (PX4). Ruff, mypy, cargo fmt, clippy and test, `specs.py check` and `ticket_refs` are clean.

## Look at first

- **Run PX4 before you approve the push.** Run `docker build -f deploy/images/px4-sitl/Dockerfile -t swarm-px4-sitl:local .` then `uv run pytest tests/simulator -rs`, and keep the output in `tests-evidences/`. `deploy/images/px4-sitl/entrypoint.sh` relies on PX4 v1.16 answering the GCS at the address it hears from. Only a real run proves it.
- **Simulator isolation: the registry is the only way to a Drone.** Read these files line by line:
  - `services/simulator/src/simulator/service/registry/adapter_registry.py`: `register` refuses a host outside `simulated_hosts`.
  - `services/simulator/src/simulator/service/commands/simulated_command_service.py`: `handle` resolves through the registry, and a refusal is logged at WARNING and written as a simulated `command_refused` entry.
  - `services/simulator/src/simulator/clients/mavlink/mavlink_drone_client.py`: the client takes its host and port from the `RegisteredDrone` only.
- **Credentials.** `services/simulator/src/simulator/service/credentials/simulated_credentials_guard.py` decodes only the JWT payload and logs only the path and the error type. `services/simulator/src/simulator/api/cli/commands/serve_command.py` refuses in `initialize` (exit 3) before any connection.
- **Operator isolation.** `services/simulator/src/simulator/models/config/simulator_config.py` (`validate_deployment`) refuses a subject outside `op.<operator_id>.`. `Command` carries no `operator_id`, so this check and the per-Operator NATS account are the whole isolation.
- **Shared root files with T0.12.** `pyproject.toml` and `uv.lock` hold both tickets' entries. The ticket that finishes first commits a lock naming the other's workspace members, which `uv sync --locked` in CI is likely to refuse. Finish T0.12 and T0.13 into the same pull request.
- **Deployment.** `deploy/charts/simulator/values.yaml` still defaults the PX4 image to `px4io/px4-sitl`, and nothing publishes `deploy/images/*`. Set `px4Sitl.image.repository` when you enable the chart in a cell.

## Assumptions accepted

- FS-010 is linked as the feature BR-014 serves, scoped to the Simulator base: accepted. The phase page scopes it that way, and AC-1 is out of scope.
- UC-002 is cited without screens: accepted. No front end changes, so TKT-21 does not apply.
- No budget is touched: accepted. None is named in the roadmap row, and the crate's `step` benchmark is under the 5 % gate.
- "A square route" and "refused and logged" are taken as written: accepted. The side and altitude are configuration defaults.
- Simulated credentials come from T0.09: accepted. The guard reads the `simulated` tag, and the NATS server checks the signature.
- The agents reported no assumptions and no decisions for this run.

## Follow-ups

- Run the PX4 test and keep its output before you approve the push (environment, TKT-6).
- Point `px4Sitl.image.repository` at the ticket's own image, and publish `deploy/images/*` from CI.
- Finish T0.12 and T0.13 into the same pull request, or commit a shared lock file with the ticket's own entries only (harness gap).
- In `SquadFlight.all_completed`, require one outcome per flight.
- Send a Squad-wide Command to the Drones concurrently, within the 5 s request deadline.
- Log the `except SENatsConnectionError` branch of `ServeCommand._serve`.
- Move the NATS connector out of `api`, so that `api` calls `service` only.
- Set `MAVLINK20` and the dialect once, not on every link opened in a thread.
- Use one exception file naming (`se_*.py`) everywhere.
- Keep `localhost` and `127.0.0.1` out of the shipped `simulated_hosts`.
- `fly` needs no NATS, yet it requires the deployment values, so the AGENT.md command fails with the shipped `conf/app.yaml`.
- Harness gap: the logger hand-off convention rule misses calls on subscripted generics.
