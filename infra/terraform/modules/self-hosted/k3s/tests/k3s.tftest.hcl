mock_provider "random" {}

variables {
  servers = [
    { name = "dev-server-1", address = "192.0.2.10" },
  ]
  agents = [
    { name = "dev-agent-1", address = "192.0.2.11" },
    { name = "dev-agent-2", address = "192.0.2.12" },
  ]
  ssh_user             = "deploy"
  ssh_private_key_path = "/fake/path/id_ed25519"
  k3s_version          = "v1.31.4+k3s1"
  kubeconfig_path      = "/fake/path/kubeconfig"
}

run "a_single_server_with_two_agents_plans_the_expected_cluster" {
  command = plan

  assert {
    condition     = length(terraform_data.server) == 0
    error_message = "A single server must leave no additional server."
  }

  assert {
    condition     = length(terraform_data.agent) == 2
    error_message = "Each agent must have one resource."
  }

  assert {
    condition     = output.api_endpoint == "https://192.0.2.10:6443"
    error_message = "The API endpoint must be the first server on port 6443."
  }

  assert {
    condition     = output.kubeconfig_path == var.kubeconfig_path
    error_message = "The kubeconfig path output must equal the variable."
  }
}

run "an_empty_server_list_is_refused" {
  command = plan

  variables {
    servers = []
  }

  expect_failures = [var.servers]
}

run "an_empty_k3s_version_is_refused" {
  command = plan

  variables {
    k3s_version = ""
  }

  expect_failures = [var.k3s_version]
}

run "the_latest_k3s_version_is_refused" {
  command = plan

  variables {
    k3s_version = "latest"
  }

  expect_failures = [var.k3s_version]
}
