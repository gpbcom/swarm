variables {
  ssh_user             = "swarm"
  ssh_private_key_path = "/nonexistent/id_ed25519"
  machines = [
    { name = "dev-server-1", address = "192.0.2.10", role = "server" },
    { name = "dev-agent-1", address = "192.0.2.11", role = "agent" },
    { name = "dev-agent-2", address = "192.0.2.12", role = "agent" },
  ]
}

run "three_machines_give_three_instances" {
  command = plan

  assert {
    condition     = length(terraform_data.machine) == 3
    error_message = "Expected one terraform_data.machine instance per machine."
  }
}

run "servers_output_lists_the_server" {
  command = plan

  assert {
    condition     = [for s in output.servers : s.name] == ["dev-server-1"]
    error_message = "Expected output.servers to hold only dev-server-1."
  }
}

run "agents_output_lists_the_agents" {
  command = plan

  assert {
    condition     = [for a in output.agents : a.name] == ["dev-agent-1", "dev-agent-2"]
    error_message = "Expected output.agents to hold dev-agent-1 and dev-agent-2."
  }
}

run "a_list_without_a_server_is_refused" {
  command = plan

  variables {
    machines = [
      { name = "dev-agent-1", address = "192.0.2.11", role = "agent" },
    ]
  }

  expect_failures = [var.machines]
}

run "an_unknown_role_is_refused" {
  command = plan

  variables {
    machines = [
      { name = "dev-server-1", address = "192.0.2.10", role = "server" },
      { name = "dev-agent-1", address = "192.0.2.11", role = "worker" },
    ]
  }

  expect_failures = [var.machines]
}

run "duplicate_names_are_refused" {
  command = plan

  variables {
    machines = [
      { name = "dev-server-1", address = "192.0.2.10", role = "server" },
      { name = "dev-server-1", address = "192.0.2.11", role = "agent" },
    ]
  }

  expect_failures = [var.machines]
}
