resource "minio_s3_bucket" "bucket" {
  for_each = var.buckets

  bucket = each.value
  acl    = "private"
}
