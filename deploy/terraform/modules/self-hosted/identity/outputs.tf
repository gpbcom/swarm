output "namespace" {
  description = "The namespace of the global layer."
  value       = kubernetes_namespace_v1.identity.metadata[0].name
}

output "admin_secret_name" {
  description = "The name of the Secret that holds the bootstrap admin of Keycloak."
  value       = kubernetes_secret_v1.admin.metadata[0].name
}
