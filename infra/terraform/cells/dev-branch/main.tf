# The operator JWT, the system account key and its JWT are public. The operator and account seeds never enter Terraform.
locals {
  cell_parameters = {
    "database.imageName"         = var.database_image
    "nats.auth.operatorJwt"      = var.nats_operator_jwt
    "nats.auth.systemAccount"    = var.nats_system_account
    "nats.auth.systemAccountJwt" = var.nats_system_account_jwt
  }
}

module "cell" {
  source = "../../modules/self-hosted/cell"

  name   = var.cell_name
  branch = var.branch
}

module "vault" {
  source = "../../modules/self-hosted/vault"

  namespace     = module.cell.namespace
  chart_version = var.openbao_chart_version
}

# On destroy the Application, with its finalizer, goes first: Argo CD removes what it deployed, then the vault and the
# namespace are removed.
module "cell_application" {
  source = "../../modules/self-hosted/cell-application"

  name               = var.cell_name
  namespace          = module.cell.namespace
  argocd_namespace   = var.argocd_namespace
  repository_url     = var.repository_url
  target_revision    = var.branch
  chart_path         = "infra/charts/cell"
  values_files       = ["../../environments/dev/values.yaml"]
  parameters         = local.cell_parameters
  apps_chart_version = var.argocd_apps_chart_version

  depends_on = [module.vault]
}
