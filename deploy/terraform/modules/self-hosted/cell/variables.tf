variable "name" {
  description = "The name of the cell, used as the namespace name. A DNS-1123 label of at most 52 characters."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]([-a-z0-9]{0,50}[a-z0-9])?$", var.name))
    error_message = "The name must be a DNS-1123 label of at most 52 characters."
  }
}

variable "branch" {
  description = "The Git branch the cell belongs to, kept in an annotation because label values cannot hold a slash."
  type        = string

  validation {
    condition     = length(var.branch) > 0
    error_message = "The branch must not be empty."
  }
}
