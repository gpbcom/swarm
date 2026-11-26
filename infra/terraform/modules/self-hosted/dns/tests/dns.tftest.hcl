mock_provider "dns" {}

run "creates_one_record_set_per_name" {
  command = plan

  variables {
    zone    = "dev.example.org."
    records = { api = "192.0.2.10" }
  }

  assert {
    condition     = contains(keys(dns_a_record_set.record), "api")
    error_message = "Expected a record set keyed by the record name."
  }

  assert {
    condition     = contains(output.fqdns, "api.dev.example.org.")
    error_message = "Expected the fully qualified name in fqdns."
  }
}

run "refuses_a_zone_without_the_trailing_dot" {
  command = plan

  variables {
    zone    = "dev.example.org"
    records = { api = "192.0.2.10" }
  }

  expect_failures = [var.zone]
}

run "refuses_an_address_that_is_not_ipv4" {
  command = plan

  variables {
    zone    = "dev.example.org."
    records = { api = "not-an-address" }
  }

  expect_failures = [var.records]
}
