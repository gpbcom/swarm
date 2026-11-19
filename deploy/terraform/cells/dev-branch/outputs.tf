output "namespace" {
  description = "The namespace of the cell."
  value       = module.cell.namespace
}

output "application_name" {
  description = "The name of the Argo CD Application of the cell."
  value       = module.cell_application.application_name
}

output "vault_address" {
  description = "The in-cluster address of the vault of the cell."
  value       = module.vault.address
}
