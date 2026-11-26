# T0.11: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🎯 Constraints

- A call without a token, with an expired token or with another Operator's identifier is refused and logged ([TICKET.md](TICKET.md), BR-008).
- A person must not be able to change their own Operator, or BR-008 is void ([`swarm-realm.json`](../../../deploy/charts/keycloak/files/swarm-realm.json#L503-L510)).
- The gateway keeps the layers of AGENT.md: the guard in `service`, the Keycloak call in `clients`, the route dependency in `api`, and no model logs ([`services/gateway/src/gateway/service/auth/access_guard.py`](../../../services/gateway/src/gateway/service/auth/access_guard.py)).
- The realm file stays self-contained and secret-free, so the chart can import it as it is ([`deploy/charts/keycloak/templates/deployment.yaml:23`](../../../deploy/charts/keycloak/templates/deployment.yaml#L23)).

## ⚖️ Choices at a glance

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | Where the Operator of a person is set | Admin-only `operator_id` in the declarative user profile | Derive it from organisation membership | The spec's organisation model is deferred |
| [D2](#d2) | Unmanaged attributes | Left off, so the policy key is absent | Enable them | Only declared attributes can exist on a user |
| [D3](#d3) | Making the live feed test deterministic | Flush the feed's own connection after join | Sleep or retry loop | One extra assert in the test |

## <a id="d1"></a>D1: Where the Operator of a person is set

**Chosen:** a declared `operator_id` attribute with view and edit for administrators only · **Where:** [`deploy/charts/keycloak/files/swarm-realm.json:503-510`](../../../deploy/charts/keycloak/files/swarm-realm.json#L503-L510) · **Source:** K16 and K10, confirmed by the reviewer

| Option | For | Against |
| --- | --- | --- |
| ✅ Declarative user profile | Keeps the existing attribute mapper ([`swarm-realm.json:112-118`](../../../deploy/charts/keycloak/files/swarm-realm.json#L112-L118)) and the realm file self-contained. Only admins can set it. Two realm tests guard it ([`tests/deploy/charts/keycloak/test_swarm_realm.py:256-265`](../../../tests/deploy/charts/keycloak/test_swarm_realm.py#L256-L265)). | Follows the spec's "each Operator an organisation" less closely. No value validation yet. |
| Derive from organisation membership | Closer to the wording of the technical page. | Needs an organisation mapper and an organisation model that carries the id, and changes the token mapper and the test contract. |

**Trade-off:** the claim the gateway reads is unchanged, so the later move to organisations does not touch the gateway.

**Revisit when:** organisations carry the Operator id (the Operator directory, T0.16).

## <a id="d2"></a>D2: Unmanaged attributes

**Chosen:** `unmanagedAttributePolicy` left unset · **Where:** [`deploy/charts/keycloak/files/swarm-realm.json:510`](../../../deploy/charts/keycloak/files/swarm-realm.json#L510) · **Source:** K16, test in [`test_swarm_realm.py:264`](../../../tests/deploy/charts/keycloak/test_swarm_realm.py#L264)

| Option | For | Against |
| --- | --- | --- |
| ✅ Off | A person cannot add or edit `operator_id` as a free attribute. | Any new user attribute must be declared first. |
| Enable unmanaged attributes | No declaration needed for new attributes. | Lets users edit their own `operator_id`, which breaks BR-008. |

**Trade-off:** a little declaration work for each new attribute, for isolation that holds.

**Revisit when:** a user attribute must be free-form, which would need its own admin-only rule for `operator_id`.

## <a id="d3"></a>D3: Making the live feed test deterministic

**Chosen:** flush the feed's NATS connection after join, before publishing · **Where:** [`services/gateway/tests/service/live/test_live_feed.py:57-59`](../../../services/gateway/tests/service/live/test_live_feed.py#L57-L59) · **Source:** FIX task (this file belongs to the shared work of T0.18, not judged as T0.11 work)

| Option | For | Against |
| --- | --- | --- |
| ✅ Flush after join | Waits for the server to acknowledge the subscription, with no timing guess. | Needs an `assert feed.client is not None` for mypy. |
| Fixed sleep | Simple. | Slow or flaky. |
| Retry publish until a frame arrives | Tolerates the race. | Slower and hides the race. |
| Flush inside `LiveFeed` or `LiveFanOut` | Fixes it for every caller. | Outside the fix's file list, and adds a flush per join in production that the race does not call for. |

**Trade-off:** the test depends on the client attribute of the feed.

**Revisit when:** a production caller also publishes right after joining.

## 📝 Assumptions behind the choices

- The admin-only user-profile attribute is an acceptable way to give each person a fixed Operator under BR-008, and the organisation model can replace it later without changing the claim: supports [D1](#d1) and [D2](#d2).
