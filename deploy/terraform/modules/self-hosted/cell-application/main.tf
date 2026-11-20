locals {
  parameters = [for key, value in var.parameters : { name = key, value = value }]
}

resource "helm_release" "application" {
  name       = var.name
  namespace  = var.argocd_namespace
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argocd-apps"
  version    = var.apps_chart_version

  values = [<<-EOT
    applications:
      ${jsonencode(var.name)}:
        namespace: ${jsonencode(var.argocd_namespace)}
        finalizers: ${jsonencode(["resources-finalizer.argocd.argoproj.io"])}
        project: default
        source:
          repoURL: ${jsonencode(var.repository_url)}
          targetRevision: ${jsonencode(var.target_revision)}
          path: ${jsonencode(var.chart_path)}
          helm:
            valueFiles: ${jsonencode(var.values_files)}
            parameters: ${jsonencode(local.parameters)}
        destination:
          server: https://kubernetes.default.svc
          namespace: ${var.namespace}
        syncPolicy:
          automated:
            prune: true
            selfHeal: true
  EOT
  ]
}
