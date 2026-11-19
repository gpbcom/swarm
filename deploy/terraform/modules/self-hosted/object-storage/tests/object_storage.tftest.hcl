mock_provider "minio" {}

run "creates_one_bucket_per_name" {
  command = plan

  variables {
    buckets = ["dev-deliverables", "dev-flight-logs"]
  }

  assert {
    condition     = length(minio_s3_bucket.bucket) == 2
    error_message = "Expected one bucket per name."
  }

  assert {
    condition     = contains(keys(minio_s3_bucket.bucket), "dev-deliverables") && contains(keys(minio_s3_bucket.bucket), "dev-flight-logs")
    error_message = "Expected the buckets to be keyed by name."
  }

  assert {
    condition     = contains(output.bucket_names, "dev-deliverables") && contains(output.bucket_names, "dev-flight-logs")
    error_message = "Expected bucket_names to hold both names."
  }
}

run "refuses_upper_case_bucket_names" {
  command = plan

  variables {
    buckets = ["Dev-Deliverables"]
  }

  expect_failures = [var.buckets]
}

run "refuses_too_short_bucket_names" {
  command = plan

  variables {
    buckets = ["ab"]
  }

  expect_failures = [var.buckets]
}
