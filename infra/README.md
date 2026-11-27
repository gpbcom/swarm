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
| `charts/nats` | The NATS cluster of the cell: 3 servers, the JetStream domain `cell`, the Operator trust, and the leaf node listener, off until it is enabled |
| `charts/nats-leaf` | The NATS leaf node of one edge: its JetStream domain, unique to the edge, and its link to the core over mTLS |
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
   credentials are added to Argo CD outside this repository, and never written in a file of `infra/`. The files of this
   repository do not set them, so this step is done by the person who runs the cluster.

## The PostgreSQL image

The cell runs the image built from `images/postgres/Dockerfile`: PostgreSQL 16 with PostGIS and TimescaleDB, on the
CloudNativePG base image. Until the image pipeline of [T0.10](../docs/specs/roadmap/01-p0-foundations.md#s02)
builds and pushes it,
you do it by hand:

```bash
docker build -t registry.example.org/swarm/database:1 infra/images/postgres
docker push registry.example.org/swarm/database:1
```

Then set the same reference as `database_image` in the dev-branch variables file. The `cells/dev-branch` root passes it
to the chart as `database.imageName`, and rendering fails when it is empty. The reference above is an example.

## Observability in the cell

A cell runs the observability charts beside the data services, all in the namespace of the cell, and the umbrella
chart `charts/cell` enables them:

| Chart | Port | Kept | Holds |
| --- | --- | --- | --- |
| `charts/otel-collector` | 4317 (OTLP gRPC), 4318 (OTLP/HTTP) | Buffers only | The collector the apps send to. It samples the traces: 100 % of the errors and of the requests over the slow threshold (250 ms), and 5 % of the rest |
| `charts/tempo` | 3200 (HTTP), 4317 (OTLP gRPC) | 14 days (`retention: 336h`) | The traces |
| `charts/prometheus` | 9090 | 15 days (`retention: 15d`) | The metrics |
| `charts/loki` | 3100 | 30 days (`retention: 720h`) | The logs |
| `charts/grafana` | 3000 | Its dashboards | The Grafana of the cell, with the datasources of the four backends and the dashboards of `charts/observability/dashboards/` |

The collector forwards the traces to Tempo, the metrics to Prometheus and the logs to Loki. Its own list of
redacted keys (`redactedKeys`) complements the redaction of the apps (see [`backend/README.md`](../backend/README.md#observability-the-signals-section)).

Grafana reads its admin password from the Secret named by `adminSecretName` in its values, `grafana-admin` by default.
Terraform and Argo CD do not write that Secret: the person who runs the cell creates it in the namespace before Grafana
starts, under the keys `adminUserKey` and `adminPasswordKey` of its values, and never in a file of this repository.

**To open Grafana in a dev cell**, forward its port to your workstation, then log in as `admin` with the password of
the Secret:

```bash
export KUBECONFIG=/path/outside/repo/dev.kubeconfig
kubectl -n cell-<branch name> port-forward svc/grafana 3000:3000
```

Open `http://localhost:3000`. The cell name is the one the script prints (see [Request a branch cell](#request-a-branch-cell)).

**To follow one SquadFrame's trace** from the flight engine through the gateway, take the `trace_parent` of the frame
(a W3C `traceparent`, `00-<trace id>-<span id>-<flags>`), which the frame carries to the browser. In Grafana, open
Explore on the Tempo datasource and search the trace id, the middle part of that value. The trace shows the spans of the
flight engine and those of the gateway that handled the same request, linked through the `traceparent` header of the
NATS message.

## Request a branch cell

A branch gets its cell with the script, or with the `dev-cell` workflow.

With the script, from the root of the repository:

```bash
export DEV_CELL_BACKEND_CONFIG=/path/outside/repo/backend.hcl
export DEV_CELL_VAR_FILE=/path/outside/repo/dev-branch.tfvars
export KUBECONFIG=/path/outside/repo/dev.kubeconfig
export DEV_CELL_TIMEOUT=15m
bash infra/scripts/dev-cell.sh --dry-run up my-branch
bash infra/scripts/dev-cell.sh up my-branch
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
- **A NATS cluster** of 3 servers, from `charts/nats`, described in [The NATS of a cell](#the-nats-of-a-cell).

The Argo CD Application of the cell follows the branch (`target_revision` is the branch) and the chart
`infra/charts/cell`, with the values of `environments/dev/values.yaml`.

## Close a branch cell

A cell is closed in one of two ways:

- **Automatically**, when the branch is deleted: the workflow runs on the `delete` event of the branch and runs `down`.
- **By hand**, with the script or the workflow: `bash infra/scripts/dev-cell.sh down my-branch`.

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

## The NATS of a cell

Each cell runs its own NATS cluster, from `charts/nats`, as the [cells](../docs/specs/technical/01-architecture.md#cells)
and the [storage overview](../docs/specs/technical/03-storage.md#overview) describe. The chart is the `nats` sub-chart of
`charts/cell`, and `environments/dev/values.yaml` sets its JetStream file storage to 1Gi for the dev cells.

- **A cluster of 3 servers** (`replicas: 3`), with the JetStream domain `cell`. The clients create each stream with 3
  replicas, so a stream survives the loss of one server.
- **Operator mode with the full resolver.** The servers trust the dev Operator through `auth.operatorJwt`, and keep the
  accounts in their resolver. The chart holds public values only.
- **One account per Operator**, limited to the subjects `op.<operator_id>.…`. A service acting for one Operator cannot
  publish or subscribe on another Operator's subjects. See
  [BR-008: Operator isolation](../docs/specs/functional/business-rules/BR-008-operator-isolation.md) and
  [roles and Operator isolation](../docs/specs/technical/06-security.md#authorisation).
- **Service, edge and simulated credentials are kept apart.** `CredentialIssuer` issues each kind on its own: `service`,
  `edge` and `simulated`. A simulated Squad uses its own credentials, never those of a real one, as the
  [simulator](../docs/specs/technical/04-engine.md#simulator) and
  [BR-014: Simulation isolation](../docs/specs/functional/business-rules/BR-014-simulation-isolation.md) require. A
  system credential is never issued for an Operator.
- **The leaf node listener over mTLS.** Port `7422` is open only when `leafnodes.enabled` is `true` and the Secret named
  by `leafnodes.tls.secretName`, `nats-leafnodes-tls`, exists. It stays off until both are true.

## The Simulator of a cell

The simulator runs in a cell from `charts/simulator`, a sub-chart of `charts/cell`. It is disabled by default, and
`simulator.enabled` turns it on. It flies only simulated Squads, as the
[simulator](../docs/specs/technical/04-engine.md#simulator) and
[BR-014: Simulation isolation](../docs/specs/functional/business-rules/BR-014-simulation-isolation.md) require.

When enabling it, give:

- `simulator.operatorId`, the Operator whose simulated Squads it flies;
- the image tags of the simulator and of the synthetic Drones;
- the Secret `simulator-nats-credentials`, holding a creds file of kind `simulated`, issued by `CredentialIssuer`. The
  Secret is created in the cluster and is never written in the repository.

The chart starts three kinds of workloads:

- the simulator itself;
- 10 synthetic Drones, written in Rust;
- one PX4 SITL Drone.

A NetworkPolicy lets only the simulator reach the synthetic and PX4 Drones. No other workload of the cell can address
them, so a simulated Drone never receives a command meant for a real one.

## Create the dev operator once

The person creates the dev Operator and its SYS account once, outside the charts and the repository. For example, with
`nsc`:

```bash
nsc add operator --generate-signing-key --sys --name swarm-dev
```

Then:

1. Copy the operator JWT, the public key of the SYS account and the SYS account JWT.
2. Put them in the three Terraform variables of the dev-branch variables file: `nats_operator_jwt`,
   `nats_system_account` and `nats_system_account_jwt`. They are passed to the chart as `nats.auth.operatorJwt`,
   `nats.auth.systemAccount` and `nats.auth.systemAccountJwt`.
3. Keep the seeds in the vault, never in the repository.

> [!CAUTION]
> The seeds are private keys. Never write a seed in the repository, in a variables file of the repository, in a chart
> value, in a log or in a ticket. Keep them in the vault only. Anyone with a seed can sign accounts for the Operator.

The Operator accounts are not in the charts. At run time, `swarm_service.shared.accounts` issues each account with `AccountIssuer`,
and `swarm_clients.shared.nats` pushes it to the servers with `AccountResolverClient`.

## Leaf node of an edge

The leaf node of an edge runs from `charts/nats-leaf`. It connects the edge to the cell's NATS over mTLS, as the
[edge and core](../docs/specs/technical/01-architecture.md#edge-and-core) and the
[links](../docs/specs/technical/06-security.md#links) pages describe. Its values are:

- `remote.url`, the `tls://` address of the cell's leaf node listener. It is required, and rendering fails without it.
- `jetstream.domain`, the JetStream domain of the edge. It is required, must be unique per edge, and must not be `cell`.
- `jetstream.fileStorage.size`, 5Gi by default. The edge buffers its messages here while the core is unreachable.
- `remote.credentialsSecret` and `remote.tlsSecret`, the names of the two Secrets below.

Create the two Secrets in the namespace of the edge before the chart starts:

- **`nats-leaf-credentials`**, with the key `edge.creds`. `CredentialIssuer` issues it with the kind `edge`, for the
  account of the Operator.
- **`nats-leaf-tls`**, with the keys `tls.crt`, `tls.key` and `ca.crt`, the certificate of the edge and the CA of the
  cell.

Each edge has its own credential, so one can be revoked without cutting the others. To revoke it, `AccountIssuer.revoke`
takes the public key of the edge's user, and returns the account with that key revoked. The new account is then pushed
with `AccountResolverClient`. The
revoked credential is then refused, and the other edges still connect.

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

### The NATS criteria of T0.09

The three acceptance criteria of [T0.09](../docs/tickets/T0.09/TICKET.md#acceptance-criteria) are checked by these tests.
Run each with `uv run pytest`, from the root of the repository:

1. **An Operator's account refuses a publication on another Operator's subject.**
   `uv run pytest tests/infra/nats/test_operator_isolation.py`, for [BR-008](../docs/specs/functional/business-rules/BR-008-operator-isolation.md).
2. **A leaf node cut for one minute replays its messages in order.**
   `uv run pytest tests/infra/nats/leaf`, for [BR-008](../docs/specs/functional/business-rules/BR-008-operator-isolation.md).
3. **Simulated Squads use credentials separate from those of real Squads.**
   `uv run pytest tests/infra/nats/test_simulated_credentials.py`, for [BR-014](../docs/specs/functional/business-rules/BR-014-simulation-isolation.md).

These tests start real `nats-server` processes. They need `nats-server` on `PATH`, and they skip when it is missing. CI
installs a pinned `nats-server` before it runs them.
