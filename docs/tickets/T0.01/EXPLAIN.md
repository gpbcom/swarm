# 📘 T0.01: Mono-repo layout and Terraform base: explanation

**Status:** ✅ Done · **Ticket:** [TICKET.md](TICKET.md) · **Progress:** [PROGRESS.md](PROGRESS.md) · **Plan:** [PLAN.md](PLAN.md)

> [!NOTE]
> The repository now has the mono-repo layout of the architecture page, with the uv, Cargo and pnpm workspaces, the
> current root `src/` moved to `services/gateway`, and the Terraform base of the dev cell. The branch is merged into
> `develop` locally. Nothing is pushed.

## What changed for users

- Anyone who clones the repository finds the layout of the architecture page: `services/`, `frontends/`, `packages/`
  (`python`, `rust`, `ts`), `deploy/terraform/` and `tests/conventions/`.
- The README says how to start.
- The dev cell is described as infrastructure as code. A person can provision its machines, k3s cluster, network,
  object storage and DNS with Terraform, from one root per cell.
- No feature changes behaviour yet: the gateway service keeps its previous command line, now under `services/gateway`.

## What changed in the code

Diff reviewed: `develop~1...develop`, 106 files, 3110 lines added and 1007 removed.

| Area | Change |
| --- | --- |
| Root | `pyproject.toml` becomes the uv workspace root, with one `uv.lock`. `package.json`, `pnpm-workspace.yaml`, `pnpm-lock.yaml` and `turbo.json` give the pnpm workspace with Turborepo. `AGENT.md`, `README.md` and `.gitignore` are updated. |
| Python service | `services/gateway/` holds the former `src/`: its `pyproject.toml`, the layer packages (`api`, `service`, `storage`, `clients`, `models`) and the CLI under `api/cli/`. Its test checks the command line. The former `src/swarm/__init__.py` is removed. |
| Rust | `packages/rust/` is a Cargo workspace, with `Cargo.toml`, `Cargo.lock` and `rust-toolchain.toml`. It has no member crate yet (the first crate comes with T0.07). |
| TypeScript | `packages/ts/` and `frontends/` are placeholders, with `.gitkeep`. `packages/python/` is a placeholder too. |
| Terraform | `deploy/terraform/modules/self-hosted/` has six modules, `machines`, `network`, `k3s`, `object-storage`, `dns` and their Terraform tests. `deploy/terraform/cells/dev/` is the dev cell root, with its providers, variables, outputs, `terraform.tfvars.example` and a test. `deploy/terraform/README.md` describes the variables. |
| CI | `.github/workflows/terraform.yml` runs the Terraform format check, validation, tests and a `terraform plan` of the dev cell. |
| Convention tests | `tests/conventions/mono_repo/` enforces the uv, Cargo, pnpm and Terraform layout, with shared helpers. |
| Specifications | `docs/specs/` is checked by `specs.py check`, which prints nothing. |

## How to test it

Run these from the repository root, with the toolchain of the ticket installed (uv, Rust 1.100 and pnpm):

```bash
uv sync
uv run ruff check services packages tests
uv run mypy services/gateway/src
uv run pytest services/gateway/tests/api/cli -n 2
uv run pytest tests/conventions/mono_repo -n 2
cargo metadata --no-deps --manifest-path packages/rust/Cargo.toml
pnpm install
python3 .claude/skills/write-specs/scripts/specs.py check
```

For Terraform, each module and the dev cell run `terraform init`, `terraform validate` and `terraform test`, as recorded
in the evidence files. A real `terraform plan` needs the CI variables of [infra/terraform/README.md](../../../infra/terraform/README.md).

