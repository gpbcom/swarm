resource "helm_release" "argocd" {
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  version          = var.chart_version
  namespace        = var.namespace
  create_namespace = true
}

resource "helm_release" "platform" {
  name       = "platform"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argocd-apps"
  version    = var.apps_chart_version
  namespace  = var.namespace

  values = [
    yamlencode({
      applications = {
        platform = {
          namespace = var.namespace
          project   = "default"
          source = {
            repoURL        = var.repository_url
            targetRevision = var.target_revision
            path           = var.platform_path
          }
          destination = {
            server    = "https://kubernetes.default.svc"
            namespace = var.namespace
          }
          syncPolicy = {
            automated = {
              prune    = true
              selfHeal = true
            }
          }
        }
      }
    })
  ]

  depends_on = [helm_release.argocd]
}
