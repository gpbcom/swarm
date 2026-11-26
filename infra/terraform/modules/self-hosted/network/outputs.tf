output "cluster_cidr" {
  description = "The CIDR of the pods."
  value       = var.cluster_cidr
}

output "service_cidr" {
  description = "The CIDR of the services."
  value       = var.service_cidr
}

output "ready" {
  description = "The firewall resource id of each machine, by machine name."
  value       = { for name, f in terraform_data.firewall : name => f.id }
}
