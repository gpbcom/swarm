# T0.08: Review note

**Verdict:** ✅ Approved · **Branch:** `ticket/T0.08`

Round 2, confirming fixes. The one blocking finding from round 1 is fixed, and the fix introduces no new blocking defect.

## What changed

- **Each cell now gets its own auth-delegator binding.** The OpenBao chart used to create one cluster-wide binding named after the release (`openbao-server-binding`), so a second branch cell would have failed to install. That chart binding is now turned off. Terraform creates a binding named after the cell's namespace (`<namespace>-openbao-auth-delegator`) and deletes it when the cell is destroyed.
- **The vault's ServiceAccount name is fixed to the release name.** This keeps the binding's subject correct even if `release_name` is overridden. The module's inputs, outputs and vault address are unchanged.
- **The editor tool's output was removed from the ticket.** The `.VSCodeCounter/` reports were dropped from the tree and ignored in `.gitignore`.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. Given a branch, when a cell is requested for it, then the branch gets its cell in minutes, with its infrastructure created by Terraform and the platform deployed by Argo CD. | tests-evidences/terraform-test-deploy-terraform-cells-dev-branch.txt (4 passed), terraform-test-deploy-terraform-modules-self-hosted-vault.txt (3 passed), terraform-validate-*.txt, pytest.txt (1382 passed, 30 skipped) | ✅ Pass. The round 1 collision is fixed. Because Helm is missing, the 30 chart rendering tests skip, so "two cells side by side" is confirmed by reading the code, not by running it. |
| 2. Given a branch with a dev cell, when the branch closes, then the cell is lost, its infrastructure destroyed by Terraform. | terraform-test-deploy-terraform-cells-dev-branch.txt, tests/ci/dev_cell | ✅ Pass. The new binding is a Terraform resource, so destroying the cell deletes it. |
| 3. Given a running dev cell, when a service needs a database credential, then the credential comes from the vault and never from a file. | terraform-test-deploy-terraform-modules-self-hosted-vault.txt, pytest.txt (tests/deploy) | ✅ Pass. Kubernetes auth keeps its token-review permission through the binding each cell gets. |

## Look at first

- **The per-cell binding:** `deploy/terraform/modules/self-hosted/vault/main.tf` lines 35-40 (chart values) and 59-78 (the new resource).
  - The name must include the namespace.
  - The subject must be ServiceAccount `var.release_name` in `var.namespace`.
  - The role must be `system:auth-delegator`.
  - These lines keep one cell's vault from reviewing tokens under another cell's identity, which is what keeps Operator isolation between cells.
- **The vault configuration chart:** `deploy/charts/vault-config/templates/_helpers.tpl`. Its name fix from before this round is still unrendered because Helm is missing, so read it by eye.

## Assumptions accepted

- No new assumption in this round. The round 1 assumptions still stand.

## Follow-ups

- Add asserts on the new binding (its name contains the namespace, its role, its subject) to `deploy/terraform/modules/self-hosted/vault/tests/vault.tftest.hcl` (K02/K15).
- The `.gitignore` entry for `.VSCodeCounter` has nothing to do with this ticket, is unanchored, and leaves the file without a final newline. Move it out of the ticket, or anchor it as `/.VSCodeCounter/` and add the newline.
- Install Helm for the checks, here and in CI, so the 30 chart rendering tests run. Add an integration check with two cells side by side once a cluster or kind is available.
- The `.claude/workflows/ticket-run.js` routing change is still waiting for your decision: it goes into T0.08's single commit unless you ask for a separate commit.
