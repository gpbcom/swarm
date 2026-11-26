mock_provider "kubernetes" {}
mock_provider "random" {}

run "plans_the_global_namespace_and_the_admin_secret_by_default" {
  command = plan

  assert {
    condition     = kubernetes_namespace_v1.identity.metadata[0].name == "global"
    error_message = "The default namespace must be global."
  }

  assert {
    condition     = kubernetes_namespace_v1.identity.metadata[0].labels["app.kubernetes.io/part-of"] == "swarm"
    error_message = "The namespace must be part of swarm."
  }

  assert {
    condition     = kubernetes_namespace_v1.identity.metadata[0].labels["swarm-layer"] == "global"
    error_message = "The namespace must be in the global layer."
  }

  assert {
    condition     = random_password.admin.length == 32
    error_message = "The admin password must be 32 characters long."
  }

  assert {
    condition     = random_password.admin.special == false
    error_message = "The admin password must have no special characters."
  }

  assert {
    condition     = kubernetes_secret_v1.admin.metadata[0].name == "keycloak-admin"
    error_message = "The default admin secret must be keycloak-admin."
  }

  assert {
    condition     = kubernetes_secret_v1.admin.metadata[0].namespace == "global"
    error_message = "The admin secret must be in the identity namespace."
  }

  assert {
    condition     = contains(keys(kubernetes_secret_v1.admin.data), "username") && contains(keys(kubernetes_secret_v1.admin.data), "password")
    error_message = "The admin secret must hold a username and a password."
  }

  assert {
    condition     = output.namespace == "global" && output.admin_secret_name == "keycloak-admin"
    error_message = "The outputs must give the namespace and the secret name."
  }
}

run "uses_a_custom_namespace" {
  command = plan

  variables {
    namespace = "identity-test"
  }

  assert {
    condition     = kubernetes_namespace_v1.identity.metadata[0].name == "identity-test"
    error_message = "The custom namespace must be used."
  }

  assert {
    condition     = output.namespace == "identity-test"
    error_message = "The namespace output must follow the variable."
  }
}

run "refuses_an_invalid_namespace" {
  command = plan

  variables {
    namespace = "Bad_Name"
  }

  expect_failures = [var.namespace]
}
