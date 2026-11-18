# The credentials are never variables. The minio provider reads MINIO_USER and MINIO_PASSWORD from its environment,
# and the dns provider reads DNS_UPDATE_KEYNAME, DNS_UPDATE_KEYALGORITHM and DNS_UPDATE_KEYSECRET.
# A disabled feature gets a placeholder endpoint, so that its provider configures without being used.
provider "minio" {
  minio_server = var.object_storage_enabled ? var.object_storage_endpoint : "localhost:9000"
}

provider "dns" {
  dynamic "update" {
    for_each = var.dns_enabled ? [var.dns_server] : []

    content {
      server = update.value
    }
  }
}
