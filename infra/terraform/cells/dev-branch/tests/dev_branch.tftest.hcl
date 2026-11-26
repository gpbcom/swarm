mock_provider "kubernetes" {}
mock_provider "helm" {}
mock_provider "random" {}

variables {
  kubeconfig_path           = "/nonexistent/kubeconfig"
  repository_url            = "https://git.example.org/swarm.git"
  database_image            = "registry.example.org/swarm/database:1"
  openbao_chart_version     = "0.0.1"
  argocd_apps_chart_version = "0.0.1"

  nats_operator_jwt       = "eyJ0eXAiOiJKV1QifQ.eyJpc3MiOiJleGFtcGxlLm9yZyJ9.c2lnbmF0dXJl"
  nats_system_account     = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
  nats_system_account_jwt = "eyJ0eXAiOiJKV1QifQ.eyJzdWIiOiJleGFtcGxlLm9yZyJ9.c2lnbmF0dXJlMg"
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

  assert {
    condition = jsonencode(output.cell_parameter_names) == jsonencode([
      "database.imageName",
      "nats.auth.operatorJwt",
      "nats.auth.systemAccount",
      "nats.auth.systemAccountJwt",
    ])
    error_message = "The cell must receive the database image and the NATS operator JWT, system account and its JWT."
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

run "refuses_an_empty_nats_operator_jwt" {
  command = plan

  variables {
    branch            = "feature/x"
    cell_name         = "cell-feature-x-1a2b3c4d"
    nats_operator_jwt = ""
  }

  expect_failures = [var.nats_operator_jwt]
}

run "refuses_a_system_account_that_is_not_an_account_key" {
  command = plan

  variables {
    branch              = "feature/x"
    cell_name           = "cell-feature-x-1a2b3c4d"
    nats_system_account = "not-a-key"
  }

  expect_failures = [var.nats_system_account]
}

run "refuses_an_empty_system_account_jwt" {
  command = plan

  variables {
    branch                  = "feature/x"
    cell_name               = "cell-feature-x-1a2b3c4d"
    nats_system_account_jwt = ""
  }

  expect_failures = [var.nats_system_account_jwt]
}
