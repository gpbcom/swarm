resource "kubernetes_namespace_v1" "identity" {
  metadata {
    name = var.namespace

    labels = {
      "app.kubernetes.io/part-of" = "swarm"
      "swarm-layer"               = "global"
    }
  }
}

resource "random_password" "admin" {
  length  = 32
  special = false
}

resource "kubernetes_secret_v1" "admin" {
  metadata {
    name      = var.admin_secret_name
    namespace = kubernetes_namespace_v1.identity.metadata[0].name
  }

  data = {
    username = "swarm-admin"
    password = random_password.admin.result
  }
}
