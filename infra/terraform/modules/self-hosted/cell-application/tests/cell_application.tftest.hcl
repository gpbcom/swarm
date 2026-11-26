mock_provider "helm" {}

run "creates_the_argo_cd_application" {
  command = plan

  variables {
    name               = "cell-feature-x-1a2b3c4d"
    namespace          = "cell-feature-x-1a2b3c4d"
    repository_url     = "https://git.example.org/swarm.git"
    target_revision    = "feature/x"
    apps_chart_version = "2.0.2"
    parameters = {
      "database.imageName" = "registry.example.org/swarm-postgres:16"
    }
  }

  assert {
    condition     = helm_release.application.name == "cell-feature-x-1a2b3c4d"
    error_message = "Expected the release to be named after the cell."
  }

  assert {
    condition     = helm_release.application.namespace == "argocd"
    error_message = "Expected the release in the Argo CD namespace."
  }

  assert {
    condition     = helm_release.application.chart == "argocd-apps"
    error_message = "Expected the argocd-apps chart."
  }

  assert {
    condition     = helm_release.application.repository == "https://argoproj.github.io/argo-helm"
    error_message = "Expected the Argo Helm repository."
  }

  assert {
    condition     = strcontains(helm_release.application.values[0], "https://git.example.org/swarm.git")
    error_message = "Expected the repository URL in the values."
  }

  assert {
    condition     = strcontains(helm_release.application.values[0], "feature/x")
    error_message = "Expected the target revision in the values."
  }

  assert {
    condition     = strcontains(helm_release.application.values[0], "infra/charts/cell")
    error_message = "Expected the chart path in the values."
  }

  assert {
    condition     = strcontains(helm_release.application.values[0], "../../environments/dev/values.yaml")
    error_message = "Expected the values file in the values."
  }

  assert {
    condition     = strcontains(helm_release.application.values[0], "resources-finalizer.argocd.argoproj.io")
    error_message = "Expected the resources finalizer in the values."
  }

  assert {
    condition     = strcontains(helm_release.application.values[0], "namespace: cell-feature-x-1a2b3c4d")
    error_message = "Expected the destination namespace in the values."
  }

  assert {
    condition     = strcontains(helm_release.application.values[0], "database.imageName")
    error_message = "Expected the parameter name in the values."
  }

  assert {
    condition     = output.application_name == "cell-feature-x-1a2b3c4d"
    error_message = "Expected the application name output."
  }
}

run "refuses_an_empty_target_revision" {
  command = plan

  variables {
    name               = "cell-feature-x-1a2b3c4d"
    namespace          = "cell-feature-x-1a2b3c4d"
    repository_url     = "https://git.example.org/swarm.git"
    target_revision    = ""
    apps_chart_version = "2.0.2"
  }

  expect_failures = [var.target_revision]
}

run "refuses_the_latest_apps_chart_version" {
  command = plan

  variables {
    name               = "cell-feature-x-1a2b3c4d"
    namespace          = "cell-feature-x-1a2b3c4d"
    repository_url     = "https://git.example.org/swarm.git"
    target_revision    = "feature/x"
    apps_chart_version = "latest"
  }

  expect_failures = [var.apps_chart_version]
}
