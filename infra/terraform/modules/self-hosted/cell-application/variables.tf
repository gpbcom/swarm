variable "name" {
  description = "The name of the Argo CD Application and of its Helm release. It is a DNS-1123 label of at most 53 characters."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", var.name)) && length(var.name) <= 53
    error_message = "The name must be a DNS-1123 label of at most 53 characters."
  }
}

variable "namespace" {
  description = "The namespace of the cluster where Argo CD deploys the cell."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", var.namespace)) && length(var.namespace) <= 63
    error_message = "The namespace must be a DNS-1123 label of at most 63 characters."
  }
}

variable "argocd_namespace" {
  description = "The namespace where Argo CD runs and where the Application is created."
  type        = string
  default     = "argocd"
}

variable "repository_url" {
  description = "The URL of the Git repository that holds the umbrella chart."
  type        = string
}

variable "target_revision" {
  description = "The Git branch, tag or commit that Argo CD deploys."
  type        = string

  validation {
    condition     = trimspace(var.target_revision) != ""
    error_message = "The target revision must not be empty."
  }
}

variable "chart_path" {
  description = "The path of the umbrella chart in the repository."
  type        = string
  default     = "infra/charts/cell"
}

variable "values_files" {
  description = "The values files of the chart, relative to the chart path."
  type        = list(string)
  default     = ["../../environments/dev/values.yaml"]
}

variable "parameters" {
  description = "The Helm parameters that override the values files, by name."
  type        = map(string)
  default     = {}
}

variable "apps_chart_version" {
  description = "The version of the argocd-apps chart. It is pinned, so it is neither empty nor latest."
  type        = string

  validation {
    condition     = trimspace(var.apps_chart_version) != "" && lower(var.apps_chart_version) != "latest"
    error_message = "The argocd-apps chart version must be pinned, neither empty nor latest."
  }
}
