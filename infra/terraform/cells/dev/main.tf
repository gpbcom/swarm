module "machines" {
  source = "../../modules/self-hosted/machines"

  machines             = var.machines
  ssh_user             = var.ssh_user
  ssh_private_key_path = var.ssh_private_key_path
}

module "network" {
  source = "../../modules/self-hosted/network"

  machines             = var.machines
  ssh_user             = var.ssh_user
  ssh_private_key_path = var.ssh_private_key_path
  api_allowed_cidrs    = var.api_allowed_cidrs

  depends_on = [module.machines]
}

module "k3s" {
  source = "../../modules/self-hosted/k3s"

  servers              = module.machines.servers
  agents               = module.machines.agents
  ssh_user             = var.ssh_user
  ssh_private_key_path = var.ssh_private_key_path
  k3s_version          = var.k3s_version
  cluster_cidr         = module.network.cluster_cidr
  service_cidr         = module.network.service_cidr
  tls_san              = var.dns_enabled ? ["api.${trimsuffix(var.dns_zone, ".")}"] : []
  kubeconfig_path      = var.kubeconfig_path

  depends_on = [module.network]
}

module "object_storage" {
  source = "../../modules/self-hosted/object-storage"
  count  = var.object_storage_enabled ? 1 : 0

  buckets = var.object_storage_buckets
}

module "dns" {
  source = "../../modules/self-hosted/dns"
  count  = var.dns_enabled ? 1 : 0

  zone    = var.dns_zone
  records = { api = module.machines.servers[0].address }
}

module "argocd" {
  source = "../../modules/self-hosted/argocd"
  count  = var.platform_enabled ? 1 : 0

  chart_version      = var.argocd_chart_version
  apps_chart_version = var.argocd_apps_chart_version
  repository_url     = var.repository_url
  target_revision    = var.platform_revision

  depends_on = [module.k3s]
}

module "identity" {
  source = "../../modules/self-hosted/identity"
  count  = var.identity_enabled ? 1 : 0

  depends_on = [module.k3s]
}

module "identity_application" {
  source = "../../modules/self-hosted/cell-application"
  count  = var.identity_enabled ? 1 : 0

  name               = "identity"
  namespace          = module.identity[0].namespace
  repository_url     = var.repository_url
  target_revision    = var.platform_revision
  chart_path         = "infra/charts/keycloak"
  values_files       = []
  apps_chart_version = var.argocd_apps_chart_version

  depends_on = [module.argocd, module.identity]
}
