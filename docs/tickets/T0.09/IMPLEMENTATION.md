# T0.09: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🎯 Constraints

- A publication on another Operator's subject must be refused, and credentials of simulated Squads must be separate from real ones (acceptance criteria of [TICKET.md](TICKET.md), BR-008 and BR-014).
- An edge's messages must be replayed in order after a one minute cut ([TICKET.md](TICKET.md)).
- Seeds never reach configuration or logs: the chart and Terraform hold public values only ([`deploy/terraform/cells/dev-branch/variables.tf:57-85`](../../../deploy/terraform/cells/dev-branch/variables.tf#L57-L85)).
- Long-running async work is an `AsyncRunnable`, every branch logs, no `Any`, one class per file ([AGENT.md](../../../AGENT.md)).
- Operators are created at run time, and edge credentials must be revocable ([PLAN.md](PLAN.md) assumptions).

## ⚖️ Choices at a glance

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | How accounts are created | Operator mode with the full resolver, issued in Python | A static server configuration | A hand-written JWT encoding to maintain |
| [D2](#d2) | What the refused-push test proves | Users of an untrusted account cannot connect | Make the client check the JWT issuer | `push()` is not shown to report that case |
| [D3](#d3) | How a refused push is detected | Presence of the `error` key | Check `data.code == 200` | A reply with neither key counts as accepted |
| [D4](#d4) | How the resolver client sends | `client.request` directly | Reuse `NatsRequester` | Timeout handling written again |
| [D5](#d5) | How simulated credentials are separated | Own key and tag in the Operator's account | A separate account | Real Drones are kept apart only later, by T0.13 |
| [D6](#d6) | Where the T0.09 criteria go in the deploy README | A new subsection | Replace or extend the T0.08 list | Two numbered lists under one heading |
| [D7](#d7) | How the new charts are documented | Layout table and cell list, plus new sections | New sections only | A summary is repeated |
| [D8](#d8) | Where the package is described | The existing packages paragraph and commands | New paragraph and lines | Longer lines |
| [D9](#d9) | How the edge leaf node is packaged | A separate chart, mTLS listener off by default | One chart for core and leaf | Two charts to version |

## <a id="d1"></a>D1: How accounts are created

**Chosen:** operator mode with a `full` resolver ([`deploy/charts/nats/templates/configmap.yaml:34-40`](../../../deploy/charts/nats/templates/configmap.yaml#L34-L40)), accounts and credentials issued by [`AccountIssuer`](../../../packages/python/swarm-nats/src/swarm_nats/service/accounts/account_issuer.py#L110) and pushed by [`AccountResolverClient`](../../../packages/python/swarm-nats/src/swarm_nats/clients/account_resolver_client.py#L58) · **Source:** PLAN.md

| Option | For | Against |
| --- | --- | --- |
| ✅ Decentralised JWT with the full resolver | Operators are created at run time, so no restart; edge credentials can be revoked by pushing the account again | No Python library issues NATS JWTs, so [`NatsJwtSigner`](../../../packages/python/swarm-nats/src/swarm_nats/service/accounts/nats_jwt_signer.py#L174) writes the encoding by hand |
| Static accounts in the server configuration | Simple | Each new Operator would need a restart, and credentials could not be revoked at run time |

**Trade-off:** the encoding is ours to maintain, and the acceptance tests against a real `nats-server` are what prove it.

**Revisit when:** a maintained Python library issues NATS JWTs.

## <a id="d2"></a>D2: What the refused-push test proves

**Chosen:** a test that credentials of an account signed by another operator never connect after the push, in [`tests/deploy/nats/resolver/test_account_registration.py:65`](../../../tests/deploy/nats/resolver/test_account_registration.py#L65) · **Source:** K14

| Option | For | Against |
| --- | --- | --- |
| ✅ Check the observable effect | nats-server 2.15.3 answers 200 to such a push, so this is what BR-008 needs | `SENatsAccountPushRefusedError` is no longer exercised there |
| Make the client check the JWT issuer | Would let `push()` report the refusal | Needs a planner decision and a new constructor argument |
| Drop the case | None given | Loses the isolation proof |

**Trade-off:** it proves the server's isolation, not that `push()` reports a refusal. The refusal paths are an open follow-up.

**Revisit when:** the follow-up test of `AccountResolverClient` is written.

## <a id="d3"></a>D3: How a refused push is detected

**Chosen:** the `error` key of the reply, held in `ERROR_KEY`, in [`account_resolver_client.py:90`](../../../packages/python/swarm-nats/src/swarm_nats/clients/account_resolver_client.py#L90) · **Source:** K33

| Option | For | Against |
| --- | --- | --- |
| ✅ `error` key present | Does not depend on the success payload, which differs between nats-server versions | A reply with neither key counts as accepted |
| `data.code == 200` | A positive check of success | Depends on the success shape |
| A Pydantic model of the reply | Typed | Not detailed in the decision; no reason given |

**Trade-off:** simplicity over strictness, accepted by the review, with a stricter check as a follow-up.

**Revisit when:** one nats-server version is pinned everywhere (see the version follow-up).

## <a id="d4"></a>D4: How the resolver client sends

**Chosen:** `connection.request` with the JWT as body and `timeout_s`, in [`account_resolver_client.py:70`](../../../packages/python/swarm-nats/src/swarm_nats/clients/account_resolver_client.py#L70) · **Source:** K33

| Option | For | Against |
| --- | --- | --- |
| ✅ Direct request | The claims update subject takes neither idempotency headers nor a typed reply; the clients layer stays free of cross-client imports | Timeout and error handling are written in this class |
| Reuse [`NatsRequester`](../../../packages/python/swarm-nats/src/swarm_nats/clients/nats_requester.py#L95) | One request path | It requires an idempotency key and a model reply |

**Trade-off:** a small amount of duplicated handling for a clean layer.

**Revisit when:** the requester gains a mode without idempotency.

## <a id="d5"></a>D5: How simulated credentials are separated

**Chosen:** an ordinary user credential with its own key, tagged `simulated`, in the Operator's account ([`credential_issuer.py:160`](../../../packages/python/swarm-nats/src/swarm_nats/service/accounts/credential_issuer.py#L160)) · **Source:** PLAN.md and review

| Option | For | Against |
| --- | --- | --- |
| ✅ Own key and tag | Same Operator limits apply, and one account per Operator stays the rule | Separation is by key and tag, not by subject |
| A separate account | Not discussed in the plan; open point | Not recorded |

**Trade-off:** keeping simulated traffic away from real Drones is the adapter registry's job in T0.13.

**Revisit when:** T0.13 is built.

## <a id="d6"></a>D6: Where the T0.09 criteria go in the deploy README

**Chosen:** a `###` subsection, in [`deploy/README.md:298`](../../../deploy/README.md#L298) · **Source:** K34

| Option | For | Against |
| --- | --- | --- |
| ✅ New subsection | Both tickets' criteria stay readable | Two numbered lists under one heading |
| Replace the T0.08 list | One list | Loses the T0.08 criteria |
| Items 4 to 6 of the same list | One list | Mixes two tickets |

**Trade-off:** a little structure for readability.

**Revisit when:** a third ticket adds criteria there.

## <a id="d7"></a>D7: How the new charts are documented

**Chosen:** rows for `charts/nats` and `charts/nats-leaf` in the Layout table and a line in "What a cell holds", as well as the new sections · **Where:** [`deploy/README.md:29-30`](../../../deploy/README.md#L29-L30) · **Source:** K34

| Option | For | Against |
| --- | --- | --- |
| ✅ Table, list and sections | The table and list stay complete | A summary is repeated |
| Sections only | No repetition | The table and list would miss two charts |

**Trade-off:** repetition for completeness.

**Revisit when:** the summaries drift from the sections.

## <a id="d8"></a>D8: Where the package is described

**Chosen:** `swarm-nats` added to the existing packages paragraph of [`AGENT.md:126-133`](../../../AGENT.md#L126-L133) and to the commands of [`README.md:178-179`](../../../README.md#L178-L179) · **Source:** K35

| Option | For | Against |
| --- | --- | --- |
| ✅ Extend in place | One list of packages, same command shape as the others | Longer paragraph and lines |
| New paragraph and lines | Shorter lines | Splits the single list |

**Trade-off:** longer lines for one place to look.

**Revisit when:** the package list grows past what one paragraph holds.

## <a id="d9"></a>D9: How the edge leaf node is packaged

**Chosen:** the separate chart [`deploy/charts/nats-leaf/templates/configmap.yaml:16-24`](../../../deploy/charts/nats-leaf/templates/configmap.yaml#L16-L24), and a core listener that is off by default and requires client certificates ([`deploy/charts/nats/templates/configmap.yaml:43-51`](../../../deploy/charts/nats/templates/configmap.yaml#L43-L51)) · **Source:** PLAN.md

| Option | For | Against |
| --- | --- | --- |
| ✅ Separate chart, mTLS, off by default | The dev cell has no certificate authority yet, and a listener without client certificates must not be exposed | The person enables it with a TLS Secret |
| Leaf inside the cell chart | Not discussed in the plan | Not recorded |

**Trade-off:** the replay test uses its own config without TLS, so mTLS is checked structurally only (a follow-up).

**Revisit when:** the first real edge connects.

## 📝 Assumptions behind the choices

- nats-server 2.15.3 accepts a push of an account signed by an untrusted operator: supports [D2](#d2).
- A refusal is the `error` key, a reply without it is accepted, any `NatsError` is one exception type: supports [D3](#d3).
- Secrets and keys of the edge Secrets match the leaf chart; the resolver is `full`; R3 survives one lost server: supports [D1](#d1) and [D9](#d9).
- `AccountIssuer.revoke` returns the account with a new operator-signed JWT: supports [D1](#d1).
- The CI pin of nats-server is verified with SHA256SUMS: supports [D8](#d8).
