# Deploy: the dev cell platform and branch cells

This folder holds what runs Swarm on the dev cluster: the Terraform roots that create the cells, the Helm charts that
describe what a cell runs, the desired state that Argo CD applies, the image of the database, and the script that
requests and closes a branch's cell. This page is for the person who runs the dev cells. It says what each part holds,
what you need, how to bootstrap the shared cluster once, how a branch gets its cell, how a service gets its database
credentials, and what the workflow needs. The decisions behind it are in
[🌐 Where it runs](../docs/specs/technical/09-deployment.md#providers),
[🧰 Infrastructure as code](../docs/specs/technical/09-deployment.md#iac),
[🚢 Delivery](../docs/specs/technical/09-deployment.md#delivery) and
[🌱 Environments](../docs/specs/technical/09-deployment.md#environments). The machines come from
[🤝 P-06](../docs/specs/roadmap/11-hardware-and-partners.md#p-06), and the work is ticket
[T0.08](../docs/tickets/T0.08/TICKET.md).

> [!NOTE]
> Terraform creates the empty cell, and Argo CD deploys Swarm on it. Terraform never installs the application charts
> itself: it only creates the namespace, the vault, and the Argo CD Application that points at the charts of this
> repository.

## Layout

| Path | Holds |
| --- | --- |
| [`terraform/`](terraform/README.md) | The Terraform modules and cell roots. `cells/dev` is the shared dev cluster, `cells/dev-branch` is one branch cell |
| `charts/cell` | The umbrella chart of a cell. It brings the database, Valkey, object storage and the vault configuration |
| `charts/database` | The CloudNativePG `Cluster` and the PgBouncer `Pooler` in transaction mode, with one role per service |
| `charts/valkey` | Valkey, the cache of the cell |
| `charts/object-storage` | MinIO, the object storage of the cell |
| `charts/vault-config` | The job that configures the vault: the database connection, one role and one Kubernetes login per service |
| `environments/dev/platform` | The Argo CD Applications of the cluster-wide operators: CloudNativePG, KEDA and the KEDA HTTP add-on |
| `environments/dev/values.yaml` | The values of every dev cell: the services, the sizes of the volumes, one instance of each part |
| `images/postgres` | The `Dockerfile` of the PostgreSQL image, with PostGIS and TimescaleDB |
| `scripts/dev-cell.sh` | Requests (`up`) or closes (`down`) the cell of a branch, by running the `cells/dev-branch` root |

The workflow that calls the script is [`.github/workflows/dev-cell.yml`](../.github/workflows/dev-cell.yml).

## Prerequisites

- **Terraform 1.10 or later** (`required_version = ">= 1.10"`), on the workstation that runs the roots.
- **Helm 3** and **kubectl**, to check the platform and to read the cluster.
- **Docker**, to build the PostgreSQL image.
- **The kubeconfig of the T0.01 dev root.** The `cells/dev` root writes it to the path of its `kubeconfig_path`, outside
  the repository. Export it as `KUBECONFIG` before you use `kubectl` or the script.
- **A backend configuration file and the variables files, kept outside the repository.** The backend file holds the
  remote state settings, and it is passed with `-backend-config`. The dev root variables file holds the machines and
  the platform settings. The dev-branch variables file holds the kubeconfig path, the repository URL, the database image
  and the chart versions. The examples are `cells/dev/terraform.tfvars.example` and
  `cells/dev-branch/terraform.tfvars.example`. Copy them to a file outside the repository and edit the copy.

> [!CAUTION]
> Never commit a backend file, a variables file, a kubeconfig or a key. They hold credentials and addresses of the real
> machines.

## Bootstrap once per cluster

The dev cluster is built in two applies of the `cells/dev` root, as the [Terraform guide](terraform/README.md) explains.

1. **Build the cluster.** Apply the dev root (T0.01) with `platform_enabled = false`. It provisions the machines, the
   firewall, k3s and the kubeconfig.
2. **Install the platform.** Apply the same root again with `platform_enabled = true`, and set `repository_url`,
   `argocd_chart_version`, `argocd_apps_chart_version` and `platform_revision` (the branch, tag or commit that Argo CD
   follows, `develop` by default). This installs Argo CD and the root Application `platform`. That Application deploys
   the cluster-wide operators of `environments/dev/platform`: the CloudNativePG operator, KEDA and the KEDA HTTP add-on.
3. **Check it.** Every Application must reach the synced and healthy state:

   ```bash
   kubectl -n argocd get applications
   ```

4. **Give Argo CD read access to the repository.** Argo CD must read `repository_url`. If the repository is private, the
   credentials are added to Argo CD outside this repository, and never written in a file of `deploy/`. The files of this
   repository do not set them, so this step is done by the person who runs the cluster.

## The PostgreSQL image

The cell runs the image built from `images/postgres/Dockerfile`: PostgreSQL 16 with PostGIS and TimescaleDB, on the
CloudNativePG base image. Until the image pipeline of [T0.10](../docs/specs/roadmap/01-p0-foundations.md#s02)
builds and pushes it,
you do it by hand:

```bash
docker build -t registry.example.org/swarm/database:1 deploy/images/postgres
docker push registry.example.org/swarm/database:1
```

Then set the same reference as `database_image` in the dev-branch variables file. The `cells/dev-branch` root passes it
to the chart as `database.imageName`, and rendering fails when it is empty. The reference above is an example.

## Request a branch cell

A branch gets its cell with the script, or with the `dev-cell` workflow.

With the script, from the root of the repository:

```bash
export DEV_CELL_BACKEND_CONFIG=/path/outside/repo/backend.hcl
export DEV_CELL_VAR_FILE=/path/outside/repo/dev-branch.tfvars
export KUBECONFIG=/path/outside/repo/dev.kubeconfig
export DEV_CELL_TIMEOUT=15m
bash deploy/scripts/dev-cell.sh --dry-run up my-branch
bash deploy/scripts/dev-cell.sh up my-branch
```

- `DEV_CELL_BACKEND_CONFIG` is the backend configuration file. It is required.
- `DEV_CELL_VAR_FILE` is the dev-branch variables file. It is required.
- `DEV_CELL_TIMEOUT` is how long the script waits for Argo CD to report the Application synced and
  healthy. It defaults to `15m`.
- `KUBECONFIG` is the kubeconfig of the cluster, read by `kubectl`.
- `--dry-run` prints the Terraform and `kubectl` commands with a `+` in front, and runs none of them.

With the workflow, open **Actions**, choose **dev-cell**, then **Run workflow**. Choose `up` or `down`, and give a
`branch` when it is not the branch you dispatch from. The workflow runs the same script, with the secrets of the
section below.

**The cell name** is built by the script from the branch: `cell-`, then the branch in lower case with every run of
characters other than `a` to `z` and `0` to `9` replaced by one hyphen, cut to 30 characters, with leading and trailing
hyphens removed, then `-`, then the first 8 hexadecimal digits of the SHA-256 of the branch name. For example, the
branch `feature/Login` gives `cell-feature-login-` followed by its 8 digits. The digest keeps two branches with the same
slug apart. The name is the namespace of the
cell and the name of its Argo CD Application.

**What a cell holds**, each part in its own namespace, named after the cell:

- **A namespace** named after the cell, labelled `swarm-cell`.
- **An OpenBao vault**, the release `openbao`, in dev server mode, with the root token in the Secret `vault-root-token`.
- **A CloudNativePG database** named `swarm`, with PostGIS and TimescaleDB. Its service `database-rw` is the primary.
- **A PgBouncer pooler** `database-pooler-rw` in transaction mode, in front of the primary.
- **Valkey**, the cache.
- **MinIO**, the object storage, with a 1 GiB volume.

The Argo CD Application of the cell follows the branch (`target_revision` is the branch) and the chart
`deploy/charts/cell`, with the values of `environments/dev/values.yaml`.

## Close a branch cell

A cell is closed in one of two ways:

- **Automatically**, when the branch is deleted: the workflow runs on the `delete` event of the branch and runs `down`.
- **By hand**, with the script or the workflow: `bash deploy/scripts/dev-cell.sh down my-branch`.

`down` runs `terraform destroy` on the `cells/dev-branch` root. Terraform removes the Argo CD Application first, with
its finalizer, so that Argo CD removes what it deployed. Then the vault and the namespace are removed.

> [!CAUTION]
> The cell is lost: its database, its cache and its objects are destroyed with it. Nothing is kept. Export any data you
> need before you close a cell.

## Database and service credentials

The configuration holds **names only**, never a secret. The Secrets are read by the jobs and the pods from the cluster,
and the values never appear in a file of this repository.

A service gets its database credential from the vault, at run time, through this path:

1. The service's pod authenticates to the vault with its Kubernetes service account. The Kubernetes auth role
   `<service>` is bound to the service account `<service>` in the cell namespace, and gives the policy `<service>`.
2. The policy lets the service read `database/creds/<service>` only.
3. The vault creates a PostgreSQL role for the service, a member of the group role `<service>`, valid for the lease
   time. The default TTL is **1 h**, and the lease can be renewed up to **24 h** at most.

The services of the dev cell are `missions`, `fleet`, `processing`, `evidence` and `notifier`, in
`environments/dev/values.yaml`. The vault-config job creates their roles on every sync.

To check that a role can be read, run the read from the vault pod. The pod is `openbao-0` in the cell namespace, which
assumes the chart's default release name `openbao`. The root token is read from the Secret into a shell variable, and
it is never printed:

```bash
NS=cell-my-branch-xxxxxxxx
TOKEN="$(kubectl -n "$NS" get secret vault-root-token -o jsonpath='{.data.token}' | base64 -d)"
kubectl -n "$NS" exec openbao-0 -- \
  env BAO_ADDR=http://127.0.0.1:8200 BAO_TOKEN="$TOKEN" bao read database/creds/missions
```

The command prints a new `username` and `password`, with a `lease_duration` of 1 h. Their presence shows that the vault,
the database connection and the role are working. The token is passed on the command line of the pod, so run this
check on a dev cell only.

> [!WARNING]
> The vault runs in **dev server mode**: it keeps its data in memory, and its unseal and root token come from the chart.
> When its pod restarts, the vault is empty. Run `argocd app sync <cell>` to configure it again: the vault-config job
> is a `PostSync` hook that reruns on every sync. Staging and production need a persistent and sealed mode, which is
> not in this folder.

## The workflow's secrets and variables

The `dev-cell` workflow reads these settings from the repository's settings. None of them is written in the repository.

| Name | Kind | Holds |
| --- | --- | --- |
| `TF_BACKEND_CONFIG` | Secret | The content of the backend configuration file. Written to a file in the runner's temporary folder |
| `DEV_CELL_TFVARS` | Secret | The content of the dev-branch variables file, without `kubeconfig_path`: the workflow appends it, pointing at the kubeconfig it writes. Written to a file in the runner's temporary folder |
| `DEV_CELL_KUBECONFIG` | Secret | The kubeconfig of the cluster. Written to a file in the runner's temporary folder |
| `AWS_ACCESS_KEY_ID` | Secret | The access key of the S3-compatible state store, read by the Terraform backend |
| `AWS_SECRET_ACCESS_KEY` | Secret | The secret key of the S3-compatible state store |
| `DEV_CELL_RUNNER` | Variable | The label of the runner that runs the job. Defaults to `ubuntu-latest` when empty |

The job fails before it runs Terraform when one of `TF_BACKEND_CONFIG`, `DEV_CELL_TFVARS` or `DEV_CELL_KUBECONFIG` is
missing or empty. The files are written with the mode `077`, so only the runner reads them.

> [!IMPORTANT]
> The runner must reach the cluster API on `6443/tcp`. The firewall of the cluster allows the cell machines and the
> CIDRs of `api_allowed_cidrs` of the dev root. When the runner is outside those networks, set `DEV_CELL_RUNNER` to a
> self-hosted runner inside them, and add its network to `api_allowed_cidrs`.

## How each acceptance criterion is checked

The ticket's acceptance criteria are checked as follows. The criteria are in
[TICKET.md](../docs/tickets/T0.08/TICKET.md#acceptance-criteria).

1. **A branch gets its cell in minutes, created by Terraform, with the platform deployed by Argo CD.** Request the cell
   with `dev-cell.sh up <branch>`, or the workflow. The script prints `Cell <name> is ready after <n> seconds.` once the
   Application is synced and healthy. Check it with `kubectl -n argocd get applications`, which lists the Application
   of the cell. The duration of the run is the time the person measures: the specifications do not quantify "in
   minutes".
2. **When the branch closes, the cell is lost and its infrastructure is destroyed by Terraform.** Delete the branch, or
   run `dev-cell.sh down <branch>`. Check that the namespace is gone with `kubectl get namespace <cell>`, and that the
   `cells/dev-branch` state no longer lists the cell.
3. **A service gets its database credential from the vault, never from a file.** Run the
   `bao read database/creds/missions` command of the section above and check that it returns a `username` and a `password` with a 1 h lease. Check that no
   file of the service holds the credential.

The `--dry-run` output and the Terraform tests of `cells/dev-branch/tests` check the commands and the variables without
creating anything.
