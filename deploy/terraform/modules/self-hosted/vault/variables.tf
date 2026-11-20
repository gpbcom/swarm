variable "namespace" {
  description = "Namespace of the cell that receives the vault."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", var.namespace)) && length(var.namespace) <= 53
    error_message = "The namespace must be a DNS-1123 label of at most 53 characters."
  }
}

variable "chart_version" {
  description = "Version of the openbao Helm chart, pinned."
  type        = string

  validation {
    condition     = var.chart_version != "" && var.chart_version != "latest"
    error_message = "The chart version must be pinned: it is neither empty nor latest."
  }
}

variable "release_name" {
  description = "Name of the Helm release, which is also the name of the vault service."
  type        = string
  default     = "openbao"
}
