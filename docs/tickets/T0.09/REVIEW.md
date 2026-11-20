# T0.09: Review note

**Verdict:** ✅ Approved · **Branch:** `feature/T0.09`

## What changed

- Each cell now runs a 3-server NATS cluster (`charts/nats`, JetStream domain `cell`), wired into the `cell` umbrella chart. The servers run in operator mode with a full resolver. The chart and Terraform only receive public values: the operator JWT and the system account key and JWT.
- Each Operator gets its own NATS account, named after its UUID. Every user credential (service, edge, simulated) may only use `op.<operator_id>.>` plus the internal NATS subjects (`_INBOX`, `$JS`, `$KV`, `$JSC`). Accounts, credentials and revocations are issued in Python (`swarm_nats.service.accounts`) and pushed to the servers with `AccountResolverClient`.
- Simulated credentials are ordinary user credentials with their own key, tagged `simulated`. A system credential cannot be issued for an Operator.
- An edge's leaf node chart (`charts/nats-leaf`) has its own JetStream domain and links to the core over mTLS with its own credential, which can be revoked. The core copies the edge's stream through a stream source, which is how messages are replayed in order after a cut.
- The new shared package `swarm-nats` provides the NATS connection, request-reply (absolute UTC deadline header plus idempotency key, no retry), an `AsyncRunnable` responder whose idempotency store is a key-value bucket, a durable pull consumer with explicit acks, a JetStream admin client and an event publisher. CI now installs a pinned nats-server so the tests run against a real server.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. Given an Operator's NATS account, when a test publishes on another Operator's subject, then the publication is refused | `tests/deploy/nats/test_operator_isolation.py::TestOperatorIsolation::test_a_publication_on_another_operators_subject_is_refused` (plus the subscribe-refused and nothing-received tests); `tests-evidences/pytest.txt` (2093 passed) | ✅ Pass |
| 2. Given a leaf node of an edge, when its link is cut for one minute and then restored, then its messages are replayed in order | `tests/deploy/nats/leaf/test_leaf_node_replay.py::TestLeafNodeReplay::test_a_leaf_node_cut_for_one_minute_replays_its_messages_in_order` (real hub and leaf, 60 s cut through a proxy, bodies 1 to 20 checked in order); `tests-evidences/pytest.txt` | ✅ Pass |
| 3. Given simulated Squads with their own credentials, when they connect to NATS, then they use credentials separate from those of real Squads | `tests/deploy/nats/test_simulated_credentials.py::TestSimulatedCredentials` (distinct keys and tags, distinct users in `/connz`, still limited to their Operator); `tests-evidences/pytest.txt` | ✅ Pass (compared with a service credential, see follow-ups) |

## Look at first

- **Operator isolation:** read `packages/python/swarm-nats/src/swarm_nats/service/accounts/credential_issuer.py` line by line, especially `MECHANISM_SUBJECTS` and `issue()`, which refuses the system kind and an account that is not the Operator's. Then read `account_issuer.py` (`issue`, `revoke` signed by the operator key) and `models/subjects/operator_subjects.py`.
- **Identity and secrets:** `service/accounts/nats_jwt_signer.py` signs and checks NATS JWTs by hand (ed25519-nkey). Check `decode()` and `_verify_key()`. Seeds are `SecretStr` and are never logged. The chart and the tfvars hold public values only (`deploy/charts/nats/templates/_helpers.tpl`, `deploy/terraform/cells/dev-branch/variables.tf`).
- **Simulator isolation:** the `SIMULATED` kind in `models/enums.py` and its tag in `credential_issuer.py::_claims`. The separation is by key and tag. Keeping simulated traffic away from real Drones is the adapter registry's job, in T0.13.
- **Edge link:** `deploy/charts/nats-leaf/templates/configmap.yaml` (remote with creds and mTLS), the core's leafnodes block in `deploy/charts/nats/templates/configmap.yaml` (`verify: true`), and `tests/deploy/nats/resolver/test_edge_credential_revocation.py`.
- **Request-reply semantics:** `clients/nats_requester.py` and `api/bus/nats_responder.py`. A failed reply is never stored. A request whose deadline has passed is dropped without a reply.

## Assumptions accepted

- K14, refused-push test replaced by an observable-effect test: accepted. It proves the server-side isolation BR-008 needs.
- K33, 'error' key means refusal, a reply without it means accepted, and any NatsError becomes one exception type: accepted, with a follow-up to test these paths.
- K34, Secret names, keys and namespace, full resolver, R3 surviving one lost server, and the wording of `revoke`: accepted. Checked against the charts and the code.
- K35, nats-server pin and package description: accepted. Checked against `python.yml` and `pyproject.toml`.

## Follow-ups

- Add tests for `AccountResolverClient`'s refusal paths (an error reply, a timeout, a reply that is not JSON).
- Criterion 3: also compare the simulated credential with an EDGE credential, which is what real Squads use.
- Criterion 2: make the replay test use, or check, the nats.conf rendered by `charts/nats-leaf`, including mTLS.
- Use one nats version for the cell chart (2.11.6), the leaf chart (2.11.8) and CI (2.15.3).
- `DurableConsumer.run` raises a builtin `RuntimeError`. Use an SE exception.
- Add DEBUG logs to the branches of `NatsResponder._reply` and `_answer` that do not log.
- `test_operator_subjects.py` builds dicts with hard-coded keys inside its test methods.
- `tests/deploy/nats/helpers.py` defines two constants twice.
- The streams exceptions sub-folders have no `__init__.py`.
- `NatsConnector.RECONNECT_ATTEMPTS` should come from configuration.
- Before the next dev-cell run, the person must add the three new NATS variables to the `DEV_CELL_TFVARS` secret, and the README's secrets table should say so.
