output "fqdns" {
  description = "The fully qualified names of the records."
  value       = [for name in keys(var.records) : "${name}.${var.zone}"]
}
