output "address" {
  description = "In-cluster address of the vault."
  value       = "http://${var.release_name}.${var.namespace}.svc:8200"
}

output "root_token_secret_name" {
  description = "Name of the Kubernetes secret that holds the root token, under the key token."
  value       = kubernetes_secret_v1.root_token.metadata[0].name
}
