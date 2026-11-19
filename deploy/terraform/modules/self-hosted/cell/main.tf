resource "kubernetes_namespace_v1" "cell" {
  metadata {
    name = var.name

    labels = {
      "app.kubernetes.io/part-of" = "swarm"
      "swarm-cell"                = var.name
    }

    annotations = {
      "swarm-branch" = var.branch
    }
  }
}

resource "random_password" "object_storage_root" {
  length  = 32
  special = false
}

resource "kubernetes_secret_v1" "object_storage_root" {
  metadata {
    name      = "object-storage-root"
    namespace = kubernetes_namespace_v1.cell.metadata[0].name
  }

  data = {
    MINIO_ROOT_USER     = "swarm-admin"
    MINIO_ROOT_PASSWORD = random_password.object_storage_root.result
  }
}
