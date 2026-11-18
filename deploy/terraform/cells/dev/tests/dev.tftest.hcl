mock_provider "random" {}
mock_provider "minio" {}
mock_provider "dns" {}

variables {
  ssh_user             = "swarm"
  ssh_private_key_path = "/nonexistent/id_ed25519"
  k3s_version          = "v1.31.4+k3s1"
  kubeconfig_path      = "/nonexistent/kubeconfig"
}

run "plans_an_empty_k3s_cluster_from_nothing" {
  command = plan

  variables {
    machines = [
      { name = "dev-server-1", address = "192.0.2.10", role = "server" },
      { name = "dev-agent-1", address = "192.0.2.11", role = "agent" },
      { name = "dev-agent-2", address = "192.0.2.12", role = "agent" },
    ]
  }

  assert {
    condition     = length(module.object_storage) == 0
    error_message = "Object storage must not be planned by default."
  }

  assert {
    condition     = length(module.dns) == 0
    error_message = "DNS must not be planned by default."
  }

  assert {
    condition     = output.api_endpoint == "https://192.0.2.10:6443"
    error_message = "The API endpoint must be the first server on port 6443."
  }

  assert {
    condition     = output.server_names == ["dev-server-1"]
    error_message = "The only server must be dev-server-1."
  }
}

run "plans_buckets_and_records_when_enabled" {
  command = plan

  variables {
    machines = [
      { name = "dev-server-1", address = "192.0.2.10", role = "server" },
      { name = "dev-agent-1", address = "192.0.2.11", role = "agent" },
    ]
    object_storage_enabled  = true
    object_storage_endpoint = "192.0.2.20:9000"
    object_storage_buckets  = ["dev-artifacts"]
    dns_enabled             = true
    dns_server              = "192.0.2.53"
    dns_zone                = "dev.example.org."
  }

  assert {
    condition     = length(module.object_storage) == 1
    error_message = "Object storage must be planned when enabled."
  }

  assert {
    condition     = length(module.dns) == 1
    error_message = "DNS must be planned when enabled."
  }
}

run "refuses_a_cell_without_a_server" {
  command = plan

  variables {
    machines = [
      { name = "dev-agent-1", address = "192.0.2.11", role = "agent" },
    ]
  }

  expect_failures = [var.machines]
}
