# T0.08: Dev cell on k3s

**Status:** ✅ Done · **Ticket:** [TICKET.md](TICKET.md) · **Choices and trade-offs:** [IMPLEMENTATION.md](IMPLEMENTATION.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🔭 What it does

- A branch gets its own dev cell on demand: a namespace on the shared dev k3s cluster, created by Terraform, with its data platform deployed by Argo CD.
- Each cell has its own PostgreSQL (PostGIS and TimescaleDB, through CloudNativePG), a PgBouncer pooler, Valkey, MinIO and an OpenBao vault. Argo CD, the CloudNativePG operator and KEDA are installed once per cluster.
- When the branch is deleted, or on demand, Terraform destroys the cell and its state.
- A service reads a short-lived database credential from the vault with its Kubernetes identity. No credential sits in a file.

## ⚙️ How it works

1. **Request the cell:** a person runs the script, or the manual workflow does. The script turns the branch into a cell name (`cell-<slug>-<8 hex of sha256>`), then runs `terraform init` with one state key per cell, `apply`, and waits for the Argo CD Application to be Synced then Healthy, in [`deploy/scripts/dev-cell.sh:42-50`](../../../deploy/scripts/dev-cell.sh#L42-L50) and [`deploy/scripts/dev-cell.sh:103-111`](../../../deploy/scripts/dev-cell.sh#L103-L111).
2. **The workflow:** [`.github/workflows/dev-cell.yml:3-17`](../../../.github/workflows/dev-cell.yml#L3-L17) starts the script on `workflow_dispatch` (`up` or `down`) and on the `delete` event of a branch, which always runs `down` ([`.github/workflows/dev-cell.yml:31-32`](../../../.github/workflows/dev-cell.yml#L31-L32)). The secrets are written to files outside the repository first ([`.github/workflows/dev-cell.yml:44-61`](../../../.github/workflows/dev-cell.yml#L44-L61)).
3. **One root, one state per branch:** [`deploy/terraform/cells/dev-branch/versions.tf:19-21`](../../../deploy/terraform/cells/dev-branch/versions.tf#L19-L21) declares a partial S3 backend, completed by the script with the key `dev-branch/<cell>.tfstate`.
4. **The namespace and its secrets:** the `cell` module creates the namespace labelled with the cell and branch, and the MinIO root secret from a random password, in [`deploy/terraform/modules/self-hosted/cell/main.tf:1-31`](../../../deploy/terraform/modules/self-hosted/cell/main.tf#L1-L31).
5. **The vault:** the `vault` module generates a root token, stores it as a secret, installs the OpenBao chart in dev server mode, and binds the vault's ServiceAccount to `system:auth-delegator` with a binding named after the namespace, in [`deploy/terraform/modules/self-hosted/vault/main.tf:6-78`](../../../deploy/terraform/modules/self-hosted/vault/main.tf#L6-L78) (chart values at lines 29-49, binding at lines 62-78).
6. **The Application of the cell:** the `cell-application` module installs an Argo CD Application, with a finalizer, that follows `deploy/charts/cell` at the branch and passes the dev values file and the database image, in [`deploy/terraform/modules/self-hosted/cell-application/main.tf:5-34`](../../../deploy/terraform/modules/self-hosted/cell-application/main.tf#L5-L34). The root wires the three modules, with the Application after the vault, in [`deploy/terraform/cells/dev-branch/main.tf:1-31`](../../../deploy/terraform/cells/dev-branch/main.tf#L1-L31).
7. **The umbrella chart:** [`deploy/charts/cell/Chart.yaml:6-20`](../../../deploy/charts/cell/Chart.yaml#L6-L20) brings in the database, Valkey, object-storage and vault-config charts, each switchable. The dev values (the five services and the sizes) are in [`deploy/environments/dev/values.yaml`](../../../deploy/environments/dev/values.yaml).
8. **The database:** a CloudNativePG `Cluster` with the PostGIS and TimescaleDB extensions, and, for each service, a `NOLOGIN` group role and a schema, in [`deploy/charts/database/templates/cluster.yaml:7-29`](../../../deploy/charts/database/templates/cluster.yaml#L7-L29). A `Pooler` runs PgBouncer in transaction mode in front of it, in [`deploy/charts/database/templates/pooler.yaml:7-13`](../../../deploy/charts/database/templates/pooler.yaml#L7-L13). The image that holds both extensions is built by [`deploy/images/postgres/Dockerfile:2-18`](../../../deploy/images/postgres/Dockerfile#L2-L18).
9. **The vault configuration:** after the sync, a PostSync Job ([`deploy/charts/vault-config/templates/job.yaml:1-48`](../../../deploy/charts/vault-config/templates/job.yaml#L1-L48)) runs an idempotent script ([`deploy/charts/vault-config/templates/configmap.yaml:29-78`](../../../deploy/charts/vault-config/templates/configmap.yaml#L29-L78)). It enables Kubernetes auth and the database secrets engine, and for each service writes a dynamic role, a read policy on `database/creds/<service>`, and a Kubernetes role bound to the service's ServiceAccount.
10. **The credential:** a service logs in with its ServiceAccount token. The vault reviews the token through the auth-delegator binding of step 5, then issues a PostgreSQL role with a TTL, a member of the service's group role.
11. **Close the cell:** `terraform destroy` removes the Application first, whose finalizer makes Argo CD delete what it deployed, then the vault, its binding and the namespace ([`deploy/terraform/cells/dev-branch/main.tf:15-16`](../../../deploy/terraform/cells/dev-branch/main.tf#L15-L16), [`deploy/scripts/dev-cell.sh:112-115`](../../../deploy/scripts/dev-cell.sh#L112-L115)).
12. **Once per cluster:** the dev root installs Argo CD and a root Application `platform` behind `platform_enabled`, in [`deploy/terraform/cells/dev/main.tf:51-61`](../../../deploy/terraform/cells/dev/main.tf#L51-L61) and [`deploy/terraform/modules/self-hosted/argocd/main.tf:1-44`](../../../deploy/terraform/modules/self-hosted/argocd/main.tf#L1-L44). The `platform` Application deploys the operators from `deploy/environments/dev/platform`, such as [`deploy/environments/dev/platform/keda.yaml:1-18`](../../../deploy/environments/dev/platform/keda.yaml#L1-L18).

## 🧱 Files and lines changed

<!-- changes -->
| File | Change | Lines in the new version | Added | Removed |
| --- | --- | --- | --- | --- |
| [`.claude/workflows/ticket-run.js`](../../../.claude/workflows/ticket-run.js) | Modified | [236](../../../.claude/workflows/ticket-run.js#L236), [254-267](../../../.claude/workflows/ticket-run.js#L254), [270](../../../.claude/workflows/ticket-run.js#L270), [272-276](../../../.claude/workflows/ticket-run.js#L272), [281-284](../../../.claude/workflows/ticket-run.js#L281) | +25 | −13 |
| [`.github/workflows/dev-cell.yml`](../../../.github/workflows/dev-cell.yml) | Added | [1-67](../../../.github/workflows/dev-cell.yml#L1) | +67 | −0 |
| [`.github/workflows/terraform.yml`](../../../.github/workflows/terraform.yml) | Modified | [28-31](../../../.github/workflows/terraform.yml#L28), [33](../../../.github/workflows/terraform.yml#L33) | +5 | −0 |
| [`.gitignore`](../../../.gitignore) | Modified | [40-43](../../../.gitignore#L40) | +4 | −0 |
| [`AGENT.md`](../../../AGENT.md) | Modified | [68-69](../../../AGENT.md#L68), [99-100](../../../AGENT.md#L99), [109-112](../../../AGENT.md#L109) | +8 | −2 |
| [`deploy/README.md`](../../../deploy/README.md) | Added | [1-224](../../../deploy/README.md#L1) | +224 | −0 |
| [`deploy/charts/cell/Chart.lock`](../../../deploy/charts/cell/Chart.lock) | Added | [1-15](../../../deploy/charts/cell/Chart.lock#L1) | +15 | −0 |
| [`deploy/charts/cell/Chart.yaml`](../../../deploy/charts/cell/Chart.yaml) | Added | [1-20](../../../deploy/charts/cell/Chart.yaml#L1) | +20 | −0 |
| [`deploy/charts/cell/values.yaml`](../../../deploy/charts/cell/values.yaml) | Added | [1-11](../../../deploy/charts/cell/values.yaml#L1) | +11 | −0 |
| [`deploy/charts/database/Chart.yaml`](../../../deploy/charts/database/Chart.yaml) | Added | [1-5](../../../deploy/charts/database/Chart.yaml#L1) | +5 | −0 |
| [`deploy/charts/database/templates/_helpers.tpl`](../../../deploy/charts/database/templates/_helpers.tpl) | Added | [1-8](../../../deploy/charts/database/templates/_helpers.tpl#L1) | +8 | −0 |
| [`deploy/charts/database/templates/cluster.yaml`](../../../deploy/charts/database/templates/cluster.yaml) | Added | [1-29](../../../deploy/charts/database/templates/cluster.yaml#L1) | +29 | −0 |
| [`deploy/charts/database/templates/pooler.yaml`](../../../deploy/charts/database/templates/pooler.yaml) | Added | [1-13](../../../deploy/charts/database/templates/pooler.yaml#L1) | +13 | −0 |
| [`deploy/charts/database/values.yaml`](../../../deploy/charts/database/values.yaml) | Added | [1-17](../../../deploy/charts/database/values.yaml#L1) | +17 | −0 |
| [`deploy/charts/object-storage/Chart.yaml`](../../../deploy/charts/object-storage/Chart.yaml) | Added | [1-6](../../../deploy/charts/object-storage/Chart.yaml#L1) | +6 | −0 |
| [`deploy/charts/object-storage/templates/networkpolicy.yaml`](../../../deploy/charts/object-storage/templates/networkpolicy.yaml) | Added | [1-14](../../../deploy/charts/object-storage/templates/networkpolicy.yaml#L1) | +14 | −0 |
| [`deploy/charts/object-storage/templates/service.yaml`](../../../deploy/charts/object-storage/templates/service.yaml) | Added | [1-14](../../../deploy/charts/object-storage/templates/service.yaml#L1) | +14 | −0 |
| [`deploy/charts/object-storage/templates/statefulset.yaml`](../../../deploy/charts/object-storage/templates/statefulset.yaml) | Added | [1-51](../../../deploy/charts/object-storage/templates/statefulset.yaml#L1) | +51 | −0 |
| [`deploy/charts/object-storage/values.yaml`](../../../deploy/charts/object-storage/values.yaml) | Added | [1-8](../../../deploy/charts/object-storage/values.yaml#L1) | +8 | −0 |
| [`deploy/charts/valkey/Chart.yaml`](../../../deploy/charts/valkey/Chart.yaml) | Added | [1-6](../../../deploy/charts/valkey/Chart.yaml#L1) | +6 | −0 |
| [`deploy/charts/valkey/templates/networkpolicy.yaml`](../../../deploy/charts/valkey/templates/networkpolicy.yaml) | Added | [1-18](../../../deploy/charts/valkey/templates/networkpolicy.yaml#L1) | +18 | −0 |
| [`deploy/charts/valkey/templates/service.yaml`](../../../deploy/charts/valkey/templates/service.yaml) | Added | [1-13](../../../deploy/charts/valkey/templates/service.yaml#L1) | +13 | −0 |
| [`deploy/charts/valkey/templates/statefulset.yaml`](../../../deploy/charts/valkey/templates/statefulset.yaml) | Added | [1-47](../../../deploy/charts/valkey/templates/statefulset.yaml#L1) | +47 | −0 |
| [`deploy/charts/valkey/values.yaml`](../../../deploy/charts/valkey/values.yaml) | Added | [1-13](../../../deploy/charts/valkey/values.yaml#L1) | +13 | −0 |
| [`deploy/charts/vault-config/Chart.yaml`](../../../deploy/charts/vault-config/Chart.yaml) | Added | [1-6](../../../deploy/charts/vault-config/Chart.yaml#L1) | +6 | −0 |
| [`deploy/charts/vault-config/templates/_helpers.tpl`](../../../deploy/charts/vault-config/templates/_helpers.tpl) | Added | [1-12](../../../deploy/charts/vault-config/templates/_helpers.tpl#L1) | +12 | −0 |
| [`deploy/charts/vault-config/templates/configmap.yaml`](../../../deploy/charts/vault-config/templates/configmap.yaml) | Added | [1-78](../../../deploy/charts/vault-config/templates/configmap.yaml#L1) | +78 | −0 |
| [`deploy/charts/vault-config/templates/job.yaml`](../../../deploy/charts/vault-config/templates/job.yaml) | Added | [1-48](../../../deploy/charts/vault-config/templates/job.yaml#L1) | +48 | −0 |
| [`deploy/charts/vault-config/values.yaml`](../../../deploy/charts/vault-config/values.yaml) | Added | [1-24](../../../deploy/charts/vault-config/values.yaml#L1) | +24 | −0 |
| [`deploy/environments/dev/platform/cloudnative-pg.yaml`](../../../deploy/environments/dev/platform/cloudnative-pg.yaml) | Added | [1-21](../../../deploy/environments/dev/platform/cloudnative-pg.yaml#L1) | +21 | −0 |
| [`deploy/environments/dev/platform/keda-http-add-on.yaml`](../../../deploy/environments/dev/platform/keda-http-add-on.yaml) | Added | [1-20](../../../deploy/environments/dev/platform/keda-http-add-on.yaml#L1) | +20 | −0 |
| [`deploy/environments/dev/platform/keda.yaml`](../../../deploy/environments/dev/platform/keda.yaml) | Added | [1-20](../../../deploy/environments/dev/platform/keda.yaml#L1) | +20 | −0 |
| [`deploy/environments/dev/values.yaml`](../../../deploy/environments/dev/values.yaml) | Added | [1-22](../../../deploy/environments/dev/values.yaml#L1) | +22 | −0 |
| [`deploy/images/postgres/Dockerfile`](../../../deploy/images/postgres/Dockerfile) | Added | [1-18](../../../deploy/images/postgres/Dockerfile#L1) | +18 | −0 |
| [`deploy/scripts/dev-cell.sh`](../../../deploy/scripts/dev-cell.sh) | Added | [1-116](../../../deploy/scripts/dev-cell.sh#L1) | +116 | −0 |
| [`deploy/terraform/README.md`](../../../deploy/terraform/README.md) | Modified | [12-15](../../../deploy/terraform/README.md#L12), [26-29](../../../deploy/terraform/README.md#L26), [31](../../../deploy/terraform/README.md#L31), [75-77](../../../deploy/terraform/README.md#L75), [128-148](../../../deploy/terraform/README.md#L128), [154-181](../../../deploy/terraform/README.md#L154), [208-211](../../../deploy/terraform/README.md#L208), [213-214](../../../deploy/terraform/README.md#L213), [220-221](../../../deploy/terraform/README.md#L220), [246-248](../../../deploy/terraform/README.md#L246) | +72 | −7 |
| [`deploy/terraform/cells/dev-branch/.terraform.lock.hcl`](../../../deploy/terraform/cells/dev-branch/.terraform.lock.hcl) | Added | [1-71](../../../deploy/terraform/cells/dev-branch/.terraform.lock.hcl#L1) | +71 | −0 |
| [`deploy/terraform/cells/dev-branch/main.tf`](../../../deploy/terraform/cells/dev-branch/main.tf) | Added | [1-31](../../../deploy/terraform/cells/dev-branch/main.tf#L1) | +31 | −0 |
| [`deploy/terraform/cells/dev-branch/outputs.tf`](../../../deploy/terraform/cells/dev-branch/outputs.tf) | Added | [1-14](../../../deploy/terraform/cells/dev-branch/outputs.tf#L1) | +14 | −0 |
| [`deploy/terraform/cells/dev-branch/providers.tf`](../../../deploy/terraform/cells/dev-branch/providers.tf) | Added | [1-10](../../../deploy/terraform/cells/dev-branch/providers.tf#L1) | +10 | −0 |
| [`deploy/terraform/cells/dev-branch/terraform.tfvars.example`](../../../deploy/terraform/cells/dev-branch/terraform.tfvars.example) | Added | [1-8](../../../deploy/terraform/cells/dev-branch/terraform.tfvars.example#L1) | +8 | −0 |
| [`deploy/terraform/cells/dev-branch/tests/dev_branch.tftest.hcl`](../../../deploy/terraform/cells/dev-branch/tests/dev_branch.tftest.hcl) | Added | [1-69](../../../deploy/terraform/cells/dev-branch/tests/dev_branch.tftest.hcl#L1) | +69 | −0 |
| [`deploy/terraform/cells/dev-branch/variables.tf`](../../../deploy/terraform/cells/dev-branch/variables.tf) | Added | [1-55](../../../deploy/terraform/cells/dev-branch/variables.tf#L1) | +55 | −0 |
| [`deploy/terraform/cells/dev-branch/versions.tf`](../../../deploy/terraform/cells/dev-branch/versions.tf) | Added | [1-22](../../../deploy/terraform/cells/dev-branch/versions.tf#L1) | +22 | −0 |
| [`deploy/terraform/cells/dev/.terraform.lock.hcl`](../../../deploy/terraform/cells/dev/.terraform.lock.hcl) | Modified | [50-95](../../../deploy/terraform/cells/dev/.terraform.lock.hcl#L50) | +46 | −0 |
| [`deploy/terraform/cells/dev/main.tf`](../../../deploy/terraform/cells/dev/main.tf) | Modified | [50-61](../../../deploy/terraform/cells/dev/main.tf#L50) | +12 | −0 |
| [`deploy/terraform/cells/dev/outputs.tf`](../../../deploy/terraform/cells/dev/outputs.tf) | Modified | [20-24](../../../deploy/terraform/cells/dev/outputs.tf#L20) | +5 | −0 |
| [`deploy/terraform/cells/dev/providers.tf`](../../../deploy/terraform/cells/dev/providers.tf) | Modified | [17-28](../../../deploy/terraform/cells/dev/providers.tf#L17) | +12 | −0 |
| [`deploy/terraform/cells/dev/terraform.tfvars.example`](../../../deploy/terraform/cells/dev/terraform.tfvars.example) | Modified | [20-26](../../../deploy/terraform/cells/dev/terraform.tfvars.example#L20) | +7 | −0 |
| [`deploy/terraform/cells/dev/tests/dev.tftest.hcl`](../../../deploy/terraform/cells/dev/tests/dev.tftest.hcl) | Modified | [4-5](../../../deploy/terraform/cells/dev/tests/dev.tftest.hcl#L4), [35-39](../../../deploy/terraform/cells/dev/tests/dev.tftest.hcl#L35), [89-147](../../../deploy/terraform/cells/dev/tests/dev.tftest.hcl#L89) | +66 | −0 |
| [`deploy/terraform/cells/dev/variables.tf`](../../../deploy/terraform/cells/dev/variables.tf) | Modified | [76-120](../../../deploy/terraform/cells/dev/variables.tf#L76) | +45 | −0 |
| [`deploy/terraform/cells/dev/versions.tf`](../../../deploy/terraform/cells/dev/versions.tf) | Modified | [17-24](../../../deploy/terraform/cells/dev/versions.tf#L17) | +8 | −0 |
| [`deploy/terraform/modules/self-hosted/argocd/main.tf`](../../../deploy/terraform/modules/self-hosted/argocd/main.tf) | Added | [1-44](../../../deploy/terraform/modules/self-hosted/argocd/main.tf#L1) | +44 | −0 |
| [`deploy/terraform/modules/self-hosted/argocd/outputs.tf`](../../../deploy/terraform/modules/self-hosted/argocd/outputs.tf) | Added | [1-9](../../../deploy/terraform/modules/self-hosted/argocd/outputs.tf#L1) | +9 | −0 |
| [`deploy/terraform/modules/self-hosted/argocd/tests/argocd.tftest.hcl`](../../../deploy/terraform/modules/self-hosted/argocd/tests/argocd.tftest.hcl) | Added | [1-91](../../../deploy/terraform/modules/self-hosted/argocd/tests/argocd.tftest.hcl#L1) | +91 | −0 |
| [`deploy/terraform/modules/self-hosted/argocd/variables.tf`](../../../deploy/terraform/modules/self-hosted/argocd/variables.tf) | Added | [1-47](../../../deploy/terraform/modules/self-hosted/argocd/variables.tf#L1) | +47 | −0 |
| [`deploy/terraform/modules/self-hosted/argocd/versions.tf`](../../../deploy/terraform/modules/self-hosted/argocd/versions.tf) | Added | [1-10](../../../deploy/terraform/modules/self-hosted/argocd/versions.tf#L1) | +10 | −0 |
| [`deploy/terraform/modules/self-hosted/cell-application/main.tf`](../../../deploy/terraform/modules/self-hosted/cell-application/main.tf) | Added | [1-34](../../../deploy/terraform/modules/self-hosted/cell-application/main.tf#L1) | +34 | −0 |
| [`deploy/terraform/modules/self-hosted/cell-application/outputs.tf`](../../../deploy/terraform/modules/self-hosted/cell-application/outputs.tf) | Added | [1-4](../../../deploy/terraform/modules/self-hosted/cell-application/outputs.tf#L1) | +4 | −0 |
| [`deploy/terraform/modules/self-hosted/cell-application/tests/cell_application.tftest.hcl`](../../../deploy/terraform/modules/self-hosted/cell-application/tests/cell_application.tftest.hcl) | Added | [1-104](../../../deploy/terraform/modules/self-hosted/cell-application/tests/cell_application.tftest.hcl#L1) | +104 | −0 |
| [`deploy/terraform/modules/self-hosted/cell-application/variables.tf`](../../../deploy/terraform/modules/self-hosted/cell-application/variables.tf) | Added | [1-68](../../../deploy/terraform/modules/self-hosted/cell-application/variables.tf#L1) | +68 | −0 |
| [`deploy/terraform/modules/self-hosted/cell-application/versions.tf`](../../../deploy/terraform/modules/self-hosted/cell-application/versions.tf) | Added | [1-10](../../../deploy/terraform/modules/self-hosted/cell-application/versions.tf#L1) | +10 | −0 |
| [`deploy/terraform/modules/self-hosted/cell/main.tf`](../../../deploy/terraform/modules/self-hosted/cell/main.tf) | Added | [1-31](../../../deploy/terraform/modules/self-hosted/cell/main.tf#L1) | +31 | −0 |
| [`deploy/terraform/modules/self-hosted/cell/outputs.tf`](../../../deploy/terraform/modules/self-hosted/cell/outputs.tf) | Added | [1-9](../../../deploy/terraform/modules/self-hosted/cell/outputs.tf#L1) | +9 | −0 |
| [`deploy/terraform/modules/self-hosted/cell/tests/cell.tftest.hcl`](../../../deploy/terraform/modules/self-hosted/cell/tests/cell.tftest.hcl) | Added | [1-104](../../../deploy/terraform/modules/self-hosted/cell/tests/cell.tftest.hcl#L1) | +104 | −0 |
| [`deploy/terraform/modules/self-hosted/cell/variables.tf`](../../../deploy/terraform/modules/self-hosted/cell/variables.tf) | Added | [1-19](../../../deploy/terraform/modules/self-hosted/cell/variables.tf#L1) | +19 | −0 |
| [`deploy/terraform/modules/self-hosted/cell/versions.tf`](../../../deploy/terraform/modules/self-hosted/cell/versions.tf) | Added | [1-14](../../../deploy/terraform/modules/self-hosted/cell/versions.tf#L1) | +14 | −0 |
| [`deploy/terraform/modules/self-hosted/vault/main.tf`](../../../deploy/terraform/modules/self-hosted/vault/main.tf) | Added | [1-78](../../../deploy/terraform/modules/self-hosted/vault/main.tf#L1) | +78 | −0 |
| [`deploy/terraform/modules/self-hosted/vault/outputs.tf`](../../../deploy/terraform/modules/self-hosted/vault/outputs.tf) | Added | [1-9](../../../deploy/terraform/modules/self-hosted/vault/outputs.tf#L1) | +9 | −0 |
| [`deploy/terraform/modules/self-hosted/vault/tests/vault.tftest.hcl`](../../../deploy/terraform/modules/self-hosted/vault/tests/vault.tftest.hcl) | Added | [1-84](../../../deploy/terraform/modules/self-hosted/vault/tests/vault.tftest.hcl#L1) | +84 | −0 |
| [`deploy/terraform/modules/self-hosted/vault/variables.tf`](../../../deploy/terraform/modules/self-hosted/vault/variables.tf) | Added | [1-25](../../../deploy/terraform/modules/self-hosted/vault/variables.tf#L1) | +25 | −0 |
| [`deploy/terraform/modules/self-hosted/vault/versions.tf`](../../../deploy/terraform/modules/self-hosted/vault/versions.tf) | Added | [1-18](../../../deploy/terraform/modules/self-hosted/vault/versions.tf#L1) | +18 | −0 |
| [`tests/ci/dev_cell/test_dev_cell_workflow.py`](../../../tests/ci/dev_cell/test_dev_cell_workflow.py) | Added | [1-136](../../../tests/ci/dev_cell/test_dev_cell_workflow.py#L1) | +136 | −0 |
| [`tests/conventions/mono_repo/test_terraform_layout.py`](../../../tests/conventions/mono_repo/test_terraform_layout.py) | Modified | [5](../../../tests/conventions/mono_repo/test_terraform_layout.py#L5), [8-9](../../../tests/conventions/mono_repo/test_terraform_layout.py#L8), [15-28](../../../tests/conventions/mono_repo/test_terraform_layout.py#L15), [39-42](../../../tests/conventions/mono_repo/test_terraform_layout.py#L39), [60-97](../../../tests/conventions/mono_repo/test_terraform_layout.py#L60), [104-106](../../../tests/conventions/mono_repo/test_terraform_layout.py#L104) | +62 | −3 |
| [`tests/deploy/charts/test_cell_chart.py`](../../../tests/deploy/charts/test_cell_chart.py) | Added | [1-139](../../../tests/deploy/charts/test_cell_chart.py#L1) | +139 | −0 |
| [`tests/deploy/charts/test_database_chart.py`](../../../tests/deploy/charts/test_database_chart.py) | Added | [1-158](../../../tests/deploy/charts/test_database_chart.py#L1) | +158 | −0 |
| [`tests/deploy/charts/test_object_storage_chart.py`](../../../tests/deploy/charts/test_object_storage_chart.py) | Added | [1-112](../../../tests/deploy/charts/test_object_storage_chart.py#L1) | +112 | −0 |
| [`tests/deploy/charts/test_valkey_chart.py`](../../../tests/deploy/charts/test_valkey_chart.py) | Added | [1-106](../../../tests/deploy/charts/test_valkey_chart.py#L1) | +106 | −0 |
| [`tests/deploy/charts/test_vault_config_chart.py`](../../../tests/deploy/charts/test_vault_config_chart.py) | Added | [1-192](../../../tests/deploy/charts/test_vault_config_chart.py#L1) | +192 | −0 |
| [`tests/deploy/environments/test_dev_environment.py`](../../../tests/deploy/environments/test_dev_environment.py) | Added | [1-114](../../../tests/deploy/environments/test_dev_environment.py#L1) | +114 | −0 |
| [`tests/deploy/images/test_postgres_image.py`](../../../tests/deploy/images/test_postgres_image.py) | Added | [1-37](../../../tests/deploy/images/test_postgres_image.py#L1) | +37 | −0 |
| [`tests/deploy/scripts/test_dev_cell_script.py`](../../../tests/deploy/scripts/test_dev_cell_script.py) | Added | [1-140](../../../tests/deploy/scripts/test_dev_cell_script.py#L1) | +140 | −0 |
| **82 files** | | | **+3587** | **−25** |
<!-- /changes -->

- [`deploy/terraform/modules/self-hosted/`](../../../deploy/terraform/modules/self-hosted/argocd/main.tf): four new modules, `argocd`, `vault`, `cell` and `cell-application`, each with variables, outputs, pinned providers and a `terraform test` with mock providers. The vault binding is at [`deploy/terraform/modules/self-hosted/vault/main.tf:62-78`](../../../deploy/terraform/modules/self-hosted/vault/main.tf#L62-L78).
- [`deploy/terraform/cells/dev-branch/`](../../../deploy/terraform/cells/dev-branch/main.tf): the new root of every branch cell, with its lock file, variables, example variables and test.
- [`deploy/terraform/cells/dev/`](../../../deploy/terraform/cells/dev/main.tf): the existing root gains the optional Argo CD bootstrap (lines [`51-61`](../../../deploy/terraform/cells/dev/main.tf#L51-L61)), its variables ([`deploy/terraform/cells/dev/variables.tf:77-120`](../../../deploy/terraform/cells/dev/variables.tf#L77-L120)), providers and tests.
- [`deploy/charts/`](../../../deploy/charts/cell/Chart.yaml): the umbrella chart `cell` and the charts `database`, `valkey`, `object-storage` and `vault-config`.
- [`deploy/charts/vault-config/templates/_helpers.tpl:1-12`](../../../deploy/charts/vault-config/templates/_helpers.tpl#L1-L12): the object name is the literal `vault-config`, because the umbrella chart aliases the chart as `vaultConfig`, which is not a valid object name.
- [`deploy/environments/dev/`](../../../deploy/environments/dev/values.yaml): the cell values and the platform Applications (CloudNativePG, KEDA, KEDA HTTP add-on).
- [`deploy/images/postgres/Dockerfile`](../../../deploy/images/postgres/Dockerfile): the PostgreSQL 16 image with TimescaleDB on top of the CNPG PostGIS image.
- [`deploy/scripts/dev-cell.sh`](../../../deploy/scripts/dev-cell.sh) and [`.github/workflows/dev-cell.yml`](../../../.github/workflows/dev-cell.yml): request and close a cell, by hand or from GitHub.
- [`.github/workflows/terraform.yml`](../../../.github/workflows/terraform.yml): the check matrix gains the new modules and root.
- [`deploy/README.md`](../../../deploy/README.md), [`deploy/terraform/README.md`](../../../deploy/terraform/README.md) and [`AGENT.md`](../../../AGENT.md): how to bootstrap, request and close a cell, and the layout rules.
- [`tests/deploy/`](../../../tests/deploy/charts/test_cell_chart.py), [`tests/ci/dev_cell/test_dev_cell_workflow.py`](../../../tests/ci/dev_cell/test_dev_cell_workflow.py) and [`tests/conventions/mono_repo/test_terraform_layout.py`](../../../tests/conventions/mono_repo/test_terraform_layout.py): tests of the charts, the environment, the image, the script, the workflow and the Terraform layout.
- [`.claude/workflows/ticket-run.js:236-285`](../../../.claude/workflows/ticket-run.js#L236-L285): a harness change outside the ticket. A review finding now goes to every task that owns a file it names. It rides in this ticket's single commit.
- [`.gitignore`](../../../.gitignore): an ignore entry for an editor tool, unrelated to the ticket (see the follow-ups).

## 🧪 How to test it

```bash
uv run pytest tests/deploy -n 2
uv run pytest tests/ci/dev_cell tests/conventions/mono_repo -n 2
for d in deploy/terraform/modules/self-hosted/{argocd,vault,cell,cell-application} deploy/terraform/cells/dev deploy/terraform/cells/dev-branch; do (cd $d && terraform init -backend=false && terraform validate && terraform test); done
bash deploy/scripts/dev-cell.sh --dry-run up my-branch
python3 .claude/skills/write-specs/scripts/specs.py check
```

The chart rendering tests need `helm` and skip without it. A real cell needs the P-06 cluster: the person runs the first `up` and `down`.

## 🔗 Evidence

- [pytest](tests-evidences/pytest.txt): 1382 passed, 30 skipped (the chart rendering tests, Helm is missing).
- [Terraform tests of the vault module](tests-evidences/terraform-test-deploy-terraform-modules-self-hosted-vault.txt), [of the dev-branch root](tests-evidences/terraform-test-deploy-terraform-cells-dev-branch.txt), [of the dev root](tests-evidences/terraform-test-deploy-terraform-cells-dev.txt), [of the argocd module](tests-evidences/terraform-test-deploy-terraform-modules-self-hosted-argocd.txt), [of the cell module](tests-evidences/terraform-test-deploy-terraform-modules-self-hosted-cell.txt) and [of the cell-application module](tests-evidences/terraform-test-deploy-terraform-modules-self-hosted-cell-application.txt).
- [Terraform validate of the dev-branch root](tests-evidences/terraform-validate-deploy-terraform-cells-dev-branch.txt) and [fmt](tests-evidences/terraform-fmt.txt).
- [ruff check](tests-evidences/ruff-check.txt), [ruff format](tests-evidences/ruff-format.txt), [mypy](tests-evidences/mypy.txt), [specs check](tests-evidences/specs-check.txt), [ticket references](tests-evidences/ticket-refs.txt) and [plan view](tests-evidences/plan-view.txt).

## 📝 Assumptions accepted

- No new assumption in the fix round. The assumptions of round 1 still hold: a cell is a namespace on the shared k3s cluster, one root with one state per branch serves every cell, the trigger is manual creation plus automatic destruction on branch deletion, and "in minutes" is not quantified (see [PLAN.md](PLAN.md)).

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| [`deploy/charts/database/templates/cluster.yaml:23-29`](../../../deploy/charts/database/templates/cluster.yaml#L23-L29) | The service roles and schemas are created by `postInitApplicationSQL`, which runs only when the cluster is first created. A service added to `global.services` of a running cell gets a vault role whose `IN ROLE` refers to a missing group role, and the first credential read fails. Document it, or move the creation into the idempotent vault-config Job. |
| [`deploy/README.md:122`](../../../deploy/README.md#L122) | "each part in its own namespace" is wrong: every part of a cell sits in the one namespace of the cell. Reword it. |
| [`.gitignore:43`](../../../.gitignore#L43) | `.VSCodeCounter` is unrelated to T0.08, unanchored, and the file now has no final newline. Move it to a separate change, or anchor it as `/.VSCodeCounter/` and add the newline. |
| [`.claude/workflows/ticket-run.js:236-285`](../../../.claude/workflows/ticket-run.js#L236-L285) | The harness change is outside the ticket and rides in its single commit. Record the person's decision on a separate commit in PROGRESS.md. |
| [`tests/deploy/charts/test_vault_config_chart.py`](../../../tests/deploy/charts/test_vault_config_chart.py) | These tests render the chart alone, so `.Chart.Name` is always `vault-config` and the alias defect cannot show. Add a test, needing no Helm, that refuses `.Chart.Name` in the object names of a sub-chart the cell aliases. |
| [`deploy/terraform/modules/self-hosted/vault/tests/vault.tftest.hcl:5-62`](../../../deploy/terraform/modules/self-hosted/vault/tests/vault.tftest.hcl#L5-L62) | No run checks the new `kubernetes_cluster_role_binding_v1.auth_delegator`. Assert its name (contains the namespace), role `system:auth-delegator` and subject (`openbao`, the cell namespace). |
| [`deploy/terraform/modules/self-hosted/vault/main.tf:62-78`](../../../deploy/terraform/modules/self-hosted/vault/main.tf#L62-L78) | The mocks cannot show that two cells coexist, and Helm is not installed for the checks. Add an integration check with two branch cells side by side once a cluster or kind is available, and install Helm for the checks and CI so the 30 chart tests run. |
