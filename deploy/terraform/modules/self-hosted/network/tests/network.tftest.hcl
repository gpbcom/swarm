variables {
  ssh_user             = "swarm"
  ssh_private_key_path = "/nonexistent/id_ed25519"
  machines = [
    { name = "dev-server-1", address = "192.0.2.10", role = "server" },
    { name = "dev-agent-1", address = "192.0.2.11", role = "agent" },
    { name = "dev-agent-2", address = "192.0.2.12", role = "agent" },
  ]
  api_allowed_cidrs = []
  cluster_cidr      = "10.42.0.0/16"
  service_cidr      = "10.43.0.0/16"
}

run "three_machines_give_three_firewalls" {
  command = plan

  assert {
    condition     = length(terraform_data.firewall) == 3
    error_message = "Expected one terraform_data.firewall instance per machine."
  }
}

run "cluster_cidr_output_is_the_default" {
  command = plan

  assert {
    condition     = output.cluster_cidr == "10.42.0.0/16"
    error_message = "Expected output.cluster_cidr to be 10.42.0.0/16."
  }
}

run "service_cidr_output_is_the_default" {
  command = plan

  assert {
    condition     = output.service_cidr == "10.43.0.0/16"
    error_message = "Expected output.service_cidr to be 10.43.0.0/16."
  }
}

run "an_invalid_api_cidr_is_refused" {
  command = plan

  variables {
    api_allowed_cidrs = ["not-a-cidr"]
  }

  expect_failures = [var.api_allowed_cidrs]
}

run "an_invalid_cluster_cidr_is_refused" {
  command = plan

  variables {
    cluster_cidr = "10.42.0.0/99"
  }

  expect_failures = [var.cluster_cidr]
}
