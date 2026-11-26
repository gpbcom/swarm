output "namespace" {
  description = "The namespace Argo CD is installed in."
  value       = helm_release.argocd.namespace
}

output "platform_application" {
  description = "The name of the root Application that deploys the cluster-wide operators."
  value       = "platform"
}
