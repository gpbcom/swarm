variable "branch" {
  description = "The Git branch the cell belongs to. Argo CD deploys this branch."
  type        = string

  validation {
    condition     = trimspace(var.branch) != ""
    error_message = "The branch must not be empty."
  }
}

variable "cell_name" {
  description = "The name of the cell, used as its namespace and as the name of its Argo CD Application. A DNS-1123 label of at most 53 characters."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", var.cell_name)) && length(var.cell_name) <= 53
    error_message = "The cell name must be a DNS-1123 label of at most 53 characters."
  }
}

variable "kubeconfig_path" {
  description = "The path of the kubeconfig of the shared dev cluster, kept outside the repository."
  type        = string
}

variable "repository_url" {
  description = "The URL of the Git repository that holds the umbrella chart."
  type        = string
}

variable "database_image" {
  description = "The reference of the database image the cell runs, passed to the chart as database.imageName."
  type        = string

  validation {
    condition     = trimspace(var.database_image) != ""
    error_message = "The database image must not be empty."
  }
}

variable "openbao_chart_version" {
  description = "The version of the openbao Helm chart, pinned."
  type        = string
}

variable "argocd_apps_chart_version" {
  description = "The version of the argocd-apps Helm chart, pinned."
  type        = string
}

variable "argocd_namespace" {
  description = "The namespace where Argo CD runs and where the Application is created."
  type        = string
  default     = "argocd"
}
