output "namespace" {
  description = "The name of the namespace of the cell."
  value       = kubernetes_namespace_v1.cell.metadata[0].name
}

output "object_storage_secret_name" {
  description = "The name of the secret that holds the object storage administrator credentials, read by the MinIO chart."
  value       = kubernetes_secret_v1.object_storage_root.metadata[0].name
}