> [!WARNING]
> The Terraform tests use mock providers. They do not prove that a real `terraform plan` or `apply` succeeds against
> the machines. That check is still open, see the follow-ups in [PROGRESS.md](PROGRESS.md#-follow-ups).

## Evidence

The outputs of the checks are in [tests-evidences/](tests-evidences/):

- Python: [ruff-check.txt](tests-evidences/ruff-check.txt), [ruff-format-check.txt](tests-evidences/ruff-format-check.txt),
  [mypy.txt](tests-evidences/mypy.txt), [pytest.txt](tests-evidences/pytest.txt),
  [pytest-gateway-api-cli.txt](tests-evidences/pytest-gateway-api-cli.txt),
  [pytest-conventions-mono_repo.txt](tests-evidences/pytest-conventions-mono_repo.txt).
- Rust: [cargo-metadata.txt](tests-evidences/cargo-metadata.txt), [cargo-test.txt](tests-evidences/cargo-test.txt),
  [cargo-clippy.txt](tests-evidences/cargo-clippy.txt), [cargo-fmt-check.txt](tests-evidences/cargo-fmt-check.txt).
- TypeScript: [pnpm-install.txt](tests-evidences/pnpm-install.txt), [pnpm-tsc.txt](tests-evidences/pnpm-tsc.txt),
  [pnpm-vitest.txt](tests-evidences/pnpm-vitest.txt), [pnpm-eslint.txt](tests-evidences/pnpm-eslint.txt).
- Terraform: [terraform-validate.txt](tests-evidences/terraform-validate.txt),
  [terraform-test.txt](tests-evidences/terraform-test.txt), [terraform-fmt-check.txt](tests-evidences/terraform-fmt-check.txt),
  and one `terraform-init`, `terraform-validate` and `terraform-test` file per module and cell.
- Specifications: [specs-check.txt](tests-evidences/specs-check.txt).

> [!CAUTION]
> The copy of [specs-check.txt](tests-evidences/specs-check.txt) on `ticket/T0.01` still holds the `PIL` traceback of the
> stopped run. The fresh output is listed in the follow-ups.

## Assumptions accepted by the reviewer

- **K16:** when the optional `TF_VAR_API_ALLOWED_CIDRS` repository variable is unset, the dev cell allows no extra CIDRs
  to reach the Kubernetes API (an empty list). This is the most restrictive choice and matches the documented Terraform
  default, so it is accepted.

The ticket's own assumptions are in [TICKET.md](TICKET.md#assumptions): the roadmap names no feature, use case or
business rule for T0.01, and the Terraform state location is the person's choice.

## 🔜 Follow-ups

Non-blocking findings of the review (TKT-12). They did not hold the merge. The same list is in
[PROGRESS.md](PROGRESS.md#-follow-ups).

| File | What to change |
| --- | --- |
| `deploy/terraform/README.md` | In the CI variables table, mark `TF_VAR_API_ALLOWED_CIDRS` as optional and say it defaults to `[]`. Also say that `DEV_CELL_MACHINES`, `TF_VAR_SSH_USER` and `TF_VAR_K3S_VERSION` are required for the plan job. |
| `.github/workflows/terraform.yml` | The repository variable names are inconsistent: `DEV_CELL_MACHINES` sits next to `TF_VAR_SSH_USER`, `TF_VAR_K3S_VERSION` and `TF_VAR_API_ALLOWED_CIDRS`. Pick one naming scheme. `terraform fmt -check -recursive deploy/terraform` runs again in every matrix job, so move it to a single job. Pin `terraform_version` to an exact release rather than `>= 1.10`, so CI is reproducible. |
| `deploy/terraform/cells/dev/providers.tf` | When object storage is disabled, the minio provider is still configured, with `localhost:9000` and no credentials. The plan job sets no `MINIO_*` variables. Run one real `terraform plan` with object storage disabled and no MinIO credentials to confirm that provider configuration does not fail. The tests use mock providers, so they cannot show this. |
| `pyproject.toml` | `[tool.pytest.ini_options] testpaths` and `[tool.mypy] files/mypy_path` name `services/gateway` directly, so adding a service means editing the root configuration. Use globs, or document the per-service command only. |
| `pyproject.toml` | The move dropped the `babel`, `langchain` and `langgraph` dependencies of the old root project, and no assumption records it. The README explains LangChain and LangGraph but not Babel. Record the decision in PROGRESS.md, or keep the dependencies. |
| `tests/conventions/mono_repo/test_python_workspace.py` | `test_the_gateway_has_the_layer_package` repeats the layer list inline. Parametrise it with `SERVICE_LAYERS` from helpers.py. |
| `deploy/terraform/modules/self-hosted/k3s/main.tf` | The `local-exec` command puts `$(dirname ${local.token_file})` inside outer double quotes, so it runs on the workstation, not on the machine. The result is the same, but write the directory as a literal local, for example `/etc/rancher/k3s`, so the intent is clear. The three copies of the token-push command could also share one local. |
| `docs/tickets/T0.01/tests-evidences/specs-check.txt` | The copy committed on `ticket/T0.01` still holds the `ModuleNotFoundError: No module named 'PIL'` traceback from the stopped run. The working tree has a newer, uncommitted version of this file and of pnpm-install.txt. Commit the fresh verifier output before the merge. |
