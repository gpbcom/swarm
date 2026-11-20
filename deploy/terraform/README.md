# Terraform: the dev cell

This folder provisions the infrastructure of Swarm's cells as code, with Terraform. This page is for the person who
runs the dev cell: it says what the folder holds, what you need before the first run, how the state is kept, how the
empty cluster is created, and what the continuous integration checks. The decisions behind it are in
[🧰 Infrastructure as code](../../docs/specs/technical/09-deployment.md#iac) and
[🌐 Where it runs](../../docs/specs/technical/09-deployment.md#providers). The machines come from
[🤝 P-06](../../docs/specs/roadmap/11-hardware-and-partners.md#p-06), and the work is ticket
[T0.01](../../docs/tickets/T0.01/TICKET.md).

> [!NOTE]
> Terraform creates the empty cell: a k3s cluster, then, on a second apply, Argo CD and the platform Application that
> deploys the cluster-wide operators. Argo CD deploys the rest of Swarm from Git. The branch cells of
> [T0.08](../../docs/specs/roadmap/01-p0-foundations.md#s02) have their own root, described in
> [Branch cells](#branch-cells).

## Layout

| Path | Holds |
| --- | --- |
| `modules/self-hosted/machines` | Prepares each machine: hostname, package index, `curl` and `ca-certificates` |
| `modules/self-hosted/network` | The `ufw` firewall of each machine: SSH, the Kubernetes API, the kubelet, VXLAN and the cluster networks |
| `modules/self-hosted/k3s` | Installs the pinned k3s release on the servers and agents, and writes the kubeconfig |
| `modules/self-hosted/object-storage` | Creates buckets on an existing MinIO endpoint (off by default) |
| `modules/self-hosted/dns` | Writes the DNS records of the cell with RFC 2136 updates (off by default) |
| `modules/self-hosted/argocd` | Argo CD, and the platform Application of the cluster-wide operators |
| `modules/self-hosted/vault` | The OpenBao vault of a cell, with its generated root token in a Secret |
| `modules/self-hosted/cell` | The namespace of a branch cell, and its generated MinIO credentials |
| `modules/self-hosted/cell-application` | The Argo CD Application of a branch cell, which deploys its chart from Git |
| `cells/dev` | The root for the dev cell: the first root, which calls the modules above with its own variables |
| `cells/dev-branch` | The root for every branch cell, with one state per branch: the key `dev-branch/<cell>.tfstate` |

One module per building block, and one root per cell, as the
[🧰 Infrastructure as code](../../docs/specs/technical/09-deployment.md#iac) section requires. The OVHcloud and Scaleway
modules are not here yet: they come in [P7](../../docs/specs/roadmap/08-p7-scale-and-reach.md), with the production
cells. A new cell is a new root under `cells/`, and a pull request.

## Prerequisites

- **Terraform 1.10 or later** (`required_version = ">= 1.10"`), on the workstation that runs it.
- **The P-06 machines**, reachable over SSH from that workstation. Each one has:
  - a key pair whose private key is kept outside the repository;
  - a user with passwordless `sudo`, named by `ssh_user`;
  - `ufw` available, because the network module configures it.
- **The operating system.** The specifications do not name one. The machines module uses `apt-get`, so the machines
  must run a Debian or Ubuntu release with `systemd`. Any other system needs a change to the modules first.
- **`ssh` and `sed` on the workstation.** The kubeconfig is copied from the first server by a local command.

> [!CAUTION]
> The network module runs `ufw --force reset` on every machine, then sets the rules again and enables the firewall. Any
> rule already on a machine is lost. Run the first apply on machines that are dedicated to the cell.

## State

The state is stored remotely, with locking, in an S3-compatible bucket. The backend is declared empty in
`cells/dev/versions.tf`:

```hcl
backend "s3" {}
```

Its settings come from a backend configuration file that you keep outside the repository, and pass with
`-backend-config`. You choose where the state lives: the object storage of the global layer, or another S3-compatible
store. The file sets these keys, and you give them values:

- `bucket` and `key`, the bucket and the object that holds the state of the dev cell;
- `region`;
- `endpoints`, whose `s3` entry is the address of the store;
- `use_path_style`;
- `use_lockfile`, so that two applies cannot write the state at once;
- the `skip_*` flags that a non-AWS store needs, such as `skip_credentials_validation`, `skip_region_validation`,
  `skip_requesting_account_id` and `skip_metadata_api_check`.

> [!WARNING]
> The state holds the k3s join token, the vault root token and the MinIO root password in clear text, because Terraform
> stores the value of each generated password. Keep the bucket private, and never commit the state or the backend
> configuration file.

## First apply

Run these commands from `deploy/terraform/cells/dev`.

1. Copy the example to a file outside the repository, such as `~/.config/swarm/dev.tfvars`, and edit it:

   ```bash
   mkdir -p ~/.config/swarm
   cp terraform.tfvars.example ~/.config/swarm/dev.tfvars
   ```

   The variables file stays outside the repository, and it is passed to each command with `-var-file`. The backend
   configuration file stays outside the repository too. Keep the paths it holds (the SSH key and the kubeconfig)
   pointing outside the repository. Its variables are:

   | Variable | Meaning |
   | --- | --- |
   | `machines` | The machines in order, each with a unique `name`, a unique `address` and a `role`, `server` or `agent`. At least one must be a server, and the first server is the API endpoint |
   | `ssh_user` | The user Terraform connects as, with passwordless `sudo` |
   | `ssh_private_key_path` | The path of the private key, outside the repository |
   | `k3s_version` | The pinned k3s release, such as `v1.31.4+k3s1` |
   | `kubeconfig_path` | Where the kubeconfig is written, outside the repository |
   | `api_allowed_cidrs` | The CIDRs, besides the cell machines, allowed to reach the API on 6443/tcp. Empty by default |
   | `object_storage_enabled`, `object_storage_endpoint`, `object_storage_buckets` | See [Object storage and DNS](#object-storage-and-dns) |
   | `dns_enabled`, `dns_server`, `dns_zone` | See [Object storage and DNS](#object-storage-and-dns) |

2. Initialise with your backend configuration file:

   ```bash
   terraform init -backend-config=<path to the backend configuration file>
   ```

3. Review the plan, with the variables file you made in step 1:

   ```bash
   terraform plan -var-file=<path to the variables file>
   ```

4. After review, apply by hand, with the same variables file. Terraform never applies from continuous integration:

   ```bash
   terraform apply -var-file=<path to the variables file>
   ```

The result is the empty k3s cluster: one server per `server` machine, joined to the first server, and one agent per
`agent` machine. The kubeconfig is written to `kubeconfig_path` with mode `0600`, and it points at the first server.
The outputs `api_endpoint`, `kubeconfig_path`, `server_names` and `agent_names` show what was built. Check the cluster
with `KUBECONFIG=<kubeconfig_path> kubectl get nodes`.

### Second apply: the platform

The platform is off on the first apply, so that the cluster exists before Argo CD is installed on it. Once the first
apply has written the kubeconfig, set these variables in the same variables file, and apply again:

| Variable | Meaning |
| --- | --- |
| `platform_enabled` | Set to `true`. It installs Argo CD and the platform Application |
| `repository_url` | The Git repository that Argo CD follows. Required when the platform is enabled |
| `argocd_chart_version` | The pinned argo-cd chart version, never `latest`. Required with the platform |
| `argocd_apps_chart_version` | The pinned argocd-apps chart version, never `latest`. Required with the platform |
| `platform_revision` | The branch, tag or commit the platform Application follows. Default `develop` |

```bash
terraform plan -var-file=<path to the variables file>
terraform apply -var-file=<path to the variables file>
```

The output `argocd_namespace` is then the namespace Argo CD is installed in, `argocd` by default. It is `null` while the
platform is off.

> [!NOTE]
> The network module lets the API port, 6443/tcp, through only from the cell machines and from `api_allowed_cidrs`,
> which is empty by default. From a workstation outside the cell, `kubectl` times out unless its address is in
> `api_allowed_cidrs` before the first apply. Otherwise, run `kubectl` on the first server instead.

## Branch cells

The root `cells/dev-branch` creates the cell of one branch: a namespace, the vault of that cell and the Argo CD
Application that deploys its chart. Its variables are:

| Variable | Meaning |
| --- | --- |
| `branch` | The Git branch the cell follows. Its Application targets this revision |
| `cell_name` | The name of the cell, and of its namespace and Application |
| `kubeconfig_path` | The kubeconfig of the dev cluster, outside the repository |
| `repository_url` | The Git repository that Argo CD follows |
| `database_image` | The image of the cell's database |
| `openbao_chart_version` | The pinned version of the OpenBao chart |
| `argocd_apps_chart_version` | The pinned version of the argocd-apps chart |
| `argocd_namespace` | The namespace of Argo CD, `argocd` by default |

The root has one state per branch, under the backend key `dev-branch/<cell>.tfstate`. The script
[`deploy/scripts/dev-cell.sh`](../scripts/dev-cell.sh) drives it: it passes `branch`, `cell_name` and the backend key,
and it reads the paths of its backend configuration file and variables file from `DEV_CELL_BACKEND_CONFIG` and
`DEV_CELL_VAR_FILE`. Start from
[`cells/dev-branch/terraform.tfvars.example`](cells/dev-branch/terraform.tfvars.example), and keep the file outside the
repository. Run the script by hand with `--dry-run` to see the Terraform commands it would
run, before a real create or destroy.

> [!CAUTION]
> Destroying a branch cell removes its vault and its namespace. The Application goes first, with its finalizer, so that
> Argo CD removes what it deployed before the namespace is deleted.

## Object storage and DNS

Both are off by default, so a first apply creates neither.

- **Object storage** creates the buckets named in `object_storage_buckets` on the MinIO endpoint named in
  `object_storage_endpoint`, as `host:port`. Set `object_storage_enabled = true`. The endpoint must already exist: MinIO
  on the cluster is deployed in [T0.08](../../docs/specs/roadmap/01-p0-foundations.md#s02).
- **DNS** writes an `api` record in `dns_zone`, pointing at the first server, to `dns_server`. Set `dns_enabled = true`,
  and give `dns_server` and `dns_zone`, the zone fully qualified with a trailing dot. When DNS is enabled, the API
  certificate also covers `api.<zone>`.

Their credentials are never variables. Export them in the shell that runs Terraform:

| Feature | Environment variables |
| --- | --- |
| Object storage (MinIO provider) | `MINIO_USER`, `MINIO_PASSWORD` |
| DNS (RFC 2136 updates) | `DNS_UPDATE_KEYNAME`, `DNS_UPDATE_KEYALGORITHM`, `DNS_UPDATE_KEYSECRET` |
| The state (S3 backend) | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` |

## Tokens and secrets

- **The k3s join token** is generated once by Terraform, and it is kept in the state. It changes only when its resource
  is replaced. It lets a machine join the cluster, so it is as sensitive as the state.
- **The kubeconfig** holds the cluster administrator credentials. It is written with mode `0600`, outside the repository.
- **The SSH key, the backend file and the variables file** stay outside the repository. The variables file takes paths
  to the key and the kubeconfig, never their content.
- **The vault root token** is generated by Terraform. It is kept in the state, and in the Kubernetes Secret
  `vault-root-token` of the cell's namespace, under `token`.
- **The MinIO root credentials** of a branch cell are generated by Terraform. The user is `swarm-admin`, and the
  password is kept in the state, and in the Kubernetes Secret `object-storage-root` of the cell's namespace.
- **The provider credentials** above are read from the environment, and are never written to a file of the repository.
- **No token or password is written to a file of the repository.** Neither the variables file nor the backend file holds
  one.

## Continuous integration

`.github/workflows/terraform.yml` runs on every change under `deploy/terraform/` and to the workflow itself.

- **`check`**, for each module (the machines, network, k3s, object storage, DNS, Argo CD, vault, cell and cell
  application modules) and for the roots `cells/dev` and `cells/dev-branch`:
  - `terraform fmt -check -recursive deploy/terraform`, once for the whole folder;
  - `terraform init -backend=false`, then `terraform validate`;
  - `terraform test`, which plans with mock providers and checks the outputs and the refusal of a cell without a server.
- **`plan`**, for `cells/dev`, after `check` passes. It writes the backend configuration from a secret, initialises
  with it, and runs `terraform plan`. It sets the SSH key and kubeconfig paths to placeholders under the runner's
  temporary folder, because a plan needs neither. It never runs `apply`.

The secrets and repository variables it reads:

| Name | Kind | Used for |
| --- | --- | --- |
| `TF_BACKEND_CONFIG` | Secret | The content of the backend configuration file |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | Secrets | The credentials of the state store |
| `DEV_CELL_MACHINES` | Repository variable | `TF_VAR_machines`, in the form of `machines` in the example |
| `TF_VAR_SSH_USER` | Repository variable | `TF_VAR_ssh_user`, read by the workflow as `vars.TF_VAR_SSH_USER` |
| `TF_VAR_K3S_VERSION` | Repository variable | `TF_VAR_k3s_version` |
| `TF_VAR_API_ALLOWED_CIDRS` | Repository variable | `TF_VAR_api_allowed_cidrs` |

> [!IMPORTANT]
> The plan job sets no `MINIO_*` or `DNS_UPDATE_*` variables. A plan that reaches object storage or DNS in CI needs
> those credentials added to the workflow first.

## What comes next

- [T0.09](../../docs/specs/roadmap/01-p0-foundations.md#s02): the NATS JetStream cluster and its Operator accounts.
- [T0.10](../../docs/specs/roadmap/01-p0-foundations.md#s02): signed images, and the refusal of unsigned images by the
  dev cell.
- [P7](../../docs/specs/roadmap/08-p7-scale-and-reach.md): the OVHcloud and Scaleway modules, for the production cells.
