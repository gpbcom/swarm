# The vault of one cell (docs/specs/technical/06-security.md#secrets).
#
# Dev server mode is the documented choice for ephemeral dev cells with simulated Drones only
# (docs/specs/technical/09-deployment.md#environments). Staging and production need a persistent, sealed mode.

resource "random_password" "root_token" {
  length  = 32
  special = false
}

resource "kubernetes_secret_v1" "root_token" {
  metadata {
    name      = "vault-root-token"
    namespace = var.namespace
  }

  data = {
    token = random_password.root_token.result
  }
}

resource "helm_release" "vault" {
  name       = var.release_name
  namespace  = var.namespace
  repository = "https://openbao.github.io/openbao-helm"
  chart      = "openbao"
  version    = var.chart_version

  values = [
    yamlencode({
      server = {
        dev = {
          enabled = true
        }
        authDelegator = {
          enabled = false
        }
        serviceAccount = {
          name = var.release_name
        }
      }
      injector = {
        enabled = false
      }
      ui = {
        enabled = false
      }
    })
  ]

  set_sensitive = [
    {
      name  = "server.dev.devRootToken"
      value = random_password.root_token.result
    }
  ]
}

# The chart's own auth-delegator binding is cluster-scoped and named after the release, so a second cell would collide
# with the first one. This binding is named after the namespace, and Terraform deletes it with the cell. It lets the
# Kubernetes auth method review service account tokens.
resource "kubernetes_cluster_role_binding_v1" "auth_delegator" {
  metadata {
    name = "${var.namespace}-openbao-auth-delegator"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "system:auth-delegator"
  }

  subject {
    kind      = "ServiceAccount"
    name      = var.release_name
    namespace = var.namespace
  }
}
