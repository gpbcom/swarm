output "api_endpoint" {
  description = "The URL of the Kubernetes API, served by the first server."
  value       = "https://${var.servers[0].address}:6443"
}

output "kubeconfig_path" {
  description = "Where the kubeconfig was written."
  value       = var.kubeconfig_path
}
