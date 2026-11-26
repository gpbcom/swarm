mock_provider "kubernetes" {}
mock_provider "random" {}

run "creates_the_empty_cell" {
  command = plan

  variables {
    name   = "cell-feature-x-1a2b3c4d"
    branch = "feature/x"
  }

  assert {
    condition     = kubernetes_namespace_v1.cell.metadata[0].name == "cell-feature-x-1a2b3c4d"
    error_message = "Expected the namespace to be named after the cell."
  }

  assert {
    condition     = kubernetes_namespace_v1.cell.metadata[0].labels["app.kubernetes.io/part-of"] == "swarm"
    error_message = "Expected the part-of label to be swarm."
  }

  assert {
    condition     = kubernetes_namespace_v1.cell.metadata[0].labels["swarm-cell"] == "cell-feature-x-1a2b3c4d"
    error_message = "Expected the swarm-cell label to be the cell name."
  }

  assert {
    condition     = kubernetes_namespace_v1.cell.metadata[0].labels["policy.sigstore.dev/include"] == "true"
    error_message = "Expected the namespace to opt in to the policy controller."
  }

  assert {
    condition     = kubernetes_namespace_v1.cell.metadata[0].annotations["swarm-branch"] == "feature/x"
    error_message = "Expected the swarm-branch annotation to be the branch."
  }

  assert {
    condition     = random_password.object_storage_root.special == false
    error_message = "Expected a password without special characters."
  }

  assert {
    condition     = random_password.object_storage_root.length >= 32
    error_message = "Expected a password of at least 32 characters."
  }

  assert {
    condition     = kubernetes_secret_v1.object_storage_root.metadata[0].name == "object-storage-root"
    error_message = "Expected the secret to be named object-storage-root."
  }

  assert {
    condition     = kubernetes_secret_v1.object_storage_root.metadata[0].namespace == "cell-feature-x-1a2b3c4d"
    error_message = "Expected the secret to be in the cell namespace."
  }

  assert {
    condition     = contains(nonsensitive(keys(kubernetes_secret_v1.object_storage_root.data)), "MINIO_ROOT_USER")
    error_message = "Expected the MINIO_ROOT_USER key."
  }

  assert {
    condition     = contains(nonsensitive(keys(kubernetes_secret_v1.object_storage_root.data)), "MINIO_ROOT_PASSWORD")
    error_message = "Expected the MINIO_ROOT_PASSWORD key."
  }

  assert {
    condition     = output.namespace == "cell-feature-x-1a2b3c4d"
    error_message = "Expected the namespace output."
  }

  assert {
    condition     = output.object_storage_secret_name == "object-storage-root"
    error_message = "Expected the object storage secret name output."
  }
}

run "refuses_a_name_that_is_not_a_dns_label" {
  command = plan

  variables {
    name   = "Feature_X"
    branch = "feature/x"
  }

  expect_failures = [var.name]
}

run "refuses_a_name_longer_than_53_characters" {
  command = plan

  variables {
    name   = "cell-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    branch = "feature/x"
  }

  expect_failures = [var.name]
}

run "refuses_an_empty_branch" {
  command = plan

  variables {
    name   = "cell-feature-x-1a2b3c4d"
    branch = ""
  }

  expect_failures = [var.branch]
}
