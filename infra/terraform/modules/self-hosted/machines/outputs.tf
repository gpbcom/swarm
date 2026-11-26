output "servers" {
  description = "The machines with the role server, in input order, as name and address."
  value       = [for m in var.machines : { name = m.name, address = m.address } if m.role == "server"]
}

output "agents" {
  description = "The machines with the role agent, in input order, as name and address."
  value       = [for m in var.machines : { name = m.name, address = m.address } if m.role == "agent"]
}

output "ready" {
  description = "A map of machine name to the id of its preparation, for depends_on in other modules."
  value       = { for name, machine in terraform_data.machine : name => machine.id }
}
