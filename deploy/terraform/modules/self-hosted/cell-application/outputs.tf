output "application_name" {
  description = "The name of the Argo CD Application of the cell."
  value       = helm_release.application.name
}
