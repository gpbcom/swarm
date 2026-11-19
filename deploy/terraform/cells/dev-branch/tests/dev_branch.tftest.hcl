mock_provider "kubernetes" {}
mock_provider "helm" {}
mock_provider "random" {}

variables {
  kubeconfig_path           = "/nonexistent/kubeconfig"
  repository_url            = "https://git.example.org/swarm.git"
  database_image            = "registry.example.org/swarm/database:1"
  openbao_chart_version     = "0.0.1"
  argocd_apps_chart_version = "0.0.1"
}

run "plans_the_cell_of_a_branch" {
  command = plan

  variables {
    branch    = "feature/x"
    cell_name = "cell-feature-x-1a2b3c4d"
  }

  assert {
    condition     = output.namespace == "cell-feature-x-1a2b3c4d"
    error_message = "The namespace must be the cell name."
  }

  assert {
    condition     = output.application_name == "cell-feature-x-1a2b3c4d"
    error_message = "The application must be named after the cell."
  }

  assert {
    condition     = output.vault_address == "http://openbao.cell-feature-x-1a2b3c4d.svc:8200"
    error_message = "The vault address must be the OpenBao service of the cell namespace."
  }
}

run "refuses_a_cell_name_that_is_not_a_label" {
  command = plan

  variables {
    branch    = "feature/x"
    cell_name = "Cell_Feature/X"
  }

  expect_failures = [var.cell_name]
}

run "refuses_a_cell_without_a_database_image" {
  command = plan

  variables {
    branch         = "feature/x"
    cell_name      = "cell-feature-x-1a2b3c4d"
    database_image = ""
  }

  expect_failures = [var.database_image]
}

run "refuses_an_empty_branch" {
  command = plan

  variables {
    branch    = ""
    cell_name = "cell-feature-x-1a2b3c4d"
  }

  expect_failures = [var.branch]
}
