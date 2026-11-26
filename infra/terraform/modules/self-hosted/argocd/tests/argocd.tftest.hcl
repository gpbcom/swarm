mock_provider "helm" {}

variables {
  chart_version      = "0.0.1"
  apps_chart_version = "0.0.1"
  repository_url     = "https://git.example.org/swarm.git"
}

run "installs_argo_cd_and_the_platform_application" {
  command = plan

  assert {
    condition     = helm_release.argocd.chart == "argo-cd"
    error_message = "Expected the argo-cd chart."
  }

  assert {
    condition     = helm_release.argocd.repository == "https://argoproj.github.io/argo-helm"
    error_message = "Expected the argo-helm repository."
  }

  assert {
    condition     = helm_release.argocd.namespace == "argocd"
    error_message = "Expected the argocd namespace."
  }

  assert {
    condition     = helm_release.argocd.version == "0.0.1"
    error_message = "Expected the pinned chart version."
  }

  assert {
    condition     = helm_release.argocd.create_namespace == true
    error_message = "Expected the namespace to be created."
  }

  assert {
    condition     = helm_release.platform.chart == "argocd-apps"
    error_message = "Expected the argocd-apps chart."
  }

  assert {
    condition     = helm_release.platform.namespace == "argocd"
    error_message = "Expected the platform release in the argocd namespace."
  }

  assert {
    condition     = strcontains(helm_release.platform.values[0], "https://git.example.org/swarm.git")
    error_message = "Expected the repository URL in the Application."
  }

  assert {
    condition     = strcontains(helm_release.platform.values[0], "develop")
    error_message = "Expected the target revision in the Application."
  }

  assert {
    condition     = strcontains(helm_release.platform.values[0], "deploy/environments/dev/platform")
    error_message = "Expected the platform path in the Application."
  }

  assert {
    condition     = output.namespace == "argocd"
    error_message = "Expected output.namespace to be argocd."
  }

  assert {
    condition     = output.platform_application == "platform"
    error_message = "Expected output.platform_application to be platform."
  }
}

run "refuses_a_floating_chart_version" {
  command = plan

  variables {
    chart_version = "latest"
  }

  expect_failures = [var.chart_version]
}

run "refuses_a_missing_repository" {
  command = plan

  variables {
    repository_url = ""
  }

  expect_failures = [var.repository_url]
}
