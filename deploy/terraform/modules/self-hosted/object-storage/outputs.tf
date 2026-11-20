output "bucket_names" {
  description = "Names of the buckets created."
  value       = [for bucket in minio_s3_bucket.bucket : bucket.bucket]
}
