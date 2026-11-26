# T0.11: Review note

**Verdict:** ✅ Approved (round 2, confirm fixes) · **Branch:** `feature/tickets`

## What changed

- **Fixed Operator per person.** The Keycloak realm now declares `operator_id` in its declarative user profile, and only an administrator can view or edit it. Unmanaged attributes stay off. Tokens can carry the Operator, and a person cannot move themselves into another Operator's data.
- **Two new realm tests** fail if the attribute is undeclared, if a user can see or edit it, or if `unmanagedAttributePolicy` appears in the profile.
- **Shared files, not judged here.** The fix diff also touches T0.18's `MissionFeedClient.subscribe` (it now flushes after subscribing) and `test_live_feed.py`. Those are T0.18's files: they are recorded in this ticket's PROGRESS.md and were not reviewed as T0.11 work.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. Given a call without a token, when it reaches the gateway, then it is refused and logged | tests-evidences/pytest.txt (services/gateway/tests/service/auth/test_access_guard.py, test_route_access.py) | ✅ Pass |
| 2. Given a call with an expired token, when it reaches the gateway, then it is refused and logged | tests-evidences/pytest.txt (services/gateway/tests/service/auth/test_token_verifier.py) | ✅ Pass |
| 3. Given a call with another Operator's identifier, when it reaches the gateway, then it is refused and logged | tests-evidences/pytest.txt (test_access_guard.py, tests/deploy/charts/keycloak/test_swarm_realm.py) | ✅ Pass |

The full pytest run in the clean tree reports 4550 passed and 79 skipped.

## Look at first

- **Identity and Operator isolation:** read the `components` block at the end of `deploy/charts/keycloak/files/swarm-realm.json` line by line. Check that `operator_id` has `view` and `edit` set to `["admin"]` only, and that the `oidc-usermodel-attribute-mapper` in the `swarm` scope still reads the same attribute.
- **Tests that guard it:** `tests/deploy/charts/keycloak/test_swarm_realm.py`, the helper `_profile` and the last two tests.
- **The gateway trusts the claim.** `services/gateway/src/gateway/models/auth/caller.py` and `services/gateway/src/gateway/service/auth/access_guard.py` are unchanged in this round. They are now safe because the realm makes the claim admin-controlled.

## Assumptions accepted

- **The Operator comes from an admin-only user-profile attribute, not from organisation membership:** accepted. BR-008 needs a value the person cannot change, and the admin-only permissions with unmanaged attributes off give that. Moving to organisations later does not change the claim the gateway reads.

## Follow-ups

- **IMPLEMENTATION.md:** record the user-profile choice against the organisation-membership alternative (explainer).
- **Value check:** consider a validator on the `operator_id` attribute (pattern or length) in the user profile (K16).
