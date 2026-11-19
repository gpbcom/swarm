mock_provider "helm" {}
mock_provider "kubernetes" {}
mock_provider "random" {}

run "installs_the_vault_of_a_cell" {
  command = plan

  variables {
    namespace     = "cell-feature-x-1a2b3c4d"
    chart_version = "0.0.1"
  }

  assert {
    condition     = helm_release.vault.chart == "openbao"
    error_message = "Expected the openbao chart."
  }

  assert {
    condition     = helm_release.vault.repository == "https://openbao.github.io/openbao-helm"
    error_message = "Expected the openbao helm repository."
  }

  assert {
    condition     = helm_release.vault.namespace == "cell-feature-x-1a2b3c4d"
    error_message = "Expected the release in the namespace of the cell."
  }

  assert {
    condition     = helm_release.vault.name == "openbao"
    error_message = "Expected the default release name."
  }

  assert {
    condition     = kubernetes_secret_v1.root_token.metadata[0].name == "vault-root-token"
    error_message = "Expected the root token secret to be named vault-root-token."
  }

  assert {
    condition     = kubernetes_secret_v1.root_token.metadata[0].namespace == "cell-feature-x-1a2b3c4d"
    error_message = "Expected the root token secret in the namespace of the cell."
  }

  assert {
    condition     = random_password.root_token.special == false
    error_message = "Expected a root token without special characters."
  }

  assert {
    condition     = random_password.root_token.length >= 32
    error_message = "Expected a root token of at least 32 characters."
  }

  assert {
    condition     = output.address == "http://openbao.cell-feature-x-1a2b3c4d.svc:8200"
    error_message = "Expected the in-cluster address of the vault."
  }

  assert {
    condition     = output.root_token_secret_name == "vault-root-token"
    error_message = "Expected the name of the root token secret."
  }
}

run "refuses_a_namespace_that_is_not_a_label" {
  command = plan

  variables {
    namespace     = "Cell_X"
    chart_version = "0.0.1"
  }

  expect_failures = [var.namespace]
}

run "refuses_a_floating_chart_version" {
  command = plan

  variables {
    namespace     = "cell-feature-x-1a2b3c4d"
    chart_version = "latest"
  }

  expect_failures = [var.chart_version]
}
