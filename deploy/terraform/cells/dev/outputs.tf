output "api_endpoint" {
  description = "The URL of the Kubernetes API, served by the first server."
  value       = module.k3s.api_endpoint
}

output "kubeconfig_path" {
  description = "Where the kubeconfig was written."
  value       = module.k3s.kubeconfig_path
}

output "server_names" {
  description = "The names of the control plane machines."
  value       = [for s in module.machines.servers : s.name]
}

output "agent_names" {
  description = "The names of the worker machines."
  value       = [for a in module.machines.agents : a.name]
}
