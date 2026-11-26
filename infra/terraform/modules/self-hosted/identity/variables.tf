variable "namespace" {
  description = "The namespace of the global layer. It is a DNS-1123 label of at most 63 characters."
  type        = string
  default     = "global"

  validation {
    condition     = can(regex("^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", var.namespace)) && length(var.namespace) <= 63
    error_message = "The namespace must be a DNS-1123 label of at most 63 characters."
  }
}

variable "admin_secret_name" {
  description = "The name of the Secret that holds the bootstrap admin of Keycloak. It is a DNS-1123 label of at most 63 characters."
  type        = string
  default     = "keycloak-admin"

  validation {
    condition     = can(regex("^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", var.admin_secret_name)) && length(var.admin_secret_name) <= 63
    error_message = "The admin secret name must be a DNS-1123 label of at most 63 characters."
  }
}
