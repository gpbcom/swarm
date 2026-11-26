# T0.08: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🎯 Constraints

- A branch gets its cell, with Terraform creating its infrastructure and Argo CD deploying the platform; closing the branch destroys it with Terraform. Database credentials come from the vault, never from a file ([TICKET.md](TICKET.md), acceptance criteria 1 to 3).
- Terraform creates the empty cell, Helm and Argo CD deploy on it, and the desired state lives in `deploy/environments` ([🚢 Deployment: delivery](../../specs/technical/09-deployment.md#delivery), [🧰 Deployment: infrastructure as code](../../specs/technical/09-deployment.md#iac)).
- The k3s machines are fixed (P-06, T0.01), so Terraform cannot create machines per branch ([PLAN.md](PLAN.md)).
- Configuration holds names, never secrets ([🔑 Security: secrets and keys](../../specs/technical/06-security.md#secrets)).
- Several branch cells must live side by side on one cluster, so no cluster-scoped name may be shared between them.
- The tests come first, with Terraform native tests using mock providers, and Helm is not installed for the checks, so the chart rendering tests skip ([REVIEW.md](REVIEW.md)).

## ⚖️ Choices at a glance

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | What a branch cell is | A namespace on the shared k3s cluster | A cluster per branch | Cells share the nodes and the cluster-wide operators |
| [D2](#d2) | The auth-delegator binding of the vault | A Terraform binding named after the namespace | The chart's binding, with a unique release name | One more resource, and a dependency on the chart's ServiceAccount name |
| [D3](#d3) | The ServiceAccount name of the vault | Pinned to the release name | Hard-coded `openbao` or the chart's computed name | One more chart value |
| [D4](#d4) | Terraform roots for branch cells | One root, one state per branch | A new root per cell | The script must pass the backend key every time |
| [D5](#d5) | What creates and closes a cell | A script and a manual workflow, destruction on branch deletion | Automatic creation on push or a pull request label | A person must ask for each cell |
| [D6](#d6) | The cell name | `cell-<slug>-<8 hex of sha256>` | The plain branch slug | A longer, less readable name |
| [D7](#d7) | The vault | OpenBao in dev server mode | HashiCorp Vault, or a persistent sealed mode | Not persistent, so dev cells only |
| [D8](#d8) | The vault configuration | An Argo CD PostSync Job, idempotent | Terraform resources on the vault | Configuration is a shell script, checked by reading |
| [D9](#d9) | The object name in `vault-config` | A literal, `vault-config` | `.Chart.Name` | The name no longer follows the chart's name |
| [D10](#d10) | Argo CD and the operators | Installed once per cluster, behind `platform_enabled` | Installed in every cell | A second apply on the dev root |
| [D11](#d11) | PgBouncer | A CloudNativePG `Pooler` | A separate PgBouncer chart | Tied to the operator |

## <a id="d1"></a>D1: What a branch cell is

**Chosen:** a namespace on the shared k3s cluster · **Where:** [`infra/terraform/modules/self-hosted/cell/main.tf:1-14`](../../../infra/terraform/modules/self-hosted/cell/main.tf#L1-L14) · **Source:** [PLAN.md](PLAN.md)

| Option | For | Against |
| --- | --- | --- |
| ✅ A namespace per branch | The P-06 machines are fixed, so only a namespace can be created per branch; it is created and destroyed in minutes | Cells share nodes, and the cluster-scoped objects must be named per cell (see D2) |
| A cluster per branch | Full isolation | Terraform cannot create machines in this repository, so it is not possible with T0.01 |

**Trade-off:** isolation is by namespace, not by machine. This is acceptable for dev cells with simulated Drones only ([🌱 Deployment: environments](../../specs/technical/09-deployment.md#environments)).

**Revisit when:** a cloud provider with machines created on demand is used for dev cells.

## <a id="d2"></a>D2: The auth-delegator binding of the vault

**Chosen:** disable the chart's binding and create `kubernetes_cluster_role_binding_v1.auth_delegator`, named `<namespace>-openbao-auth-delegator` · **Where:** [`infra/terraform/modules/self-hosted/vault/main.tf:35-37`](../../../infra/terraform/modules/self-hosted/vault/main.tf#L35-L37) and [`infra/terraform/modules/self-hosted/vault/main.tf:62-78`](../../../infra/terraform/modules/self-hosted/vault/main.tf#L62-L78) · **Source:** K15, found by the review of round 1

| Option | For | Against |
| --- | --- | --- |
| ✅ A Terraform binding per namespace | The cluster-scoped name is unique per cell; the module's interface and the vault address are unchanged; Terraform deletes it on destroy | One more resource, and it depends on the ServiceAccount name (D3) |
| Keep the chart's binding, make the release name unique per cell | No extra resource | The chart's binding is named after the release (`openbao-server-binding`), and the release name fixes the vault address that the K02 test fixes |
| A cluster-wide lock, or no binding | No new resource | The worker gave no reason to prefer it, and without the binding Kubernetes auth cannot review tokens |

**Trade-off:** a resource the chart used to own is now owned by the module. The binding is not asserted by any test yet (see the follow-ups in [EXPLAIN.md](EXPLAIN.md)).

**Revisit when:** the chart makes the binding's name configurable, or a cluster to run two cells side by side is available to test it.

## <a id="d3"></a>D3: The ServiceAccount name of the vault

**Chosen:** `server.serviceAccount.name = var.release_name` · **Where:** [`infra/terraform/modules/self-hosted/vault/main.tf:38-40`](../../../infra/terraform/modules/self-hosted/vault/main.tf#L38-L40) · **Source:** K15

| Option | For | Against |
| --- | --- | --- |
| ✅ Pin it to the release name | The subject of the binding ([`main.tf:73-77`](../../../infra/terraform/modules/self-hosted/vault/main.tf#L73-L77)) is right for any release name | One extra chart value |
| Hard-code `openbao` | Simple | Wrong as soon as `release_name` is overridden |
| Rely on the chart's computed fullname | No extra value | The binding would depend on how the chart computes the name |

**Trade-off:** one more chart value, for a deterministic subject.

**Revisit when:** the chart changes how it names its ServiceAccount.

## <a id="d4"></a>D4: Terraform roots for branch cells

**Chosen:** one root, `cells/dev-branch`, with one state per branch (key `dev-branch/<cell>.tfstate`) · **Where:** [`infra/terraform/cells/dev-branch/versions.tf:19-21`](../../../infra/terraform/cells/dev-branch/versions.tf#L19-L21) · **Source:** [PLAN.md](PLAN.md)

| Option | For | Against |
| --- | --- | --- |
| ✅ One root, one state per branch | A cell for a new branch needs no pull request; destroying a cell removes only its state | The key is passed by [`infra/scripts/dev-cell.sh:91-93`](../../../infra/scripts/dev-cell.sh#L91-L93), so running `terraform` by hand needs the same key |
| One root per cell (the rule "a new cell is a new root and a pull request") | Matches the documented layout | The plan records that it cannot apply to cells created on demand |

**Trade-off:** the layout rule is bent for on-demand cells, and recorded in [`AGENT.md`](../../../AGENT.md).

**Revisit when:** cells stop being per branch.

## <a id="d5"></a>D5: What creates and closes a cell

**Chosen:** creation by a person, with the script or the manual workflow; destruction on request or when the branch is deleted · **Where:** [`.github/workflows/dev-cell.yml:3-17`](../../../.github/workflows/dev-cell.yml#L3-L17) · **Source:** [PLAN.md](PLAN.md), an assumption

| Option | For | Against |
| --- | --- | --- |
| ✅ On demand, destroyed on branch deletion | The roadmap says "on demand"; the specifications do not fix a trigger, so this is the most conservative | Each cell must be asked for |
| Automatic creation on push, or a pull request label | Fewer manual steps | No page of the specifications asks for it, and a cell costs cluster resources |

**Trade-off:** the dispatch workflow applies and destroys with `-auto-approve` ([`infra/scripts/dev-cell.sh:96`](../../../infra/scripts/dev-cell.sh#L96)), so there is no review of a plan.

**Revisit when:** the product owner states how cells are requested.

## <a id="d6"></a>D6: The cell name

**Chosen:** `cell-` + branch slug cut to 30 characters + `-` + 8 hex of sha256 of the branch · **Where:** [`infra/scripts/dev-cell.sh:42-50`](../../../infra/scripts/dev-cell.sh#L42-L50) · **Source:** [PLAN.md](PLAN.md)

| Option | For | Against |
| --- | --- | --- |
| ✅ Slug plus hash | At most 44 characters, a DNS label and a valid Helm release name; two branches that slug alike still get different names | Less readable |
| The plain slug | Readable | Branches such as `a/b` and `a-b` collide, and a long branch breaks the 63-character limit |

**Trade-off:** readability for uniqueness. **Revisit when:** a name length limit other than 63 applies.

## <a id="d7"></a>D7: The vault

**Chosen:** OpenBao, in dev server mode with a random root token kept in a Kubernetes secret · **Where:** [`infra/terraform/modules/self-hosted/vault/main.tf:6-57`](../../../infra/terraform/modules/self-hosted/vault/main.tf#L6-L57) · **Source:** [PLAN.md](PLAN.md), the module header ([`main.tf:1-4`](../../../infra/terraform/modules/self-hosted/vault/main.tf#L1-L4))

| Option | For | Against |
| --- | --- | --- |
| ✅ OpenBao, dev mode | The row accepts either vault; dev mode needs no unseal for ephemeral cells with simulated Drones only | Not persistent and not sealed, so it is not for staging or production |
| HashiCorp Vault | Named in the specification | The reason it was not chosen is not recorded: open point |
| A persistent sealed mode | Suited to staging and production | More set-up for a cell that lives as long as a branch |

**Trade-off:** the token is a Terraform state value, so the state backend must be protected. **Revisit when:** staging or production cells are built.

## <a id="d8"></a>D8: The vault configuration

**Chosen:** an Argo CD PostSync Job that runs an idempotent shell script · **Where:** [`infra/charts/vault-config/templates/job.yaml:8-10`](../../../infra/charts/vault-config/templates/job.yaml#L8-L10) and [`infra/charts/vault-config/templates/configmap.yaml:9-78`](../../../infra/charts/vault-config/templates/configmap.yaml#L9-L78) · **Source:** [PLAN.md](PLAN.md)

| Option | For | Against |
| --- | --- | --- |
| ✅ PostSync Job | Runs after the database exists and on every sync; the service list comes from `global.services`; the token and the password never leave the cluster | A shell script, tested by reading and by chart tests that skip without Helm |
| Terraform vault provider | Declarative | The reason it lost is not recorded: open point |

**Trade-off:** a role is created for a service the database does not know yet when it is added later (the first follow-up in [EXPLAIN.md](EXPLAIN.md)). **Revisit when:** the Job also creates the group roles and schemas.

## <a id="d9"></a>D9: The object name in `vault-config`

**Chosen:** the literal `vault-config` · **Where:** [`infra/charts/vault-config/templates/_helpers.tpl:1-4`](../../../infra/charts/vault-config/templates/_helpers.tpl#L1-L4) · **Source:** fix after round 1, read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ A literal | The umbrella chart aliases the chart as `vaultConfig`, and `.Chart.Name` then gives that alias, which is not a valid Kubernetes name | The name does not follow a renamed chart |
| `.Chart.Name` | The usual Helm convention | Created objects named `vaultConfig` in the cell |

**Trade-off:** a fixed name. The tests render the chart alone, so they could not have caught this (follow-up). **Revisit when:** a test refuses `.Chart.Name` in aliased charts.

## <a id="d10"></a>D10: Argo CD and the operators

**Chosen:** installed once per cluster by the dev root behind `platform_enabled`, with a root Application for the operators · **Where:** [`infra/terraform/cells/dev/main.tf:51-61`](../../../infra/terraform/cells/dev/main.tf#L51-L61) · **Source:** [PLAN.md](PLAN.md)

| Option | For | Against |
| --- | --- | --- |
| ✅ Once per cluster | The operators and CRDs are cluster-wide, so a second installation per cell would collide | Needs a second apply, once the first has built the cluster and written the kubeconfig ([`infra/terraform/cells/dev/variables.tf:77-81`](../../../infra/terraform/cells/dev/variables.tf#L77-L81)) |
| In every cell | Self-contained cells | Cluster-scoped objects shared by all cells |

**Trade-off:** a bootstrap step by the person. **Revisit when:** the cluster is created with the platform in one apply.

## <a id="d11"></a>D11: PgBouncer

**Chosen:** a CloudNativePG `Pooler` in transaction mode · **Where:** [`infra/charts/database/templates/pooler.yaml:7-13`](../../../infra/charts/database/templates/pooler.yaml#L7-L13) · **Source:** [PLAN.md](PLAN.md)

| Option | For | Against |
| --- | --- | --- |
| ✅ CNPG `Pooler` | The specification asks for PgBouncer in transaction mode in front of each primary ([🗄️ Storage: PostgreSQL and PostGIS](../../specs/technical/03-storage.md#postgresql)); the operator manages it with the cluster | Tied to CloudNativePG |
| A separate PgBouncer chart | Independent of the operator | No reason for it is recorded: open point |

**Trade-off:** the pooler follows the operator's lifecycle. **Revisit when:** the database is no longer run by CloudNativePG.

## 📝 Assumptions behind the choices

- A branch's cell is a namespace on the shared k3s cluster: supports [D1](#d1), [D10](#d10).
- One root with a state per branch serves every cell: supports [D4](#d4).
- The most conservative trigger, on demand with destruction on branch deletion: supports [D5](#d5).
- The row leaves HashiCorp Vault or OpenBao open: supports [D7](#d7).
