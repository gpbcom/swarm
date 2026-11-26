mock_provider "random" {}
mock_provider "minio" {}
mock_provider "dns" {}
mock_provider "helm" {}
mock_provider "kubernetes" {}

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
    condition     = length(module.argocd) == 0
    error_message = "Argo CD must not be planned by default."
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

run "installs_argo_cd_when_the_platform_is_enabled" {
  command = plan

  variables {
    machines = [
      { name = "dev-server-1", address = "192.0.2.10", role = "server" },
      { name = "dev-agent-1", address = "192.0.2.11", role = "agent" },
    ]
    platform_enabled          = true
    repository_url            = "https://git.example.org/swarm.git"
    argocd_chart_version      = "0.0.1"
    argocd_apps_chart_version = "0.0.1"
  }

  assert {
    condition     = length(module.argocd) == 1
    error_message = "Argo CD must be planned when the platform is enabled."
  }

  assert {
    condition     = output.argocd_namespace == "argocd"
    error_message = "The Argo CD namespace must be argocd."
  }
}

run "refuses_the_platform_without_a_repository" {
  command = plan

  variables {
    machines = [
      { name = "dev-server-1", address = "192.0.2.10", role = "server" },
      { name = "dev-agent-1", address = "192.0.2.11", role = "agent" },
    ]
    platform_enabled          = true
    repository_url            = ""
    argocd_chart_version      = "0.0.1"
    argocd_apps_chart_version = "0.0.1"
  }

  expect_failures = [var.repository_url]
}

run "refuses_the_platform_with_a_floating_chart_version" {
  command = plan

  variables {
    machines = [
      { name = "dev-server-1", address = "192.0.2.10", role = "server" },
      { name = "dev-agent-1", address = "192.0.2.11", role = "agent" },
    ]
    platform_enabled          = true
    repository_url            = "https://git.example.org/swarm.git"
    argocd_chart_version      = "latest"
    argocd_apps_chart_version = "0.0.1"
  }

  expect_failures = [var.argocd_chart_version]
}

run "plans_no_identity_by_default" {
  command = plan

  variables {
    machines = [
      { name = "dev-server-1", address = "192.0.2.10", role = "server" },
      { name = "dev-agent-1", address = "192.0.2.11", role = "agent" },
    ]
  }

  assert {
    condition     = length(module.identity) == 0
    error_message = "Identity must not be planned by default."
  }

  assert {
    condition     = length(module.identity_application) == 0
    error_message = "The identity Application must not be planned by default."
  }
}

run "plans_identity_when_enabled_with_the_platform" {
  command = plan

  variables {
    machines = [
      { name = "dev-server-1", address = "192.0.2.10", role = "server" },
      { name = "dev-agent-1", address = "192.0.2.11", role = "agent" },
    ]
    platform_enabled          = true
    identity_enabled          = true
    repository_url            = "https://git.example.org/swarm.git"
    argocd_chart_version      = "0.0.1"
    argocd_apps_chart_version = "0.0.1"
  }

  assert {
    condition     = length(module.identity) == 1
    error_message = "Identity must be planned when enabled."
  }

  assert {
    condition     = length(module.identity_application) == 1
    error_message = "The identity Application must be planned when enabled."
  }

  assert {
    condition     = module.identity_application[0].application_name == "identity"
    error_message = "The identity Application must be named identity."
  }
}

run "refuses_identity_without_the_platform" {
  command = plan

  variables {
    machines = [
      { name = "dev-server-1", address = "192.0.2.10", role = "server" },
      { name = "dev-agent-1", address = "192.0.2.11", role = "agent" },
    ]
    identity_enabled = true
  }

  expect_failures = [var.identity_enabled]
}
