variable "chart_version" {
  description = "The pinned version of the argo-cd chart to install."
  type        = string

  validation {
    condition     = trimspace(var.chart_version) != "" && lower(trimspace(var.chart_version)) != "latest"
    error_message = "The argo-cd chart version must be pinned: it cannot be empty or latest."
  }
}

variable "apps_chart_version" {
  description = "The pinned version of the argocd-apps chart that creates the platform Application."
  type        = string

  validation {
    condition     = trimspace(var.apps_chart_version) != "" && lower(trimspace(var.apps_chart_version)) != "latest"
    error_message = "The argocd-apps chart version must be pinned: it cannot be empty or latest."
  }
}

variable "namespace" {
  description = "The namespace Argo CD is installed in, and where the platform Application lives."
  type        = string
  default     = "argocd"
}

variable "repository_url" {
  description = "The URL of the Git repository that holds the desired state of the cluster."
  type        = string

  validation {
    condition     = trimspace(var.repository_url) != ""
    error_message = "The repository URL cannot be empty."
  }
}

variable "target_revision" {
  description = "The branch, tag or commit of the repository that Argo CD follows."
  type        = string
  default     = "develop"
}

variable "platform_path" {
  description = "The path in the repository of the cluster-wide operators that the platform Application deploys."
  type        = string
  default     = "deploy/environments/dev/platform"
}
